import shutil, sysconfig, psutil, json, time, os, subprocess, sys
import openwfom
from pywinauto.application import Application, AppStartError
from pywinauto.controls.menuwrapper import MenuItemInfo
import cv2, threading
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

class Frame(object):
    """docstring for Frame."""

    def __init__(self, win_name):
        # cv2 drawing variables
        self.drawing = False
        self.dragging = False
        self.sf = 1
        self.ix, self.iy, self.x, self.y, self.cx, self.cy = -1,-1,-1,-1,-1,-1
        self.win_name = win_name
        self.selected_idx = 0
        self.num_sfs = 0
        self.active = True
        self.update = {}
        threading.Thread(target=self._view_frame).start()

    def _format_frame(self, frame, label="", to_shape=(800,800), padding=25):

        # Reformat to unsigned 8bit int if not
        if frame.dtype == 'uint16':
            frame = frame.astype('uint8')
        # Store current frame shape
        fs = frame.shape
        # Set scaling factor
        sf = min(to_shape)/(max(fs)+2*padding)
        # Resive the Frame to fit in to_shape size (w/ padding)
        frame = cv2.resize(frame, (0,0), fx=sf, fy=sf)

        # Calculate the padding in x (pad[1]) and y (pad[0])
        pad_y = int(max(0, (to_shape[0] - frame.shape[0]))/2)
        pad_x = int(max(0, (to_shape[1] - frame.shape[1]))/2)

        # Add padding
        gray = np.pad(frame, ((pad_y, pad_y), (pad_x, pad_x)), 'constant')
        # COnvert to RGB
        rgb = cv2.cvtColor(gray, cv2.COLOR_BGR2RGB)
        # Add label
        cv2.putText(rgb, label, (pad_x, pad_y+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        return rgb

    def _mouse_callback(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            if x < 800:
                # Mouse selected main frame
                self.drawing = True
                self.ix, self.iy, self.x, self.y = x,y,x,y
            else:
                # Mouse selected sub frame
                self.selected_idx = int(y/800*(self.num_sfs))

        elif event == cv2.EVENT_MOUSEMOVE:
            self.cx, self.cy = x, y
            if self.drawing:
                self.x, self.y = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.update = {
                "AOILeft":min(self.x, self.ix),
                "AOIBottom":min(self.y, self.iy),
                "AOIWidth":abs(self.x-self.ix),
                "AOIHeight":abs(self.y-self.iy)
            }
            print(self.update)
            self.ix, self.iy, self.x, self.y = -1, -1, -1, -1

    def view(self, img_dict, img_names):
        # Update the objects 'frame' variable
        self._update_frame(img_dict, img_names)
        return self.active

    def _view_frame(self):
        # Open a new cv2 window
        cv2.namedWindow(self.win_name)
        cv2.setMouseCallback(self.win_name, self._mouse_callback)
        # Create an empty frame
        self.frame = self._format_frame(np.zeros((1000,1000), 'uint8'), 'Waiting for Images...')
        # Run a loop while the frame is active
        while self.active:
            # Draw a circle to make mouse position more visible
            cv2.circle(self.frame, (self.cx, self.cy), 10, (255,0,0), 5, 1, 0)
            # Draw a rectangle on main frame for AOI
            cv2.rectangle(self.frame,(self.ix,self.iy),(self.x,self.y),(0,255,0))
            # Show the resulting frame using OpenCV
            cv2.imshow(self.win_name, self.frame)

            # Quit the program if the Q button is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.active = False
                break

    def _update_frame(self, img_list, img_names):
        # Calculate number of frames
        self.num_sfs = len(img_list)
        # Get name of chosen main frame
        mf_name = img_names[self.selected_idx]
        # Establish the main frame
        mf = self._format_frame(img_list[self.selected_idx], mf_name)
        # Skip calculation of there are no sub frames
        if len(img_list) == 1:
            self.frame = mf
        else:
            sf = []
            for i, img in enumerate(img_list):
                # Calculate the size of each sub frame -> MF_Height / # of Sub Frames
                sf_dim = int(mf.shape[0]/len(img_list))
                sf.append(self._format_frame(img, img_names[i], (sf_dim, sf_dim)))
            # Combine the subframes vertically
            sf = cv2.vconcat(sf)
            # Combine subframes and main frame horizontally
            self.frame = cv2.hconcat([mf[:sf.shape[0]], sf])

    def close(self):
        self.active = False
        cv2.destroyAllWindows()

class Settings(object):
    """docstring for Settings."""

    def __init__(self, path_to_settings=""):
        self._check_java()
        self.JAR_PATH = "{0}\\viewing\\java\\JARS\\".format(openwfom.__path__[0])

    def set(self, setting):

        print("Setting {0} from the GUI...".format(setting))

        path = "{0}{1}.jar".format(self.JAR_PATH, setting)
        subprocess.call(["java", "-jar", path])

    def _check_java(self):

        print("Checking Version of Java Runtime Environment")

        try:
            out = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT).decode("utf-8")
            version = ""
            if out[0] == "'":
                raise EnvironmentError("Java is not installed on your machine.")
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

            print("JRE {0} is installed".format(version))

        except Exception as e:
            msg = "Could not find the correct version of the Java Runtime Environment"
            raise EnvironmentError(msg)

class Solis(object):

    """

    This class is used for interaction between the Java GUI's and Andor SOLIS.

    It is initiated in both the Test and Run Modes.

    """

    def __init__(self):
        self.JSON_SETTINGS = {}

        print("Checking if SOLIS is Open...")

        if not self._check_solis():
            print("SOLIS is not open. Opening it now...")
            self._open_solis()
        else:
            print("SOLIS is already open...")
        time.sleep(3)
        self._connect_to_camera()

    def preview():
        # FIXME add external script to preview the camera in Solis
        pass

    def _check_solis(self):
        if "AndorSolis.exe" in [p.name() for p in psutil.process_iter()]:
            return True
        else:
            return False

    def _info(self):

        """

        For information on the 'Info' GUI go here:
        https://github.com/ryan-byrne/wfom/wiki/Usage#1-info-gui

        """

        print("Waiting for Run Info from GUI...")

        if os.path.isfile("settings.json"):
            os.remove("settings.json")
        path = "{0}info.jar".format(self.JAR_PATH)
        subprocess.call(["java", "-jar", path])

        self._read_json_settings()

        self._create_path_to_files()

    def _camera(self):

        """

        For information on the 'Camera' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#2-camera-gui

        """

        # The Camera JAR is opened to be able to control the Camera settings.
        print("Opening Camera Settings GUI...")

        os.chdir("JavaGUI")
        subprocess.Popen(["java", "-jar","JARs\\camera.jar"])
        os.chdir("..")

        print("Waiting for Camera settings to be Deployed")
        self._read_zyla_settings()
        OLD_ZYLA_SETTINGS = self.ZYLA_SETTINGS

        # A loop then waits for 'deployed' to be the last line of settings.txt
        while True:
            # Read the settings from the txt file generated by the GUI
            self._read_zyla_settings()
            update = False
            # Loop through each setting
            if len(self.ZYLA_SETTINGS) > 11:
                self._reset_zyla_settings()
                break
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
                print("Updating Preview with new Settings", "standing")
                # Set the new parameters
                self._set_parameters()
                time.sleep(1)
                try:
                    self._view()
                except:
                    self._abort()
            # Read settings from settings.txt
            self._read_zyla_settings()
            OLD_ZYLA_SETTINGS = self.ZYLA_SETTINGS
            time.sleep(0.05)
        # Create the Camera object in settings.json
        self._deploy_json_camera_settings()

    def _reset_zyla_settings(self):
        with open("resources/solis_scripts/settings.txt", "r+") as f:
            lines = f.readlines()
            f.seek(0)
            f.writelines([line for line in lines[:-1]])
            f.truncate()
        f.close()

    def _open_solis(self):

        """

        Opens a new instance of AndorSolis.exe

        The command will Timeout after 10 seconds

        """

        try:
            app = Application().start("C:\\Program Files\\Andor SOLIS\\AndorSolis.exe", timeout=10)
        except Exception as e:
            raise FileNotFoundError("You may not have SOLIS Installed.")

    def _connect_to_camera(self):

        """

        Attaches a pywinauto controller to the Andor Window.

        The connection times out after 3 seconds.

        It then creates the variable 'self.soliswin' which will be used by
        the script later.

        """

        print("Attempting to Connect to Camera...")
        try:
            self.solis = Application().connect(title_re="Andor SOLIS", timeout=10)
            self.soliswin = self.solis.window(title_re="Andor SOLIS", found_index=0)
            self._view()
        except Exception as e:
            try:
                self._abort()
                self._view()
            except Exception as e:
                msg = "Unable to connect to the Camera via SOLIS"
                raise ConnectionError(msg)

    def _restart_solis(self):

        """

        Exits current instance of SOLIS, allows the user to turn on the Camera,
        then reopens SOLIS.

        """

        for p in psutil.process_iter():
            if p.name() == "AndorSolis.exe":
                p.kill()
                break
        input("Power on the camera then press [ENTER]")
        self._open_solis()
        self._connect_to_camera()

    def _preview(self):

        """

        For information on the 'Preview' GUI go here https://github.com/ryan-byrne/wfom/wiki/Usage#5-preview-gui

        """

        print("Previewing settings. Select 'Begin Acquisition' start.")

        os.chdir("JavaGUI")
        subprocess.call(["java", "-jar","JARs/preview.jar"])
        os.chdir("..")

    def set_parameters(self):

        """

        Executes the Solis PGM 'set_parameters.pgm', which reads the SETTINGS
        from 'settings.txt' and deploys them to the camera.

        If the Menu Item is not enabled, an error prompt will appear.

        """

        self._abort()
        cwd = os.getcwd()
        set_param = r"resources\solis_scripts\set_parameters.pgm"
        file = r'"%s\%s"' % (cwd, set_param)
        print("Setting parameters in SOLIS...")
        try:
            self.soliswin.menu_select("File -> Run Program By Filename")
            open_opt = self.solis.window(title_re="Open")
            file_name = open_opt.Edit.set_text(file)
            open_opt.Button.click()
        except (Exception, MenuItemNotEnabled) as e:
            msg = "The camera is likely not attached and/or plugged in."
            raise ConnectionError(msg)

    def _deploy_json_camera_settings(self):

        """

        Reads the Zyla 'settings.txt' file, converts it to a Python dict and
        sends the settings to 'settings.json'

        """

        # Update the self.ZYLA_SETTINGS list file
        self._read_zyla_settings()

        print("Updating the Camera settings in 'settings.json'")
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

    def view(self):

        print("Attempting to Initiate Camera Preview in SOLIS")
        self.soliswin.menu_select("Acquisition->Take Video")

    def abort(self):

        print("Attempting to Abort Camera Preview in SOLIS")
        self.soliswin.menu_select("Acquisition->Abort Acquisition")

    def _make_directories(self):
        try:
            print("Making directory: "+self.PATH_TO_FILES)
            os.mkdir(self.PATH_TO_FILES)
            print("Making directory: "+self.PATH_TO_FILES+"/CCD")
            os.mkdir(self.PATH_TO_FILES+"/CCD")
            print("Making directory: "+self.PATH_TO_FILES+"/webcam")
            os.mkdir(self.PATH_TO_FILES+"/webcam")
            src = "JavaGUI/settings.json"
            dst = self.PATH_TO_FILES+"/settings.json"
            print("Moving JavaGUI/settings.json to "+self.PATH_TO_FILES+"\\settings.json")
            shutil.move(src, dst)
        except Exception as e:
            msg = "Could not make the directories at {0}".format(self.PATH_TO_FILES)
            raise e

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

        print("Reading the 'settings.json' file...")
        try:
            with open("JavaGUI\\settings.json", "r+") as f:
                self.JSON_SETTINGS = json.load(f)
            f.close()
        except Exception as e:
            msg = "Unable to find the 'settings.json' file. It may have been deleted."
            raise e

    def acquire(self):

        """

        * Read the current Zyla Settings
        * Write the settings to 'settings.json'
        * Make the acquisition directories and send 'settings.json' to them

        """

        self._read_json_settings()

        self._make_directories()

        self._finalise_zyla_settings()

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
            raise e

    def _acquisition_countdown(self):
        total_time = 2*float(self.JSON_SETTINGS["run"]["run_len"])*float(self.JSON_SETTINGS["run"]["num_run"])
        while total_time > -1:

            min = str(int(total_time/60))
            sec = str(int(total_time % 60))

            if min == "0":
                msg = "{0} sec Remaining".format(sec)
            else:
                msg = "{0} min {1} sec Remaining".format(min, sec)

            print("Acquisition Started. "+msg)

            time.sleep(1)
            total_time -= 1
        print( "Acquisition complete. Files have been saved to: "+self.PATH_TO_FILES)

    def _create_path_to_files(self):

        print("Creating path to acquisition files...")

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
        drive = "C:\\"
        path = drive+"wfom_data\\files\\"
        if os.path.isdir(drive+"wfom_data"):
            pass
        else:
            print("Directory for acquisition files ({0}) does not exist. Creating it now.".format(path))
            os.mkdir(drive+"wfom_data")
            os.mkdir(drive+"wfom_data\\files\\")
        if not os.path.isdir(path + mouse + "_" + str(d)):
            path = path + mouse + "_" + str(d)
        else:
            path = path + mouse + "_" + str(d+1)
        self.PATH_TO_FILES = path

    def _finalise_zyla_settings(self):

        self._read_zyla_settings()

        """
        settings.txt format:

        0 binning
        1 height
        2 bottom
        3 width
        4 left
        5 exposure time
        6 Framerate
        7 Run Duration
        8 Spool File Stem
        9 Spool File Directory
        10 Number of Runs

        """

        self.ZYLA_SETTINGS[7] = self.JSON_SETTINGS["run"]["run_len"]
        self.ZYLA_SETTINGS[9] = self.PATH_TO_FILES + "\\CCD"
        self.ZYLA_SETTINGS[10] = self.JSON_SETTINGS["run"]["num_run"]
        with open("resources\\solis_scripts\\settings.txt", "r+") as f:
            f.seek(0)
            f.writelines([line + "\n" for line in self.ZYLA_SETTINGS])
        f.close()
