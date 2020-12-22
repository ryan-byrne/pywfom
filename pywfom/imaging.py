import numpy as np
import threading, time, traceback, os, ctypes, platform, queue
import sys
from PIL import Image, ImageDraw, ImageFont

# TODO: Synchronize trigger of andor with spinnakers
# TODO: Make sure every class has a get_max/get_min


def error_frame(msg):

    # Create a frame announcing the error
    img = Image.fromarray(np.zeros((500,500), "uint8"))
    draw = ImageDraw.Draw(img)
    draw.text((10, 175), "ERROR:", 255)
    draw.text((10,225), msg, 255)
    return np.asarray(img)

def loading_frame(height, width):
    # Create a frame announcing the error
    img = Image.fromarray(np.zeros((height,width), "uint8"))
    draw = ImageDraw.Draw(img)
    draw.text((height, width), "Loading Frame...", 255)
    return np.asarray(img)

class Test(object):

    def __init__(self, settings):

        self.ERROR = None

        self.frame = loading_frame(500,500)

        self.set(settings)

    def _start(self):
        pass

    def _stop(self):
        pass

    def read(self):

        if self.ERROR:
            return error_frame(self.ERROR)

        if self.dtype == 'uint8':
            max = 255
        else:
            max = 65024

        if self.master:
            time.sleep(1/self.framerate)

        return np.random.randint(0,max,size=(self.height, self.width), dtype=self.dtype)

    def set(self, setting, value=None):

        self._stop()

        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                self._set(k, v)
        else:
            self._set(setting, value)

        self._start()

    def _set(self, setting, value):

        if TYPES[setting] in [int, float]:
            value = min(self.get_max(setting), max(self.get_min(setting), value))

        setattr(self, setting, value)

    def get(self, setting):
        return getattr(self, setting)

    def get_max(self, setting):
        _max = {
            "height":1000,
            "width":1400,
            "frameRate":100,
            'offsetX':1390,
            'offsetY':990,
            'index':10,
            'framerate':100.0
        }
        return _max[setting]

    def get_min(self, setting):

        _min = {
            'height':10,
            'width':10,
            'offsetX':1,
            'framerate':1.0,
            'offsetY':1,
            'index':0
        }

        return _min[setting]

    def close(self):
        self.active = False

class Spinnaker(object):

    def __init__(self, settings):
        # TODO: Grab images

        self.ERROR = None

        try:
            print("Importing Spinnaker SDK Libraries...")
            global PySpin
            import PySpin

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
            self.set(settings)
        except Exception as e:
            for k, v in settings.items():
                setattr(self, k, v)
            if type(e).__name__ == "ModuleNotFoundError":
                msg = "\nYou have not installed PySpin\n\n\
                Follow the instructions at:\n\nhttps://github.com/ryan-byrne/pywfom/wiki/Cameras:-Spinnaker\n\n"
            else:
                msg = str(e)
            self.ERROR = msg
            self.frame = error_frame("({0}) {1}".format(self.name, msg))
            return

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

        # TODO: Fix issue with switching indexes

        if setting in ['name', 'device']:
            pass
        elif setting == 'index':
            self.camera = self.system.GetCameras().GetByIndex(value)
            self.camera.Init()
            for node in self.camera.GetNodeMap().GetNodes():
                pit = node.GetPrincipalInterfaceType()
                name = node.GetName()
                if pit == PySpin.intfICommand:
                    self.methods[name] = PySpin.CCommandPtr(node)
                elif pit in self._pointers:
                    self.settings[name] = self._pointers[pit](node)
        elif setting == 'master':
            # TODO: Change Trigger Mode
            pass
        elif setting == 'dtype':
            # TODO: Change Format
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

    def __init__(self, settings, test=False):

        # TODO: Add Mono12 Support
        # TODO: Fix dark picture problem
        # TODO: Set AOI

        self.ERROR, self._handle = None, None

        global andor
        try:

            from pywfom.utils import andor
            self.set(settings)

        except Exception as e:
            self.ERROR = str(e)

    def _start(self):

        if not self._handle:
            return

        self.img_size_bytes = self.get("ImageSizeBytes")
        andor.SetBool(self._handle, 'SensorCooling', True)

        self._buffers = queue.Queue()

        for i in range(10):
            buf = np.zeros((self.img_size_bytes), 'uint8')
            andor.QueueBuffer(
                self._handle,
                buf.ctypes.data_as(andor.POINTER(andor.AT_U8)),
                buf.nbytes
            )
            self._buffers.put(buf)

        self._img_stride = self.get('AOIStride')

        andor.Command(self._handle, "AcquisitionStart")

    def _stop(self):

        if not self._handle:
            return

        andor.Command(self._handle, "AcquisitionStop")
        andor.Flush(self._handle)

    def read(self):
        try:
            buf = self._buffers.get()
            ptr, length = andor.WaitBuffer(self._handle, 100)
            img = np.empty((self._height, self._width), dtype="uint16")
            andor.ConvertBuffer(
                ptr,
                img.ctypes.data_as(andor.POINTER(andor.AT_U8)),
                self._width,
                self._height,
                self._img_stride,
                'Mono16',
                'Mono16',
            )
            andor.QueueBuffer(self._handle, buf.ctypes.data_as(andor.POINTER(andor.AT_U8)), buf.nbytes)
            self._buffers.put(buf)
        except Exception as e:
            msg = 'Unable to read frame ({0})'.format(str(e)) if not self.ERROR else self.ERROR
            img = error_frame(msg)

        return img

    def set(self, setting, value=None):
        # TODO: Fix issue of changing index and losing settings
        print("Adjusting Andor settings...")

        self._stop()

        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                self._set(k, v)
        else:
            self._set(setting, value)

        self._start()

    def _set(self, setting, value):
        print('Setting {0} -> {1}'.format(setting, value))
        """
              "device":"andor",
              "index":0,
              "master":true,
              "name":"zyla",
              "dtype":"uint16",
              "height":2000,
              "width":2000,
              "offsetX":1,
              "offsetY":1,
              "binning":"2x2",
              "framerate":10.0
        """
        if not andor:
            return

        if setting == 'index':
            self._handle = andor.Open(value)
            if not self._handle:
                raise ConnectionError('Unable to connect to Andor at idx:{0}'.format(value))
        elif setting in ['device', 'name'] or not self._handle:
            pass
        elif setting == 'master':
            if value:
                andor.SetEnumString(self._handle, 'TriggerMode', 'Internal')
                andor.SetEnumString(self._handle, 'CycleMode', 'Continuous')
                andor.SetEnumString(self._handle, 'AuxiliaryOutSource', 'FireRowN')
            else:
                andor.SetEnumString(self._handle, 'TriggerMode', 'External')
                andor.SetEnumString(self._handle, 'CycleMode', 'Fixed')
                andor.SetInt(self._handle, 'FrameCount', 1)
        elif setting == 'dtype':
            andor.SetEnumString(self._handle, 'PixelEncoding', andor.CONVERT[value])
        elif setting == 'binning':
            andor.SetEnumString(self._handle, 'AOIBinning', value)
        elif setting == 'framerate':
            andor.SetFloat(self._handle, 'FrameRate', value)
        elif setting == 'height':
            andor.SetInt(self._handle, 'AOIHeight', value)
        elif setting == 'width':
            andor.SetInt(self._handle, 'AOIWidth', value)
        elif setting == 'offsetY':
            value += self.height
            andor.SetInt(self._handle, 'AOITop', value)
        elif setting == 'offsetX':
            andor.SetInt(self._handle, 'AOILeft', value)

        setattr(self, setting, value)

    def close(self):
        try:
            self._stop()
        except:
            pass
        self.active = False

