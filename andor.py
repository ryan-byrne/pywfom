import psutil, os, json, time, subprocess
from pywinauto import Application
from colorama import Fore, Style
from shutil import copyfile
from datetime import datetime
from resources.camera.atcore import *
import numpy as np

class Andor():

    def __init__(self, mode):
        if mode == 1:
            print("Intialising Andor SDK3")
            os.chdir("resources/camera")
            self.sdk3 = ATCore() # Initialise SDK3
            os.chdir("../..")
            self.hndl = self.sdk3.open(0)
            try:
                # Default Settings for all runs
                self.name = self.sdk3.get_string(self.hndl, "CameraName")
                self.interface = self.sdk3.get_string(self.hndl, "InterfaceType")
                self.sdk3.set_bool(self.hndl, "FastAOIFrameRateEnable", True)
                print("Successsfully connected to: {0} via {1}".format(self.name, self.interface))
                self.max_framerate = self.sdk3.get_float(self.hndl, "MaxInterfaceTransferRate")
                self.pixel_readout_rate = self.sdk3.get_enum_string(self.hndl, "PixelReadoutRate")
                self.simple_preamp_gain_control = self.sdk3.get_enum_string(self.hndl,
                                                                            "SimplePreAmpGainControl",
                                                                            "16-bit (low noise & high well capacity)")
                print("Maximum Transfer Rate: {0} fps".format(self.max_framerate))
                print("PixelReadoutRate: {0}".format(self.pixel_readout_rate))
                #self.sdk3.set_enum_string(self.hndl, "ElectronicShutteringMode", "Global")
                print("Initiating Sensor Cooling")
                self.sdk3.set_bool(self.hndl, "SensorCooling", True)
                self.sdk3.set_enum_string(self.hndl, "CycleMode", "Continuous")
                #self.sdk3.set_bool(self.hndl, "RollingShutterGlobalClear", True)
                self.sdk3.set_enum_string(self.hndl, "AuxiliaryOutSource", "FireAny")
                self.sdk3.set_enum_string(self.hndl, "PixelEncoding", "Mono16")
                self.connected = 1
            except ATCoreException:
                print("Error connecting to the Camera!")
                self.connected = 0
        else:
            self.connected = 1
            if "AndorSolis.exe" in (p.name() for p in psutil.process_iter()):
                print("SOLIS is already running...")
                pass
            else:
                print("Opening SOLIS")
                subprocess.call("C:\Program Files\Andor SOLIS\AndorSolis.exe")
            self.solis = Application().connect(title_re="Andor")
            self.soliswin = self.solis.window(title_re="Andor")
            self.py = Application().connect(title_re="python")
            self.pywin = self.py.window(title_re="python")


    def deploy_settings(self, settings, path):
        s = settings

        self.width, self.height = int(s["width"]), int(s["height"])

        print("\nDeploying the following settings to the Camera:\n")
        # Run specific settings
        self.sdk3.strobe_order = s["strobe_order"]
        self.sdk3.set_float(self.hndl, "ExposureTime", float(s["exposure"]))
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
        if not self.save:
            pass
        else:
            name = "run"+str(len(os.listdir(path+"/CCD/"))+1)
            dst = path+'/CCD/'+name
            os.mkdir(dst)
            self.dst = dst

    def acquire_single_frame(self):

        h = int(self.height/int(self.binning[0]))
        w = int(self.width/int(self.binning[0]))

        self.sdk3.set_enum_string(self.hndl, "PixelEncoding", "Mono32")
        self.image_size_bytes = self.sdk3.get_int(self.hndl, "ImageSizeBytes")
        print("Acquiring single frame from camera")
        buf = np.empty((self.image_size_bytes,), dtype='B')
        self.sdk3.queue_buffer(self.hndl, buf.ctypes.data, self.image_size_bytes)
        self.sdk3.command(self.hndl, "AcquisitionStart")
        wait_buf = self.sdk3.wait_buffer(self.hndl)
        self.sdk3.command(self.hndl, "AcquisitionStop")
        self.sdk3.flush(self.hndl)
        self.sdk3.close(self.hndl)
        print(buf)
        im = Image.frombytes(mode="I", size=(h, w), data=buf)
        im.show()

    def acquire2(self):
        # Establishing Buffers
        num_frm = 100
        num_buf = 10
        buf = np.empty((num_frm, self.image_size_bytes), dtype='uint16')
        for i in range(num_buf):
            self.sdk3.queue_buffer(self.hndl, buf.ctypes.data, self.image_size_bytes)
        self.sdk3.command(self.hndl, "AcquisitionStart")
        t = time.time()
        for i in range(num_frm):
            self.sdk3.wait_buffer(self.hndl)
            self.sdk3.queue_buffer(self.hndl, buf[i%num_buf].ctypes.data, self.image_size_bytes)
        print("Stopping Acquisiton")
        if not camera.save:
            pass
        else:
            num_acq = len(os.listdir(self.dst))
            name = "/data"+str(num_acq+1)+".h5"
            h5f = h5py.File(self.dst+name, 'w')
            h5f.create_dataset('dataset_1', data=buf, compression="gzip", compression_opts=1)
            h5f.close()
        self.sdk3.command(self.hndl, "AcquisitionStop")
        self.sdk3.flush(self.hndl)

    def set_parameters(self, settings, path):
        print(path)
        s = ["height", "bottom", "width", "top", "exposure_time", "framerate"]

        print("Creating zyla_settings.txt file...")

        with open("resources/solis_scripts/zyla_settings.txt", "w+") as f:
            f.write(str(settings["binning"][0])+"\n")
            for setting in s:
                f.write(str(settings[setting])+"\n")
            f.write("_"+"\n")
            f.write(path)

        file = '"%s\%s"' % (cwd, set_param)

        print("Setting parameters in SOLIS...")
        self.soliswin.menu_select("File -> Run Program By Filename")
        open_opt = self.solis.window(title_re="Open")
        file_name = open_opt.Edit.set_text(file)
        time.sleep(1)
        open_opt.Button.click()

    def preview(self):
        input("\nPress [ENTER] to Preview\n")
        print("Previewing Zyla video...")
        self.soliswin.menu_select("Acquisition->Take Video")

    def acquire():
        input("\nPress [ENTER] to Acquire\n")
        self.soliswin.menu_select
        cwd = os.getcwd()

        spra_deaux = "resources\solis_scripts\SPRA_deaux"

        files = '"%s\%s"' % (cwd, spra_deaux)

        print("Beginning Acquisiton in SOLIS...")
        app = Application().connect(title_re="Andor")
        andor = app.window(title_re="Andor")
        andor.menu_select("File->Open")
        open_opt = app.window(title_re="Open")
        file_name = open_opt.Edit.set_text(files)
        open_opt.ComboBox3.select('Andor Program Files  (*.pgm)')
        time.sleep(1)
        open_opt.Button.click()
        andor.menu_select("File -> Run Program")

if __name__ == '__main__':
    camera = Andor(0)
    settings = {
        "binning":"4x4",
        "height":2048,
        "bottom":1,
        "width":2048,
        "top":1,
        "exposure_time":0.000000,
        "f":1,
        "rdur":5.00000,
        "spool_stim":"runA_stim",
        "spoollocation":"D:/test/runA",
        "ntrials":1
    }
    camera.set_parameters(settings)
    camera.preview()
    camera.acquire()
