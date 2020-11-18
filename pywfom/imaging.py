import numpy as np
import threading, time, traceback, cv2, os, ctypes, platform, queue, threading, sys
from ctypes import POINTER, c_int, c_uint, c_double
"""
try:
    import PySpin
except ModuleNotFoundError:
    msg = "\nPySpin is not installed\nFollow the directions here to install it:\
    \n\nhttps://github.com/ryan-byrne/pywfom/wiki/Cameras:-Spinnaker\n"
    raise ModuleNotFoundError(msg
    )

_stdcall_libraries = {}

arch, plat = platform.architecture()

if platform.mac_ver() != "":
    raise OSError("The Andor SDK3 is not currently compatible with MacOS")

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
"""

class Camera(object):

    def __init__(self, type="", index=0, name="", config=None):

        for k, v in config.items():
            self._set(k,v)

        if not self.type and type not in ["spinnaker", "andor", "webcam", "test"]:
            raise Exception("You must indicate a Camera Type.")

        self._start()

        self.frame = np.zeros((500,500), dtype="uint8")
        self.active = True
        self.error_msg = ""

        threading.Thread(target=self._update_frame).start()

    def _start(self):

        if self.type == "webcam":
            self._camera = cv2.VideoCapture(self.index)
            self.error_msg = ""

    def _stop(self):
        if self.type == "webcam":
            pass

    def _update_frame(self):

        while self.active:

            if self.error_msg != "":
                self._error_frame()
                continue

            # Generates a numpy array for the self.frame variable
            if self.type == "webcam":
                self.frame = self._get_webcam_frame()

            elif self.type == "spinnaker":
                self.frame = self._get_spinnaker_frame()

            elif self.type == "andor":
                self.frame = self._get_andor_frame()

            else:
                self.frame = self._get_test_frame()


    def _error_frame(self):

        #print("ERROR: "+self.error_msg)

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

    def _get_andor_frame(self):
        # If not paused or testing, get next buffer from camera
        try:
            buf = self._buffers.get()
            WaitBuffer(self._handle, 100)
            self.error_msg = ""
            # Reformat buffer to a frame
            frame = np.array(buf).view(np.uint16).reshape((self.height, self.width))
            # Queue up next buffer
            QueueBuffer(self._handle, buf.ctypes.data_as(POINTER(AT_U8)), buf.nbytes)
            self._buffers.put(buf)
            return frame
        except:
            self.error_msg = "{0}:{1} at index:{2}".format(self.type,self.name,self.index)

    def _get_webcam_frame(self):
        try:
            frame = self._camera.read()[1]
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.error_msg = ""
            x, y, w, h = self.OffsetX, self.OffsetY, self.Width, self.Height
            return frame[y:h+y, x:w+x]
        except:
            self.error_msg = "{0}:{1} at index:{2}".format(self.type,self.name,self.index)

    def _get_spinnaker_frame(self):
        try:
            image_result = self._camera.GetNextImage(1000)
            img = np.reshape(   image_result.GetData(),
                                (image_result.GetHeight(),image_result.GetWidth())
                            )
            image_result.Release()
            self.frame = img
            self.error_msg = ""
        except:
            self.error_msg = "{0}:{1} at index:{2}".format(self.type,self.name,self.index)

    def _get_test_frame(self):

        if self.dtype == 'uint8':
            max = 255
        else:
            max = 65024

        return np.random.randint(0,max,size=(self.Height, self.Width), dtype=self.dtype)

    def set(self, param, value=None):

        # TODO: Change camera type -> check if andor

        self._stop()

        if type(param).__name__ == 'dict':
            for k, v in param.items():
                self._set(k, v)
        else:
            self._set(param, value)

        self._start()

    def _set(self, param, value):

        if param in ["camera"]:
            return

        setattr(self, param, value)

    def get(self, param):
        pass

    def _get(self, param):
        pass

    def get_max(self, param):
        if self.type in ["webcam", "test"]:
            if param == "Height":
                return 700
            elif param == "Width":
                return 1200

    def close(self):
        self.active = False


class Andor(object):

    def __init__(self, config):
        '''camera initialisation - note that this should be called  from derived classes
        *AFTER* the properties have been defined'''

        print("{1} : Initialising Andor Camera at Port {0}".format(camera_idx, name))
        self._handle = Open(camera_idx)

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
            "PixelEncoding":str,
            "SerialNumber":str
        }

        if not settings:
            self.settings = {}
            self.settings["index"] = camera_idx
            self.settings["name"] = name
            self.settings["type"] = "andor"
        else:
            self.settings = settings


        self._num_bfrs = num_bfrs
        self.error_msg = ""
        self.active = False

        self.get("SerialNumber")

        if self.settings["SerialNumber"][:3] == "SFT":
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
                self.error_msg = ""
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
            for setting in param:
                self._get(setting)
        else:
            self._get(param)

    def _get(self, param):

        if param in ["index", "name", "type"] or not self._handle:
            return

        print(self.settings)

        print("{1} : Getting {0} -> ".format(param, self.settings["name"]), end="")

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

        print(val)
        self.settings[param] = val

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

class FlirError(Exception):
    pass

