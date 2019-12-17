import shutil, psutil, json, time, os, subprocess, path, sys, win32api, serial

from pywinauto import Application
from serial import Serial
from datetime import datetime
from shutil import copyfile

from pywinauto.controls.menuwrapper import MenuItemNotEnabled
from pywinauto.findwindows import ElementNotFoundError

def read_json_settings():
    with open("JSPLASSH/settings.json", "r") as f:
        settings = json.load(f)
    f.close()
    return settings

def update_json_settings(old_settings):
    parameters = ["binning", "height", "bottom", "width", "length", "exposure", "framerate"]
    with open("JSPLASSH/settings.json", "r+") as f:
        settings = json.load(f)
        settings["camera"] = {}
        for i in range(len(parameters)):
            settings["camera"][parameters[i]] = old_settings[i]
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

def update_zyla_settings(path):
    print("Updating settings.txt file")
    print("Reading settings from settings.json")
    json_settings = read_json_settings()
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

def main():
    andor = Andor()
    arduino = Arduino("COM4")
    andor.info_gui()
    andor.camera_gui()
    arduino.strobe_gui()
    arduino.stim_gui()
    andor.set_parameters(preview=False)
    arduino.turn_on_strobing()
    andor.acquire()
    arduino.turn_off_strobing()

def test():
    andor = Andor()
    andor.info_gui()

class Andor():

    def __init__(self):
        print("Initializing SOLIS...")
        pids = [(p.pid) for p in psutil.process_iter() if p.name() == "AndorSolis.exe"]
        print(pids)
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
        self.path = ""
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
        cwd = os.getcwd()
        set_param = "resources\solis_scripts\set_parameters.pgm"
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

        update_zyla_settings(self.path)

        self.settings = read_json_settings()

        print("Moving JSPLASSH/settings.json to "+self.path+"/settings.json")
        src = "JSPLASSH/settings.json"
        dst = self.path+"/settings.json"
        shutil.move(src, dst)

        self.abort()
        cwd = os.getcwd()
        acquire = "resources\solis_scripts\\acquire.pgm"
        file = '"%s\%s"' % (cwd, acquire)

        self.soliswin.menu_select("File -> Run Program By Filename")
        open_opt = self.solis.window(title_re="Open")
        file_name = open_opt.Edit.set_text(file)
        open_opt.Button.click()
        print("\n"+"*"*25+"Acquisition Successfully Initiated"+"*"*25+"\n")
        time.sleep(2*float(self.settings["run"]["run_len"])*float(self.settings["run"]["num_run"]))
        subprocess.Popen(r'explorer /select,"{0}"/'.format(self.path))

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

        settings = read_json_settings()
        mouse = settings["info"]["mouse"]

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
        print("Opening Camera Settings GUI...")
        os.chdir("JSPLASSH")
        subprocess.Popen(["java", "-jar","camera.jar"])
        os.chdir("..")
        print("Waiting for Camera settings to be Deployed")
        old_settings = read_zyla_settings()
        while len(old_settings) < 12:
            # Read the settings from the txt file generated by the GUI

            settings = read_zyla_settings()

            update = False
            # Loop through each setting
            for i in range(len(old_settings)):
                if i > 7:
                    # Stop when you get to the File Names
                    break
                old = int(round(float(old_settings[i])))
                new = int(round(float(settings[i])))
                if old != new:
                    # Get ready to update if a setting has changed
                    update = True
                else:
                    pass
            if update:
                print("Updating Preview with new Settings")
                self.set_parameters(True)
                time.sleep(3)
                self.preview()
            old_settings = read_zyla_settings()
            time.sleep(1)
        print("Deploying settings to Camera")
        print("Update settings.json file")
        settings = update_json_settings(old_settings)
        self.settings = settings

    def run_gui(self):
        camera = Andor()

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, port):
        print("Attempting to Connect to Arduino at Serial Port: "+port)
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
            print("Successfully connected to Arduino at {0}".format(port))
        except serial.SerialException as e:
            win32api.MessageBox(0, "Can not enable the Arduino", "Arduino Error")
            print(e.strerror)
            sys.exit()

    def disable(self):
        print("Enabling Python Arduino Communication")
        self.ser.close()

    def enable(self):
        print("Enabling Python-Arduino Communication")
        self.ser.open()
        time.sleep(3)

    def set_strobe_order(self):
        order = ""
        for led in self.strobe_order:
            order += led[0]
        print("Setting the Strobe order on the Arduino to: "+order)
        self.ser.write(order.encode())

    def clear(self):
        self.ser.write("0000".encode())

    def strobe_gui(self):
        print("Waiting to Recieve Strobe Settings from GUI...")
        self.disable()
        os.chdir("JSPLASSH")
        subprocess.call(["java", "-jar", "strobe.jar"])
        os.chdir("..")
        self.enable()
        settings = read_json_settings()
        self.strobe_order = settings["strobe_order"]
        self.set_strobe_order()

    def stim_gui(self):
        print("Waiting to Recieve Stim Settings from GUI...")
        os.chdir("JSPLASSH")
        subprocess.call(["java", "-jar", "stim.jar"])
        os.chdir("..")
        print("Updating settings.txt file")
        update_zyla_settings(False)

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