class Webcam(object):

    def __init__(self, settings):

        print("Importing Webcam Libraries...")
        global cv2
        import cv2

        self.height, self.width = 500, 500

        self.frame = loading_frame(self.height, self.width)
        self.ERROR = None

        self.set(settings)

    def read(self):
        ret, img = self._camera.read()
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        x, y, w, h = self.offsetX, self.offsetY, self.width, self.height
        return img_gray[y:h+y, x:w+x]

    def set(self, setting, value=None):

        print("Adjusting webcam settings...")

        #self.frame = loading_frame(self.height, self.width)

        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                self._set(k, v)
        else:
            self._set(setting, value)

        if not self._camera.isOpened():
            self.frame = error_frame("({0}) no Webcam found at index:{1}".format(self.name, self.index))
            return

    def _set(self, setting, value):

        if setting == "index":
            self._camera = cv2.VideoCapture(value)
            if not self._camera.isOpened():
                self.ERROR = "No Webcam found at index {0}".format(value)
            else:
                self.ERROR = None

        elif self.ERROR:
            pass

        elif setting in self.__dict__ and getattr(self, setting) == value:
            return

        elif setting in ['framerate', 'height', 'width']:
            value = min(self.get_max(setting), max(self.get_min(setting), value))

        setattr(self, setting, value)

    def get(self, setting):
        return getattr(self, setting)

    def get_max(self, setting):

        _max = {
            "framerate":cv2.CAP_PROP_FPS,
            "height":cv2.CAP_PROP_FRAME_HEIGHT,
            "width":cv2.CAP_PROP_FRAME_WIDTH,
        }

        if setting == 'framerate':
            return float(self._camera.get(_max['framerate']))
        elif setting == 'index':
            return 10
        elif setting == 'offsetX':
            return self.width - 10
        elif setting == 'offsetY':
            return self.height - 10
        else:
            return int(self._camera.get(_max[setting]))

    def get_min(self, setting):

        _mins = {
            'index':0,
            'framerate':1.0,
            'height':10,
            'width':10,
            'offsetY':1,
            'offsetX':1
        }

        return _mins[setting]

    def close(self):
        self.active = False

OPTIONS = {
    'dtype':['uint8','uint16'],
    'device':['andor', 'spinnaker', 'webcam', 'test'],
    'binning':['1x1','2x2','4x4','8x8'],
    'master':[True, False]
}

TYPES = {
    "device":str,
    "name":str,
    "index":int,
    "height":int,
    "width":int,
    "framerate":float,
    "master":bool,
    "dtype":str,
    "offsetX":int,
    "offsetY":int,
    'binning':str,
    'exposure_time':float
}

DEFAULT = {
    "device":"test",
    "name":"default",
    "index":0,
    "height":700,
    "width":1200,
    "framerate":50.0,
    "master":True,
    "dtype":"uint8",
    "offsetX":0,
    "offsetY":0,
    'binning':'1x1',
    'exposure_time':0.01
}

DEVICES = {
    'andor':Andor,
    'webcam':Webcam,
    'test':Test,
    'spinnaker':Spinnaker
}
