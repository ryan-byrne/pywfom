import cv2, threading, time, sys, queue
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
        if cap.read()[0]:
            cameras.append({'interface':'opencv','index':i})
        else:
            continue
        cap.release()

    return cameras

class CameraException(Exception):
    pass

class Camera(object):

    def __init__(self, interface=None, index=None, id=None, **config):

        """

        interface : ['opencv', 'andor', 'spinnaker']
        index : int
        primary : bool

        """

        if None in [interface, index, id]:
            raise CameraException("Incomplete camera configuration")

        if ( interface == 'opencv' ):
            self._camera = _OpenCV(index=index, id=id, **config)
        elif ( interface == 'andor' ):
            self._camera = _Andor(index=index, id=id, **config)
        elif ( interface == 'spinnaker' ):
            self._camera = _Spinnaker(index=index, id=id, **config)

        self.start()

    def _loading_feed(self):
        return (np.zeros(
            (self._camera.aoi['height'], self._camera.aoi['width']),
            np.uint8)
        )

    def start(self):
        self.active = True
        self.feed = queue.Queue()
        threading.Thread(target=self._capture_frames).start()

    def _capture_frames(self):
        while self.active:
            # Keep the buffer size small for the feed
            if self.feed.qsize() > 1:
                with self.feed.mutex:
                    self.feed.queue.clear()
            else:
                self.feed.put(self._camera.get_next_frame())

    def get(self, setting):
        self._camera.get(setting)

    def stop(self):
        self._camera.stop()

    def set(self, **settings):
        self._camera.set(settings)

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

    def __init__(self, index=None, id=None, **config):

        self.set(**config)

        self.index = index
        self.id = id
        self.interface = 'opencv'

        self._video_cap = cv2.VideoCapture(self.index)
        self._capturing = False

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
        self.dtype = '8-bit'

    def set(self, **settings):
        [setattr(self,k,v) for k,v in settings.items()]

    def get_next_frame(self):
        if not self._video_cap.isOpened():
            return None
        else:
            ret, img = self._video_cap.read()
            if not ret:
                return None
            else:
                return img

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
