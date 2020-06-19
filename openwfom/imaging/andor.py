from ctypes import POINTER, c_int, c_uint, c_double
import time, os, ctypes, platform, queue, cv2, threading, sys
import numpy as np

_stdcall_libraries = {}

arch, plat = platform.architecture()

if plat.startswith('Windows'):
    try:
        _stdcall_libraries['ATCORE'] = ctypes.WinDLL('atcore.dll')
        _stdcall_libraries['ATUTIL'] = ctypes.WinDLL('atutility.dll')
    except OSError:
        print('\natcore and atutlity DLL not found\n')
        print("Add {0} to your PATH\n".format("C:\\Program Files\\Andor SDK3"))
        raise
else:
    _stdcall_libraries['ATCORE'] = ctypes.CDLL('atcore.so')
    _stdcall_libraries['ATUTIL'] = ctypes.CDLL('atutility.so')

# typedefs
AT_H = ctypes.c_int
AT_BOOL = ctypes.c_int
AT_64 = ctypes.c_int64
AT_U8 = ctypes.c_uint8
AT_16 = ctypes.c_int16
AT_U16 = ctypes.c_uint16
AT_WC = ctypes.c_wchar


# Defines
errorCodes = {}


def errCode(name, value):
    errorCodes[value] = name


AT_INFINITE = 0xFFFFFFFF
AT_CALLBACK_SUCCESS = 0

AT_TRUE = 1
AT_FALSE = 0

AT_SUCCESS = 0
errCode('AT_ERR_NOTINITIALISED', 1)
errCode('AT_ERR_NOTIMPLEMENTED', 2)
errCode('AT_ERR_READONLY', 3)
errCode('AT_ERR_NOTREADABLE', 4)
errCode('AT_ERR_NOTWRITABLE', 5)
errCode('AT_ERR_OUTOFRANGE', 6)
errCode('AT_ERR_INDEXNOTAVAILABLE', 7)
errCode('AT_ERR_INDEXNOTIMPLEMENTED', 8)
errCode('AT_ERR_EXCEEDEDMAXSTRINGLENGTH', 9)
errCode('AT_ERR_CONNECTION', 10)
errCode('AT_ERR_NODATA', 11)
errCode('AT_ERR_INVALIDHANDLE', 12)
errCode('AT_ERR_TIMEDOUT', 13)
errCode('AT_ERR_BUFFERFULL', 14)
errCode('AT_ERR_INVALIDSIZE', 15)
errCode('AT_ERR_INVALIDALIGNMENT', 16)
errCode('AT_ERR_COMM', 17)
errCode('AT_ERR_STRINGNOTAVAILABLE', 18)
errCode('AT_ERR_STRINGNOTIMPLEMENTED', 19)

errCode('AT_ERR_NULL_FEATURE', 20)
errCode('AT_ERR_NULL_HANDLE', 21)
errCode('AT_ERR_NULL_IMPLEMENTED_VAR', 22)
errCode('AT_ERR_NULL_READABLE_VAR', 23)
errCode('AT_ERR_NULL_READONLY_VAR', 24)
errCode('AT_ERR_NULL_WRITABLE_VAR', 25)
errCode('AT_ERR_NULL_MINVALUE', 26)
errCode('AT_ERR_NULL_MAXVALUE', 27)
errCode('AT_ERR_NULL_VALUE', 28)
errCode('AT_ERR_NULL_STRING', 29)
errCode('AT_ERR_NULL_COUNT_VAR', 30)
errCode('AT_ERR_NULL_ISAVAILABLE_VAR', 31)
errCode('AT_ERR_NULL_MAXSTRINGLENGTH', 32)
errCode('AT_ERR_NULL_EVCALLBACK', 33)
errCode('AT_ERR_NULL_QUEUE_PTR', 34)
errCode('AT_ERR_NULL_WAIT_PTR', 35)
errCode('AT_ERR_NULL_PTRSIZE', 36)
errCode('AT_ERR_NOMEMORY', 37)

errCode('AT_ERR_HARDWARE_OVERFLOW', 100)

