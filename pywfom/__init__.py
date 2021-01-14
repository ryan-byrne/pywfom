import pkgutil, argparse, sys, os, json, pywfom, threading, shutil, zipfile, time
from tqdm import tqdm
import numpy as np
from .imaging import Camera
from .control import Arduino
from .viewing import Main, Viewer, ArduinoConfig, StimConfig, CameraConfig, _set_icon
import tkinter as tk
from PIL import Image, ImageTk

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

    msg = "Specify the path to the run directory you wish to view or compress"
    parser.add_argument(    '-p',
                            '--path',
                            type=str,
                            default=None,
                            help=msg
                            )

    msg = "Remove a run directory after it has been compressed"
    parser.add_argument(    '-r',
                            '--remove',
                            action='store_true',
                            default=False,
                            help=msg
                            )

    args = parser.parse_args()

    return args

def set_default(system):

    settings = organize_settings(system)

    if tk.messagebox.askyesno('Set as Default', 'Set current settings as default?'):
        with open("{0}/{1}".format(pywfom.__path__[0],'utils/default.json'),'w') as f:
            json.dump(settings, f)
        f.close()

def organize_settings(system):

    settings = {}

    for category, value in system.__dict__.items():
        if category in ["user","mouse", "directory","runs","run_length"]:
            settings[category] = value
        elif category == 'arduino':
            settings[category] = {}
            for setting, value in system.arduino.__dict__.items():
                if setting[0] == '_' or setting == 'ERROR':
                    continue
                else:
                    settings[category][setting] = value
        elif category == 'cameras':
            settings['cameras'] = []
            for cam in system.cameras:
                cam_settings = {}
                for setting, value in cam.__dict__.items():
                    if setting[0] == '_' or setting in ['ERRORS', 'WARNINGS', 'frame']:
                        continue
                    else:
                        cam_settings[setting] = value
                settings['cameras'].append(cam_settings)

        else:
            continue

    return settings

def load_settings(frame):

    file = tk.filedialog.askopenfile(parent=frame.root, defaultextension='.json')

    if file is None:
        return
    else:
        frame.system.close()
        config = json.load(file)
        frame.system = System(config=config)

def save_settings(frame):

    file = tk.filedialog.asksaveasfile(mode="w", parent=frame.root, defaultextension=".json")

    if file is None:
        return
    else:
        settings = organize_settings(frame.system)
        json.dump(settings, file)
        file.close()

def _compress_run(run_dir, remove):

    zip = zipfile.ZipFile( run_dir+'.zip', 'w', compression=zipfile.ZIP_DEFLATED )
    name = run_dir.split('/')[-1]

    for root, dirs, files in os.walk(run_dir):
        for i, file in enumerate(tqdm(files, 'Compressing {0}'.format(name), unit='frames')):
            zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(root, '..')))

    if remove:
        shutil.rmtree(run_dir)

# Command Line functions
def quickstart():

    system = System()
    root = tk.Tk()
    root.title('pyWFOM Quickstart')
    path = "{0}/img/quick.png".format(os.path.dirname(pywfom.__file__))

    _set_icon(root, 'quick')

    render = ImageTk.PhotoImage( Image.open(path) )

    img = tk.Label(root, image=render)

    img.image = render

    img.pack()


    for setting in ['user', 'mouse']:

        value = tk.simpledialog.askstring(
            'pyWFOM Quickstart',
            'What is the name of the {0}?'.format(setting.title())
        )

        setattr(system, setting, value)

    setattr(system, 'directory', tk.filedialog.askdirectory(
        title="Select a directory to save to..."
    ))
    setattr(system, 'runs', tk.simpledialog.askinteger(
        'pyWFOM Quickstart',
        'How many runs?'
    ))
    setattr(system, 'run_length', tk.simpledialog.askfloat(
        'pyWFOM Quickstart',
        'How long (in seconds) for each run?'
    ))

    root.destroy()

    frame = Main(system)
    frame.root.mainloop()

def test():

    root = tk.Tk()
    frame = tk.Frame(root)
    frame.root = root
    system = System()
    ard = CameraConfig(system.cameras[0], frame.root)
    root.mainloop()

