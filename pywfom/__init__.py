import pkgutil, argparse, sys, os, json, pywfom, cv2, threading, shutil, time, tempfile
import numpy as np
from .imaging import Camera
from .control import Arduino
from .viewing import Main, Viewer, _ArduinoConfig
import tkinter as tk

# Retrieve command line arguments
def _get_args():

    """
    This function simply checks for arguments when the script is

    and stores them in their corresponding variable.

    Example:

    wfom 0

    """

    parser = argparse.ArgumentParser(description="Command line tool for the pywfom library.")

    msg = "Run a diagnostic test of your pywfom installation."
    parser.add_argument('-t', '--test', dest='test', action='store_true', default=False, help=msg)

    msg = "Stop pyWFOM from printing to the console."
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', default=False, help=msg)

    msg = "Option to run pywfom with Solis' built-in User Interface."
    parser.add_argument('-s', '--solis', dest='solis', action='store_true', default=False, help=msg)

    msg = "Use previously saved configuration (.json) file"
    parser.add_argument(    '-c',
                            '--config',
                            dest='config',
                            type=str,
                            nargs='?',
                            default="",
                            help=msg
                            )

    return parser.parse_args()

def _get_viewer_args():

    parser = argparse.ArgumentParser(description="Command line viewer for pywfom runs")

    msg = "Select a run directory from the GUI"
    parser.add_argument('-s', '--select', dest='select', action='store_true', default=True, help=msg)

    msg = "Specify the path to the run directory you wish to view."
    parser.add_argument(    '-p',
                            '--path',
                            type=str,
                            default=None,
                            help=msg
                            )

    args = parser.parse_args()

    args.select = False if args.path else True

    return args

# Command Line functions
def quickstart():
    wfom = pywfom.System()

def test():

    root = tk.Tk()
    frame = tk.Frame(root)
    frame.root = root

    frame.system = System()

    ard = _ArduinoConfig(frame, frame.root)
    ard._StimConfig(ard, ard.root)
    root.mainloop()

def view():

    """
    View previous run

    """

    args = _get_viewer_args()
    frame = Viewer(args)
    frame.root.mainloop()

def main():

    """
    Configure Interface settings

    """

    args = _get_args()

    if args.quiet:
        sys.stdout = open(os.devnull, 'w')

    if args.solis:
        solis()
    elif args.test:
        test()
    else:
        system = System(args.config)
        frame = Main(system)
        frame.root.mainloop()

def solis():
    pass

class System(object):

    """Class Wrapper for the OpenWFOM System"""

    def __init__(self, config=None):

        super(System, self).__init__()

        if not config or config == "":
            config = json.loads(pkgutil.get_data(__name__, 'utils/default.json'))
        else:
            config = json.load(open(config, 'r'))

        for k,v in config.items():

            if k == 'cameras':
                v = [Camera(config=cfg) for cfg in config['cameras']]
            elif k == 'arduino':
                v = Arduino(config=config['arduino'])
            setattr(self, k, v)

    def acquire(self):

        for cam in self.cameras:
            if cam.ERRORS:
                tk.messagebox.showerror('Camera Error',message=cam.ERRORS[0])
                return

        if self.arduino.ERROR:
            tk.messagebox.showerror('Arduino Error',message=self.arduino.ERROR)
            return

        threading.Thread(target=self._acquire_frames).start()

    def close(self):
        [cam.close() for cam in self.cameras]
        self.arduino.close()

    def _make_run_directory(self, i):

        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        mouse_dir = os.path.join(self.directory, self.mouse)

        if not os.path.exists(mouse_dir):
            os.mkdir(mouse_dir)

        runs = len(os.listdir(mouse_dir))

        run_dir = os.path.join(self.directory, mouse_dir, "run"+str(runs))

        os.mkdir(run_dir)

        with open(run_dir+"/config.json", 'w') as f:
            json.dump(_organize_settings(self), f)
        f.close()

        return run_dir

    def _acquire_frames(self):

        master = []

        for i, cam in enumerate(self.cameras):
            if cam.master:
                master.append(i)

        if len(master)>1:
            messagebox.showerror(
                title='Acquisition Error',
                message='Too many master cameras. There can only be one!'
            )
            return
        else:
            master = master[0]

        self.arduino.start_strobing()

        for i in range(self.runs):

            path = self._make_run_directory(i)
            run_frms = self.run_length*self.cameras[master].framerate
            num_frms = 0
            # TODO: Write frames simultaneously
            # TODO: Write to disk in thread

            while num_frms < run_frms:

                self._frames = {}
                fname = "{0}/frame{1}.npz".format(path, num_frms)

                for cam in self.cameras:
                    t = threading.Thread(target=self._read_camera_frame, args=(cam,))
                    t.start()
                    t.join()


                threading.Thread(target=self._save_frames, args=(fname,)).start()

                num_frms+=1

        self.arduino.stop_strobing()

    def _save_frames(self, fname):
        data = [v for k,v in self._frames.items()]
        np.savez(fname, *data)

    def _read_camera_frame(self, camera):
        self._frames[camera.name] = camera.read()
