import shutil, psutil, json, time, os, subprocess, path, sys, win32api, serial
from serial import Serial
from datetime import datetime
from shutil import copyfile

from argparse import ArgumentParser

from pywinauto import Application
from pywinauto.timings import TimeoutError
from pywinauto.controls.menuwrapper import MenuItemNotEnabled
from pywinauto.base_wrapper import ElementNotEnabled
from pywinauto.findwindows import ElementNotFoundError

def get_args():

    parser = ArgumentParser()

    parser.add_argument("-q", "--quiet",
                    action="store_true", dest="quiet", default=False,
                    help="Don't print status messages to stdout")
    parser.add_argument("-y",
                    action="store_true", dest="yes", default=False,
                    help="Automatically accept errors and continue")

    args = parser.parse_args()

    return args

args = get_args()

def prompt(msg):
    if args.quiet:
        pass
    else:
        print(msg)

def error_prompt(msg):
    if args.yes or (input(msg+"  Continue anyways? [y/n] ") == "y"):
        pass
    else:
        sys.exit()

def read_json_settings():
    with open("JavaGUI/settings.json", "r") as f:
        settings = json.load(f)
    f.close()
    return settings

def update_json_settings(OLD_SETTINGS):
    parameters = ["binning", "height", "bottom", "width", "length", "exposure", "framerate"]
    with open("JavaGUI/settings.json", "r+") as f:
        settings = json.load(f)
        settings["camera"] = {}
        for i in range(len(parameters)):
            settings["camera"][parameters[i]] = OLD_SETTINGS[i]
        f.seek(0)
        json.dump(settings, f)
        f.truncate()
    f.close()
    return settings

def read_zyla_settings():
    #print("Reading settings.txt file")
    with open("resources/solis_scripts/settings.txt", "r") as f:
        settings = f.readlines()
    f.close()
    return [x.strip() for x in settings]

def update_zyla_settings(path, settings):
    print("Updating settings.txt file")
    print("Reading settings from settings.json")
    json_settings = settings
    with open("resources/solis_scripts/settings.txt", "r+") as f:
        settings = f.readlines()
        settings = [x.strip() for x in settings]
        count = 0
        f.seek(0)
        for s in settings:
            count += 1
            if count == 8:
                f.write(json_settings["run"]["run_len"]+"\n")
            elif count == 10 and path:
                f.write(path+"\n")
            elif count == 11:
                f.writelines(json_settings["run"]["num_run"]+"\n")
            else:
                f.writelines(s+"\n")
    f.close()

def test():

    """

    settings.json Status Flag:

    0: Begin Acquisition
    1: Open Info GUI
    2: Open Camera GUI
    3: Open Strobe GUI
    4: Open Stim GUI
    5: Open Preview GUI
    6: Settings Deployed


    """

    status = 5

    andor = Andor()
    arduino = Arduino("COM4")
    webcam = Webcam()

    COMMAND_ARRAY = [
        andor.acquire,
        andor.info,
        andor.camera,
        arduino.strobe,
        arduino.stim,
        andor.preview
    ]

    while status > 0:
        COMMAND_ARRAY[status]()
        status = read_json_settings()["status"]