class CameraError(Exception):
    def __init__(self, fcnName, errNo):
        self.errNo = errNo
        self.fcnName = fcnName

    def __str__(self):
        return 'when calling %s - %s' % (self.fcnName, errorCodes[self.errNo])


# special case for buffer timeout
AT_ERR_TIMEDOUT = 13
AT_ERR_NODATA = 11


class TimeoutError(CameraError):
    pass

AT_HANDLE_UNINITIALISED = -1
AT_HANDLE_SYSTEM = 1

### Functions ###
STRING = POINTER(AT_WC)

# classes so that we do some magic and automatically add byrefs etc ... can classify outputs

class _meta(object):
    pass


class OUTPUT(_meta):
    def __init__(self, val):
        self.type = val
        self.val = POINTER(val)

    def getVar(self, bufLen=0):
        v = self.type()
        return v, ctypes.byref(v)


class _OUTSTRING(OUTPUT):
    def __init__(self):
        self.val = STRING

    def getVar(self, bufLen):
        v = ctypes.create_unicode_buffer(bufLen)
        return v, v


OUTSTRING = _OUTSTRING()


class _OUTSTRLEN(_meta):
    def __init__(self):
        self.val = c_int


OUTSTRLEN = _OUTSTRLEN()

def stripMeta(val):
    if isinstance(val, _meta):
        return val.val
    else:
        return val


class dllFunction(object):
    def __init__(self, name, args=[], argnames=[], lib='ATCORE'):
        self.f = getattr(_stdcall_libraries[lib], name)
        self.f.restype = c_int
        self.f.argtypes = [stripMeta(a) for a in args]

        self.fargs = args
        self.fargnames = argnames
        self.name = name

        self.inp = [not isinstance(a, OUTPUT) for a in args]
        self.in_args = [a for a in args if not isinstance(a, OUTPUT)]
        self.out_args = [a for a in args if isinstance(a, OUTPUT)]

        self.buf_size_arg_pos = -1
        for i in range(len(self.in_args)):
            if isinstance(self.in_args[i], _OUTSTRLEN):
                self.buf_size_arg_pos = i

        ds = name + '\n\nArguments:\n===========\n'
        for i in range(len(args)):
            an = ''
            if i < len(argnames):
                an = argnames[i]
            ds += '\t%s\t%s\n' % (args[i], an)

        self.f.__doc__ = ds

    def __call__(self, *args):
        ars = []
        i = 0
        ret = []

        if self.buf_size_arg_pos >= 0:
            bs = args[self.buf_size_arg_pos]
        else:
            bs = 255

        for j in range(len(self.inp)):
            if self.inp[j]:  # an input
                ars.append(args[i])
                i += 1
            else:  # an output
                r, ar = self.fargs[j].getVar(bs)
                ars.append(ar)
                ret.append(r)
                # print r, r._type_

        # print ars
        res = self.f(*ars)
        # print res

        if not res == AT_SUCCESS:
            if res == AT_ERR_TIMEDOUT or res == AT_ERR_NODATA:
                # handle timeouts as a special case, as we expect to get them
                raise TimeoutError(self.name, res)
            else:
                raise CameraError(self.name, res)

        if len(ret) == 0:
            return None
        if len(ret) == 1:
            return ret[0]
        else:
            return ret

def dllFunc(name, args=[], argnames=[], lib='ATCORE'):
    f = dllFunction(name, args, argnames, lib)
    globals()[name[3:]] = f


dllFunc('AT_InitialiseLibrary')
dllFunc('AT_FinaliseLibrary')

dllFunc('AT_Open', [c_int, OUTPUT(AT_H)])
dllFunc('AT_Close', [AT_H])

dllFunc('AT_IsImplemented', [AT_H, STRING, OUTPUT(AT_BOOL)])
dllFunc('AT_IsReadable', [AT_H, STRING, OUTPUT(AT_BOOL)])
dllFunc('AT_IsWritable', [AT_H, STRING, OUTPUT(AT_BOOL)])
dllFunc('AT_IsReadOnly', [AT_H, STRING, OUTPUT(AT_BOOL)])

