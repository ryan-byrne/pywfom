import psutil, os, json, time
from colorama import Fore, Style
from shutil import copyfile
from datetime import datetime
from resources.camera.atcore import *
import numpy as np

class Andor():

    def __init__(self):
        print("Intialising Andor SDK3")
        os.chdir("resources/camera")
        self.sdk3 = ATCore() # Initialise SDK3
        os.chdir("../..")
        self.hndl = self.sdk3.open(0)
        try:
            self.sdk3.get_bool(self.hndl, "CameraPresent")
            self.connected = 1
        except ATCoreException:
            self.connected = 0

    def acquire(skd3, hndl, self):
        num_bufs = 10
        frames_to_acquire = 15
        image_size_bytes = self.sdk3.get_int(hndl, "ImageSizeBytes")
        buf = np.empty((imageSizeBytes,), dtype='B')
        self.sdk3.queue_buffer(hndl,buf.ctypes.data,imageSizeBytes)
        buf2 = np.empty((imageSizeBytes,), dtype='B')
        self.sdk3.queue_buffer(hndl,buf2.ctypes.data,imageSizeBytes)
        self.sdk3.command(hndl, "AcquisitionStart")
        self.sdk3.command(hndl, "SoftwareTrigger")
        (returnedBuf, returnedSize) = self.sdk3.wait_buffer(hndl)
        pixels = buf.view(dtype='H')
        self.sdk3.command(hndl,"AcquisitionStop")
