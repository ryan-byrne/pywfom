import numpy as np
import time, threading
import tkinter as tk
from PIL import Image, ImageTk

class TestCamera(object):

    """

    TestCamera is meant to create a virtual camera, which creates a random
    numpy array in the shape of an image, then stores it as the variable frame.

    """

    def __init__(self, name="", size=(500,500), dtype='uint8', settings=None):
        self.settings = {}
        self.settings["Height"] = size[0]
        self.settings["Width"] = size[1]
        self.settings["name"] = name
        self.settings["type"] = "test"
        self.name = name
        self.error_msg = ""
        self.settings['dtype'] = dtype
        self.settings["AcquisitionFrameRate"] = 100
        print("Initializing Test Camera: {0}".format(name))
        self.active = True
        self.frame = np.random.randint(0,255,size=size, dtype=dtype)
        threading.Thread(target=self.make_image).start()


    def make_image(self):

        """

        Module that updates the self.frame variable

        """

        if self.settings["dtype"] == 'uint8':
            max = 255
        else:
            max = 65024

        while self.active:
            h, w = self.settings["Height"], self.settings["Width"]
            self.frame = np.random.randint(0,max,size=(h, w), dtype=self.settings["dtype"])
            #Maximuz FPS to 100
            time.sleep(1/self.settings["AcquisitionFrameRate"])

    def set(self, param, value=None):
        if type(param).__name__ == "dict":
            for p in param.keys():
                self._set(p, param[p])
        else:
            self._set(param, value)

    def _set(self, param, value):
        self.settings[param] = value

    def close(self):
        print("Closing Test Camera: {0}".format(self.name))
        self.active = False
