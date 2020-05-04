import shutil, psutil, json, time, os, subprocess, path, sys, serial
import argparse, re, importlib, win32api
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

def _prompt(msg, style):

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
        _render_ascii('quiet', "Shh. I am running in 'Quiet Mode'. I will only\
        notify you if an Error occurs.")
    else:
        _render_ascii(style, msg)

    print("")

def _options_prompt(question, opts):

    print("\n"+question+"\n")
    for i in range(len(opts)):
        print("[{0}] {1}".format(i, opts[i]))

    answer = input("\n> ")
    a = int(answer)

    if a-1 > len(opts) or a < 0:
        raise ValueError

    return opts[a]

def _error_prompt(e, msg):

    """

    This function is called when an error is found.

    * Prints a red 'ERROR'
    * Prints the message script
    * Asks if the user would like to continue despite the error

    """

    if isinstance(e, str):
        e_msg = e
    else:
        e_msg = str(e)

    err = colored('ERROR: ', 'red')
    c_msg = colored(msg, 'yellow')

    _prompt(err+e_msg+". "+c_msg, 'two_staring')

    if args.yes:
        print("Continuing...")
        time.sleep(3)
    elif (_options_prompt("Continue anyways?", ["Yes", "No"]) == "Yes"):
        pass
    else:
        sys.exit()

def _render_ascii(file, msg):
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
    with open(_path_to_openwfom()+"\\resources\\asciiart\\"+file+"_mouse.txt") as f:
        lines = f.readlines()
        for line in lines:
            print(line, end="")
    f.close()

def _path_to_openwfom():
    return os.path.dirname(os.__file__)+"\site-packages\wfom"

def _welcome_banner(mode):

    # Set CWD to the location of 'wfom' Python Package
    os.chdir(os.path.dirname(os.__file__)+"\\site-packages\\wfom")

    # Clear the Command Prompt Screen
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

