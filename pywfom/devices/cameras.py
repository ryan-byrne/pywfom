import cv2, threading, time, cv2, sys

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

class Camera(object):

    def __init__(self, index, device):

        self.index = index
        self.device = device
        self.name = "New Camera"
        self.feed = None

        if ( device == 'webcam' ):
            self._camera = cv2.VideoCapture(index)
            if not self._camera.isOpened():
                raise

        self._active = True

    def info(self):
        return({'device':self.device,'index':self.index})

    def close(self):
        self._active = False
        if self.device == 'webcam':
            self._camera.release()

    def read(self):
        return self._camera.read()[1]

    def feed(self):
        while True:
            img = self.read()
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
