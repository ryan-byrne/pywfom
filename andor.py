import psutil, os, json, time
from colorama import Fore, Style
from shutil import copyfile
from datetime import datetime
from resources.camera.atcore import *
import numpy as np
from PIL import Image
import h5py

class Andor():

    def __init__(self):
        print("Intialising Andor SDK3")
        os.chdir("resources/camera")
        self.sdk3 = ATCore() # Initialise SDK3
        os.chdir("../..")
        self.hndl = self.sdk3.open(0)
        try:
            # Default Settings for all runs
            name = self.sdk3.get_string(self.hndl, "CameraName")
            print("Successsfully connected to: {0}".format(name))
            self.connected = 1
            self.sdk3.set_bool(self.hndl, "SensorCooling", True)
            self.sdk3.set_enum_string(self.hndl, "CycleMode", "Continuous")
            self.sdk3.set_enum_string(self.hndl, "PixelEncoding", "Mono16")
            self.sdk3.set_bool(self.hndl, "RollingShutterGlobalClear", True)
        except ATCoreException:
            print("Camera not connected!")
            self.connected = 0

    def deploy_settings(self, settings):
        s = settings

        self.width, self.height = int(s["width"]), int(s["height"])

        print("Deploying the following settings to the Camera:\n")
        # Run specific settings
        self.sdk3.strobe_order = s["strobe_order"]
        self.sdk3.set_float(self.hndl, "ExposureTime", float(s["exposure_time"]))
        self.framerate = self.sdk3.get_float(self.hndl, "FrameRate")
        #self.sdk3.set_float(self.hndl, "ExposureTime", float(s["exposure_time"]))
        print("Framerate: {0} fps".format(self.framerate))
        self.sdk3.set_int(self.hndl, "AOIHeight", self.height)
        self.sdk3.set_int(self.hndl, "AOIWidth", self.width)
        print("Height: {0} pixels".format(self.height))
        print("Width: {0} pixels".format(self.width))
        self.sdk3.set_enum_string(self.hndl, "AOIBinning", s["binning"])
        self.binning = s["binning"]
        print("Binning: {0}".format(self.binning))
        self.image_size_bytes = self.sdk3.get_int(self.hndl, "ImageSizeBytes")

    def acquire_single_frame(self):
        print("Acquiring single frame from camera")
        buf = np.empty((self.image_size_bytes,), dtype='uint16')
        self.sdk3.queue_buffer(self.hndl, buf, self.image_size_bytes)
        self.sdk3.command(self.hndl, "AcquisitionStart")
        wait_buf = self.sdk3.wait_buffer(self.hndl,)
        self.sdk3.command(self.hndl, "AcquisitionStop")
        self.sdk3.flush(self.hndl)
        self.sdk3.close(self.hndl)
        return(buf)

    def create_run_directory(self, path):
        name = "run"+str(len(os.listdir(path+"/CCD/"))+1)
        dst = path+'/CCD/'+name
        os.mkdir(dst)
        return dst

    def acquire(self, num_frm, path):
        #*************** Get Buffer from Camera *********************
        #print("\n{0} Acquiring {1} frames {0}\n".format("*"*10, num_frm))
        #print("Exposure time set to: {0}".format(self.exposure_time))
        t0 = time.time()
        num_buf = 5
        buf = np.empty((num_frm, self.image_size_bytes), dtype='uint16')
        for i in range(num_buf):
            self.sdk3.queue_buffer(self.hndl, buf[i].ctypes.data, self.image_size_bytes)
        #print("Starting acquisition")
        self.sdk3.command(self.hndl, "AcquisitionStart")
        for i in range(num_frm):
            self.sdk3.wait_buffer(self.hndl)
            self.sdk3.queue_buffer(self.hndl, buf[i%num_buf].ctypes.data, self.image_size_bytes)
        #print("Stopping acquisition")
        self.sdk3.command(self.hndl, "AcquisitionStop")
        self.sdk3.flush(self.hndl)
        #**************** Determine File Name ************
        num_acq = len(os.listdir(path))
        name = "/data"+str(num_acq+1)+".h5"
        #**************** Send buffer to hdf5 ************
        #print("Saving acquisition to: "+name)
        #h5f = h5py.File(path+name, 'w')
        #h5f.create_dataset('dataset_1', data=buf)
        #h5f.close()
        #print("\n{0} File delivered to {1} {0}\n".format("*"*10, dst))
        t = time.time()-t0
        print("\nAcquisition took {0} sec".format(t))
        print("FPS: {0} frames/sec".format(num_frm/t))

if __name__ == '__main__':
    camera = Andor()
    settings = {
                    "exposure_time":0.01,
                    "height":2048,
                    "width":2048,
                    "binning":"4x4",
                    "strobe_order":["Red", "Blue"]
                    }
    if camera.connected > 0:
        camera.deploy_settings(settings)
        dst = camera.create_run_directory("D:/test/")
        print("Acquiring Frames. Press CTR+C to Stop")
        while True:
            camera.acquire(5, dst)
    else:
        pass
