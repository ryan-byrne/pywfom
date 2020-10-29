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

    def __init__(self, camera_idx=0, name="", num_bfrs=10):
        '''camera initialisation - note that this should be called  from derived classes
        *AFTER* the properties have been defined'''

        self.settings = {}

        self.settings["index"] = camera_idx
        self.settings["name"] = name
        self.settings["type"] = "andor"
        self.types = {
            "AOIHeight":int,
            "AOIWidth":int,
            "AOILeft":int,
            "AOITop":int,
            "index":int,
            "name":str,
            "AOIBinning":str,
            "AuxiliaryOutSource":str,
            "CycleMode":str,
            "FrameRate":float,
            "TriggerMode":str,
            "PixelEncoding":str
        }
        self._num_bfrs = num_bfrs

        self.error_msg = ""
        self.active = False

        print("{1} : Initialising Andor Camera at Port {0}".format(camera_idx, name))
        self._handle = Open(camera_idx)
        self.serial_number = self.get("SerialNumber")

        if self.serial_number[:3] == "SFT":
            # If SimCam Andor Object
            self.error_msg = "No Andor Camera found (idx={0})".format(camera_idx)
            self._error_frame()
            return
        else:
            # If physical Andor Camera
            firmware = self.get("FirmwareVersion")
            self.set(self.settings)

        threading.Thread(target=self._update_buffers).start()

    def _create_buffers(self):

        """

        Internal Method to create Queue of 1D Numpy buffers which the Camera
        will then populate.

        """

        if not self.active:
            return

        # Get size of buffers
        self.image_size_bytes = self.get("ImageSizeBytes")
        # Get New height
        self.height = self.get("AOIHeight")
        # Get new width
        self.width = self.get("AOIWidth")
        # Create empty frame
        self.frame = np.zeros((self.height, self.width), dtype='uint16')

        # Return if in test mode
        if self.test:
            return

        # Flushing camera buffers
        Flush(self._handle)
        # Create empty queue for buffers
        self._buffers = queue.Queue()

        print("\nCreating {3} buffers of {0} bytes, for a {1}x{2} Image".format(
                self.image_size_bytes,
                self.height,
                self.width,
                self._num_bfrs
        ))

        # Populate the queue and buffer with empty numpy arrays
        for i in range(self._num_bfrs):
            buf = np.zeros((self.image_size_bytes), 'uint8')
            QueueBuffer(self._handle, buf.ctypes.data_as(POINTER(AT_U8)), buf.nbytes)
            self._buffers.put(buf)

    def _update_buffers(self):

        # Create initial buffers
        self._create_buffers()

        Command(self._handle, "AcquisitionStart")

        print("Reading camera buffer and sending to self.frame...")

        self.active = True
        self._paused = False

        # Update frame while camera is active
        while self.active:
            # Continue if acquisition is paused
            if self._paused:
                continue
            # If not paused or testing, get next buffer from camera
            try:
                buf = self._buffers.get()
                WaitBuffer(self._handle, 100)
            except:
                msg = "Could not read buffer"
                print(msg)
                self.error_msg = msg
                self._error_frame()
                self.active = False
                break
            # Reformat buffer to a frame
            self.frame = np.array(buf).view(np.uint16).reshape((self.height, self.width))
            # Queue up next buffer
            QueueBuffer(self._handle, buf.ctypes.data_as(POINTER(AT_U8)), buf.nbytes)
            self._buffers.put(buf)

    def _set(self, setting, value):

        cmd = {
            'bool':SetBool,
            'str':SetEnumString,
            'int':SetInt,
            'float':SetFloat
        }
        print("{0} : Setting {1} -> {2}".format(self.settings['name'], setting, value))
        self.settings[setting] = value

        if setting in ['name', 'index'] or not self.active:
            return

        try:
            print("{2} : Setting {0} -> {1}".format(setting, value, self.settings["name"]))
            cmd[type(value).__name__](self._handle, setting, value)
        except CameraError as e:
            if e.errNo in [2, 5]:
                TypeError("'{0}' cannot be '{1}'".format(setting, type(value).__name__))
            elif e.errNo == 6:
                ValueError("'{0}' is out of range for '{1}'".format(setting, type(value).__name__))
            else:
                raise

    def set(self, param, val=""):

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

        # Pausing acquisition
        self._paused = True

        if type(param).__name__ == 'dict':
            for setting in param.keys():
                self._set(setting, param[setting])
        else:
            self._set(param, val)

        # Reset the buffers
        self._create_buffers()
        # Continue acquiring with new settings
        self._paused = False

    def get(self, param):

        if type(param).__name__ == 'list':
            settings = {}
            for setting in param:
                settings[setting] = self._get(setting)
            return settings
        else:
            return self._get(param)

    def _get(self, param):

        print("{1} : Getting {0}".format(param, self.settings["name"]))

        try:
            val = GetString(self._handle, param, 255).value
        except:
            try:
                i = GetEnumIndex(self._handle, param).value
                val = GetEnumStringByIndex(self._handle, param, i, 255).value
            except:
                try:
                    val = GetInt(self._handle, param).value
                except:
                    try:
                        val = GetFloat(self._handle, param).value
                    except:
                        val = GetBool(self._handle, param).value
        return val

    def _error_frame(self):

        print("ERROR: "+self.error_msg)

        img = np.zeros((512,512,3), np.uint8)
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10,500)
        fontScale              = 0.75
        fontColor              = (255,255,255)
        lineType               = 2

        cv2.putText(img,"ERROR: "+self.error_msg,
            bottomLeftCornerOfText,
            font,
            fontScale,
            fontColor,
            lineType)

        self.frame = img

    def close(self):
        try:
            print("Shutting down {0}...".format(self.serial_number))
            Command(self._handle, "AcquisitionStop")
            self.active = False
        except:
            pass
        Close(self._handle)
        FinaliseLibrary()

InitialiseUtilityLibrary()
InitialiseLibrary()
