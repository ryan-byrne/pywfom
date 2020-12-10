import numpy as np
import threading, time, traceback, os, ctypes, platform, queue
import sys
from PIL import Image, ImageDraw, ImageFont

def error_frame(msg):

    # Create a frame announcing the error
    img = Image.fromarray(np.zeros((500,500), "uint8"))
    draw = ImageDraw.Draw(img)
    draw.text((10, 175), "ERROR:", 255)
    draw.text((10,225), msg, 255)
    return np.asarray(img)

def loading_frame():
    # Create a frame announcing the error
    img = Image.fromarray(np.zeros((500,500), "uint8"))
    draw = ImageDraw.Draw(img)
    draw.text((200,250), "Loading Frame...", 255)
    return np.asarray(img)

def update_frame(camera):

    camera.active = True

    while camera.active:

        try:
            camera.frame = camera.read()
        except Exception as e:
            camera.frame = error_frame(str(e))

class CameraError(Exception):
    """docstring for CameraError."""
    pass

class Camera(object):

    def __init__(self, config=None):

        # Establish default settings
        self.error_msg = ""
        self._camera = None
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

        # Check settings in the configuration file
        for k, v in config.items():
            self._set(k,v)

        self._start()

        threading.Thread(target=self._update_frame).start()

    def _update_frame(self):

        frame_function = {
            "webcam":self._get_webcam_frame,
            "spinnaker":self._get_spinnaker_frame,
            "andor":self._get_andor_frame,
            "test":self._get_test_frame
        }

    def _start(self):

        self.frame = self._loading_frame()

        try:

            if self.device not in ["webcam", "spinnaker", "andor", "test"]:
                self.error_msg = "Invalid device type '{0}'".format(self.device)
                return

            elif self.device == "webcam":
                self._camera = cv2.VideoCapture(self.index)
                if not self._camera.isOpened():
                    raise CameraError

            elif self.device == "spinnaker":
                import PySpin
                self._camera = PySpin.System.GetInstance().GetCameras()[self.index]

            elif self.device == "andor":
                from pywfom import andor
                self._camera = andor
                self._handle = self._camera.Open(self.index)
                if not self._handle.value == self._camera.AT_SUCCESS:
                    raise IndexError
                self._buffer = queue.Queue()
                for i in range(10):
                    bits = 8 if self.dtype == "uint8" else 16
                    buf = np.zeros((self.Height*self.Width*bits), self.dtype)
                    self._camera.QueueBuffer(
                        self._handle,
                        buf.ctypes.data_as(self._camera.POINTER(self._camera.AT_U8)),
                        buf.nbytes
                    )
                    self._buffer.put(buf)

            else:
                self._camera = None

            msg = ""

        except (IndexError, CameraError, AttributeError) as e:
            msg = "({2}) No '{1}' camera not found with index:{0}".format(self.index, self.device, self.name)
        except (ModuleNotFoundError, OSError) as e:
            msg = str(e)+"\n\nFollow the directions at:\
            \n\n\thttps://github.com/ryan-byrne/pywfom/wiki\n"

        self.error_msg = msg

        if self.error_msg != "":
            print(msg)

    def _stop(self):

        if self.device == "webcam":
            pass

    def _get_andor_frame(self):
        buf = self._buffer.get()
        self._camera.AT_WaitBuffer

    def _get_webcam_frame(self):
        if not self._camera.isOpened():
            self.error_msg = "No webcam found at index: {0}".format(self.index)
            raise
        else:
            ret, frame = self._camera.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.error_msg = ""
            x, y, w, h = self.OffsetX, self.OffsetY, self.Width, self.Height
            return frame[y:h+y, x:w+x]

    def _get_spinnaker_frame(self):
        image_result = self._camera.GetNextImage(1000)
        img = np.reshape(   image_result.GetData(),
                            (image_result.GetHeight(),image_result.GetWidth())
                        )
        image_result.Release()
        self.frame = img

    def _get_test_frame(self):

        if self.dtype == 'uint8':
            max = 255
        else:
            max = 65024

        time.sleep(1/self.AcquisitionFrameRate)

        return np.random.randint(0,max,size=(self.Height, self.Width), dtype=self.dtype)

    def trigger(arg):
        pass

    def _set(self, param, value):
        try:
            if type(value).__name__ != type(self.default[param]).__name__:
                msg = "\n\n '{0}' must be of type '{1}', not '{2}'\
                \nSetting to default of {3}".format(
                    param,
                    type(self.default[param]).__name__,
                    type(value).__name__,
                    self.default[param]
                )
                setattr(self, param, self.default[param])
            else:
                setattr(self, param, value)
                self.error_msg = ""
        except KeyError:
            msg = "\n\n'{0}' is not a valid configuration setting\n".format(param)
            self.error_msg = msg

    def get(self, param):
        pass

    def _get(self, param):
        pass

    def get_max(self, param):

        if self.error_msg != "":
            return

        # TODO: Add maximum functions for other cameras

        if self.device == "webcam":
            functions = {
                "Height":self._camera.get(4),
                "Width":self._camera.get(3)
            }
        elif self.device == "test":
            functions = {
                "Height":700,
                "Width":1200
            }

        return int(functions[param])

    def close(self):
        self.active = False

