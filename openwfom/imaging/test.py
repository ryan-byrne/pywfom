import numpy as np
import time, threading
import tkinter as tk
from PIL import Image, ImageTk

class TestCamera(object):

    """

    TestCamera is meant to create a virtual camera, which creates a random
    numpy array in the shape of an image, then stores it as the variable frame.

    """

    def __init__(self, config):

        self.set(config)

        self.error_msg = ""

        print("Initializing Test Camera: {0}".format(self.name))
        self.active = True
        self.frame = np.random.randint(0,255,size=(self.Height, self.Width), dtype=self.dtype)
        threading.Thread(target=self.make_image).start()


    def make_image(self):

        """

        Module that updates the self.frame variable

        """

        if self.dtype == 'uint8':
            max = 255
        else:
            max = 65024

        while self.active:
            h, w = self.Height, self.Width
            t = time.time()
            self.frame = np.random.randint(0,max,size=(h, w), dtype=self.dtype)
            try:
                self.AcquisitionFrameRate = 1/(time.time()-t)
            except:
                pass
            self.tic = time.time()

    def get_max(self, dim):
        return 2000

    def set(self, param, value=None):
        if type(param).__name__ == "dict":
            for k, v in param.items():
                self._set(k, v)
        else:
            self._set(param, value)

    def _set(self, param, value):
        print(param, value)
        setattr(self, param, value)

    def close(self):
        print("Closing Test Camera: {0}".format(self.name))
        self.active = False