dllFunc('AT_SetInt', [AT_H, STRING, AT_64])
dllFunc('AT_GetInt', [AT_H, STRING, OUTPUT(AT_64)])
dllFunc('AT_GetIntMax', [AT_H, STRING, OUTPUT(AT_64)])
dllFunc('AT_GetIntMin', [AT_H, STRING, OUTPUT(AT_64)])

dllFunc('AT_SetFloat', [AT_H, STRING, c_double])
dllFunc('AT_GetFloat', [AT_H, STRING, OUTPUT(c_double)])
dllFunc('AT_GetFloatMax', [AT_H, STRING, OUTPUT(c_double)])
dllFunc('AT_GetFloatMin', [AT_H, STRING, OUTPUT(c_double)])

dllFunc('AT_SetBool', [AT_H, STRING, AT_BOOL])
dllFunc('AT_GetBool', [AT_H, STRING, OUTPUT(AT_BOOL)])

dllFunc('AT_SetEnumerated', [AT_H, STRING, c_int])
dllFunc('AT_SetEnumeratedString', [AT_H, STRING, STRING])
dllFunc('AT_GetEnumerated', [AT_H, STRING, OUTPUT(c_int)])
dllFunc('AT_GetEnumeratedCount', [AT_H, STRING, OUTPUT(c_int)])
dllFunc('AT_IsEnumeratedIndexAvailable', [AT_H, STRING, c_int, OUTPUT(AT_BOOL)])
dllFunc('AT_IsEnumeratedIndexImplemented', [AT_H, STRING, c_int, OUTPUT(AT_BOOL)])
dllFunc('AT_GetEnumeratedString', [AT_H, STRING, c_int, OUTSTRING, OUTSTRLEN])

dllFunc('AT_SetEnumIndex', [AT_H, STRING, c_int])
dllFunc('AT_SetEnumString', [AT_H, STRING, STRING])
dllFunc('AT_GetEnumIndex', [AT_H, STRING, OUTPUT(c_int)])
dllFunc('AT_GetEnumCount', [AT_H, STRING, OUTPUT(c_int)])
dllFunc('AT_IsEnumIndexAvailable', [AT_H, STRING, c_int, OUTPUT(AT_BOOL)])
dllFunc('AT_IsEnumIndexImplemented', [AT_H, STRING, c_int, OUTPUT(AT_BOOL)])
dllFunc('AT_GetEnumStringByIndex', [AT_H, STRING, c_int, OUTSTRING, OUTSTRLEN])

dllFunc('AT_Command', [AT_H, POINTER(AT_WC)])

dllFunc('AT_SetString', [AT_H, STRING, STRING])
dllFunc('AT_GetString', [AT_H, STRING, OUTSTRING, OUTSTRLEN])
dllFunc('AT_GetStringMaxLength', [AT_H, STRING, OUTPUT(c_int)])

dllFunc('AT_QueueBuffer', [AT_H, POINTER(AT_U8), c_int])
dllFunc('AT_WaitBuffer', [AT_H, OUTPUT(POINTER(AT_U8)), OUTPUT(c_int), c_uint])
dllFunc('AT_Flush', [AT_H])

#####################################
# Utility library (for unpacking etc ...)
dllFunc('AT_InitialiseUtilityLibrary', lib='ATUTIL')
dllFunc('AT_FinaliseUtilityLibrary', lib='ATUTIL')
dllFunc('AT_ConvertBuffer', [POINTER(AT_U8), POINTER(AT_U8), AT_64, AT_64, AT_64, STRING, STRING], lib='ATUTIL')
dllFunc('AT_ConvertBufferUsingMetadata', [POINTER(AT_U8), POINTER(AT_U8), AT_64, STRING], lib='ATUTIL')

