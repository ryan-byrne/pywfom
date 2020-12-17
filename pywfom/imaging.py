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

def update_frame(camera):

    camera.active = True

    while camera.active:
        try:
            camera.frame = camera.read()
        except Exception as e:
            camera.frame = error_frame("({0}) {1}".format(camera.name, str(e)))

class Test(object):

    def __init__(self, settings):

        self.height, self.width = 500,500
        self.frame = loading_frame(self.height, self.width)

        self.set(settings)

        threading.Thread(target=update_frame, args=(self,)).start()

    def _start(self):
        pass

    def _stop(self):
        pass

    def read(self):

        if self.dtype == 'uint8':
            max = 255
        else:
            max = 65024

        if self.master:
            time.sleep(1/self.framerate)

        return np.random.randint(0,max,size=(self.height, self.width), dtype=self.dtype)

    def set(self, setting, value=None):

        self._stop()

        #self.frame = loading_frame(self.height, self.width)

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
            self.frame = error_frame("({0}) {1}".format(self.name, msg))
            return

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

        # TODO: Fix issue with switching indexes

        if setting in ['name', 'device']:
            pass
        elif setting == 'index':
            self.camera = self.system.GetCameras().GetByIndex(value)
            self.camera.Init()
            input()
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

        # TODO: Add binning
        # TODO: Add Mono12 Support
        # TODO: fix stride

        self._stg_conv = {
            "Height":"AOIHeight",
            "Width":"AOIWidth",
            "OffsetX":"AOILeft",
            "OffsetY":"AOITop",
            "AcquisitionFrameRate":"FrameRate",
            "Binning":"AOIBinning",
            'uint12':0,
            'uint12p':1,
            "uint16":2,
            "uint32":3
        }

        try:
            global andor
            from pywfom.utils import andor
            self._buffers = queue.Queue()
            self.set(settings)
            print("({0}) Successfully Initialized Andor:{1}".format(self.name, self.get("SerialNumber")))
            self.ERROR = None
        except Exception as e:
            for k,v in settings.items():
                setattr(self, k, v)
            name = e.__class__.__name__
            if name == "OSError":
                msg = str(e)
            else:
                msg = "{0} : Could not connect to Andor camera at idx:{1}".format(e.error, self.index)
            self.ERROR = "({0}) {1}".format(self.name, msg)
            self.frame = error_frame(self.ERROR)

        if not test:
            threading.Thread(target=update_frame, args=(self,)).start()

    def _start(self):

        self._img_size_bytes = self.get("ImageSizeBytes")
        self._buffers = queue.Queue()

        for i in range(10):
            buf = np.zeros((self._img_size_bytes), 'uint8')
            andor.QueueBuffer(
                self._handle,
                buf.ctypes.data_as(andor.POINTER(andor.AT_U8)),
                buf.nbytes
            )
            self._buffers.put(buf)

        self._height, self._width = self.get("Height"), self.get("Width")

        andor.Command(self._handle, "AcquisitionStart")

    def _stop(self):

        try:
            andor.Command(self._handle, "AcquisitionStop")
            andor.Flush(self._handle)
        except:
            pass

    def read(self):

        if self.ERROR:
            time.sleep(0.1)
            return error_frame(self.ERROR)

        buf = self._buffers.get()
        andor.WaitBuffer(self._handle, 100)
        img = np.array(buf).view('uint16').reshape(self._height, self._width)
        andor.QueueBuffer(self._handle, buf.ctypes.data_as(andor.POINTER(andor.AT_U8)), buf.nbytes)
        self._buffers.put(buf)
        return img

    def set(self, setting, value=None):

        print("Adjusting Andor settings...")

        self._stop()
        self.frame = loading_frame()
        if type(setting).__name__ == 'dict':
            for k, v in setting.items():
                self._set(k, v)
        else:
            self._set(setting, value)

        self._start()

    def _set(self, setting, value):
        s = setting
        if setting in self._stg_conv.keys():
            setting = self._stg_conv[setting]

        if setting in ['name', 'device']:
            pass
        elif setting == 'index':
            print("Starting Andor Camera at idx:{0}".format(value))
            self.close()
            self._handle = andor.Open(value)
            if self.get("SerialNumber")[:3] == "SFT":
                raise andor.AndorError('AT_Open', 7)
            andor.Flush(self._handle)
        elif setting == 'master':
            if not value:
                andor.SetEnumString(self._handle, "TriggerMode", "External")
                andor.SetEnumString(self._handle, "CycleMode", "Fixed")
                andor.SetEnumString(self._handle, "FrameCount", 1)
            else:
                andor.SetEnumString(self._handle, "CycleMode", "Continuous")
                andor.SetEnumString(self._handle, "AuxiliaryOutSource", "FireRow1")
        elif setting == "AOITop":
            value = self.Height - value
        elif setting == "dtype":
            andor.SetEnumIndex(self._handle, "PixelEncoding", self._stg_conv[value])
        elif setting == "AOIBinning":
            andor.SetEnumString(self._handle, "AOIBinning", value)
        else:
            upper, lower = self.get_max(setting), self.get_min(setting)
            value = min(max(lower, value), upper)
            try:
                andor.SetInt(self._handle, setting, value)
            except:
                andor.SetFloat(self._handle, setting, value)

        setattr(self, s, value)

    def get(self, setting):
        if setting in self._stg_conv.keys():
            setting = self._stg_conv[setting]

        try:
            value = andor.GetInt(self._handle, setting).value
        except:
            try:
                value = andor.GetFloat(self._handle, setting).value
            except:
                try:
                    value = andor.GetString(self._handle, setting, 255).value
                except:
                    idx = andor.GetEnumIndex(self._handle, setting).value
                    value = andor.GetEnumStringByIndex(self._handle, setting, idx, 255).value

        return value

    def get_max(self, setting):
        if setting in self._stg_conv.keys():
            setting = self._stg_conv[setting]
        try:
            return andor.GetIntMax(self._handle, setting).value
        except:
            return andor.GetFloatMax(self._handle, setting).value

    def get_min(self, setting):
        if setting in self._stg_conv.keys():
            setting = self._stg_conv[setting]
        try:
            return andor.GetIntMin(self._handle, setting).value
        except:
            return andor.GetFloatMin(self._handle, setting).value

    def close(self):
        try:
            self.stop()
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

        self.set(settings)

        threading.Thread(target=update_frame, args=(self,)).start()

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

        if setting in self.__dict__ and getattr(self, setting) == value:
            return
        elif setting == "index":
            self._camera = cv2.VideoCapture(value)
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
    'dtype':['uint8','uint16','uint32'],
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
    'binning':str
}

DEFAULT = {
    "device":"test",
    "name":"",
    "index":0,
    "height":700,
    "width":1200,
    "framerate":50.0,
    "master":True,
    "dtype":"uint8",
    "offsetX":0,
    "offsetY":0,
    'binning':'1x1'
}

DEVICES = {
    'andor':Andor,
    'webcam':Webcam,
    'test':Test,
    'spinnaker':Spinnaker
}
