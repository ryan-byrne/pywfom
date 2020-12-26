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

def loading_frame(height=500, width=500):
    # Create a frame announcing the error
    img = Image.fromarray(np.zeros((height,width), "uint8"))
    draw = ImageDraw.Draw(img)
    draw.text((int(height/2)-50, int(width/2)), "Loading Frame...", 255)
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

    """
    Class object for control of a Spinnaker Camera
    """

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

        """
        Method for changing setting(s) on the camera
        """

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

class Camera(object):

    """
    A Camera Interface for the PyWFOM System
    """

    def __init__(self, device='webcam', index=0, **kwargs):

        # TODO: Build out andor
        # TODO: build out spinnaker

        # Create a to store any errors that may occur
        self.ERRORS, self.WARNINGS = [], []

        # Create a temporary loading frame
        self.frame = loading_frame()

        # Establish the Camera handler
        self._handler = self._startup(device, index)

        # Check for configuration in keyword arguments
        config = kwargs['config'] if 'config' in kwargs else kwargs

        self.set(config=config)

    def get(self, setting=None):
        return None

    def get_min(self, setting):

        if setting == 'index':
            return 0
        elif setting == 'offset_x':
            return 1
        elif setting == 'offset_y':
            return 1
        elif self.device == 'webcam':
            return self._get_webcam_min(setting)
        elif self.device == 'andor':
            return self._get_andor_min(setting)
        elif self.device == 'spinnaker':
            return self._get_spinnaker_min(setting)
        else:
            return self._get_test_min(setting)

    def get_max(self, setting):

        if setting == 'index':
            return 10
        elif setting == 'offset_x':
            return self.get_max('width') - self.width+1
        elif setting == 'offset_y':
            return self.get_max('height') - self.height+1
        elif self.device == 'webcam':
            return self._get_webcam_max(setting)
        elif self.device == 'andor':
            return self._get_andor_max(setting)
        elif self.device == 'spinnaker':
            return self._get_spinnaker_max(setting)
        else:
            return self._get_test_max(setting)

    def _get_webcam_max(self, setting):

        _guide = {
            'height':int(self._handler.get(4)),
            'width':int(self._handler.get(3)),
            'framerate':30.0
        }

        return _guide[setting]

    def _get_webcam_min(self, setting):

        _guide = {
            'height':10,
            'width':10,
            'framerate':1.0
        }

        return _guide[setting]

    def _get_andor_max(self, setting):
        # TODO:
        _guide = {
            'height':2400,
            'width':2400,
            'index':10,
            'framerate':100.0
        }
        return _guide[setting]

    def _get_andor_min(self, setting):
        # TODO:
        _guide = {
            'height':50,
            'width':50,
            'index':0,
            'framerate':5.0
        }
        return _guide[setting]

    def _get_spinnaker_max(self, setting):
        # TODO:
        _guide = {
            'height':2400,
            'width':2400,
            'index':10,
            'framerate':100.0
        }
        return _guide[setting]

    def _get_spinnaker_min(self, setting):
        # TODO:
        _guide = {
            'height':50,
            'width':50,
            'index':0,
            'framerate':5.0
        }
        return _guide[setting]

    def _get_test_max(self, setting):

        _guide = {
            'height':2400,
            'width':2400,
            'framerate':100.0
        }

        return _guide[setting]

    def _get_test_min(self, setting):

        _guide = {
            'height':50,
            'width':50,
            'framerate':5.0
        }

        return _guide[setting]

    def read(self):

        """
        Read and return current frame read from Camera Interface
        """

        if self.device == 'webcam':
            return self._read_webcam_frame()

        elif self.device == 'andor':
            return self._read_andor_frame()

        elif self.device == 'spinnaker':
            return self._read_spinnaker_frame()

        else:
            time.sleep(1/self.framerate)
            return np.random.randint(0,255,size=(self.height, self.width)).astype(self.dtype)

    def set(self, **kwargs):

        """
        :param dict config: Dictionary containing multiple settings
        :param string device: Device type for the new :class:`Camera` object.
        :param string name: (optional) Names the :class:`Camera` object.
        :param int index: Sets the index :class:`Camera` will connect to.
        :param int height: Sets the height of the :class:`Camera` frame.
        :param int width: Sets the width of the :class:`Camera` frame.
        :param int offset_x: Sets the width of the :class:`Camera` frame.
        :param int offset_y: Sets the width of the :class:`Camera` frame.
        :param string binning: Sets the binning of the :class:`Camera` frame.
        :param string dtype: Sets the datatype of the :class:`Camera` frame.
        :param bool master: Establishes whether :class:`Camera` is self-triggered.
        :param float framerate: Sets the framerate the :class:`Camera` read at
        """

        self._stop_acquiring()

        settings = kwargs['config'] if 'config' in kwargs else kwargs

        for k, v in settings.items():

            if not hasattr(self, k) or v != getattr(self, k) or k in TYPES:
                self._set(k,v)
            else:
                continue

        self._start_acquiring()

    def close(self):
        self._stop_acquiring()

    def _startup(self, device, index):

        self.device, self.index = device, index

        if device == 'webcam':
            return self._start_webcam(index)
        elif device == 'spinnaker':
            return self._start_spinnaker(index)
        elif device == 'andor':
            return self._start_andor(index)
        else:
            return None

    def _shutdown(self):
        pass

    def _start_webcam(self, index):

        global cv2
        import cv2

        cam = cv2.VideoCapture(index)

        _guide = {
            'framerate':cam.get(5),
            'height':int(cam.get(4)),
            'width':int(cam.get(3)),
            'offset_x':1,
            'offset_y':1,
            'master':True,
            'name':'NewWebcam',
            'dtype':'uint8',
            'binning':'2x2',
        }

        if not cam.isOpened():
            self.ERRORS.append('No webcam found at index:{0}'.format(index))
            return None
        else:
            for attr in _guide.keys():
                if hasattr(self, attr):
                    continue
                elif attr in _guide:
                    setattr(self, attr, _guide[attr])
                else:
                    setattr(self, attr, 1)
            return cam

    def _start_spinnaker(self, index):

        try:
            global PySpin
            import PySpin

            self._system = PySpin.System.GetInstance()
            return self._system.GetCameras().GetByIndex(index)
        except Exception as e:
            self.frame = error_frame(str(e))
            self.ERRORS.append(str(e))
            return None

    def _start_andor(self, index):

        try:
            global andor
            from .utils import andor
            return andor.Open(0)
        except Exception as e:
            self.frame = error_frame(str(e))
            self.ERRORS.append(str(e))
            return None

    def _set(self, setting, value):

        if setting == 'device':
            self.frame = loading_frame()
            self._shutdown()
            self._handler = self._startup(value, self.index)

        elif setting == 'index':
            self.frame = loading_frame()
            self._shutdown()
            self._handler = self._startup(self.device, value)

        elif setting == 'name' or not self._handler:
            pass

        elif setting == 'master':
            # TODO: COmplete
            pass

        elif setting == 'binning':
            # TODO: Complete
            pass

        elif setting == 'dtype':
            # TODO: Complete
            pass

        else:
            value = max(min(value, self.get_max(setting)), self.get_min(setting))
            if self.device == 'webcam':
                self._set_webcam(setting, value)
            else:
                pass

        setattr(self, setting, value)

    def _set_webcam(self, setting, value):

        if setting == 'framerate':
            self._handler.set(5, value)

        setattr(self, setting, value)

    def _stop_acquiring(self):

        if not self._handler and self.device != 'test':
            return

        self._acquiring = False

        if self.device == 'andor':
            andor.Command(self._handler, 'AcquisitionStop')
        elif self.device == 'spinnaker':
            pass
        elif self.device == 'webcam':
            pass
        else:
            self._handler = None

    def _start_acquiring(self):

        if not self._handler and self.device != 'test':
            return

        self._acquiring = True

        if self.device == 'andor':
            andor.Command(self._handler, 'AcquisitionStop')

        threading.Thread(target=self._update_frame).start()

    def _read_webcam_frame(self):
        ret, img = self._handler.read()
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        x, y, w, h = self.offset_x, self.offset_y, self.width, self.height
        return img_gray[y:h+y, x:w+x]

    def _read_andor_frame(self):
        pass

    def _update_frame(self):

        while self._acquiring:

            try:

                self.frame = self.read()

            except Exception as e:

                msg = self.ERRORS[0] if self.ERRORS else str(e)

                self.frame = error_frame(msg)


OPTIONS = {
    'dtype':['uint8','uint12', 'uin12p', 'uint16'],
    'device':['andor', 'spinnaker', 'webcam', 'test'],
    'binning':['1x1','2x2','4x4','8x8'],
    'master':[True, False]
}

TYPES = {
  "name":str,
  "index":int,
  "device":str,
  "height":int,
  "width":int,
  "offset_x":int,
  "offset_y":int,
  "binning":str,
  "dtype":str,
  "master":bool,
  "framerate":float
}