class Camera(object):
    def __init__(self, camNum):
        '''camera initialisation - note that this should be called  from derived classes
        *AFTER* the properties have been defined'''
        print("Initialising Camera at Port {0}".format(camNum))
        self.camNum = camNum
        self._handle = Open(self.camNum)
        self.serial_number = self.get("SerialNumber")
        if self.serial_number[:3] == "SFT":
            raise ConnectionError("No Andor Cameras were found")
        self.active = True
        self.num_bufs = 100
        print("\nSuccessfully Opened Camera {0}\nSN: {1}\nFirmware Version: {2}\n".format(camNum, self.get("SerialNumber"), self.get("FirmwareVersion")))

    def set(self, val, param=""):

        """

        Sets the Camera value of Setting 'param' to 'val'.

        self.set(param="FrameRate", val=25) or self.set("FrameRate", 25)

        Also can take 'dict' objects to handle multiple settings as once.

        For example:

        val = {
            "AOIHeight":500,
            "AOIWidth":500
        }

        Would set both "AOIHeight" and "AOIWidth"

        """

        if type(val).__name__ == 'dict':
            for setting in val.keys():
                self._set(setting, val[setting])
        else:
            self._set(param, val)

    def _set(self, setting, value):

        cmd = {
            'bool':SetBool,
            'str':SetEnumString,
            'int':SetInt,
            'float':SetFloat
        }

        #print("Setting {0} -> {1}".format(setting, value))

        try:
            cmd[type(value).__name__](self._handle, setting, value)
        except CameraError as e:
            if e.errNo == 2:
                TypeError("'{0}' cannot be '{1}'".format(setting, type(value).__name__))
            elif e.errNo == 6:
                ValueError("'{0}' is out of range for '{1}'".format(setting, type(value).__name__))
            else:
                raise

    def get(self, param):

        cmd = {
            'bool':GetBool,
            'str':GetString,
            'int':GetInt,
            'float':GetFloat
        }

        try:
            return cmd['str'](self._handle, param, 255).value
        except:
            try:
                return cmd['int'](self._handle, param).value
            except:
                try:
                    return cmd['float'](self._handle, param).value
                except:
                    try:
                        return cmd['bool'](self._handle, param).value
                    except:
                        raise TypeError("{0} is not an available setting for {1}".format(param, self.get("SerialNumber")))

    def capture(self, mode, val, view=False, save=False, path=""):

        """

        mode : Whether to capture for # of Frames, or # of Seconds
        val : Value of either frames or seconds the camera will capture
        view : Display preview of Camera as it captures
        save : Save data to disk as it captures
        path : Where to save data captured.

        """

        if save and path == "":
            raise ValueError("You must provide a path if you wish to save your data.")
        elif mode not in ['frames', 'time']:
            raise ValueError("Capture mode must be set to either 'frames' or 'time'")
        elif mode == 'frames' and type(val).__name__ != 'int':
            raise ValueError("'val' must be an 'int' when 'mode' is set to frames")
        elif mode == 'time' and type(val).__name__ not in ['int', 'float']:
            raise ValueError("'val' must be an 'int' or 'float' when 'mode' is set to frames")
        else:
            nbytes = self.get("ImageSizeBytes")
            h = self.get("AOIHeight")
            w = self.get("AOIWidth")
            self.set("CycleMode", "Continuous")
            print("Grabbing {0}x{1} Frame(s) from {2}".format(h,w,self.serial_number))

        if view:
            #print("Creating 2D Frame Array...")
            self.frame = np.zeros((h, w))
            self.view = True
            threading.Thread(target=self._show_frame).start()
        else:
            pass

        #print("Creating and Queuing Buffers...")
        buffers = queue.Queue()
        for i in range(self.num_bufs):
            buf = np.zeros((nbytes), 'uint8')
            QueueBuffer(self._handle, buf.ctypes.data_as(POINTER(AT_U8)), buf.nbytes)
            buffers.put(buf)

        #print("Starting Acquisition...")
        Command(self._handle, "AcquisitionStart")
        for i in range(val):
            buf = buffers.get()
            WaitBuffer(self._handle, 100)
            QueueBuffer(self._handle, buf.ctypes.data_as(POINTER(AT_U8)), buf.nbytes)
            buffers.put(buf)

        Command(self._handle, "AcquisitionStop")
        Flush(self._handle)

    def _show_frame(self):
        print("Starting preview of frame...")
        while self.active:
            if self.view:
                cv2.imshow(self.serial_number, self.frame)
                cv2.waitKey(1)
            else:
                pass

    def shutdown(self):
        print("Shutting down {0}...".format(self.get("SerialNumber")))
        self.active = False
        Close(self._handle)
        FinaliseLibrary()

InitialiseUtilityLibrary()
InitialiseLibrary()