def _get_args():

    """

    This function simply checks for arguments when the script is called
    and stores them in their corresponding variable.

    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-q", "--quiet",
                    action="store_true", dest="quiet", default=False,
                    help="Don't print status messages to stdout")

    parser.add_argument("-y", "--auto-yes",
                    action="store_true", dest="yes", default=False,
                    help="Automatically accept errors and continue")

    parser.add_argument("-t", "--test",
                    action="store_true", dest="test", default=False,
                    help="Runs the test function instead of run")

    parser.add_argument("-v", "--verbose",
                    action="store_true", dest="test", default=False,
                    help="Runs the test function instead of run")

    args = parser.parse_args()


    return args

def _get_drive():
    drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
    d = _options_prompt("Which drive would you like to save your data to?", drives)
    return d

def _log_test_file(results):
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

    _welcome_banner("Run")

    andor = Andor()
    arduino = Arduino("COM4")
    webcam = Webcam()

    # Create the dict for the required
    COMMANDS = {
        "info":andor._info,
        "camera":andor._camera,
        "strobe_order":arduino._strobe,
        "stim":arduino.stim,
        "run":arduino.stim,
        "preview":andor._preview
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
            andor._read_json_settings()

    # Begin Acquisition
    andor._acquire()

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

    _welcome_banner("Test")

    _prompt("Running diagnostic test on WFOM...", "standing")

    _prompt("Testing connection to Camera and SOLIS", "standing")
    andor = Andor()
    _prompt("Testing connection to Arduino", "standing")
    arduino = Arduino("COM4")
    _prompt("Testing connection to Webcams", "standing")
    webcam = Webcam()

    _prompt("Logging test File", "share_mouse")

    try:
        path = _log_test_file(arduino.TEST_RESULTS+andor.TEST_RESULTS)
    except Exception as e:
        path = "nowhere"
        msg = "Could not create the log test file."
        _error_prompt(e, msg)

    _prompt("Test Complete... The Following Errors were logged to {0}".format(colored(os.getcwd()+"\\"+path, 'green')), "sitting")

    for error in arduino.TEST_RESULTS + andor.TEST_RESULTS:
        print(colored('ERROR: ', 'red')+" "+str(error))

def erase_archive():
    pass

class Andor():

    """

    This class is used for interaction between the Java GUI's and Andor SOLIS.

    It is initiated in both the Test and Run Modes.

    """

    def __init__(self):

        self.PATH_TO_FILES = ""

        self.JSON_SETTINGS = {}

        self.TEST_RESULTS = []

        self._check_java()

        _prompt("Checking if SOLIS is Open...", "standing")

        pids = [(p.pid) for p in psutil.process_iter() if p.name() == "AndorSolis.exe"]
        if len(pids) < 1:
            _prompt("SOLIS is not open. Opening it now...", 'standing')
            self._open_solis()
        else:
            _prompt("SOLIS is already open...", "standing")
        self._connect_to_solis()

    def _info(self):

        """

        For information on the 'Info' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#1-info-gui

        """

        _prompt("Waiting for Run Info from GUI...", "sitting")

        os.chdir("JavaGUI")
        if os.path.isfile("settings.json"):
            os.remove("settings.json")
        subprocess.call(["java", "-jar", "JARs/info.jar"])
        os.chdir("..")

        self._read_json_settings()

        self._create_path_to_files()

    def _camera(self):

        """

        For information on the 'Camera' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#2-camera-gui

        """
        _prompt("Opening Camera Settings GUI...", "standing")
        os.chdir("JavaGUI")
        subprocess.Popen(["java", "-jar","JARs/camera.jar"])
        os.chdir("..")

        _prompt("Waiting for Camera settings to be Deployed", 'sitting')
        self._read_zyla_settings()
        OLD_ZYLA_SETTINGS = self.ZYLA_SETTINGS
        while True:
                # Read the settings from the txt file generated by the GUI
                self._read_zyla_settings()
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
                    _prompt("Updating Preview with new Settings", "standing")
                    self._set_parameters()
                    time.sleep(3)
                    self._view()
                self._read_zyla_settings()
                OLD_ZYLA_SETTINGS = self.ZYLA_SETTINGS
                if len(OLD_ZYLA_SETTINGS) == 12:
                    self._deploy_json_camera_settings()
                    break
                time.sleep(3)

    def _open_solis(self):

        """

        Opens a new instance of AndorSolis.exe

        The command will Timeout after 10 seconds

        """

        try:
            app = Application().start(r"C:\Program Files\Andor SOLIS\AndorSolis.exe", timeout=10)
        except Exception as e:
            msg = "You may not have SOLIS Installed."
            _error_prompt(e, msg)

    def _connect_to_solis(self):

        """

        Attaches a pywinauto controller to the Andor Window.

        The connection times out after 3 seconds.

        It then creates the variable 'self.soliswin' which will be used by
        the script later.

        """

        _prompt("Attempting to Connect to SOLIS", "standing")
        try:
            self.solis = Application().connect(title_re="Andor SOLIS", timeout=3)
            self.soliswin = self.solis.window(title_re="Andor SOLIS", found_index=0)
            self._view()
        except Exception as e:
            msg = "The window to SOLIS may have closed."
            _error_prompt(e, msg)

    def _preview(self):

        """

        For information on the 'Preview' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#5-preview-gui

        """

        _prompt("Previewing settings. Select 'Begin Acquisition' start.", "sitting")

        os.chdir("JavaGUI")
        subprocess.call(["java", "-jar","JARs/preview.jar"])
        os.chdir("..")

    def _set_parameters(self):

        """

        Executes the Solis PGM 'set_parameters.pgm', which reads the SETTINGS
        from 'settings.txt' and deploys them to the camera.

        If the Menu Item is not enabled, an error prompt will appear.

        """

        self._abort()
        cwd = os.getcwd()
        set_param = r"resources\solis_scripts\set_parameters.pgm"
        file = r'"%s\%s"' % (cwd, set_param)
        _prompt("Setting parameters in SOLIS...", "standing")
        try:
            self.soliswin.menu_select("File -> Run Program By Filename")
            open_opt = self.solis.window(title_re="Open")
            file_name = open_opt.Edit.set_text(file)
            open_opt.Button.click()
        except (Exception, MenuItemNotEnabled) as e:
            msg = "The camera is likely not attached and/or plugged in."
            _error_prompt(e, msg)

    def _deploy_json_camera_settings(self):

        """

        Reads the Zyla 'settings.txt' file, converts it to a Python dict and
        sends the settings to 'settings.json'

        """

        # Update the self.ZYLA_SETTINGS list file
        self._read_zyla_settings()

        _prompt("Updating the Camera settings in 'settings.json'", "standing")
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

    def _check_java(self):

        _prompt("Checking Version of Java Runtime Environment", 'standing')

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
            if float(version[:3]) < 1.7:
                raise EnvironmentError("Your version of Java Runtime Environment\
                is {0}. 1.7 or up is required.")

            _prompt("JRE {0} is installed".format(version), "standing")

        except Exception as e:
            msg = ""
            _error_prompt(e, msg)

    def _view(self):

        _prompt("Attempting to Initiate Camera Preview in SOLIS", "standing")

        try:
            self.soliswin.menu_select("Acquisition->Take Video")
        except Exception as e:
            msg = "The camera is likely not attached and/or plugged in."
            _error_prompt(e, msg)

    def _abort(self):

        _prompt("Attempting to Abort Camera Preview in SOLIS", "standing")

        try:
            self.soliswin.menu_select("Acquisition->Abort Acquisition")
        except Exception as e:
            msg = "The camera is likely not attached and/or plugged in."
            _error_prompt(e, msg)

    def _make_directories(self):
        try:
            _prompt("Making directory: "+self.PATH_TO_FILES, "standing")
            os.mkdir(self.PATH_TO_FILES)
            _prompt("Making directory: "+self.PATH_TO_FILES+"/CCD", "standing")
            os.mkdir(self.PATH_TO_FILES+"/CCD")
            _prompt("Making directory: "+self.PATH_TO_FILES+"/webcam", "standing")
            os.mkdir(self.PATH_TO_FILES+"/webcam")
            src = "JavaGUI/settings.json"
            dst = self.PATH_TO_FILES+"/settings.json"

            _prompt("Moving JavaGUI/settings.json to "+self.PATH_TO_FILES+"\\settings.json", "share")
            shutil.move(src, dst)
        except Exception as e:
            msg = "Could make the directories at {0}".format(self.PATH_TO_FILES)
            _error_prompt(e, msg)

    def _read_zyla_settings(self):

        """

        Checks the settings currently deployed to the camera and stored in the
        'settings.txt' file.

        """

        with open("resources\\solis_scripts\\settings.txt", "r") as f:
            ZYLA_SETTINGS = f.readlines()
        f.close()
        self.ZYLA_SETTINGS = [x.strip() for x in ZYLA_SETTINGS]

    def _read_json_settings(self):

        _prompt("Reading the 'settings.json' file...", "standing")
        try:
            with open("JavaGUI\\settings.json", "r+") as f:
                self.JSON_SETTINGS = json.load(f)
            f.close()
        except Exception as e:
            msg = "Unable to find the 'settings.json' file. It may have been deleted."
            _error_prompt(e, msg)

    def _acquire(self):

        """

        * Read the current Zyla Settings
        * Write the settings to 'settings.json'
        * Make the acquisition directories and send 'settings.json' to them

        """

        self._read_json_settings()

        self._make_directories()

        self._abort()

        cwd = os.getcwd()
        acquire = r"resources\solis_scripts\acquire.pgm"
        file = r'"%s\%s"' % (cwd, acquire)
        try:
            self.soliswin.menu_select("File -> Run Program By Filename")
            open_opt = self.solis.window(title_re="Open")
            file_name = open_opt.Edit.set_text(file)
            open_opt.Button.click()
            self._acquisition_countdown()
        except (Exception, MenuItemNotEnabled) as e:
            msg = "The camera is likely not attached and/or plugged in."
            _error_prompt(e, msg)

    def _acquisition_countdown(self):
        total_time = 2*float(self.JSON_SETTINGS["run"]["run_len"])*float(self.JSON_SETTINGS["run"]["num_run"])
        while total_time > -1:

            min = str(int(total_time/60))
            sec = str(int(total_time % 60))

            if min == "0":
                msg = "{0} sec Remaining".format(sec)
            else:
                msg = "{0} min {1} sec Remaining".format(min, sec)

            _prompt("Acquisition Started. "+msg, "sitting")

            time.sleep(1)
            total_time -= 1
        _prompt( "Acquisition complete. Files have been saved to: "+self.PATH_TO_FILES,
                'finished')

    def _create_path_to_files(self):

        _prompt("Creating path to acquisition files...", 'standing')

        mouse = self.JSON_SETTINGS["info"]["mouse"]
        with open("JavaGUI\\archive.json", "r+") as f:
            archive = json.load(f)
            d = archive["mice"][mouse]["last_trial"]+1
            archive["mice"][mouse]["last_trial"] = d
            f.seek(0)
            json.dump(archive, f, indent=4)
            f.truncate()
        f.close()
        mouse = self.JSON_SETTINGS["info"]["mouse"]
        drive = _get_drive()
        path = drive+"wfom_data\\files\\"
        if os.path.isdir(drive+"wfom_data"):
            pass
        else:
            _prompt("Directory for acquisition files ({0}) does not exist. Creating it now.".format(path),
            'standing')
            os.mkdir(drive+"wfom_data")
            os.mkdir(drive+"wfom_data\\files\\")
        if not os.path.isdir(path + mouse + "_" + str(d)):
            path = path + mouse + "_" + str(d)
        else:
            path = path + mouse + "_" + str(d+1)
        self.PATH_TO_FILES = path

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, port):
        _prompt("Attempting to Connect to Arduino at Serial Port: "+port, "standing")
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
            _prompt("Successfully connected to Arduino at {0}".format(self.port), "standing")
        except Exception as e:
            msg = "Unable to connect to the Arduino. Ensure that it is plugged in and connected to "+self.port
            _error_prompt(e, msg)

    def _disable(self):
        _prompt("Disabling Python <-> Arduino Communication", "standing")
        try:
            self.ser.close()
        except Exception as e:
            msg = "Unable to connect to the Arduino. Ensure that it is plugged in and connected to "+self.port
            _error_prompt(e, msg)

    def _enable(self):
        _prompt("Enabling Python <-> Arduino Communication", "standing")
        try:
            self.ser.open()
        except Exception as e:
            msg = "Unable to connect to the Arduino. Ensure that it is plugged in and connected to "+self.port
            _error_prompt(e, msg)
        time.sleep(3)

    def _set_strobe_order(self):
        order = ""
        for led in self.strobe_order:
            order += led[0]
        _prompt("Setting the Strobe order on the Arduino to: "+order, "standing")
        try:
            self.ser.write(order.encode())
        except Exception as e:
            msg = "Unable to connect to the Arduino. Ensure that it is plugged in and connected to "+self.port
            _error_prompt(msg)

    def _clear(self):
        self.ser.write("0000".encode())

    def _strobe(self):

        """

        For information on the 'Strobe' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#3-strobe-gui

        """

        _prompt("Waiting to Recieve Strobe Settings from GUI...", "sitting")
        self._disable()
        os.chdir("JavaGUI")
        subprocess.call(["java", "-jar", "JARs/strobe.jar"])
        os.chdir("..")
        self._enable()

    def _stim(self):

        """

        For information on the 'Stim' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#4-stim-gui

        """

        _prompt("Waiting to Recieve Stim Settings from GUI...", "sitting")
        os.chdir("JavaGUI")
        subprocess.call(["java", "-jar", "JARs/stim.jar"])
        os.chdir("..")

    def _turn_on_strobing(self):
        self.ser.write("S".encode())

    def _turn_off_strobing(self):
        self.ser.write("s".encode())

class Webcam():
    """docstring for Webcam."""

    def __init__(self):
        self.connected = 1

os.system('COLOR 07')
if __name__ == '__main__':
    args = _get_args()
    # wfom.py run from the command line (look for arguments)
    if args.test:
        test()
    else:
        run()
else:
    # wfom run as a python module
    args = _get_args()
