import shutil, psutil, json, time, os, subprocess, path, sys, win32api, serial
import argparse, re
from serial import Serial
from datetime import datetime
from shutil import copyfile
from pyfiglet import Figlet
from termcolor import colored
from pywinauto.application import Application, AppStartError
from pywinauto.timings import TimeoutError
from pywinauto.controls.menuwrapper import MenuItemNotEnabled
from pywinauto.base_wrapper import ElementNotEnabled
from pywinauto.findwindows import ElementNotFoundError

def prompt(msg):

    """

    This function is called instead of 'print'

    It checks if the script is running in quiet mode, then prints the message
    if it is not.


    """

    os.system("cls")

    w = Figlet(font='speed')
    print(w.renderText("OpenWFOM"))
    print("")

    if args.quiet:
        render_ascii('mouse', "Shh. I am running in 'Quiet Mode'. I will only\
        notify you if an Error occurs.")
    else:
        render_ascii('mouse', msg)

    print("")

def error_prompt(e, msg):

    """

    This function is called when an error is found.

    * Prints a red 'ERROR'
    * Prints the message script
    * Asks if the user would like to continue despite the error

    """

    err = colored('ERROR: ', 'red')

    q = colored('Continue anyway? [y/n] ', 'yellow')

    msg = colored(msg, 'red', attrs=['blink'])

    input_script = "{0} \n\n{1}".format(msg, q)

    print(err, e)
    print("\n")

    if args.yes:
        print(msg)
        time.sleep(3)
    elif (input(input_script) == "y"):
        pass
    else:
        sys.exit()

def render_ascii(name, msg):
    """

    Print the talking mouse

    """
    # set max len of string
    mlen = 51
    l = len(msg)
    # set indent
    ind = 5
    print((ind+1)*" "+"_"*min([l+2, mlen+2]))
    print(ind*" "+"/ "+min([l+1, mlen+1])*" "+"\\")
    for i in range(1+int(l/mlen)):
        msg_line = msg[mlen*i:mlen*(i+1)]
        print(ind*" "+"| " + msg_line + min(l-len(msg_line), mlen-len(msg_line))*" "+" |")
    print((ind-1)*" "+" \_"+"_"*13+" "+min([l-13,mlen-13])*"_"+"/")
    print((ind+15)*" "+"V")
    with open("resources/asciiart/"+name+".txt") as f:
        lines = f.readlines()
        for line in lines:
            print(line, end="")
    f.close()

def welcome_banner(mode):

    os.system("cls")

    w = Figlet(font='speed')
    print(w.renderText("OpenWFOM"))
    print("")

    m = Figlet(font='cybermedium')
    print(m.renderText(" "*3+mode+" Mode"))

    if mode == "Test":
        print("\n A diagnostic test of your OpenWFOM installation will begin shortly.")
    else:
        print("\n The screen to input 'Run Settings' will appear shortly.")

    time.sleep(3)

