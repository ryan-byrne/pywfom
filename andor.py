import psutil, os, json, time, subprocess, pyautogui, shutil, path, win32api
from pywinauto import Application
from pywinauto.controls.menuwrapper import MenuItemNotEnabled
from pywinauto.findwindows import ElementNotFoundError
from colorama import Fore, Style
from shutil import copyfile
from datetime import datetime
from resources.camera.atcore import *
from arduino import Arduino
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
            print("Initializing SOLIS...")
            pids = [(p.pid) for p in psutil.process_iter() if p.name() == "AndorSolis.exe"]
            if len(pids) < 2:
                print("Opening SOLIS")
                subprocess.Popen("C:\Program Files\Andor SOLIS\AndorSolis.exe")
                while True:
                    try:
                        self.solis = Application().connect(title_re="Andor")
                        self.soliswin = self.solis.window(title_re="Andor")
                        self.deployed = False
                        print("\n")
                        break
                    except ElementNotFoundError:
                        print("Waiting for SOLIS to Open...", end="\r")
                        pass

            else:
                print("SOLIS is already open")
                pass
            self.solis = Application().connect(title_re="Andor")
            self.soliswin = self.solis.window(title_re="Andor")
            self.deployed = False
            try:
                self.preview()
            except MenuItemNotEnabled:
                pids = [(p.pid) for p in psutil.process_iter() if p.name() == "AndorSolis.exe"]
                for pid in pids:
                    psutil.Process(pid).terminate()
                win32api.MessageBox(0, "Camera is Not Detected", "SOLIS Error")
                sys.exit()


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

    def set_parameters(self):
        self.abort()
        s = ["height", "bottom", "width", "top", "exposure_time", "framerate"]
        cam_settings = self.settings["camera"]
        print("Creating zyla_settings.txt file...")
        cwd = os.getcwd()
        set_param = "resources\solis_scripts\set_parameters.pgm"
        spool_path = self.path+"/CCD"
        run_name = "run0"
        with open("resources/solis_scripts/zyla_settings.txt", "w+") as f:
            f.write(str(cam_settings["binning"][0])+"\n")
            for setting in s:
                f.write(str(cam_settings[setting])+"\n")
            f.write(self.settings["run"]["run_len"]+"\n")
            f.write(run_name+"\n")
            f.write(spool_path+"\n")
            f.write(self.settings["run"]["num_run"])

        file = '"%s\%s"' % (cwd, set_param)

        print("Setting parameters in SOLIS...")
        self.soliswin.menu_select("File -> Run Program By Filename")
        open_opt = self.solis.window(title_re="Open")
        file_name = open_opt.Edit.set_text(file)
        open_opt.Button.click()

    def preview(self):
        print("Previewing Zyla video...")
        self.soliswin.menu_select("Acquisition->Take Video")

    def abort(self):
        try:
            print("Aborting Zyla Video.")
            self.soliswin.menu_select("Acquisition->Abort Acquisition")
        except MenuItemNotEnabled:
            pass

    def acquire(self):

        print("Moving JSPLASSH/settings.json to "+self.path+"/settings.json")
        src = "JSPLASSH/settings.json"
        dst = self.path+"/settings.json"
        shutil.move(src, dst)

        print("Files to be sent to: {0}".format(self.path))
        self.abort()
        cwd = os.getcwd()
        acquire = "resources\solis_scripts\\acquire.pgm"
        file = '"%s\%s"' % (cwd, acquire)

        self.soliswin.menu_select("File -> Run Program By Filename")
        open_opt = self.solis.window(title_re="Open")
        file_name = open_opt.Edit.set_text(file)
        open_opt.Button.click()
        print("\n"+"*"*25+"Acquisition Successfully Initiated"+"*"*25+"\n")
        time.sleep(float(self.settings["run"]["run_len"])*float(self.settings["run"]["num_run"]))

    def info_gui(self):
        print("Waiting for Run Info from GUI...")
        os.chdir("JSPLASSH")
        if os.path.isfile("settings.json"):
            os.remove("settings.json")
        subprocess.call(["java", "-jar", "info.jar"])
        os.chdir("..")

        cpu_name = os.environ['COMPUTERNAME']
        print("This computer's name is "+cpu_name)
        if cpu_name == "DESKTOP-TFJIITU":
            path = "S:/WFOM/data/"
        else:
            path = "C:/WFOM/data/"

        date = str(datetime.now())[:10]

        with open("JSPLASSH/settings.json") as f:
            settings = json.load(f)
            mouse = settings["info"]["mouse"]
        f.close()

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
        print("Making directory: "+path+"/webcam")
        os.mkdir(path+"/webcam")

        self.path = path

    def camera_gui(self):
        print("Waiting for Camera parameters from GUI...")
        os.chdir("JSPLASSH")
        subprocess.Popen(["java", "-jar","camera.jar"])
        os.chdir("..")
        old_settings = {"camera":{"fake"}}
        print("Waiting for Camera settings to be Deployed")
        while not self.deployed:
            with open("JSPLASSH/settings.json") as f:
                self.settings = json.load(f)
            f.close()
            if "camera" not in self.settings.keys():
                pass
            else:
                update = False
                for k in self.settings["camera"].keys():
                    if len(old_settings.keys()) == 1 or self.settings["camera"][k] != old_settings["camera"][k]:
                        self.settings["run"] = {"run_len":"5.0", "num_run":"1"}
                        update = True
                if update:
                    print("Updating Preview with new Settings")
                    self.set_parameters()
                    time.sleep(3)
                    self.preview()
            old_settings = self.settings
            time.sleep(1)
            try:
                #deployed = self.settings.camera.deployed
                self.deployed = self.settings["camera"]["deployed"]
            except KeyError:
                self.deployed = False
        print("Deploying settings to Camera")

if __name__ == '__main__':
    andor = Andor(0)
