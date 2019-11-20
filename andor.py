import psutil, os, json, time, subprocess, pyautogui, shutil, path, win32api
from pywinauto import Application
from pywinauto.controls.menuwrapper import MenuItemNotEnabled
from pywinauto.findwindows import ElementNotFoundError
from colorama import Fore, Style
from shutil import copyfile
from datetime import datetime
from arduino import Arduino
import numpy as np

class Andor():

    def __init__(self):
        print("Initializing SOLIS...")
        pids = [(p.pid) for p in psutil.process_iter() if p.name() == "AndorSolis.exe"]
        if len(pids) < 1:
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
        time.sleep(1)
        try:
            print("Trying to Preview")
            self.preview()
        except MenuItemNotEnabled:
            try:
                print("Trying to Abort Preview")
                self.abort()
            except MenuItemNotEnabled:
                print("Andor is not open. Closing all Andor related Processes")
                pids = [(p.pid) for p in psutil.process_iter() if p.name() == "AndorSolis.exe"]
                for pid in pids:
                    psutil.Process(pid).terminate()
                win32api.MessageBox(0, "Camera is Not Detected", "SOLIS Error")
                sys.exit()

    def set_parameters(self, preview):
        self.abort()

        with open("JSPLASSH/settings.json") as f:
            self.settings = json.load(f)
        f.close()

        if preview:
            run_len = "5"
            num_run = "1"
        else:
            run_len = self.settings["run"]["run_length"]
            num_run = self.settings["run"]["num_runs"]

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
            f.write(run_len+"\n")
            f.write(run_name+"\n")
            f.write(spool_path+"\n")
            f.write(num_run)
        f.close()
        file = '"%s\%s"' % (cwd, set_param)
        print("Setting parameters in SOLIS...")
        self.soliswin.menu_select("File -> Run Program By Filename")
        open_opt = self.solis.window(title_re="Open")
        file_name = open_opt.Edit.set_text(file)
        open_opt.Button.click()
        print("Reading FrameRate + ExposureTime from zyla_settings.txt")

    def get_framerate(self):
        with open("resources/solis_scripts/zyla_settings.txt", "r") as f:
            count = 0
            for item in f.readlines():
                if count == 5:
                    et = item
                    print("\nExposureTime: "+item)
                    self.update_json_settings("camera", "exposure_time", item)
                elif count == 6:
                    fr = item
                    print("\nFramerate: "+item)
                    self.update_json_settings("camera", "framerate", item)
                else:
                    pass
                count += 1
        f.close()

    def update_json_settings(self, type, param, value):
        with open("JSPLASSH/settings.json", "r+") as f:
            self.settings = json.load(f)
            self.settings[type][param] = value
            f.seek(0)
            json.dump(self.settings, f)
            f.truncate()
        f.close()

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
        self.get_framerate()
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
        time.sleep(float(self.settings["run"]["run_length"])*float(self.settings["run"]["num_runs"]))

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
                    self.set_parameters(True)
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
    andor = Andor()
    andor.get_framerate()
