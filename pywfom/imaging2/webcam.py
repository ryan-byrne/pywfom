import cv2, threading
import numpy as np

class Camera(object):
    """docstring for SimpleUSB."""

    def __init__(self, config):

        for k, v in config.items():
            self._set(k,v)

        self.frame = np.zeros((self.Height, self.Width), self.dtype)

        try:
            self.cap = cv2.VideoCapture(self.index)
            self.active = True
            self.error_msg = ""
        except:
            self.active = False
            self.error_msg = "Error"

        threading.Thread(target=self.update).start()

    def update(self):

        while self.active:
            ret, frame = self.cap.read()
            frame = frame[
                self.OffsetY:self.Height-self.OffsetY,
                self.OffsetX:self.Width-self.OffsetX
            ]
            print(frame.shape)
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def set(self, param, value=None):

        if type(param).__name__ == 'dict':
            for k, v in param.items():
                self._set(k, v)
        else:
            self._set(param, value)

    def _set(self, param,value):
        print("Setting {0} to {1}".format(param, value))
        setattr(self, param, value)

    def close(self):
        self.active = False
