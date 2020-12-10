import numpy as np
import threading, time, traceback, cv2, os, ctypes, platform, queue, threading
import sys, PySpin
from pywfom import andor
from PIL import Image, ImageDraw, ImageFont

class CameraError(Exception):
    """docstring for CameraError."""
    pass

class Camera(object):

    def __init__(self, config=None):

        # Establish default settings
        self.camera = None
        self.default = {
            "device":"webcam",
            "name":"default1",
            "index":0,
            "Height":700,
            "Width":1200,
            "AcquisitionFrameRate":50.0,
            "master":True,
            "dtype":"uint16",
            "OffsetX":0,
            "OffsetY":0
        }
        self.max_frame = (None, None)

        if not config:
            config = self.default

        for k, v in config.items():
            setattr(self, k, v)

        try:

            print("Initializing '{0}' at index:{1}".format(self.device, self.index))

            if self.device not in ["webcam", "spinnaker", "andor", "test"]:
                raise TypeError("Invalid device type '{0}'".format(self.device))
                return

            devices = {
                "webcam":Webcam,
                "spinnaker":Spinnaker,
                "andor":Andor,
                "test":Test
            }

            self.camera = devices[self.device](self, config)

        except (IndexError, CameraError, AttributeError) as e:
            msg = "({2}) No '{1}' camera not found with index:{0}".format(config['index'], config['device'], config['name'])

    def _update(self):

        self.active = True

        while self.active:
            # Ignore if there's an error
            # Generates a numpy array for the self.frame variable
            try:
                self.frame = self.camera.read()
            except Exception as e:
                self.frame = self._error_frame(traceback.format_exc())

    def _error_frame(self, msg):

        # Create a frame announcing the error
        img = Image.fromarray(np.zeros((500,500), "uint8"))
        draw = ImageDraw.Draw(img)
        draw.text((10, 175), "ERROR:", 255)
        draw.text((10,225), msg, 255)
        return np.asarray(img)

    def _loading_frame(self):
        # Create a frame announcing the error
        img = Image.fromarray(np.zeros((500,500), "uint8"))
        draw = ImageDraw.Draw(img)
        draw.text((200,250), "Loading Frame...", 255)
        return np.asarray(img)

    def set(self, setting, value=None):

        self.camera.stop()

        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                self._set(k, v)
        else:
            self._set(setting, value)

        self.camera.start()

    def _set(self, setting, value):

        if setting in ['master', 'device', 'name'] or not self.camera:
            setattr(self, setting, value)
            return

        vtype = type(value).__name__
        stype = type(self.default[setting]).__name__

        try:

            if stype != vtype:
                msg = "WARNING: '{0}' must be of type '{1}', not '{2}'\
                \nSetting to default of {3}".format(setting,stype,vtype,self.default[setting])
                print(msg)
                value = self.default[setting]
            elif value > self.camera.get_max(setting):
                msg = "WARNING: '{0}' must be less than the maximum of {1}".format(setting,self.camera.get_max(setting))
                print(msg)

            self.camera.set(setting, value)
            setattr(self, setting, value)

        except KeyError:

            msg = "\n\n'{0}' is not a valid configuration setting\n".format(setting)
            self.error_msg = msg

    def close(self):
        self.active = False

class Andor(object):

    def __init__(self, camera):

        self._handle = andor.Open(config['index'])
        print(self._handle)
        self._load_buffers()

    def set(self, setting, value):

        stype = type(setting).__name__

        setfunc = {
            'bool':andor.SetBool,
            'str':andor.SetEnumString,
            'int':andor.SetInt,
            'float':andor.SetFloat
        }

        setfunc[stype](self._handle, setting, value)
        setattr(self, setting, value)

    def start(self):
        andor.Command(self._handle, "AcquisitionStart")

    def stop(self):
        andor.Command(self._handle, "AcquisitionStop")

    def read(self):
        buf = self._buffers.get()
        andor.WaitBuffer(self._handle, 1000)
        img = (buf[::2]*buf[1::2]).reshape(self.height, self.width)
        andor.QueueBuffer(self._handle, buf.ctypes.data_as(POINTER(AT_U8)), buf.nbytes)

    def _load_buffers(self):
        self.num_bufs = 10
        self._buffers = queue.Queue()
        self._buffers.queue.clear()
        andor.Flush(self._handle)

        for i in range(self.num_bufs):
            buf = np.zeros((self.get("ImageSizeBytes")), 'uint8')
            andor.QueueBuffer(self._handle, buf.ctypes.data_as(POINTER(AT_U8)), buf.nbytes)
            self._buffers.put(buf)

    def shutdown(self):
        self.active = False
        andor.Close(self._handle)
        andor.FinaliseLibrary()

class Spinnaker(object):

    def __init__(self, config):

        self.system = PySpin.System.GetInstance()
        self.camera = self._system.GetCameras()[self.index]
        self.camera.Init()

    def read(self):
        image_result = self.camera.GetNextImage(1000)
        img = np.reshape(   image_result.GetData(),
                            (image_result.GetHeight(),image_result.GetWidth())
                        )
        image_result.Release()
        self.frame = img

    def set(self, setting, value):

        if setting in ["device", "name", "master"]:
            return
        elif setting == "index" and value == self.index:
            return

        vtype = type(value).__name__

        pointers = {
            'int':PySpin.CIntegerPtr,
            'str':PySpin.CEnumerationPtr,
            'float':PySpin.CFloatPtr,
            'bool':PySpin.CBooleanPtr
        }
        # Create the node map
        nodemap = self.camera.GetNodeMap()
        # Find the desired node using the pointers
        node = pointers[vtype](nodemap.GetNode(setting))
        if vtype == 'str':
            node_value = PySpin.CEnumEntryPtr(node.GetEntryByName(value))
            node.SetIntValue(node_value.GetValue())
        else:
            node.SetValue(value)

class Webcam(object):

    def __init__(self, index):
        self.index = index

        self.camera = cv2.VideoCapture(self.index)
        if not self.camera.isOpened():
            raise CameraError

    def read(self):
        if not self.camera.isOpened():
            raise ConnectionError("No webcam found at index: {0}".format(self.index))
        else:
            ret, frame = self.camera.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.error_msg = ""
            x, y, w, h = self.OffsetX, self.OffsetY, self.Width, self.Height
            return frame[y:h+y, x:w+x]

    def get_max(self, setting):
        maxes = {
            "Height":self.camera.get(4),
            "Width":self.camera.get(3)
        }
        return maxes[setting]

class Test(object):
    """docstring for Test."""

    def __init__(self, config):

        for k, v in config.items():
            self.set(k, v)

    def read(self):

        if self.dtype == 'uint8':
            max = 255
        else:
            max = 65024

        if self.master:
            time.sleep(1/self.AcquisitionFrameRate)

        return np.random.randint(0,max,size=(self.Height, self.Width), dtype=self.dtype)

    def set(self, setting, value):
        setattr(self, setting, value)

    def get_max(self, setting):
        maximums = {
            "Height":1000,
            "Width":1400,
            "AcquisitionFrameRate":100
        }
        return maximums[setting]

    def start(self):
        pass

    def stop(self):
        pass