def view():

    args = _get_viewer_args()
    run_dir = args.path if args.path else None
    frame = Viewer(run_dir)
    frame.root.mainloop()

def main():

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

def archive():

    root = tk.Tk()

    _set_icon(root, 'zip')

    args = _get_viewer_args()

    args.path = tk.filedialog.askdirectory() if not args.path else args.path

    if not args.path:
        return

    remove = False if not args.remove or not tk.messagebox.askyesno('Archive', 'Delete compressed Run Directory?') else True

    if args.path.split('/')[-1][:3] == 'run':
        _compress_run(args.path, remove)
    else:
        for subdir, dirs, files in os.walk(args.path):
            for i, run in enumerate(tqdm(dirs)):
                _compress_run(subdir+run, remove)

def solis():
    pass

class System(object):

    """

    Class wrapper for :py:mod:`pywfom`

    :Example:

    .. code-block:: python

        import pywfom

        wfom = pywfom.System('path/to/config.json') # default.json used if empty

        wfom.directory = 'path/to/data' # Path to save run data

        wfom.acquire() # Saves data to wfom.directory

        wfom.close() # Closes system

    :param config:

        * `str`_ : Path to local :ref:`JSON Configuration File`
        * `dict`_ : Configure from dictionary
        * ``None``: Use :ref:`Default Configuration`

    :ivar cameras: A list of :py:class:`pywfom.imaging.Camera`'s
    :vartype cameras: `list`_
    :ivar arduino: :py:class:`pywfom.control.Arduino`
    :vartype arduino: `object`_
    :ivar user: Name of the user conducting the run
    :vartype user: `str`_
    :ivar mouse: Name of the mouse used in the run
    :vartype mouse: `str`_
    :ivar directory:
        Path to directory where :ref:`Acquisition Files` and a copy of the
        :ref:`JSON Configuration File` will be saved
    :vartype directory: `str`_
    :ivar runs: Number of runs to be carried out
    :vartype runs: `int`_
    :ivar run_length: Length of each run (in seconds)
    :vartype run_length: `float`_

    """

    def __init__(self, config=None):

        super(System, self).__init__()

        if not config or config == "":
            config = json.loads(pkgutil.get_data(__name__, 'utils/default.json'))
        elif type(config) == type({}):
            config = config
        else:
            config = json.load(open(config, 'r'))

        for k,v in config.items():

            if k == 'cameras':
                v = [Camera(config=cfg) for cfg in config['cameras']]
            elif k == 'arduino':
                v = Arduino(config=config['arduino'])
            setattr(self, k, v)

    def acquire(self):

        """
        Begin acquiring :ref:`Acquisition Files` on your :py:mod:`pywfom`
        System.

        """

        for cam in self.cameras:
            if cam.ERRORS:
                tk.messagebox.showerror('Camera Error',message=cam.ERRORS[0])
                return

        if self.arduino.ERROR:
            tk.messagebox.showerror('Arduino Error',message=self.arduino.ERROR)
            return

        threading.Thread(target=self._acquire_frames).start()

    def close(self):
        """
        Close each :py:class:`pywfom.imaging.Camera` and :py:class:`pywfom.control.Arduino`
        """
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
            json.dump(organize_settings(self), f)
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
            print('Beginning Run {0} of {1}'.format(i+1, self.runs))
            while num_frms < run_frms:

                self._data = {}
                fname = "{0}/frame{1}.npz".format(path, num_frms)

                for cam in self.cameras:
                    t = threading.Thread(target=self._read_camera_frame, args=(cam,))
                    t.start()
                    t.join()
                t = threading.Thread(target=self._read_arduino)
                t.start()
                t.join()


                threading.Thread(target=self._save_data, args=(fname,)).start()

                num_frms+=1

        self.arduino.stop_strobing()

    def _save_data(self, fname):
        data = [v for k,v in self._data.items()]
        np.savez(fname, *data)

    def _read_arduino(self):
        self._data['arduino'] = self.arduino.read()

    def _read_camera_frame(self, camera):
        self._data[camera.name] = camera.read()