def get_args(skip):

    """

    This function simply checks for arguments when the script is called
    and stores them in their corresponding variable.

    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-q", "--quiet",
                    action="store_true", dest="quiet", default=False,
                    help="Don't print status messages to stdout")
    parser.add_argument("-y",
                    action="store_true", dest="yes", default=skip,
                    help="Automatically accept errors and continue")

    parser.add_argument("-t", "--test",
                    action="store_true", dest="test", default=False,
                    help="Runs the test function instead of run")

    args = parser.parse_args()


    return args

def log_test_file(results):
    now = datetime.now()
    log_name = now.strftime("%m-%d-%Y-%H%M%S") + ".txt"
    path = "resources\\tests\\{0}".format(log_name)
    with open(path, "w+") as f:
        for line in results:
            f.write(line+"\n")
    f.close()
    return path

def run():

    """

    This function will execute when an acquisition is to be taken.

    It starts by initiating each of the required classes: Andor, Arduino, and
    Webcam.

    A specific command will then be run from the COMMAND_ARRAY depending on
    the status flag contained within the settings.json file.

    settings.json Status Flag:

    0: Begin Acquisition
    1: Open Info GUI
    2: Open Camera GUI
    3: Open Strobe GUI
    4: Open Stim GUI
    5: Open Preview GUI
    6: Settings Deployed


    """

    welcome_banner("Run")

    andor = Andor()
    arduino = Arduino("COM4")
    webcam = Webcam()

    # Create the dict for the required
    COMMANDS = {
        "info":andor.info,
        "camera":andor.camera,
        "strobe_order":arduino.strobe,
        "stim":arduino.stim,
        "run":arduino.stim,
        "preview":andor.preview
    }

    # Loop until you've completed the settings.json file
    while True:
        # See which settings are missing from settings.json
        st = set(andor.JSON_SETTINGS.keys())
        TO_BE_COMPLETED = [ele for ele in COMMANDS.keys() if ele not in st]
        # See if there are any missing settings
        if len(TO_BE_COMPLETED) == 0:
            # Exit loop if no
            break
        else:
            # Run command if yes
            COMMANDS[TO_BE_COMPLETED[0]]()
            andor.read_json_settings()

    # Begin Acquisition
    andor.acquire()

def test():

    """

    This script should be run immediatly after the setup.py installation.

    It checks the following:
        1) Installation of correct Java Runtime
        2) Connection to Camera and SOLIS
        3) Connection to Arduino
        4) Connection to Webcams
        5)

    """

    welcome_banner("Test")

    prompt("Running diagnostic test on WFOM...")

    prompt("Testing connection to Camera and SOLIS")
    andor = Andor()
    prompt("Testing connection to Arduino")
    arduino = Arduino("COM4")
    prompt("Testing connection to Webcams")
    webcam = Webcam()

    prompt("Logging test File")

    try:
        path = log_test_file(arduino.TEST_RESULTS+andor.TEST_RESULTS)
    except Exception as e:
        path = "nowhere"
        msg = "Could not create the log test file."
        error_prompt(e, msg)

    prompt("Test Complete... The Following Errors were logged to {0}".format(colored(os.getcwd()+"\\"+path, 'green')))

    for error in arduino.TEST_RESULTS + andor.TEST_RESULTS:
        print(colored('ERROR: ', 'red')+" "+str(error))

class Andor():

    """

    This class is used for interaction between the Java GUI's and Andor SOLIS.

    It is initiated in both the Test and Run Modes.

    """

    def __init__(self):

        self.PATH_TO_FILES = ""

        self.JSON_SETTINGS = {}

        self.TEST_RESULTS = []

        self.check_java()

        prompt("Checking if SOLIS is Open...")

        pids = [(p.pid) for p in psutil.process_iter() if p.name() == "AndorSolis.exe"]
        if len(pids) < 1:
            prompt("SOLIS is not open. Opening it now...")
            self.open_solis()
        else:
            prompt("SOLIS is already open...")
        self.connect_to_solis()

    def info(self):

        """

        For information on the 'Info' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#1-info-gui

        """

        prompt("Waiting for Run Info from GUI...")

        os.chdir("JavaGUI")
        if os.path.isfile("settings.json"):
            os.remove("settings.json")
        subprocess.call(["java", "-jar", "JARs/info.jar"])
        os.chdir("..")

        self.read_json_settings()

        self.create_path_to_files()

    def camera(self):

        """

        For information on the 'Camera' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#2-camera-gui

        """
        prompt("Opening Camera Settings GUI...")
        os.chdir("JavaGUI")
        subprocess.Popen(["java", "-jar","JARs/camera.jar"])
        os.chdir("..")

        prompt("Waiting for Camera settings to be Deployed")
        self.read_zyla_settings()
        OLD_ZYLA_SETTINGS = self.ZYLA_SETTINGS
        while True:
                # Read the settings from the txt file generated by the GUI
                self.read_zyla_settings()
                update = False
                # Loop through each setting
                for i in range(len(self.ZYLA_SETTINGS)):
                    if i > 7:
                        # Stop when you get to the File Names
                        break
                    # Setting from Last Scan
                    old = float(OLD_ZYLA_SETTINGS[i])
                    # Setting from latest scan
                    new = float(self.ZYLA_SETTINGS[i])
                    if old != new:
                        # Get ready to update if a setting has changed
                        update = True
                    else:
                        pass
                if update:
                    prompt("Updating Preview with new Settings")
                    self.set_parameters()
                    time.sleep(3)
                    self.view()
                self.read_zyla_settings()
                OLD_ZYLA_SETTINGS = self.ZYLA_SETTINGS
                if len(OLD_ZYLA_SETTINGS) == 12:
                    self.deploy_json_camera_settings()
                    break
                time.sleep(3)

    def open_solis(self):

        """

        Opens a new instance of AndorSolis.exe

        The command will Timeout after 10 seconds

        """

        try:
            app = Application().start(r"C:\Program Files\Andor SOLIS\AndorSolis.exe", timeout=10)
        except Exception as e:
            msg = "You may not have SOLIS Installed."
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def connect_to_solis(self):

        """

        Attaches a pywinauto controller to the Andor Window.

        The connection times out after 3 seconds.

        It then creates the variable 'self.soliswin' which will be used by
        the script later.

        """

        prompt("Attempting to Connect to SOLIS")
        try:
            self.solis = Application().connect(title_re="Andor SOLIS", timeout=3)
            self.soliswin = self.solis.window(title_re="Andor SOLIS", found_index=0)
            self.view()
        except Exception as e:
            msg = "The window to SOLIS may have closed."
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def preview(self):

        """

        For information on the 'Preview' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#5-preview-gui

        """

        prompt("Review the Settings. Select 'Begin Acquisition' start.")

        os.chdir("JavaGUI")
        subprocess.call(["java", "-jar","JARs/preview.jar"])
        os.chdir("..")

    def set_parameters(self):

        """

        Executes the Solis PGM 'set_parameters.pgm', which reads the SETTINGS
        from 'settings.txt' and deploys them to the camera.

        If the Menu Item is not enabled, an error prompt will appear.

        """

        self.abort()
        cwd = os.getcwd()
        set_param = r"resources\solis_scripts\set_parameters.pgm"
        file = r'"%s\%s"' % (cwd, set_param)
        prompt("Setting parameters in SOLIS...")
        try:
            self.soliswin.menu_select("File -> Run Program By Filename")
            open_opt = self.solis.window(title_re="Open")
            file_name = open_opt.Edit.set_text(file)
            open_opt.Button.click()
        except (Exception, MenuItemNotEnabled) as e:
            msg = "The camera is likely not attached and/or plugged in."
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def deploy_json_camera_settings(self):

        """

        Reads the Zyla 'settings.txt' file, converts it to a Python dict and
        sends the settings to 'settings.json'

        """

        # Update the self.ZYLA_SETTINGS list file
        self.read_zyla_settings()

        prompt("Updating the Camera settings in 'settings.json'")
        parameters = ["binning", "height", "bottom", "width", "length", "exposure", "framerate"]

        # Open 'settings.json' to be editable
        with open("JavaGUI/settings.json", "r+") as f:
            # Create an empty dict under self.JSON_SETTINGS.camera
            self.JSON_SETTINGS["camera"] = {}
            # Iterate through each parameter and match it with its ZYLA_SETTING
            for i in range(len(parameters)):
                self.JSON_SETTINGS["camera"][parameters[i]] = self.ZYLA_SETTINGS[i]
            f.seek(0)
            json.dump(self.JSON_SETTINGS, f)
            f.truncate()
        f.close()

    def check_java(self):

        prompt("Checking Version of Java Runtime Environment")

        try:
            out = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT).decode("utf-8")
            version = ""
            for l in out:
                if len(version) > 0 and l == '"':
                    break
                elif l in [".", "_"] or l.isdigit():
                    version += l
                else:
                    continue

        except Exception as e:
            msg = ""
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

        prompt("JRE {0} is installed".format(version))

        if float(version[:3]) < 1.8:
            msg = "JRE 1.8 or higher is required to run OpenWFOM"
            self.TEST_RESULTS.append(msg)
            error_prompt(msg)

    def view(self):

        prompt("Attempting to Initiate Camera Preview in SOLIS")

        try:
            self.soliswin.menu_select("Acquisition->Take Video")
        except Exception as e:
            msg = "The camera is likely not attached and/or plugged in."
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def abort(self):

        prompt("Attempting to Abort Camera Preview in SOLIS")

        try:
            self.soliswin.menu_select("Acquisition->Abort Acquisition")
        except Exception as e:
            msg = "The camera is likely not attached and/or plugged in."
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def make_directories(self):
        try:
            prompt("Making directory: "+self.PATH_TO_FILES)
            os.mkdir(self.PATH_TO_FILES)
            prompt("Making directory: "+self.PATH_TO_FILES+"/CCD")
            os.mkdir(self.PATH_TO_FILES+"/CCD")
            prompt("Making directory: "+self.PATH_TO_FILES+"/webcam")
            os.mkdir(self.PATH_TO_FILES+"/webcam")
            src = "JavaGUI/settings.json"
            dst = self.PATH_TO_FILES+"/settings.json"

            prompt("Moving JavaGUI/settings.json to "+self.PATH_TO_FILES+"/settings.json")
            shutil.move(src, dst)
        except Exception as e:
            msg = "Could make the directories at {0}".format(self.PATH_TO_FILES)
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def update_zyla_settings(self):

        prompt("Updating settings.txt file")
        prompt("Reading settings from settings.json")

        self.update_json_settings()

        # Loop through each settings (or)
        for setting in self.read_zyla_settings():
            count += 1
            if count == 8:
                f.write(self.JSON_SETTINGS["run"]["run_len"]+"\n")
            elif count == 10 and self.PATH_TO_FILES:
                f.write(self.PATH_TO_FILES+"\n")
            elif count == 11:
                f.writelines(self.JSON_SETTINGS["run"]["num_run"]+"\n")
            else:
                f.writelines(s+"\n")

    def read_zyla_settings(self):

        """

        Checks the settings currently deployed to the camera and stored in the
        'settings.txt' file.

        """

        with open("resources/solis_scripts/settings.txt", "r") as f:
            ZYLA_SETTINGS = f.readlines()
        f.close()
        self.ZYLA_SETTINGS = [x.strip() for x in ZYLA_SETTINGS]

    def read_json_settings(self):

        prompt("Reading the 'settings.json' file...")
        try:
            with open("JavaGUI/settings.json", "r+") as f:
                self.JSON_SETTINGS = json.load(f)
            f.close()
        except Exception as e:
            msg = "Unable to find the 'settings.json' file. It may have been deleted."
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def acquire(self):

        """

        * Read the current Zyla Settings
        * Write the settings to 'settings.json'
        * Make the acquisition directories and send 'settings.json' to them

        """

        self.read_json_settings()

        self.make_directories()

        self.abort()

        cwd = os.getcwd()
        acquire = r"resources\solis_scripts\acquire.pgm"
        file = r'"%s\%s"' % (cwd, acquire)
        try:
            self.soliswin.menu_select("File -> Run Program By Filename")
            open_opt = self.solis.window(title_re="Open")
            file_name = open_opt.Edit.set_text(file)
            open_opt.Button.click()
            self.acquisition_countdown()
        except (Exception, MenuItemNotEnabled) as e:
            msg = "The camera is likely not attached and/or plugged in."
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def acquisition_countdown(self):
        total_time = 2*float(self.JSON_SETTINGS["run"]["run_len"])*float(self.JSON_SETTINGS["run"]["num_run"])
        while total_time > -1:

            min = str(int(total_time/60))
            sec = str(int(total_time % 60))

            if min == "0":
                msg = "{0} sec Remaining".format(sec)
            else:
                msg = "{0} min {1} sec Remaining".format(min, sec)

            prompt("Acquisition Started. "+msg)

            time.sleep(1)
            total_time -= 1

    def create_path_to_files(self):
        mouse = self.JSON_SETTINGS["info"]["mouse"]
        with open("JavaGUI/archive.json", "r+") as f:
            archive = json.load(f)
            d = archive["mice"][mouse]["last_trial"]+1
            archive["mice"][mouse]["last_trial"] = d
            f.seek(0)
            json.dump(archive, f, indent=4)
            f.truncate()
        f.close()
        mouse = self.JSON_SETTINGS["info"]["mouse"]
        path = "D:/WFOM/data/"
        if not os.path.isdir(path + mouse + "_" + str(d)):
            path = path + mouse + "_" + str(d)
        else:
            path = path + mouse + "_" + str(d+1)
        self.PATH_TO_FILES = path

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, port):
        prompt("Attempting to Connect to Arduino at Serial Port: "+port)
        self.port = port
        self.TEST_RESULTS = []
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
            prompt("Successfully connected to Arduino at {0}".format(self.port))
        except Exception as e:
            msg = "Unable to connect to the Arduino. Ensure that it is plugged in and connected to "+self.port
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def disable(self):
        prompt("Disabling Python <-> Arduino Communication")
        try:
            self.ser.close()
        except Exception as e:
            msg = "Unable to connect to the Arduino. Ensure that it is plugged in and connected to "+self.port
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def enable(self):
        prompt("Enabling Python <-> Arduino Communication")
        try:
            self.ser.open()
        except Exception as e:
            msg = "Unable to connect to the Arduino. Ensure that it is plugged in and connected to "+self.port
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)
        time.sleep(3)

    def set_strobe_order(self):
        order = ""
        for led in self.strobe_order:
            order += led[0]
        prompt("Setting the Strobe order on the Arduino to: "+order)
        try:
            self.ser.write(order.encode())
        except Exception as e:
            msg = "Unable to connect to the Arduino. Ensure that it is plugged in and connected to "+self.port
            self.TEST_RESULTS.append(e)
            error_prompt(e, msg)

    def clear(self):
        self.ser.write("0000".encode())

    def strobe(self):

        """

        For information on the 'Strobe' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#3-strobe-gui

        """

        prompt("Waiting to Recieve Strobe Settings from GUI...")
        self.disable()
        os.chdir("JavaGUI")
        subprocess.call(["java", "-jar", "JARs/strobe.jar"])
        os.chdir("..")

    def stim(self):

        """

        For information on the 'Stim' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#4-stim-gui

        """

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

os.system('COLOR 07')
if __name__ == '__main__':
    args = get_args(False)
    # wfom.py run from the command line (look for arguments)
    if args.test:
        test()
    else:
        run()
else:
    # wfom run as a python module
    args = get_args(True)
