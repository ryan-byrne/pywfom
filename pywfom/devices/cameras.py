import cv2, threading, time, cv2, sys, queue

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

    def __init__(self, config=None, **kwargs):

        """

        interface : ['opencv', 'andor', 'spinnaker']
        index : int
        primary : bool



        """

        [setattr(self, k, v) for k,v in config.items()]

        print('pywfom :: Initalizing {0}:{1}'.format(self.interface, self.index))

        self._capturing = False
        self.feeding = True
        self._saving = False

        self._frame_buffer = queue.Queue()

        if ( self.interface == 'opencv' ):
            self._camera_handler = cv2.VideoCapture(self.index)

    def read(self):
        if (self.interface == 'opencv'):
            return self._camera_handler.read()[1]

    def start(self):

        # Start capturing frames
        pass

    def stop(self):

        # Stop Capturing Frames
        self.feeding = False
        self._capturing = False
        self._saving = False

    def set(self):

        # Declare settings
        pass

    def get(self):

        # Return Settings
        pass

    def clear(self):

        # Clear the buffer
        pass

    def trigger(self):

        # Trigger the release of a frame
        pass

    def close(self):

        self.stop()

        if (self.interface == 'opencv'):
            self._camera_handler.release()

    def json(self):

        # Return Camera settings as a dictionary

        json_settings = {}

        for k, v in self.__dict__.items():
            if k[0] != '_':
                json_settings[k] = v

        return json_settings
