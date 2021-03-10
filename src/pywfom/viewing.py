import json, os, pywfom, pkgutil, zipfile, time
from tqdm import tqdm
import numpy as np
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

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

    cam = frame.system.cameras[frame.selected_frame]

    _set_icon(frame.root, "configure")
    CameraConfig(cam, frame.root)

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
        CameraConfig(cam, frame.root)
    else:
        return

def convert_frame(frame, max_size):

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

    img = ImageTk.PhotoImage(image = Image.fromarray(frame).resize((h, w)))

    return img, scale

# File Related functions
def _set_dir(system):

    if filedialog.askdirectory():
        system.directory = filedialog.askdirectory()

class Main(tk.Frame):

    """
    :py:class:`tkinter.Frame` to monitor camera frames, Arduino status, and set file directory

    :param system: System interface to be monitored/set
    :type system: :py:class:`pywfom.System`

    .. figure:: img/main_gui.png
      :align: center
      :width: 700

    :(A) Selected Camera Frame:

        :``Camera Status``:
            * :py:class:`tkinter.Label`
            * Shows the selected camera's:
                * :py:data:`name`
                * :py:data:`device`
                * :py:data:`height`
                * :py:data:`width`
                * :py:data:`binning`
                * :py:data:`framerate`

        :``Edit``:
            * :py:class:`tkinter.Button`
            * Opens :py:class:`CameraConfig`

        :``Remove``:
            * :py:class:`tkinter.Button`
            * Deletes selected :py:class:`pywfom.imaging.Camera` from :py:class:`pywfom.System`

    :(B) Camera Thumbnails:

        :``Thumbnails``:
            * Selectable images of each :py:class:`pywfom.imaging.Camera` in :py:class:`pywfom.System`

        :``Add Camera``:
            * :py:class:`tkinter.Button`
            * Adds a :py:class:`pywfom.imaging.Camera` to :py:class:`pywfom.System`

    :(C) Arduino and Run Status:

        :``Select Port``:
            * :py:class:`tkinter.ttk.Spinbox`
            * Calls :py:func:`pywfom.control.list_ports`
            * Sets :py:data:`pywfom.control.Arduino.port`

        :``Configure``:
            * :py:class:`tkinter.Button`
            * Opens :py:class:`ArduinoConfig`

        :``Arduino Status``:
            * :py:class:`tkinter.Label`
            * Displays :py:class:`pywfom.control.Arduino.ERROR`

        :``Current Directory``:
            * :py:class:`tkinter.Label`
            * Sets :py:data:`pywfom.System.directory`

        :``Browse``:
            * :py:class:`tkinter.Button`
            * Opens Dialog which sets :py:data:`pywfom.System.directory`

    :(D) Control Buttons:

        :``Configure``: (:py:class:`tkinter.Button`)

    """

    def __init__(self, system):

        self.system = system

        # General Application Settings
        self.root = tk.Tk()
        self.btns = []
        s = ttk.Style(self.root)
        s.theme_use('clam')
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
            command=lambda:ArduinoConfig(self.system.arduino, self.root),
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
            command=lambda:_set_dir(self.system),
            padx=10,
            pady=5
        ).pack(side='left')

        tk.Button(
            file_frame,
            text="Configure",
            padx=10,
            pady=5,
            command=lambda:RunConfig(self.system, self.root)
        ).pack(side='left')

    def _create_buttons(self):

        # Create frame for buttons
        self.btn_frm = tk.Frame(self.right_side)

        # Create buttons
        tk.Button(
            self.btn_frm,
            text="Close",
            command=self.close,
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        tk.Button(
            self.btn_frm,
            text="Save",
            command=lambda frm=self:pywfom.save_settings(self),
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        tk.Button(
            self.btn_frm,
            text="Load",
            command=lambda frm=self:pywfom.load_settings(self),
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        tk.Button(
            self.btn_frm,
            text="Make Default",
            command=lambda:pywfom.set_default(self.system),
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        self.acquire_btn = tk.Button(
            self.btn_frm,
            text="Acquire",
            command=self._acquire,
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        self.btn_frm.pack(pady=30)

    def _create_run_widgets(self):
        tk.Label(self.right_side, text='Acquiring').pack()

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
            image, self.scale = convert_frame(frame, (800,1000))
        else:
            # Draw main image
            cam = self.system.cameras[self.selected_frame]
            image, self.scale = convert_frame(cam.frame, (800,1000))

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
            img, _ = convert_frame(cam.frame, thumbnail_size)
            self.thumbnails[i].img = img
            self.thumbnails[i].config(image=img, borderwidth=3, relief="flat", bg="white")
            self.thumbnails[i].bind("<Button-1>",lambda event, idx=i: self.change_main_frame(event, idx))
            self.thumbnail_labels[i].pack()
            self.thumbnails[i].pack()

        self.thumbnails[self.selected_frame].config(borderwidth=10,relief="ridge", bg="green")

    def _acquire(self):

        for cam in self.system.cameras:
            if cam.ERRORS:
                tk.messagebox.showerror('Camera Error',message=cam.ERRORS[0])
                return

        if self.system.arduino.ERROR:
            tk.messagebox.showerror('Arduino Error',message=self.arduino.ERROR)
            return

        if tk.messagebox.askyesno('pyWFOM', 'Start Acquisition?'):
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

class Viewer(tk.Frame):

    """
    View acquisition files from a specified run directory

    :param run_directory: Path to run directory being viewed
    :type run_directory: str_

    """

    def __init__(self, run_dir=None):

        self.root = tk.Tk()
        s = ttk.Style(self.root)
        s.theme_use('clam')
        _set_icon(self.root, 'view')

        self.root.bind('<space>', self._toggle_play)
        self.root.bind('<Right>', self._slide_right)
        self.root.bind('<Left>', self._slide_left)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Escape>", self.close)

        self.paused = False

        # Set directory and run name
        if not run_dir:
            run_dir = filedialog.askdirectory(
                title='Select a run folder to view',
                parent=self.root
            )

        # Record configuration
        zip = zipfile.ZipFile(run_dir, 'r') if run_dir.split('/')[-1][-3:] == 'zip' else None
        run_name = run_dir.split('/')[-1][:-4] if zip else run_dir.split('/')[-1]
        f = zip.open(run_name+'/config.json') if zip else open(run_dir+'/config.json')
        self.config = json.load(f)

        # Set title to run name
        self.root.title(run_name)

        # Record frames from files
        self.frames = []
        num_frms = len(zip.infolist())-1 if zip else len(os.listdir(run_dir))-1

        for i in tqdm(range(num_frms), desc='Loading {0}'.format(run_name), unit='frame'):
            path = run_name if zip else run_dir
            fname = '{0}/frame{1}.npz'.format(path, i)
            f = zip.open(fname) if zip else fname
            self.frames.append(np.load(f))

        # Set Framerate of Viewing
        for i, cam in enumerate(self.config['cameras']):
            if cam['master']:
                self.framerate = cam['framerate']
        self.current_frame = 0


        # Create widgets
        self._create_info_widgets()
        self._create_viewing_frames()
        self._create_controls()
        self._create_arduino_data()
        self._update()

    def _create_info_widgets(self):

        info_frm = tk.Frame(self.root)
        info_frm.pack()

        lbls = [
            'Framerate:',
            self.framerate,
            'Mouse:',
            self.config['mouse'],
            'User:',
            self.config['user']
        ]

        for i, text in enumerate(lbls):
            tk.Label(info_frm, text=text).grid(row=0, column=i)

    def _create_viewing_frames(self):

        view_frm = tk.Frame(self.root)
        view_frm.pack()

        self.cam_frms = []

        for i, cam in enumerate(self.config['cameras']):
            tk.Label(view_frm, text=cam['name']).grid(row=0, column=i)
            frm = tk.Canvas(view_frm)
            frm.grid(row=1, column=i)
            self.cam_frms.append(frm)

    def _create_controls(self):

        control_frm = tk.Frame(self.root)
        control_frm.pack()

        self.slider = tk.Scale(
            control_frm, orient=tk.HORIZONTAL, from_=0, to=len(self.frames), length=600
        )
        self.slider.grid(row=0, column=0)
        self.slider.bind('<Button-1>', self._slider_callback)
        self.slider.bind('<ButtonRelease-1>', self._set_frame)

        self.play_pause = tk.Button(control_frm,command=self._toggle_play,text='||')
        self.play_pause.grid(row=0, column=1)

    def _create_arduino_data(self):

        ard_frm = tk.Frame(self.root)
        ard_frm.pack()

        # Create LED Widget
        led_frm = tk.Frame(ard_frm)
        tk.Label(led_frm, text='Current Led: ').pack(side='left')
        self.current_led = tk.Label(led_frm)
        self.current_led.pack(side='left')
        led_frm.grid(row=0, column=0, columnspan=2)

        # Create daq widgets
        self.daq_values = []
        daq_frm = tk.Frame(ard_frm)
        tk.Label(daq_frm, text='Data Acquisition').grid(row=0, column=0, columnspan=3)
        tk.Label(daq_frm, text='name').grid(row=1, column=0)
        tk.Label(daq_frm, text='pin').grid(row=1, column=1)
        tk.Label(daq_frm, text='value').grid(row=1, column=2)

        for i, daq in enumerate(self.config['arduino']['data_acquisition']):

            tk.Label(daq_frm, text=daq['name']).grid(row=i+2, column=0)
            tk.Label(daq_frm, text=daq['pin']).grid(row=i+2, column=1)
            d = tk.Label(daq_frm)
            d.grid(row=i+2, column=2)
            self.daq_values.append(d)

        daq_frm.grid(row=1, column=0)


        # Create stim widgets
        self.stim_pos = []
        stim_frm = tk.Frame(ard_frm)
        tk.Label(stim_frm, text='Stim').grid(row=0, column=0, columnspan=3)
        tk.Label(stim_frm, text='name').grid(row=1, column=0)
        tk.Label(stim_frm, text='type').grid(row=1, column=1)
        tk.Label(stim_frm, text='position').grid(row=1, column=2)

        for i, stim in enumerate(self.config['arduino']['stim']):
            tk.Label(stim_frm, text=stim['name']).grid(row=i+2, column=0)
            tk.Label(stim_frm, text=stim['type']).grid(row=i+2, column=1)

            s = tk.Label(stim_frm)
            s.grid(row=i+2, column=2)
            self.stim_pos.append(s)

        stim_frm.grid(row=1, column=1)

    def _update_arduino_widgets(self, message):

        self.current_led.config(
            text=self.config['arduino']['strobing']['leds'][int(message.split('d')[0])]['name']
        )

        daq_array = message.split('d')[1].split('m')[0].split(',')[:-1]
        for i, daq in enumerate(daq_array):
            self.daq_values[i].config(text=daq)

        stim_pos_array = message.split('d')[1].split('m')[1].split(',')[:-1]
        for i, stim in enumerate(stim_pos_array):
            self.stim_pos[i].config(text=stim)

    def _update(self):

        try:
            frame = self.frames[self.current_frame]
        except:
            self.current_frame = 0
            frame = self.frames[self.current_frame]

        for i, data in enumerate(frame.files):
            if i == len(self.cam_frms):
                self._update_arduino_widgets(str(frame.get(data)))
            else:
                canvas = self.cam_frms[i]
                img, _ = convert_frame(frame.get(data), (500,500))
                canvas.create_image(0,0,image=img,anchor="nw")
                canvas.image = img
                canvas.config(height=img.height(),width=img.width())

        if not self.paused:
            self.current_frame+=1
            self.play_pause.config(text='||')
            self.slider.set(self.current_frame)
        else:
            self.play_pause.config(text='►')

        self.root.after(int(1/self.framerate*1000), self._update)

    def _set_frame(self, event=None):
        self.current_frame = self.slider.get()

    def _slider_callback(self,event=None):
        self.paused = True

    def _slide_left(self, event=None):
        self.paused = True
        self.current_frame -= 1
        self.slider.set(self.current_frame)

    def _slide_right(self, event=None):
        self.paused = True
        self.current_frame += 1
        self.slider.set(self.current_frame)

    def _toggle_play(self, event=None):
        self.paused = not self.paused

    def close(self, event=None):
        self.root.destroy()

class CameraConfig(tk.Toplevel):

    """
    :py:class:`tkinter.Toplevel` to configure a specified Camera's settings


    :param camera: Camera whose settings will be edited
    :type camera: :py:class:`pywfom.imaging.Camera`
    :param master: Window which opened :py:class:`CameraConfig`
    :type master: :py:class:`tkinter.Tk`


    .. figure:: img/camera.png
      :align: center
      :width: 200

    """

    def __init__(self, camera=None, master=None):

        super().__init__(master = master)

        self.camera = camera

        self.root = master

        self.root.bind('<Return>', self.destroy)

        self._init_settings = {}
        for setting in pywfom.imaging.TYPES:
            self._init_settings[setting] = getattr(self.camera, setting)

        _set_icon(self.root, 'configure')

        self.title("({0}) Settings".format(self.camera.name))

        self.widget_frm = tk.Frame(self)
        self._create_widgets()
        self._create_buttons()

    def _create_widgets(self):

        self.names = []
        self.vars = []
        count = 0

        settings_frm = tk.Frame(self)
        settings_frm.pack()

        for i, (k,v) in enumerate(self.camera.__dict__.items()):

            if k[0] == '_' or k in ['frame', 'ERRORS', 'WARNINGS']:
                continue
            elif k in ['index', 'height', 'width', 'offset_x', 'offset_y']:
                var = tk.IntVar(value=v)
                entry = tk.Spinbox(
                    settings_frm,
                    from_=self.camera.get_min(k),
                    to=self.camera.get_max(k),
                )
            elif k in pywfom.imaging.OPTIONS:
                var = tk.StringVar(value=v)
                entry = ttk.Combobox(
                    settings_frm,
                    values=pywfom.imaging.OPTIONS[k],
                    state='readonly',
                )
            else:
                var = tk.StringVar(value=v)
                entry = tk.Entry(settings_frm)
            entry.config(textvariable=var, width=10, justify='center')
            var.trace('w', lambda nm, idx, mode, i=count:self._callback(i))
            count+=1
            self.names.append(k)
            self.vars.append(var)
            entry.grid(row=i, column=1, pady=3, padx=5)
            tk.Label(settings_frm, text=k.title()).grid(row=i, column=0)

    def _create_buttons(self):

        button_frm = tk.Frame(self)
        button_frm.pack()

        for i, (name, func) in enumerate([('Reset', self._reset), ('Done', self.destroy)]):
            btn = tk.Button(button_frm, text=name, command=func, padx=5, pady=5)
            btn.grid(row=0, column=i, padx=10, pady=10)

    def _callback(self, index):

        name = self.names[index]

        try:
            value = pywfom.imaging.TYPES[name](self.vars[index].get())
        except:
            return

        self.camera.set(config={name:value})

    def _reset(self):

        for i, (k,v) in enumerate(self._init_settings.items()):
            self.vars[i].set(v)

    def _close(self, event=None):
        if event and event.widget.widgetName in ['frame', 'ttk::combobox']:
            pass
        else:
            _set_icon(self.root, 'icon')
            self.destroy()

class ArduinoConfig(tk.Toplevel):

    """
    :py:class:`tkinter.Toplevel` to configure the Arduino's settings


    :param arduino: Arduino whose settings will be edited
    :type camera: :py:class:`pywfom.control.Arduino`
    :param master: Window which opened :py:class:`ArduinoConfig`
    :type master: :py:class:`tkinter.Tk`

    """


    def __init__(self, arduino=None, master=None):

        # TODO: Get this to actually change settings on the arduino

        super().__init__(master = master)

        self.names, self.pins, self.daq_names, self.daq_pins= [], [], [], []
        self.stim_names = []
        self.root = master
        self.arduino = arduino
        self._init_settings = {}
        for k,v in self.arduino.__dict__.items():
            self._init_settings[k] = v
        _set_icon(self.root, 'configure')
        self.title("Arduino Settings")
        self.root.bind('<Return>', self.destroy)
        self.strobe_frm = tk.Frame(self)
        self.stim_frm = tk.Frame(self)
        self.daq_frm = tk.Frame(self)
        self.btn_frm = tk.Frame(self)
        self._update()

    def _update(self):
        self._create_strobe_widgets()
        self._create_stim_widgets()
        self._create_daq_widgets()
        self._create_buttons()

    def _create_strobe_widgets(self):

        self.strobe_frm.destroy()
        self.strobe_frm = tk.Frame(self)

        tk.Label(self.strobe_frm,text='Strobe Settings:').grid(row=0,column=0,columnspan=4)

        # Create and Bind Trigger Widgets
        tk.Label(self.strobe_frm,text='Trigger').grid(row=1, column=0)
        self.trig = tk.IntVar(value=self.arduino.strobing['trigger'])
        tk.Spinbox(self.strobe_frm,from_=0,to=40,width=2,justify='center', textvariable=self.trig).grid(row=1, column=1)
        self.trig.trace('w', self._strobing_callback)

        self.names = []
        self.pins = []
        count = 0

        for i, led in enumerate(self.arduino.strobing['leds']):

            # Create widget for each led
            name = tk.StringVar(value=led['name'])
            tk.Entry(self.strobe_frm,width=7,justify='center',textvariable=name).grid(row=i+2, column=0)
            name.trace('w', self._strobing_callback)
            self.names.append(name)

            pin = tk.IntVar(value=led['pin'])
            tk.Spinbox(self.strobe_frm,from_=0,to=40,width=2,justify='center',textvariable=pin).grid(row=i+2, column=1)
            pin.trace('w', self._strobing_callback)
            self.pins.append(pin)

            tk.Button(self.strobe_frm,text='Remove',
                command=lambda i=i:self._remove_led(i)
            ).grid(row=i+2, column=2)
            tk.Button(self.strobe_frm,text='Test',
                command=lambda pin=pin:self.arduino.toggle_led(pin.get())
            ).grid(row=i+2, column=3)
            count+=1

        tk.Button(self.strobe_frm,text='Add LED',command=self._add_led
        ).grid(row=count+3, column=0, columnspan=4)

        tk.Button(self.strobe_frm,text='Test',command=self._test_trigger
        ).grid(row=1, column=2, columnspan=2)

        self.strobe_frm.pack()

    def _create_stim_widgets(self):

        self.stim_frm.destroy()
        self.stim_frm = tk.Frame(self)

        tk.Label(self.stim_frm,text='Stim Settings:').grid(row=0,column=0,columnspan=4)

        count = 0
        self.stim_names = []

        for i, stim in enumerate(self.arduino.stim):

            name = tk.StringVar(value=stim['name'])
            tk.Entry(self.stim_frm,textvariable=name, width=10, justify='center'
            ).grid(row=i+1, column=0)
            name.trace('w', self._stim_callback)
            self.stim_names.append(name)

            ttk.Label(self.stim_frm,text=stim['type'],width=12,justify='center'
            ).grid(row=i+1, column=1)

            tk.Button(self.stim_frm,text='Remove',command=lambda i=i:self._remove_stim(i)
            ).grid(row=i+1, column=2)

            tk.Button(self.stim_frm,text='Configure',
                command= lambda i=i:StimConfig(self.arduino, i, self.root)
            ).grid(row=i+1, column=3)

            count += 1

        tk.Button(self.stim_frm,text='Add Stim',command=self._add_stim
        ).grid(row=count+2, column=0, columnspan=4)

        self.stim_frm.pack()

    def _create_daq_widgets(self):

        self.daq_frm.destroy()
        self.daq_frm = tk.Frame(self)

        tk.Label(self.daq_frm,text='Data Acquisition').grid(row=0, column=0, columnspan=4)

        self.daq_names = []
        self.daq_pins = []
        count = 0

        for i, daq in enumerate(self.arduino.data_acquisition):

            dn = tk.StringVar(name='{0}dname'.format(i), value=daq['name'])
            tk.Entry(self.daq_frm, textvariable=dn, width=7,justify='center').grid(row=i+1, column=0)
            self.daq_names.append(dn)
            dn.trace('w', self._daq_callback)

            dp = tk.IntVar(name='{0}dpin'.format(i), value=daq['pin'])
            tk.Spinbox(self.daq_frm,from_=0,to=40,width=2,textvariable=dp).grid(row=i+1, column=1)
            self.daq_pins.append(dp)
            dp.trace('w', self._daq_callback)

            tk.Button(self.daq_frm,text = 'Remove',command=lambda i=i: self._remove_daq(i)
            ).grid(row=i+1, column=2)

            tk.Button(self.daq_frm,text = 'Test',
                command=lambda: DaqView(self.arduino, self.root)
            ).grid(row=i+1, column=3)

            count+=1

        tk.Button(self.daq_frm,text='Add DAQ',command=self._add_daq
        ).grid(row=count+2, column=0, columnspan=4)

        self.daq_frm.pack()

    def _create_buttons(self):

        self.btn_frm.destroy()
        self.btn_frm = tk.Frame(self)

        tk.Button(self.btn_frm, text='Reset', command=self._reset).pack(side='left')
        tk.Button(self.btn_frm, text='Done', command=self.destroy).pack(side='left')

        self.btn_frm.pack()

    def _strobing_callback(self, nm, idx, mode):

        self.arduino.strobing['trigger'] = self.trig.get()

        self.arduino.strobing['leds'] = []

        for i in range(len(self.names)):
            self.arduino.strobing['leds'].append({
                'pin':self.pins[i].get(),
                'name':self.names[i].get()
            })

        self.arduino.set_trigger()
        self.arduino.set_leds()

    def _daq_callback(self, nm, idx, mode):

        self.arduino.data_acquisition = []

        for i in range(len(self.daq_names)):
            self.arduino.data_acquisition.append({
                'name':self.daq_names[i].get(),
                'pin':self.daq_pins[i].get()
            })

        self.arduino.set_daq()

    def _stim_callback(self, nm, idx, mode):

        for i in range(len(self.stim_names)):
            self.arduino.stim[i]['name'] = self.stim_names[i].get()
            self.arduino.stim[i]['type'] = self.stim_types[i].get()

    def _test_trigger(self):

        if not messagebox.askyesno(
            'Test Trigger',
            "Test the exposure trigger? This will strobe the LEDs."):
            return
        else:
            self.arduino.start_strobing()
            messagebox.showinfo('Testing Trigger', 'Press OK to Stop')
            self.arduino.stop_strobing()

    def _add_led(self):
        self.arduino.strobing['leds'].append({'name':'newLED','pin':1})
        self.arduino.set_leds()
        self._update()

    def _remove_led(self, i):
        self.arduino.strobing['leds'].pop(i)
        self.arduino.set_leds()
        self._update()

    def _add_stim(self):
        stim =  {
            "name":"newStim",
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
        self.set_daq()
        self._update()

    def _remove_daq(self, i):
        self.arduino.data_acquisition.pop(i)
        self.set_daq()
        self._update()

    def _reset(self):
        # TODO: Fix this so it actually resets
        self.arduino.set(config=self._init_settings)
        self._update()

    def _close(self, event):
        _set_icon(self.root, 'icon')
        self.destroy()

class StimConfig(tk.Toplevel):

    """
    :py:class:`tkinter.Toplevel` to configure the an Arduino's stim settings


    :param arduino: Arduino whose stim will be edited
    :type arduino: :py:class:`pywfom.control.Arduino`
    :param index: Index of the stim
    :type index: int_
    :param master: Window which opened :py:class:`StimConfig`
    :type master: :py:class:`tkinter.Tk`

    """

    def __init__(self, arduino, index, master):

        # TODO: Complete

        super().__init__(master = master)

        self.root = master

        self.bind('<Escape>', self.destroy)

        self.arduino = arduino
        self.stim = arduino.stim[index]
        self._init_settings = self.stim.copy()
        self.vars = []
        self.pins = []

        self._create_widgets()


    def _create_widgets(self):

        stim_frm = tk.Frame(self)
        row = 0
        self.vars = []
        self.names = []
        self.pins = []

        for i, (k,v) in enumerate(self.stim.items()):

            tk.Label(stim_frm, text=k.title()).grid(row=row, column=0)

            if k == 'pins':
                entry = tk.Frame(stim_frm)
                for i, pin in enumerate(v):
                    var = tk.IntVar(value=pin)
                    tk.Spinbox(entry, width=2, from_=0, to=40,textvariable=var).pack()
                    var.trace('w', lambda nm, idx, mode, i=i:self._callback(i, True))
                    self.pins.append(var)
                self.vars.append(var)
                self.names.append(k)
                entry.grid(row=row, column=1)
                row+=1
                continue
            elif k == 'steps_per_revolution':
                var = tk.IntVar(value=v)
                entry = tk.Spinbox(stim_frm, width=3, from_=0, to=3000)
            elif k == 'type':
                var = tk.StringVar(value=v)
                entry = ttk.Combobox(
                    stim_frm,
                    values=pywfom.control.OPTIONS['stim_types'],
                    state='readonly'
                )
            else:
                var = tk.StringVar(value=v)
                entry = tk.Entry(stim_frm)
            try:
                entry.config(textvariable=var, width=10, justify='center')
            except:
                pass

            var.trace('w', lambda nm, idx, mode, i=i:self._callback(i))
            self.vars.append(var)
            self.names.append(k)

            entry.grid(row=row, column=1)

            row+=1

        tk.Button(stim_frm, text='Reset').grid(row=row, column=0)
        tk.Button(stim_frm, text='Test', command=self._test).grid(row=row, column=1)

        stim_frm.pack()

        tk.Button(self, text='Done', command=self.destroy).pack()

    def _callback(self, index, pins=False):

        tic = time.time()

        name = 'pins' if pins else self.names[index]
        value = [pin.get() for pin in self.pins] if pins else self.vars[index].get()

        self.arduino.stim[0][name] = value

        self.arduino.set_stim()

    def _reset(self):
        # TODO: COmplete
        pass

    def _test(self):
        # 10 RPM
        for i in range(500):
            self.arduino.increase_step()
            time.sleep(0.01)

class DaqView(tk.Toplevel):

        def __init__(self, arduino, master):

            # TODO: Complete

            super().__init__(master = master)

            self.root.bind('<Return>', self.destroy)

            self.arduino = arduino
            self._create_widgets()
            self._update()

        def _create_widgets(self):

            self.data = []

            for i, daq in enumerate(self.arduino.data_acquisition):
                tk.Label(self, text=daq['name']).grid(row=i, column=0)
                tk.Label(self, text=daq['pin']).grid(row=i, column=1)
                d = tk.Label(self)
                self.data.append(d)
                d.grid(row=i, column=2)

            tk.Button(self, text='Done', command=self.destroy).grid(row=i+1, column=0, columnspan=3)

        def _update(self):

            if not self.arduino.DAQ_MSG:
                return

            for i, d in enumerate(self.data):
                val = str(self.arduino.DAQ_MSG).split('_')[1][1:].split(',')[i]
                d.config(text=val)

            self.after(10, self._update)

class RunConfig(tk.Toplevel):

    """
    Configure the run file
    """

    def __init__(self, system=None, master=None):

        super().__init__(master = master)

        self.system = system
        self.root = master
        self.root.bind('<Return>', self.destroy)
        _set_icon(self.root, 'configure')

        self._init_settings = {}

        for k,v in self.system.__dict__.items():
            if k not in ['runs', 'run_length', 'user', 'mouse']:
                continue
            else:
                self._init_settings[k] = v

        self._create_widgets()
        self._create_buttons()

    def _create_widgets(self):

        self.vars = []
        self.names = []
        count = 0

        widget_frm = tk.Frame(self)
        widget_frm.pack()

        for i, (k,v) in enumerate(self.system.__dict__.items()):

            if k in ['arduino', 'cameras','directory'] or k[0] == '_':
                continue
            elif k == 'runs':
                var = tk.IntVar()
                entry = tk.Spinbox(widget_frm,from_=1,to=100, width=3)
            else:
                var = tk.StringVar()
                entry = tk.Entry(widget_frm, width=7)

            tk.Label(widget_frm, text=k.title()).grid(row=i, column=0)
            entry.config(textvariable=var, justify='center')
            entry.grid(row=i, column=1, padx=10, pady=5)
            var.set(v)
            var.trace('w', lambda nm, idx, mode, i=count:self._callback(i))
            self.vars.append(var)
            self.names.append(k)
            count+=1

    def _create_buttons(self):

        btn_frm = tk.Frame(self)
        btn_frm.pack()

        tk.Button(btn_frm,text='Reset',command=self._reset, padx=10, pady=3).pack(side='left', padx=10)
        tk.Button(btn_frm,text='Done',command=self.destroy, padx=10, pady=3).pack(side='left', pady=10)

    def _callback(self, index):

        name = self.names[index]

        try:
            value = float(self.vars[index].get()) if name == 'run_length' else self.vars[index].get()
        except:
            return

        setattr(self.system, name, value)

    def _reset(self):

        for i, (k,v) in enumerate(self._init_settings.items()):
            self.vars[i].set(v)

class Acquisition(tk.Toplevel):

    """
    Configure the run file
    """

    def __init__(self, system=None, master=None):
        pass
