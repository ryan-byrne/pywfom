import cv2, threading, time, sys, queue, os
import numpy as np

from pywfom.devices.utils import *

"""
import win32com.client

wmi = win32com.client.GetObject ("winmgmts:")
for usb in wmi.InstancesOf ("Win32_USBHub"):
    print usb.DeviceID
"""

def find_cameras():

    cameras = []

    # OpenCV
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap is None or not cap.isOpened():
            continue
        else:
            cameras.append({'interface':'opencv','index':i})

    return cameras

class CameraException(Exception):
    pass

class Camera(object):

    def __init__(self, **config):

        """

        interface : ['opencv', 'andor', 'spinnaker']
        index : int
        primary : bool

        """

        if 'interface' not in config or 'index' not in config:
            raise CameraException("Incomplete camera configuration")
        else:
            self.interface, self.index = config['interface'], config['index']
        print("Initialzing {}:{}".format(config['interface'], config['index']))

        if ( config['interface'] == 'opencv' ):
            self._camera = _OpenCV(**config)
        elif ( config['interface'] == 'andor' ):
            self._camera = _Andor(**config)
        elif ( config['interface'] == 'spinnaker' ):
            self._camera = _Spinnaker(**config)

        self.start()

    def start(self):
        self.active, self.acquiring = True, False
        self.feed = queue.Queue()
        self.acquired_frames = queue.Queue()
        threading.Thread(target=self._capture_frames).start()

    def _capture_frames(self):
        while self.active:
            # Keep the buffer size small for the feed
            frame = self._camera.get_next_frame()
            if self.feed.qsize() > 1:
                with self.feed.mutex:
                    self.feed.queue.clear()
            else:
                self.feed.put(frame)

            if self.acquiring:
                self.acquired_frames.put(frame)

    def get(self, setting):
        self._camera.get(setting)

    def stop(self):
        self._camera.stop()

    def set(self, **settings):
        self._camera.set(**settings)

    def close(self):
        self.active = False
        try:
            self._camera.close()
            del self._camera
        except:
            pass

    def json(self):
        return self._camera.json()

class _OpenCV(object):
    """docstring for _OpenCV."""

    def __init__(self, **config):

        self.id = os.urandom(6).hex()

        self._video_cap = cv2.VideoCapture(config['index'])

        self._PROPS = {
            "fullWidth":3,
            "fullHeight":4,
            "width":3,
            "height":4,
            "framerate":5
        }

        self.aoi = {
            "x":0,
            "y":0,
            "width":int(self.get('width')),
            "height":int(self.get('height')),
            "fullHeight":int(self.get('height')),
            "fullWidth":int(self.get('width')),
            "binning":"1x1",
            "centered":False
        }
        self.framerate = self.get('framerate')
        self.primary = False
        self.dtype = 'uint16'

        self.set(**config)

        self._capturing = False

    def set(self, **settings):
        [setattr(self,k,v) for k,v in settings.items()]

    def get_next_frame(self):
        if not self._video_cap.isOpened():
            return None
        else:
            ret, img = self._video_cap.read()
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            x, y, w, h = self.aoi['x'], self.aoi['y'], self.aoi['width'], self.aoi['height']
            frame = img_gray[y:h+y, x:w+x]
            if not ret:
                return None
            else:
                return frame

    def close(self):
        pass

    def get(self, setting):
        return self._video_cap.get( self._PROPS[setting] )

    def json(self):
        # Return Camera settings as a dictionary

        json_settings = {}

        for k, v in self.__dict__.items():
            if k[0] != '_' and k:
                json_settings[k] = v

        return json_settings

class _Andor(object):

    def __init__(self):
        pass

class _Spinnaker(object):

    def __init__(self):
        pass

class _Test(object):

    def __init__ (self, **config):

        self.set(**config)

        self.interface = 'test'
        self.id = os.urandom(6).hex()

        self._capturing = False

        self.aoi = {
            "x":0,
            "y":0,
            "width":int(self.get('width')),
            "height":int(self.get('height')),
            "fullHeight":int(self.get('height')),
            "fullWidth":int(self.get('width')),
            "binning":"1x1",
            "centered":False
        }
        self.framerate = self.get('framerate')
        self.primary = False
        self.dtype = '8-bit'

    def set(self, **settings):
        [setattr(self,k,v) for k,v in settings.items()]

    def get_next_frame(self):
        return np.random.randint(0, self.dtype[0], size=self.size, dtype=self.dtype[1])

    def close(self):
        pass

    def get(self, setting):
        return getattr(self, setting)

    def json(self):
        # Return Camera settings as a dictionary

        json_settings = {}

        for k, v in self.__dict__.items():
            if k[0] != '_' and k:
                json_settings[k] = v

        return json_settings