class Test(object):

    def __init__(self, settings):

        self.default = {
            "device":"test",
            "name":"default1",
            "index":0,
            "Height":700,
            "Width":1200,
            "AcquisitionFrameRate":50.0,
            "master":True,
            "dtype":"uint8",
            "OffsetX":0,
            "OffsetY":0
        }

        for k, v in settings.items():
            self.set(k, v)

        threading.Thread(target=update_frame, args=(self,)).start()

    def start(self):
        pass

    def stop(self):
        pass

    def read(self):
        if self.dtype == 'uint8':
            max = 255
        else:
            max = 65024

        if self.master:
            time.sleep(1/self.AcquisitionFrameRate)

        return np.random.randint(0,max,size=(self.Height, self.Width), dtype=self.dtype)

    def set(self, setting, value=None):

        self.stop()

        self.frame = loading_frame()

        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                setattr(self, k, v)
        else:
            setattr(self, setting, value)

        self.start()

    def get(self, setting):
        return getattr(self, setting)

    def get_max(self, setting):
        maximums = {
            "Height":1000,
            "Width":1400,
            "AcquisitionFrameRate":100
        }
        return maximums[setting]

    def close(self):
        self.active = False

class Spinnaker(object):

    def __init__(self, settings):

        import PySpin

        self.writable, self.available = PySpin.IsWritable, PySpin.IsAvailable

        self._pointers = {
            PySpin.intfIFloat: PySpin.CFloatPtr,
            PySpin.intfIBoolean: PySpin.CBooleanPtr,
            PySpin.intfIInteger: PySpin.CIntegerPtr,
            PySpin.intfIEnumeration: PySpin.CEnumerationPtr,
            PySpin.intfIString: PySpin.CStringPtr
        }

        self.settings = {}
        self.methods = {}

        self.system = PySpin.System.GetInstance()
        self.camera = self.system.GetCameras().GetByIndex(settings['index'])
        self.camera.Init()

        for node in self.camera.GetNodeMap().GetNodes():
            pit = node.GetPrincipalInterfaceType()
            name = node.GetName()
            if pit == PySpin.intfICommand:
                self.methods[name] = PySpin.CCommandPtr(node)
            elif pit in self._pointers:
                self.settings[name] = self._pointers[pit](node)


        self.set("AcquisitionFrameRateEnable", True)

        for k, v in settings.items():
            self.set(k, v)

        threading.Thread(target=update_frame, args=(self,)).start()

    def start(self):
        self.camera.BeginAcquisition()

    def stop(self):
        try:
            self.camera.EndAcquisition()
        except:
            pass

    def read(self):
        return self.camera.GetNextImage(1000).GetNDArray()

    def set(self, setting, value=None):

        self.stop()
        self.frame = loading_frame()
        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                self._set(k, v)
        else:
            self._set(setting, value)

        self.start()

    def _set(self, setting, value):

        if setting in ['name', 'device', 'index', 'master', 'dtype']:
            pass
        else:

            node = self.settings[setting]

            if node.GetName() == "AcquisitionFrameRateEnable":
                node.SetValue(value)
                return

            if value > self.get_max(setting):
                value = self.get_max(setting)
                print("({0}) Setting {1} to the maximum value of {2}".format(self.name, setting, value))
            elif value < self.get_min(setting):
                value = self.get_min(setting)
                print("({0}) Setting {1} to the minimum value of {2}".format(self.name, setting, value))

            if node.GetName() == "AcquisitionFrameRate":
                node.SetValue(value)
                setattr(self, setting, value)
                return

            while value%self.get_inc(setting) != 0:
                value+= 1

            node.SetValue(value)

        setattr(self, setting, value)

    def get(self, setting):
        try:
            return self.settings[setting].GetValue()
        except:
            try:
                return self.settings[setting].ToString()
            except:
                return None

    def get_max(self, setting):
        return self.settings[setting].GetMax()

    def get_min(self, setting):
        return self.settings[setting].GetMin()

    def get_inc(self, setting):
        return self.settings[setting].GetInc()

    def close(self):
        self.active = False

class Andor(object):

    def __init__(self, settings):

        self.default = {
            "device":"test",
            "name":"default1",
            "index":0,
            "Height":700,
            "Width":1200,
            "AcquisitionFrameRate":50.0,
            "master":True,
            "dtype":"uint8",
            "OffsetX":0,
            "OffsetY":0
        }

        from pywfom import andor

        for k, v in settings.items():
            setattr(self, k, v)

    def start(self):
        pass

    def stop(self):
        pass

    def read(self):
        if self.dtype == 'uint8':
            max = 255
        else:
            max = 65024

        if self.master:
            time.sleep(1/self.AcquisitionFrameRate)

        return np.random.randint(0,max,size=(self.Height, self.Width), dtype=self.dtype)

    def _set(self, setting, value):
        pass

    def get(self, setting):
        return getattr(self, setting)

    def get_max(self, setting):
        maximums = {
            "Height":1000,
            "Width":1400,
            "AcquisitionFrameRate":100
        }
        return maximums[setting]

    def close(self):
        self.active = False

class Webcam(object):

    global cv2
    import cv2

    def __init__(self, settings):

        self.default = {
            "device":"test",
            "name":"default1",
            "index":0,
            "Height":700,
            "Width":1200,
            "AcquisitionFrameRate":50.0,
            "master":True,
            "dtype":"uint8",
            "OffsetX":0,
            "OffsetY":0
        }

        for k, v in settings.items():
            setattr(self, k, v)

    def start(self):
        pass

    def stop(self):
        pass

    def read(self):
        if self.dtype == 'uint8':
            max = 255
        else:
            max = 65024

        if self.master:
            time.sleep(1/self.AcquisitionFrameRate)

        return np.random.randint(0,max,size=(self.Height, self.Width), dtype=self.dtype)

    def _set(self, setting, value):
        pass

    def get(self, setting):
        return getattr(self, setting)

    def get_max(self, setting):
        maximums = {
            "Height":1000,
            "Width":1400,
            "AcquisitionFrameRate":100
        }
        return maximums[setting]

    def close(self):
        self.active = False
