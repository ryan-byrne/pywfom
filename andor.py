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

    def create_camera_file_folder(mouse):
        date = str(datetime.now())[:10]
        cpu_name = os.environ['COMPUTERNAME']
        # Check to make sure the proper computer is being used
        print("This computer's name is "+cpu_name)
        if cpu_name == "DESKTOP-TFJIITU":
            path = "S:/WFOM/data/"
        else:
            path = "C:/WFOM/data/"
            check = input("It looks like you are not using a designated work station. Would you like to continue? (y/n) ")
            if check == "y":
                pass
            else:
                exit()
        with open("JSPLASSH/archive.json", "r+") as f:
            archive = json.load(f)
            d = archive["mice"][mouse]["last_trial"]+1
            archive["mice"][mouse]["last_trial"] = d
            f.seek(0)
            json.dump(archive, f, indent=4)
            f.truncate()
        f.close()
        if not os.path.isdir(path + mouse + "_" + str(d)):
            path = path + mouse + "_" + str(d)
        else:
            path = path + mouse + "_" + str(d+1)
        print("Making directory: "+path)
        os.mkdir(path)
        print("Making directory: "+path+"/CCD")
        os.mkdir(path+"/CCD")
        print("Making directory: "+path+"/auxillary")
        os.mkdir(path+"/auxillary")
        print("Making directory: "+path+"/webcam")
        os.mkdir(path+"/webcam")
        print("Copying JSPLASSH/settings.json to "+path+"/settings.json")
        src = "JSPLASSH/settings.json"
        dst = path+"/settings.json"
        copyfile(src, dst)
        return dst

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