class Spinnaker(object):
    """docstring for Flir."""

    def __init__(self, config):

        for k, v in config.items():
            setattr(self, k, v)

        self.pointers = {
            float:PySpin.CFloatPtr,
            int:PySpin.CIntegerPtr,
            str:PySpin.CEnumerationPtr
        }

        self.active, self.paused = False, True

        self.system = PySpin.System.GetInstance()
        self.error_msg = ""

        # Check chosen index for a camera
        try:
            print("{0} : Connecting to Camera (PySpin Index: {1})".format(self.name, self.index))
            self.camera = self.system.GetCameras()[self.index]
            print("{0} : Initialising (FLIR SN: {1})".format(self.name, self.get_serial_number()))
            # initialize camera and create node map
            try:
                self.camera.DeInit()
                self.camera.Init()
                self.active = True
            except PySpin.SpinnakerException:
                self.error_msg = "Camera is already started at idx={0}".format(self.index)
                self._error_frame()
            self.nodemap = self.camera.GetNodeMap()
        except IndexError:
            self.error_msg = "No FLIR Camera Found (idx={0})".format(self.index)
            print("ERROR: "+self.error_msg)
            self._error_frame()
            return

        # Get the current setting of the camera
        self.get(list(self.types.keys()))

        # Create a temporary frame while the camera loads
        self.frame = np.zeros((500,500), 'uint8')

        threading.Thread(target=self._update_frames).start()

    def set(self, param, value=""):

        if self.error_msg != "":
            print("Unable change setting. Error in "+self.name)
            return

        self._stop_camera()

        if type(param).__name__ == 'dict':
            for k, v in param.items():
                self._set(k, v)
        else:
            self._set(param, value)

        self._start_camera()
        self.paused = False

    def _set(self, param, value):

        if not self.paused:
            print("{0} : Unable to change settings. Camera is still acquiring.".format(self.name))
            return
        elif param in ['name', 'index', 'type']:
            return

        node = self.pointers[self.types[param]](self.nodemap.GetNode(param))

        if self.types[param] == str:
            node.SetIntValue(node.GetEntryByName(value).GetValue())
            return
        elif self.types[param] == float:
            pass
        else:
            if param in ["Height", "Width"]:
                min = 40
            else:
                min = self.get_min(param)
            max = self.get_max(param)
            inc = self.get_inc(param)

            if value > max:
                value = max
            elif value < min:
                value = min
            else:
                pass

            while not (value - min)%inc == 0:
                value += 1

        node.SetValue(value)

    def get(self, param=None):

        self._stop_camera()

        if type(param).__name__ == "list":
            for p in param:
                self._get(p)
        else:
            self._get(param)

        self._start_camera()

    def _get(self, param):

        if param in ["index", "name", "type"]:
            return param

        print("{0} : Getting {1} -> ".format(self.settings['name'], param), end="")

        node = self.pointers[self.types[param]](self.nodemap.GetNode(param))

        if self.types[param] == str:
            value = node.GetCurrentEntry().GetSymbolic()
        else:
            value = node.GetValue()

        print(value)
        self.settings[param] = value
        return value

    def get_max(self, param):
        node = self.pointers[self.types[param]](self.nodemap.GetNode(param))
        return node.GetMax()

    def get_inc(self, param):
        node = self.pointers[self.types[param]](self.nodemap.GetNode(param))
        return node.GetInc()

    def get_min(self, param):
        node = self.pointers[self.types[param]](self.nodemap.GetNode(param))
        return node.GetMin()

    def get_serial_number(self):
        return PySpin.CStringPtr(self.camera.GetTLDeviceNodeMap().GetNode('DeviceSerialNumber')).GetValue()

    def _update_frames(self):

        self.active = True

        while self.active:
            if self.paused:
                continue
            try:
                image_result = self.camera.GetNextImage(1000)
                img = np.reshape(   image_result.GetData(),
                                    (image_result.GetHeight(),image_result.GetWidth())
                                )
                image_result.Release()
                self.frame = img
                self.error_msg = ""

            except PySpin.SpinnakerException as e:
                self.error_msg = "Timed out waiting for image"
                self._error_frame()
                pass

        self._stop_camera()

    def _start_camera(self):

        try:
            self.paused = False
            self.camera.BeginAcquisition()
            print("{0} : Acquiring frames".format(self.name))
        except:
            self._error_frame()
            return

    def _stop_camera(self):
        try:
            self.paused = True
            self.camera.EndAcquisition()
            print("{0} : Stopping Acquisition".format(self.name))
        except:
            self._error_frame()
            return

    def _error_frame(self):
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

        self.active = False

        print("Clearing Camera list...")

        self.system.GetCameras().Clear()

class Webcam(object):
    """docstring for SimpleUSB."""

    def __init__(self, config):

        for k, v in config.items():
            self._set(k,v)

        self.frame = np.zeros((self.Height, self.Width), self.dtype)

        try:
            self.cap = cv2.VideoCapture(self.index)
            self.active = True
            self.error_msg = ""
        except:
            self.active = False
            self.error_msg = "Error"

        threading.Thread(target=self.update).start()

    def update(self):

        while self.active:
            ret, frame = self.cap.read()
            frame = frame[
                self.OffsetY:self.Height-self.OffsetY,
                self.OffsetX:self.Width-self.OffsetX
            ]
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def set(self, param, value=None):
        print(param)
        if type(param).__name__ == 'dict':
            for k, v in param.items():
                self._set(k, v)
        else:
            self._set(param, value)

    def _set(self, param, value):
        if param in ["cap"]:
            return
        else:
            setattr(self, param, value)

    def close(self):
        self.active = False

#InitialiseUtilityLibrary()
#InitialiseLibrary()
