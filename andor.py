import psutil, os, json, time
from colorama import Fore, Style
from shutil import copyfile
from datetime import datetime
from resources.camera.atcore import *
import numpy as np
from PIL import Image

class Andor():

    def __init__(self):
        print("Intialising Andor SDK3")
        os.chdir("resources/camera")
        self.sdk3 = ATCore() # Initialise SDK3
        os.chdir("../..")
        self.hndl = self.sdk3.open(0)
        try:
            self.sdk3.set_bool(self.hndl, "SensorCooling", True)
            self.connected = 1
        except ATCoreException:
            print("Unable to connect to the Camera!")
            self.connected = 0

    def deploy_settings(self, settings):
        s = settings
        print("Deploying settings to the Camera")
        self.sdk3.set_float(self.hndl, "ExposureTime", float(s["exposure"]))
        self.exposure_time = self.sdk3.get_float(self.hndl, "ExposureTime")
        self.sdk3.set_enum_string(self.hndl, "PixelEncoding", "Mono32")
        self.sdk3.set_enum_string(self.hndl, "AOIBinning", s["binning"])
        self.sdk3.strobe_order = s["strobe_order"]
        self.sdk3.set_enum_string(self.hndl, "CycleMode", "Continuous")
        self.height = self.sdk3.set_int(self.hndl, "AOIHeight", int(s["height"]))
        self.width = self.sdk3.set_int(self.hndl, "AOIWidth", int(s["width"]))
        self.image_size_bytes = self.sdk3.get_int(self.hndl, "ImageSizeBytes")


    def acquire_single_frame(self):
        print("Acquiring single frame from camera")
        buf = np.empty((self.image_size_bytes,), dtype='uint32')
        self.sdk3.queue_buffer(self.hndl, buf.ctypes.data, self.image_size_bytes)
        self.sdk3.command(self.hndl, "AcquisitionStart")
        wait_buf = self.sdk3.wait_buffer(self.hndl,)
        self.sdk3.command(self.hndl, "AcquisitionStop")
        self.sdk3.flush(self.hndl)
        self.sdk3.close(self.hndl)
        return(buf)

    def acquire(self, num_frm, exp):
        print("Acquiring {0} frames".format(num_frm))
        self.sdk3.set_float(self.hndl, "ExposureTime", exp)
        e = self.sdk3.get_float(self.hndl, "ExposureTime")
        print("Exposure time set to: {0}".format(e))
        num_buf = num_frm
        buf = np.empty((num_frm, self.image_size_bytes), dtype='uint32')
        for i in range(num_buf):
            self.sdk3.queue_buffer(self.hndl, buf[i].ctypes.data, self.image_size_bytes)
        print("Starting acquisition")
        self.sdk3.command(self.hndl, "AcquisitionStart")
        t0 = time.time()
        for i in range(num_frm):
            self.sdk3.wait_buffer(self.hndl)
            self.sdk3.queue_buffer(self.hndl, buf[i%num_buf].ctypes.data, self.image_size_bytes)
        print("Acquisition took {0} sec".format(time.time()-t0))
        print("Stopping acquisition")
        self.sdk3.command(self.hndl, "AcquisitionStop")
        self.sdk3.flush(self.hndl)
        return buf


if __name__ == '__main__':
    camera = Andor()
    exposure_time = 0.0068
    frames = camera.acquire(3, exposure_time)
    for frame in frames:
        img = Image.frombytes(size=(camera.height, camera.width), data=frame, mode="I")
        img.show()