class Andor():

    def __init__(self):

        self.path = ""

        prompt("Checking if SOLIS is Open...")

        pids = [(p.pid) for p in psutil.process_iter() if p.name() == "AndorSolis.exe"]
        if len(pids) < 1:
            prompt("SOLIS is not open. Opening it now...")
            self.open_solis()
        else:
            prompt("SOLIS is already open...")
        self.connect_to_solis()

    def open_solis(self):
        try:
            app = Application().start("C:\Program Files\Andor SOLIS\AndorSolis.exe", timeout=10)
        except TimeoutError:
            error_prompt("Opening SOLIS Timed Out.")

    def connect_to_solis(self):
        prompt("Attempting to Connect to SOLIS")
        try:
            self.solis = Application().connect(title_re="Andor SOLIS", timeout=3)
            self.soliswin = self.solis.window(title_re="Andor SOLIS", found_index=0)
            self.view()
        except TimeoutError:
            error_prompt("Connection to SOLIS Timed Out.")
        except MenuItemNotEnabled:
            error_prompt("Connection to the Camera Failed.")

    def set_parameters(self, preview):
        self.abort()
        cwd = os.getcwd()
        set_param = "resources\solis_scripts\set_parameters.pgm"
        file = '"%s\%s"' % (cwd, set_param)
        prompt("Setting parameters in SOLIS...")
        try:
            self.soliswin.menu_select("File -> Run Program By Filename")
            open_opt = self.solis.window(title_re="Open")
            file_name = open_opt.Edit.set_text(file)
            open_opt.Button.click()
        except MenuItemNotEnabled:
            error_prompt("Menu Item Not Enabled in SOLIS. Camera is likely disconnected.")

    def view(self):
        prompt("Attempting to Initiate Camera Preview in SOLIS")
        try:
            self.soliswin.menu_select("Acquisition->Take Video")
        except MenuItemNotEnabled:
            error_prompt("Unable to View. Camera not connected.")

    def abort(self):
        prompt("Attempting to Abort Camera Preview in SOLIS")
        try:
            self.soliswin.menu_select("Acquisition->Abort Acquisition")
        except MenuItemNotEnabled:
            error_prompt("Unable to Abort.")

    def acquire(self):

        prompt("Making directory: "+self.path)
        os.mkdir(self.path)
        prompt("Making directory: "+self.path+"/CCD")
        os.mkdir(self.path+"/CCD")
        prompt("Making directory: "+self.path+"/webcam")
        os.mkdir(self.path+"/webcam")

        update_zyla_settings(self.path, self.settings)

        src = "JavaGUI/settings.json"
        dst = self.path+"/settings.json"

        prompt("Moving JavaGUI/settings.json to "+self.path+"/settings.json")
        shutil.move(src, dst)

        self.abort()
        cwd = os.getcwd()
        acquire = "resources\solis_scripts\\acquire.pgm"
        file = '"%s\%s"' % (cwd, acquire)

        self.soliswin.menu_select("File -> Run Program By Filename")
        open_opt = self.solis.window(title_re="Open")
        file_name = open_opt.Edit.set_text(file)
        open_opt.Button.click()
        prompt("\n"+"*"*25+"Acquisition Successfully Initiated"+"*"*25+"\n")
        time.sleep(2*float(self.settings["run"]["run_len"])*float(self.settings["run"]["num_run"]))
        subprocess.Popen(r'explorer /select,"{0}"/'.format(self.path))

    def info(self):

        prompt("Waiting for Run Info from GUI...")
        os.chdir("JavaGUI")
        if os.path.isfile("settings.json"):
            os.remove("settings.json")
        subprocess.call(["java", "-jar", "JARs/info.jar"])
        os.chdir("..")

        self.settings = read_json_settings()

        mouse = self.settings["info"]["mouse"]
        path = "D:/WFOM/data/"
        with open("JavaGUI/archive.json", "r+") as f:
            archive = json.load(f)
            d = archive["mice"][mouse]["last_trial"]+1
            archive["mice"][mouse]["last_trial"] = d
            f.seek(0)
            json.dump(archive, f, indent=4)
            f.truncate()
            self.archive = archive
        f.close()

        if not os.path.isdir(path + mouse + "_" + str(d)):
            path = path + mouse + "_" + str(d)
        else:
            path = path + mouse + "_" + str(d+1)

        self.path = path

    def camera(self):
        prompt("Opening Camera Settings GUI...")
        if "camera" in self.settings.keys():
            # Settings already established
            prompt(self.settings)
            SETTINGS_NAME = self.settings["camera"]
            self.settings["camera"] = self.archive["settings"][SETTINGS_NAME]
            self.deployed = True
        else:
            os.chdir("JavaGUI")
            subprocess.Popen(["java", "-jar","JARs/camera.jar"])
            os.chdir("..")
            self.deployed = False
        prompt("Waiting for Camera settings to be Deployed")
        OLD_SETTINGS = read_zyla_settings()
        while not self.deployed:
                # Read the settings from the txt file generated by the GUI
                settings = read_zyla_settings()
                update = False
                # Loop through each setting
                for i in range(len(OLD_SETTINGS)):
                    if i > 7:
                        # Stop when you get to the File Names
                        break
                    old = float(OLD_SETTINGS[i])
                    new = float(settings[i])
                    if old != new:
                        # Get ready to update if a setting has changed
                        update = True
                    else:
                        pass
                if update:
                    prompt("Updating Preview with new Settings")
                    self.set_parameters(True)
                    time.sleep(3)
                    self.view()
                OLD_SETTINGS = read_zyla_settings()
                if len(OLD_SETTINGS) == 12:
                    self.deployed = True
                    self.settings = update_json_settings(OLD_SETTINGS)
                time.sleep(3)

    def preview(self):
        os.chdir("JavaGUI")
        subprocess.Popen(["java", "-jar","JARs/preview.jar"])
        os.chdir("..")

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, port):
        prompt("Attempting to Connect to Arduino at Serial Port: "+port)
        self.port = port
        try:
            self.ser = serial.Serial(
                port=self.port,\
                baudrate=115200,\
                parity=serial.PARITY_NONE,\
                stopbits=serial.STOPBITS_ONE,\
                bytesize=serial.EIGHTBITS,\
                    timeout=0)
            time.sleep(3)
            self.connected = 1
            prompt("Successfully connected to Arduino at {0}".format(port))
        except serial.SerialException as e:
            error_prompt("Arduino is not Connected.")

    def disable(self):
        prompt("Enabling Python Arduino Communication")
        self.ser.close()

    def enable(self):
        prompt("Enabling Python-Arduino Communication")
        self.ser.open()
        time.sleep(3)

    def set_strobe_order(self):
        order = ""
        for led in self.strobe_order:
            order += led[0]
        prompt("Setting the Strobe order on the Arduino to: "+order)
        self.ser.write(order.encode())

    def clear(self):
        self.ser.write("0000".encode())

    def strobe(self):
        prompt("Waiting to Recieve Strobe Settings from GUI...")
        self.disable()
        os.chdir("JavaGUI")
        subprocess.call(["java", "-jar", "JARs/strobe.jar"])
        os.chdir("..")
        self.enable()
        settings = read_json_settings()
        self.strobe_order = settings["strobe_order"]
        self.set_strobe_order()

    def stim(self):
        prompt("Waiting to Recieve Stim Settings from GUI...")
        os.chdir("JavaGUI")
        subprocess.call(["java", "-jar", "JARs/stim.jar"])
        os.chdir("..")

    def turn_on_strobing(self):
        self.ser.write("S".encode())

    def turn_off_strobing(self):
        self.ser.write("s".encode())

class Webcam():
    """docstring for Webcam."""

    def __init__(self):
        self.connected = 1

if __name__ == '__main__':
    test()
