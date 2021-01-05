import pkgutil, argparse, sys, os, json, pywfom, cv2, threading, shutil, time
import numpy as np
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
from .imaging import Camera
from .control import Arduino

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

    msg = "Print additional text while running pywfom."
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help=msg)

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

    args = vars(parser.parse_args())

    return args

# Command Line functions
def quickstart():
    wfom = pywfom.System()

def test():
    system = pywfom.System()
    cam = system.cameras[0]
    cam.set(height=2400, width=2400, framerate=60)
    while True:
        pass
    cam.close()

def view():

    """
    View frames, adjust settings, and monitor device connections

    """

    system = _startup()

    if not system:
        return

    frame = Main(tk.Tk(), system)
    frame.root.mainloop()

def configure():

    """
    Configure Interface settings

    """

    system = _startup()

    if not system:
        return

    frame = Config(tk.Tk(), system)
    frame.root.mainloop()

def solis():
    pass

# GUI Functions
def _startup():

    args = _get_args()

    if not args['verbose']:
        sys.stdout = open(os.devnull, 'w')

    if args['solis']:
        solis()

    if args['test']:
        test()
        return None

    return System(args['config'])

def _set_icon(root, name="icon"):
    path = "{0}/img/{1}.png".format(os.path.dirname(pywfom.__file__), name)
    photo = tk.PhotoImage(
        master = root,
        file = path
    )
    root.iconbitmap(path)
    root.iconphoto(False, photo)

# Camera related functions
def _edit_camera(frame, i=None):

    if i:
        frame.selected_frame = i

    _set_icon(frame.root, "configure")
    _CameraConfig(frame, frame.root)

def _delete_camera(frame, i=None, viewing=False):

    if i or i == 0:
        frame.selected_frame = i

    frame.system.cameras.pop(frame.selected_frame).close()

    if viewing:
        frame.thumbnails.pop(frame.selected_frame).pack_forget()
        frame.thumbnail_labels.pop(frame.selected_frame).pack_forget()
        frame.selected_frame = 0

def _add_thumbnail(frame, name):
    frame.thumbnails.append(tk.Label(frame.thumbnails_frame))
    frame.thumbnail_labels.append(tk.Label(frame.thumbnails_frame, text=name))

def _add_camera(frame, viewing=True):

    config = json.loads(pkgutil.get_data(__name__, 'utils/default.json'))
    cam = pywfom.imaging.Camera(config=config['cameras'][0])
    frame.system.cameras.append(cam)

    if viewing:
        _add_thumbnail(frame, cam.name)
        frame.selected_frame = len(frame.system.cameras)-1
        _CameraConfig(frame, frame.root)
    else:
        return

# File Related functions
def _set_dir(parent):
    parent.system.directory = tk.filedialog.askdirectory()

def _load(frame):

    f = filedialog.askopenfile(parent=frame.root)

    if not f:
        return

    config = json.load(f)
    f.close()

    frame.system.close()
    frame._startup(config)

def _set_default(frame):

    settings = _organize_settings(frame.system)

    if messagebox.askyesno('Set as Default', 'Set current settings as default?'):
        with open("{0}/{1}".format(pywfom.__path__[0],'utils/default.json'),'w') as f:
            json.dump(settings, f)
        f.close()

def _organize_settings(system):

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

def _save(frame):

    _cameras = []

    for cam in frame.system.cameras:

        _camera_settings = {}

        for setting in pywfom.imaging.TYPES:
            _camera_settings[setting] = cam.get(setting)

        _cameras.append(_camera_settings)


    _config = {
        'file':frame.file.__dict__,
        'arduino':frame.arduino.__dict__,
        'cameras':_cameras
    }

    fname = filedialog.asksaveasfile(mode="w", parent=frame.root, defaultextension=".json")

    if fname is None:
        return
    else:
        json.dump(_config, fname)
        fname.close()

