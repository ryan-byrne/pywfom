import numpy as np
import threading, time, traceback, os, ctypes, platform, queue
import sys
from PIL import Image, ImageDraw, ImageFont

PySpin, andor = None, None

# TODO: Synchronize trigger of andor with spinnakers

def error_frame(msg=""):

    """
    Create an error frame displaying a specified message.

    :param string msg: Message to be displayed on the error frame
    """

    img = Image.fromarray(np.zeros((500,500), "uint8"))
    draw = ImageDraw.Draw(img)
    draw.text((10, 175), "ERROR:", 255)
    draw.text((10,225), msg, 255)
    return np.asarray(img)

def loading_frame(height=500, width=500):

    """
    Create a temporary frame displaying a 'loading' message.

    :param int height: Height of the loading frame (in pixels)
    :param int width: Width of the loading frame (in pixels)
    """

    img = Image.fromarray(np.zeros((height,width), "uint8"))
    draw = ImageDraw.Draw(img)
    draw.text((int(height/2)-50, int(width/2)), "Loading Frame...", 255)
    return np.asarray(img)

class Camera(object):

    """
    A Camera Interface for the PyWFOM System

    :param string device: Type of camera
    :param int index: Index of the camera
    """

    def __init__(self, device='test', index=0, **kwargs):

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

    def read(self):

        """
        Read and return Camera's latest frame as a numpy array
        """

        if self.device == 'webcam':
            ret, img = self._handler.read()
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            x, y, w, h = self.offset_x, self.offset_y, self.width, self.height
            return img_gray[y:h+y, x:w+x]

        elif self.device == 'andor':
            return self._read_andor_frame()

        elif self.device == 'spinnaker':
            return self._handler.GetNextImage(1000).GetNDArray()

        else:
            time.sleep(1/self.framerate)
            return np.random.randint(0,255,size=(self.height, self.width)).astype(self.dtype)

    def set(self, **kwargs):

        """
        Establish camera settings either by including a configuration
        dictionary, or setting individual keyword arguments.

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

        self.frame = loading_frame()

        self._stop_acquiring()

        settings = kwargs['config'] if 'config' in kwargs else kwargs

        for k, v in settings.items():

            if not hasattr(self, k) or v != getattr(self, k) or k in TYPES:
                self._set(k,v)
            else:
                continue

        self._start_acquiring()

    def close(self):
        """
        Closes the Camera Interface

        """
        self._stop_acquiring()

    def get(self, setting=None):

        """
        Gets the current value of the specified setting

        :param string setting: Setting value to be returned
        """

        if self.device == 'webcam' or not self._handler:
            return getattr(self, setting)
        elif self.device == 'andor':
            return self._get_andor(setting)
        elif self.device == 'spinnaker':
            return self._get_spinnaker(setting)

    def get_min(self, setting):

        """
        Gets the minimum value of the specified setting

        :param string setting: Minimum setting to be returned
        """

        FUNCTIONS = {
            'webcam':self._get_webcam_min,
            'andor':self._get_andor_min,
            'spinnaker':self._get_spinnaker_min
        }

        if setting == 'offset_x':
            return 1
        elif setting == 'offset_y':
            return 1
        elif setting == 'index':
            return 0
        if not self._handler:
            return DEFAULT_MINIMUMS[setting]
        else:
            return FUNCTIONS[self.device](setting)

    def get_max(self, setting):

        """
        Gets the maximum value of the specified setting

        :param string setting: Maximum setting to be returned
        """

        FUNCTIONS = {
            'webcam':self._get_webcam_max,
            'andor':self._get_andor_max,
            'spinnaker':self._get_spinnaker_max
        }

        if setting == 'offset_x':
            return self.get_max('width') - self.width+1
        elif setting == 'offset_y':
            return self.get_max('height') - self.height+1
        elif setting == 'index':
            return 10
        elif not self._handler:
            return DEFAULT_MAXIMUMS[setting]
        else:
            return FUNCTIONS[self.device](setting)

    def _startup(self, device, index):

        self.ERRORS, self.WARNINGS = [], []

        self.device, self.index = device, index

        if device == 'webcam':
            return self._start_webcam(index)
        elif device == 'spinnaker':
            return self._start_spinnaker(index)
        elif device == 'andor':
            return self._start_andor(index)
        else:
            return None

    def _start_webcam(self, index):

        global cv2
        import cv2

        try:
            cam = cv2.VideoCapture(index)
            if not cam.isOpened():
                raise ConnectionError('No webcam found at index:{0}'.format(index))
            return cam
        except Exception as e:
            self.frame = error_frame(str(e))
            self.ERRORS.append(str(e))
            return None

    def _start_spinnaker(self, index):

        try:

            # TODO: startup with storing settings
            global PySpin
            import PySpin

            self._system = PySpin.System.GetInstance()
            cam = self._system.GetCameras().GetByIndex(index)
            cam.Init()
            """
            for node in cam.GetNodeMap().GetNodes():
                pit = node.GetPrincipalInterfaceType()
                name = node.GetName()
                if pit == PySpin.intfICommand:
                    self.methods[name] = PySpin.CCommandPtr(node)
                elif pit in self._pointers:
                    self.settings[name] = self._pointers[pit](node)
            """
            return cam

        except Exception as e:
            msg = 'Could not initialize spinnaker camera at index {0}'.format(index)
            self.frame = error_frame(msg)
            self.ERRORS.append(msg)
            return None

    def _start_andor(self, index):

        try:
            global andor
            from .utils import andor

            # Create camera handler
            _hndl = andor.Open(0)

            # Create and populate buffers of a certain byte size
            _img_size = andor.GetInt(_hndl, "ImageSizeBytes")
            self._buffers = queue.Queue()
            for i in range(10):
                _buf = np.zeros((_img_size), 'uint8')
                andor.QueueBuffer(
                    _hndl,
                    buf.ctypes.data_as(andor.POINTER(andor.AT_U8)),
                    buf.nbytes
                )
                self._buffers.put(buf)

            # Store the image stride
            self._img_stride = andor.GetInt(_hndl, 'AOIStride')
            return _hndl

        except Exception as e:
            self.frame = error_frame(str(e))
            self.ERRORS.append(str(e))
            return None

    def _start_acquiring(self):

        if not self._handler and self.device != 'test':
            return

        self._acquiring = True

        if self.device == 'andor':
            andor.Command(self._handler, 'AcquisitionStart')
        elif self.device == 'spinnaker':
            self._handler.BeginAcquisition()

        threading.Thread(target=self._update_frame).start()

    def _stop_acquiring(self):

        if not self._handler and self.device != 'test':
            return

        self._acquiring = False

        if self.device == 'andor':
            andor.Command(self._handler, 'AcquisitionStop')
        elif self.device == 'spinnaker':
            self._handler.EndAcquisition()
        elif self.device == 'webcam':
            pass
        else:
            self._handler = None

    def _read_andor_frame(self):
        # TODO: test
        buf = self._buffers.get()
        ptr, length = andor.WaitBuffer(self._handle, 100)
        img = np.empty((self._height, self._width), dtype="uint8")
        andor.ConvertBuffer(
            ptr,
            img.ctypes.data_as(andor.POINTER(andor.AT_U8)),
            self._width,
            self._height,
            self._img_stride,
            'Mono12',
            andor.CONVERT[self.dtype],
        )
        andor.QueueBuffer(self._handle, buf.ctypes.data_as(andor.POINTER(andor.AT_U8)), buf.nbytes)
        self._buffers.put(buf)

    def _shutdown(self):
        pass

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
            'framerate':1.0,
            'offset_x':1
        }

        return _guide[setting]

    def _get_andor_max(self, setting):
        # TODO:
        pass

    def _get_andor_min(self, setting):
        # TODO:
        pass

    def _get_spinnaker_max(self, setting):
        pass

    def _get_spinnaker_min(self, setting):
        # TODO:
        pass

    def _set(self, setting, value):

        if setting == 'device':
            self._shutdown()
            self._handler = self._startup(value, self.index)

        elif setting == 'index':
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
            elif self.device == 'spinnaker':
                self._set_spinnaker(setting, value)
            elif self.device == 'andor':
                self._set_andor(setting, value)
            else:
                pass

        setattr(self, setting, value)

    def _set_webcam(self, setting, value):

        if setting == 'framerate':
            self._handler.set(5, value)

        setattr(self, setting, value)

    def _set_spinnaker(self, setting, value):
        pass

    def _set_andor(self, setting, value):
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

DEFAULT_MAXIMUMS = {
    'height':2400,
    'width':2400,
    'framerate':100.0
}

DEFAULT_MINIMUMS = {
    'height':50,
    'width':50,
    'framerate':5.0
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