class System(object):

    """Class Wrapper for the OpenWFOM System"""

    def __init__(self, config=None):

        super(System, self).__init__()

        if not config:
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

        self.writing = True

        for i, cam in enumerate(self.cameras):
            if cam.master:
                master = i

        for i in range(self.runs):

            path = self._make_run_directory(i)
            run_frms = self.run_length*self.cameras[i].framerate
            num_frms = 0
            # TODO: Write frames simultaneously
            # TODO: Write to disk in thread

            while num_frms < run_frms:
                frames = {cam.name: cam.read() for cam in self.cameras}
                fname = "{0}/frame{1}.npz".format(path, num_frms)
                np.savez(fname,frames)
                num_frms+=1

    def _write_frames_to_file(self, fname, frames):
        pass

class Main(tk.Frame):

    """
    Monitor camera frames, Arduino status, and set file directory

    """

    def __init__(self, parent, system):

        self.system = system

        # General Application Settings
        self.root = parent
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.close)
        self.root.title("pywfom")
        self.root.bind('<FocusIn>', self._close_children)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        _set_icon(self.root)

        # Create Each Side of the Window
        self.right_side = tk.Frame(self.root)
        self.left_side = tk.Frame(self.root)
        self.right_side.pack(side='right', padx=20, pady=20)
        self.left_side.pack(side='right', expand=True, fill=tk.X)

        # Main viewing window to the left
        self._create_main_window()
        # Camera thumnails to the right
        self._create_thumnnails()
        # Widgets to do with Arduino control and monitoring
        self._create_arduino_widgets()
        # Control the file settings
        self._create_file_widgets()
        # Create Main Nav buttons
        self._create_buttons()
        # Begin Updating the Frame
        self._update()

    def _close_children(self, event):
        _set_icon(self.root)
        for child in self.root.winfo_children():
            if child.widgetName == 'toplevel':
                child.destroy()
            else:
                continue

    def _create_main_window(self):

        self.rect = None
        self.drawing = False
        self.selected_frame, self.ix, self.iy, self.x, self.y = 0,0,0,0,0
        self.offset_x, self.offset_y, self.scale = 0,0,0


        # Add widgets to label
        _lbl_frame = tk.Frame(self.left_side)

        self.main_lbl = tk.Label(   _lbl_frame,
                                    font=("Helvetica", 14))
        self.main_lbl.pack(side='left')

        tk.Button(  _lbl_frame,
                    text='Edit',
                    command=lambda frm=self:_edit_camera(frm),
                    padx=10,
                    pady=5
        ).pack(side='left')

        tk.Button(  _lbl_frame,
                    text='Remove',
                    command=lambda frm=self:_delete_camera(frm, viewing=True),
                    padx=10,
                    pady=5
        ).pack(side='left')

        _lbl_frame.pack()

        # Create Canvas and subcanvas to add buttons
        self.canvas = tk.Canvas(    self.left_side,
                                    cursor="cross"
                                )
        self.canvas.pack(padx=10)

        # Set Canvas bindings
        self.canvas.bind("<Button-1>", self.set_aoi_start)
        self.canvas.bind("<ButtonRelease-1>", self.set_aoi_end)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<Button-3>", self.reset_aoi)
        self.canvas.bind("<Button-2>", self.reset_aoi)

    def _create_thumnnails(self):

        # Create empty thumnails
        self.thumbnails_frame = tk.Frame(self.right_side)
        self.thumbnails_frame.pack()
        self.thumbnails, self.thumbnail_labels = [], []

        # Create thumbnails
        for i, cam in enumerate(self.system.cameras):
            _add_thumbnail(self, cam.name)

        tk.Button(
            self.right_side,
            text='Add Camera',
            command=lambda frm=self:_add_camera(frm),
            padx=10,
            pady=5
        ).pack(pady=10)

    def _create_arduino_widgets(self):

        # Create frame
        arduino_frm = tk.Frame(self.right_side)
        arduino_frm.pack(pady=20)

        # Create+pack Arduino Widgets
        tk.Label(
            arduino_frm,
            text="Arduino: "
        ).pack()

        # Create port frame
        port_frm = tk.Frame(arduino_frm)
        port_frm.pack()

        tk.Label(
            port_frm,
            text="Port: "
        ).pack(side='left')

        self._port_combo = ttk.Combobox(
            port_frm,
            values=[self.system.arduino.port],
            state='readonly'
        )
        self._port_combo.pack(side='left')
        self._port_combo.current(0)
        self._port_combo.bind('<Button-1>',
            lambda e: self._port_combo.config(values=pywfom.control.list_ports())
        )
        self._port_combo.bind('<<ComboboxSelected>>',
            lambda e: self.system.arduino.set(port=e.widget.get().split(' - ')[0])
        )

        tk.Button(
            port_frm,
            text="Configure",
            command=lambda frm=self:_ArduinoConfig(frm, frm.root),
            padx=10,
            pady=5
        ).pack(side='left')

        self.arduino_status = tk.Label(arduino_frm)
        self.arduino_status.pack()

    def _create_file_widgets(self):

        tk.Label(
            self.right_side,
            text='Run:'
        ).pack()

        # Create File Directory
        file_frame = tk.Frame(self.right_side)
        file_frame.pack()

        run_frame = tk.Frame(self.right_side)
        run_frame.pack()

        tk.Label(
            file_frame,
            text="Save to:",
            font=("Helvetica", 10, 'bold')
        ).pack(side='left')

        self.dir_name = tk.Label(file_frame)
        self.dir_name.pack(side='left')

        tk.Button(
            file_frame,
            text="Browse",
            command=lambda frm=self:_set_dir(self),
            padx=10,
            pady=5
        ).pack(side='left')

        tk.Button(
            file_frame,
            text="Configure",
            padx=10,
            pady=5,
            command=lambda frm=self:_FileConfig(frm, frm.root)
        ).pack(side='left')

    def _create_buttons(self):

        # Create frame for buttons
        btn_frm = tk.Frame(self.right_side)

        # Create buttons
        tk.Button(
            btn_frm,
            text="Close",
            command=self.close,
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        tk.Button(
            btn_frm,
            text="Save",
            command=lambda frm=self:_save(self),
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        tk.Button(
            btn_frm,
            text="Load",
            command=lambda frm=self:_load(self),
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        tk.Button(
            btn_frm,
            text="Make Default",
            command=lambda frm=self:_set_default(frm),
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        self.acquire_btn = tk.Button(
            btn_frm,
            text="Acquire",
            command=self._acquire,
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        btn_frm.pack(pady=30)

    def _update(self):

        self._draw_main_image()

        self._draw_thumnails()

        msg = "Ready" if not self.system.arduino.ERROR else self.system.arduino.ERROR
        self.arduino_status.config(text=msg)

        self.dir_name.config(text=self.system.directory)

        self.root.after(10, self._update)

    def _draw_main_image(self):

        if len(self.system.cameras) == 0:
            frame = pywfom.imaging.error_frame("No Cameras Configured")
            image = self.convert_frame(frame, (800,1000), True)
        else:
            # Draw main image
            cam = self.system.cameras[self.selected_frame]
            image = self.convert_frame(cam.frame, (800,1000), True)

            h, w, fr = cam.height, cam.width, cam.framerate

            self.main_lbl.config(
                text="{0} ({1}): {2}x{3}, {4} fps".format(
                    cam.name,
                    cam.device.title(),
                    w,
                    h,
                    round(fr,2)
                )
            )

        self.canvas.config(height=image.height(), width=image.width())
        self.canvas.create_image(0,0,image=image,anchor="nw")
        self.canvas.delete(self.rect)
        if 0 in [self.ix, self.iy, self.x, self.y]:
            pass
        else:
            self.rect = self.canvas.create_rectangle(self.ix, self.iy, self.x, self.y, fill="", outline="green")
        self.canvas.image = image

    def _draw_thumnails(self):

        # Draw thumnails
        if len(self.system.cameras) == 0:
            return

        tn_height = self.root.winfo_height()/len(self.system.cameras)/3

        thumbnail_size = (tn_height, tn_height)

        for i, cam in enumerate(self.system.cameras):
            img = self.convert_frame(cam.frame, thumbnail_size, False)
            self.thumbnails[i].img = img
            self.thumbnails[i].config(image=img, borderwidth=3, relief="flat", bg="white")
            self.thumbnails[i].bind("<Button-1>",lambda event, idx=i: self.change_main_frame(event, idx))
            self.thumbnail_labels[i].pack()
            self.thumbnails[i].pack()

        self.thumbnails[self.selected_frame].config(borderwidth=10,relief="ridge", bg="green")

    def _acquire(self):

        if tk.messagebox.askyesno("pywfom", message="Start acquistion?"):
            self.system.acquire()

    def close(self, event=None):
        self.system.close()
        self.root.destroy()

    def set_aoi_start(self, event):

        self.ix = event.x
        self.iy = event.y

    def set_aoi_end(self, event):

        self.x = event.x
        self.y = event.y
        w = self.x-self.ix
        h = self.y-self.iy

        if 0 in [w,h]:
            self.ix, self.iy, self.x, self.y = 0,0,0,0
            return

        if w < 0:
            self.ix = self.x
            w = abs(w)
        if h < 0:
            self.iy = self.y
            h = abs(h)

        cam = self.system.cameras[self.selected_frame]

        x, y, he, wi = "offset_x", "offset_y", "height", "width"

        cam.set(
            height=int(h/self.scale),
            width=int(w/self.scale),
            offset_x=int(getattr(cam,x)+self.ix/self.scale),
            offset_y=int(getattr(cam,y)+self.iy/self.scale)
        )

        self.ix, self.iy, self.x, self.y = 0,0,0,0

    def draw_rectangle(self, event):
        self.x, self.y = event.x, event.y

    def reset_aoi(self, event):
        cam = self.system.cameras[self.selected_frame]
        cam.set(
            height=cam.get_max("height"),
            width=cam.get_max("width"),
            offset_x=1,
            offset_y=1
        )

    def change_main_frame(self, event, idx):
        self.selected_frame = idx

    def convert_frame(self, frame, max_size, main):

        if frame.dtype == "uint16":
            frame = frame.astype(np.uint8)
        else:
            pass

        # Create main viewing frame
        max_dim = max(frame.shape[0], frame.shape[1])
        if max_dim < max_size[0]:
            scale = max_size[0]/max_dim
        elif max_dim > max_size[1]:
            scale = max_size[1]/max_dim
        else:
            scale = 1

        w, h = int(scale*frame.shape[0]), int(scale*frame.shape[1])

        if main:
            self.scale = scale

        img = ImageTk.PhotoImage(image = Image.fromarray(frame).resize((h, w)))

        return img

class Config(tk.Frame):

    # TODO: Build out

    def __init__(self, parent, system):

        self.system = system

        # General Application Settings
        self.root = parent
        self.root.resizable(width=False, height=False)
        self.root.bind("<Escape>", self._close)
        self.root.title("WFOM Configuration")
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        _set_icon(self.root, 'configure')

        self._error_msg = tk.Frame(self.root)

        self._file_frame = tk.Frame(self.root)
        self._create_file_widgets()
        self._arduino_frame = tk.Frame(self.root)
        self._create_arduino_widgets()
        self._camera_frame = tk.Frame(self.root)
        self._create_camera_widgets()

    def _create_file_widgets(self):

        self._file_frame.pack_forget()

        tk.Label(self._file_frame, text='File').grid(row=0, column=0, columnspan=3)

        for i, (k,v) in enumerate(self.system.__dict__.items()):

            var = tk.StringVar()
            var.set(v)
            if k in ['arduino', 'cameras']:
                continue
            elif k == 'directory':
                tk.Label(self._file_frame, text=k.title()).grid(row=i, column=0)
                self.path = tk.Label(self._file_frame)
                self.path.grid(row=i, column=1)
                tk.Button(self._file_frame,text='Browse').grid(row=i, column=2)
            else:
                tk.Label(self._file_frame,text=k.title()).grid(row=i,column=0)
                tk.Entry(self._file_frame, textvariable=var).grid(row=i,column=1)

        self._file_frame.pack(side='left')

    def _create_arduino_widgets(self):

        self._arduino_frame.pack_forget()

        tk.Label(self._arduino_frame, text='Arduino').grid(row=0, column=0, columnspan=2)

        tk.Label(self._arduino_frame,text="Port: ").grid(row=1, column=0)

        self._port_combo = ttk.Combobox(self._arduino_frame,values=[self.system.arduino.port],state='readonly')
        self._port_combo.insert(0,"Current Port ({0})".format(self.system.arduino.port))
        self._port_combo.bind('<Button-1>',
            lambda e: self._port_combo.config(values=pywfom.control.list_ports())
        )
        self._port_combo.bind('<<ComboboxSelected>>',
            lambda e: self.system.arduino.set(port=e.widget.get().split(' - ')[0])
        )
        self._port_combo.grid(row=1, column=1)

        tk.Button(  self._arduino_frame,
                    text='Configure',
                    command=lambda frm=self:_ArduinoConfig(frm, frm.root)
        ).grid(row=1, column=3)

        tk.Label(self._arduino_frame, text='Status: ').grid(row=2, column=0)
        status = 'Ready' if not self.system.arduino.ERROR else "ERROR"
        lbl = tk.Label(self._arduino_frame, text=status)
        if self.system.arduino.ERROR:
            lbl.bind('<Enter>', lambda event, msg=status:self._show_msg(event, msg))
        lbl.grid(row=2, column=1)

        self._arduino_frame.pack(side='left')

    def _create_camera_widgets(self):

        # TODO: Remove cameras

        self._camera_frame.pack_forget()

        tk.Label(self._camera_frame, text='Cameras').grid(row=0, column=0, columnspan=4)

        tk.Label(self._camera_frame, text='Name').grid(row=1, column=0)
        tk.Label(self._camera_frame, text='Type').grid(row=1, column=1)
        tk.Label(self._camera_frame, text='Status').grid(row=1, column=2)

        count=0
        for i, cam in enumerate(self.system.cameras):
            tk.Label(self._camera_frame, text=cam.name).grid(row=i+2, column=0)
            tk.Label(self._camera_frame, text=cam.device).grid(row=i+2, column=1)
            status = 'Ready' if not cam.ERRORS else "ERROR"
            lbl = tk.Label(self._camera_frame, text=status)
            self.msg = tk.Label(self._camera_frame)
            if cam.ERRORS:
                lbl.bind('<Enter>', lambda event, msg=status:self._show_msg(event, msg))
            lbl.grid(row=i+2, column=2)
            tk.Button(  self._camera_frame,
                        text='Remove',
                        command=lambda i=i:self._delete(i)
            ).grid(row=i+2, column=3)
            tk.Button(  self._camera_frame,
                        text='Edit',
                        command=lambda i=i:_CameraConfig(self, self.root, self.system.cameras[i])
            ).grid(row=i+2, column=4)
            count+=1

        tk.Button( self._camera_frame, text='Add Camera', command= lambda :self._add()
        ).grid(row=count+2, column=0, columnspan=5)

        self._camera_frame.pack(side='left')

    def _show_msg(self, event, msg):
        # TODO: Add error popup
        print(event.__dict__)

    def _hide_msg(self, event):
        # TODO: Remove error popup
        pass

    def _delete(self,i):
        _delete_camera(self,i)
        self._create_camera_widgets()

    def _add(self):
        _add_camera(self, False)
        self._create_camera_widgets()

    def _edit_camera(self):
        pass

    def _close(self, event=None):
        self.system.arduino.close()
        [cam.close() for cam in self.system.cameras]
        self.root.destroy()

class _CameraConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None, camera=None):

        super().__init__(master = master)

        if not camera:
            self.camera = parent.system.cameras[parent.selected_frame]
        else:
            self.camera = camera

        self.root = parent.root

        self._init_settings = {}
        for setting in pywfom.imaging.TYPES:
            self._init_settings[setting] = getattr(self.camera, setting)

        self.parent = parent
        _set_icon(self.root, 'configure')

        self.title("({0}) Settings".format(self.camera.name))

        self.widget_frm = tk.Frame(self)
        self._update_widgets()

    def _update_widgets(self):

        self.widget_frm.destroy()
        self.widget_frm = tk.Frame(self)

        setting_frm = tk.Frame(self.widget_frm)

        for i, (k, v) in enumerate(self.camera.__dict__.items()):

            if k[0] == '_' or k not in pywfom.imaging.TYPES:
                continue

            v = str(v)

            lbl = tk.Label(setting_frm, text=k.title(), width=len(k))
            lbl.grid(row=i, column=0, sticky='E', pady=5)

            if k in pywfom.imaging.OPTIONS:
                entry = ttk.Combobox(
                    setting_frm,
                    width=8,
                    values=pywfom.imaging.OPTIONS[k],
                    justify='center'
                )
                entry.insert(0, v)
                entry.config(state='readonly')
                entry.bind('<<ComboboxSelected>>', lambda event, k=k:self._callback(event,k))

            elif k in ["framerate", 'name']:
                entry = tk.Entry(
                    setting_frm,
                    width=8,
                    justify='center'
                )
                entry.insert(0, v)
            else:
                entry = tk.Spinbox(
                    setting_frm,
                    width=4,
                    from_= self.camera.get_min(k),
                    to = self.camera.get_max(k),
                    justify='center'
                )
                entry.delete(0, 'end')
                entry.insert(0, v)
                entry.config(
                    command=lambda entry=entry, k=k:self._callback(entry, k)
                )
                entry.bind('<Button-1>', lambda event, k=k:self._callback(event, k))

            entry.grid(row=i, column=1, sticky='W', pady=5)
            entry.bind('<FocusOut>', lambda event, k=k:self._callback(event, k))

        setting_frm.pack()
        button_frm = tk.Frame(self.widget_frm)
        button_frm.pack(pady=10)

        reset_btn = tk.Button(button_frm, text='Reset', command=self._reset)
        reset_btn.pack(side='left', padx=10)
        done_btn = tk.Button(button_frm, text='Done', command=self._close)
        done_btn.pack(side='left')

        self.widget_frm.pack()

    def _callback(self, event, setting):

        try:
            value = pywfom.imaging.TYPES[setting](event.widget.get())
        except:
            value = pywfom.imaging.TYPES[setting](event.get())

        if setting == 'name':
            self.parent.thumbnail_labels[self.parent.selected_frame].config(text=value)

        self.camera.set( config = {setting:value} )

    def _reset(self):
        self.camera.set(config=self._init_settings)
        self._update_widgets()

    def _close(self, event=None):
        if event and event.widget.widgetName in ['frame', 'ttk::combobox']:
            pass
        else:
            _set_icon(self.root, 'icon')
            self.destroy()

class _ArduinoConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        # TODO: Get this to actually change settings on the arduino

        super().__init__(master = master)

        self.parent = parent
        self.root = self.parent.root
        self.arduino = parent.system.arduino
        self.reset = self.arduino.__dict__.copy()
        _set_icon(self.root, 'configure')
        self.title("Arduino Settings")
        self.strobe_frm = tk.Frame(self)
        self._create_strobe_widgets()
        self.stim_frm = tk.Frame(self)
        self._create_stim_widgets()
        self.daq_frm = tk.Frame(self)
        self._create_daq_widgets()
        self.btn_frm = tk.Frame(self)
        self._create_buttons()

    def _update(self):
        self._create_strobe_widgets()
        self._create_stim_widgets()
        self._create_daq_widgets()
        self._create_buttons()

    def _create_strobe_widgets(self):

        self.strobe_frm.destroy()
        self.strobe_frm = tk.Frame(self)

        tk.Label(
            self.strobe_frm,
            text='Strobe Settings:').grid(row=0,column=0,columnspan=4)

        tk.Label(
            self.strobe_frm,
            text='Trigger'
        ).grid(row=1, column=0)

        self.trig = tk.Spinbox(
            self.strobe_frm,
            from_=0,
            to=40,
            width=2,
            justify='center'
        )
        self.trig.grid(row=1, column=1)
        self.trig.delete(0, 'end')
        self.trig.insert(0, self.arduino.strobing['trigger'])

        self.leds = []

        for i, led in enumerate(self.arduino.strobing['leds']):

            name = tk.Entry(
                self.strobe_frm,
                width=7,
                justify='center'
            )
            name.bind('<FocusOut>', lambda event, i=i:self._callback(event, i, 'led'))
            name.grid(row=i+2, column=0)
            name.insert(0, led['name'])

            pin = tk.Spinbox(
                self.strobe_frm,
                from_=0,
                to=40,
                width=2,
                justify='center'
            )
            pin.bind('<FocusOut>', lambda event, i=i:self._callback(event, i, 'led'))
            pin.bind('<Button-1>', lambda event, i=i:self._callback(event, i, 'led'))
            pin.grid(row=i+2, column=1)
            pin.delete(0, 'end')
            pin.insert(0, led['pin'])

            tk.Button(
                self.strobe_frm,
                text='Remove',
                command=lambda i=i:self._remove_led(i)
            ).grid(row=i+2, column=2)

            tk.Button(
                self.strobe_frm,
                text='Test',
                command=lambda pin=i:self.arduino.toggle_led(pin)
            ).grid(row=i+2, column=3)

        tk.Button(
            self.strobe_frm,
            text='Add LED',
            command=self._add_led
        ).grid(row=i+3, column=0, columnspan=4)

        tk.Button(
            self.strobe_frm,
            text='Test',
            command=self._test_trigger()
        ).grid(row=1, column=2, columnspan=2)

        self.strobe_frm.pack()

    def _create_stim_widgets(self):

        self.stim_frm.destroy()
        self.stim_frm = tk.Frame(self)

        tk.Label(
            self.stim_frm,
            text='Stim Settings:').grid(row=0,column=0,columnspan=4)

        count = 0

        for i, stim in enumerate(self.arduino.stim):

            tk.Label(
                self.stim_frm,
                text = "{0} ({1})".format(stim['name'], stim['type'])
            ).grid(row=i+1, column=0)

            tk.Button(
                self.stim_frm,
                text = 'Remove',
                command= lambda i=i:self._remove_stim(i)
            ).grid(row=i+1, column=1)

            tk.Button(
                self.stim_frm,
                text = 'Configure',
                command= lambda i=i:self._StimConfig(self, self.root, i)
            ).grid(row=i+1, column=2)

            count += 1

        tk.Button(
            self.stim_frm,
            text='Add Stim',
            command=self._add_stim
        ).grid(row=count+2, column=0, columnspan=4)

        self.stim_frm.pack()

    def _create_daq_widgets(self):

        self.daq_frm.destroy()
        self.daq_frm = tk.Frame(self)

        tk.Label(
            self.daq_frm,
            text='Data Acquisition'
        ).grid(row=0, column=0, columnspan=4)

        count = 0
        self.daqs = []

        for i, daq in enumerate(self.arduino.data_acquisition):

            daq_name = tk.Entry(
                self.daq_frm,
                text = daq['name'],
                width=7,
                justify='center'
            )
            daq_name.insert(0, daq['name'])
            daq_name.bind('<FocusOut>', lambda e, i=i:self._callback(e,i))
            daq_name.grid(row=i+1, column=0)

            daq = tk.Spinbox(
                self.daq_frm,
                from_=0,
                to=40,
                width=2
            )
            daq.grid(row=i+1, column=1)
            daq.bind('<Button-1>', lambda e, i=i:self._callback(e,i))
            daq.bind('<FocusOut>', lambda e, i=i:self._callback(e,i))

            tk.Button(
                self.daq_frm,
                text = 'Remove',
                command=lambda i=i: self._remove_daq(i)
            ).grid(row=i+1, column=2)

            tk.Button(
                self.daq_frm,
                text = 'Test',
                command=lambda i=i: self._DaqConfig(self, self.root, i)
            ).grid(row=i+1, column=3)

            count+=1

        tk.Button(
            self.daq_frm,
            text='Add DAQ',
            command=self._add_daq
        ).grid(row=count+2, column=0, columnspan=4)

        self.daq_frm.pack()

    def _create_buttons(self):

        self.btn_frm.destroy()
        self.btn_frm = tk.Frame(self)

        tk.Button(self.btn_frm, text='Reset', command=self._reset).pack(side='left')
        tk.Button(self.btn_frm, text='Deploy', command=self._deploy).pack(side='left')

        self.btn_frm.pack()

    def _callback(self,event,i,name):
        pass

    def _test_trigger(self):
        # TODO:
        pass

    def _add_led(self):
        self.arduino.strobing['leds'].append({'name':'newLED','pin':1})
        self._update()

    def _remove_led(self, i):
        self.arduino.strobing['leds'].pop(i)
        self._update()

    def _add_stim(self):
        stim =  {
            "name":"default",
            "type":"2PinStepper",
            "pins":{
                "step":5,
                "dim":6
            },
            "pre_stim":4.0,
            "stim":7.0,
            "post_stim":8.0
        }
        self.arduino.stim.append(stim)
        self._update()

    def _remove_stim(self, i):
        self.arduino.stim.pop(i)
        self._update()

    def _add_daq(self):
        self.arduino.data_acquisition.append({'name':'newDAQ','pin':1})
        self._update()

    def _remove_daq(self, i):
        self.arduino.data_acquisition.pop(i)
        self._update()

    def _reset(self):
        self.arduino.set(config=self.reset)
        self._update()

    def _deploy(self):

        strobing = {
            'trigger':self.trig.get(),
            'leds':[]
        }

        print(self.trig.get())
        for led in self.leds:
            print(led.get())
        for stim in self.stims:
            print(stim)
        for daq in self.daqs:
            print(daq.get())

    def _close(self, event):
        _set_icon(self.root, 'icon')
        self.destroy()

    class _StimConfig(tk.Toplevel):

        def __init__(self, parent, master, index):

            # TODO: Complete

            super().__init__(master = master)

            self.stim_settings = parent.arduino.stim[index]

            self._create_widgets()

        def _create_widgets(self):

            for i, (k, v) in enumerate(self.stim_settings.items()):
                tk.Label(self, text=k).grid(row=i, column=0)
                tk.Label(self, text=v).grid(row=i, column=1)

    class _DaqConfig(tk.Toplevel):

        def __init__(self, parent, master, index):

            # TODO: Complete

            super().__init__(master = master)

            self.daq = parent.arduino.data_acquisition[index]

            self._create_widgets()

        def _create_widgets(self):

            for i, (k, v) in enumerate(self.daq.items()):
                tk.Label(self, text=k).grid(row=i, column=0)
                tk.Label(self, text=v).grid(row=i, column=1)

class _FileConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        # TODO: Get this to actually change settings on the arduino

        super().__init__(master = master)

        self.system = parent.system
        _set_icon(self.root, 'configure')

        self._init_system = self.system.__dict__.copy()

        self._create_widgets()
        self._create_buttons()

    def _create_widgets(self):

        widget_frm = tk.Frame(self)

        for i, (k,v) in enumerate(self.system.__dict__.items()):
            var = tk.StringVar()
            var.set(v)
            if k in ['arduino', 'cameras','directory']:
                continue

            elif k == 'runs':

                tk.Label(widget_frm,text=k.title()).grid(row=i,column=0)
                entry = tk.Spinbox(widget_frm,from_=0,to=100,width=3,justify='center',textvariable=var)
                entry.grid(row=i,column=1)
            else:

                tk.Label(widget_frm,text=k.title()).grid(row=i,column=0)
                entry = tk.Entry(widget_frm, textvariable=var, width=7,justify='center')
                entry.grid(row=i,column=1)

            entry.bind('<FocusOut>',
                lambda event, k=k:self._callback(k, event))
            entry.bind('<Return>',
                lambda event, k=k:self._callback(k, event))
            entry.bind('<Button-1>',
                lambda event, k=k:self._callback(k, event))

            widget_frm.pack()

    def _callback(self, setting, event):
        # TODO: Spinbox changes to new value on press, not old
        setattr(self.system, setting, event.widget.get())

    def _create_buttons(self):

        button_frm = tk.Frame(self)
        button_frm.pack()

        tk.Button(button_frm,text='Reset').pack(side='left')
        tk.Button(button_frm,text='Done').pack(side='left')
