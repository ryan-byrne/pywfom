import numpy as np
import time, cv2, json, os, pkgutil
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

import pywfom

def _set_icon(root, name="icon"):
    path = "{0}/img/{1}.png".format(os.path.dirname(pywfom.__file__), name)
    photo = tk.PhotoImage(
        master = root,
        file = path
    )
    root.iconbitmap(path)
    root.iconphoto(False, photo)

def _config_arduino(frame):
    _ArduinoConfig(frame, frame.root)

def _config_file(frame):
    _FileConfig(frame, frame.root)

def _set_dir(parent):
    parent.file.directory = tk.filedialog.askdirectory()

def _edit_camera(frame, i=None):

    if i:
        frame.selected_frame = i

    _set_icon(frame.root, "configure")
    _CameraConfig(frame, frame.root)

def _delete_camera(frame, i=None):

    if i:
        frame.selected_frame = i

    frame.cameras.pop(frame.selected_frame).close()
    frame.thumbnails.pop(frame.selected_frame).pack_forget()
    frame.thumbnail_labels.pop(frame.selected_frame).pack_forget()
    frame.selected_frame = 0

def _load(frame):

    f = filedialog.askopenfile(parent=frame.root)

    if not f:
        return

    config = json.load(f)
    f.close()

    frame._shutdown()
    frame._startup(config)

def _save(frame):

    _cameras = []

    for cam in frame.cameras:

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

def _startup(config):
    # Initiate each component's Class
    c = [
        pywfom.imaging.DEVICES[cfg['device']](cfg) for cfg in config["cameras"]
    ]
    a = Arduino(config["arduino"])
    f = Writer(config=config["file"])

    return c, a, f

class Main(tk.Frame):

    def __init__(self, parent, system):

        self.cameras, self.arduino, self.file = system.cameras, system.arduino, system.file

        print("Opening Viewing Frame...")

        # General Application Settings
        self.root = parent
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.close)
        self.root.title("pywfom")
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
                    command=lambda frm=self:_delete_camera(frm),
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
        for i, cam in enumerate(self.cameras):
            self.add_thumnail(cam.name)

        tk.Button(
            self.right_side,
            text='Add Camera',
            command=self._add_camera,
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
            values=[self.arduino.port],
            state='readonly'
        )
        self._port_combo.pack(side='left')
        self._port_combo.current(0)
        self._port_combo.bind('<Button-1>', lambda e: self._get_ports(e))
        self._port_combo.bind('<<ComboboxSelected>>', lambda e: self._change_port(e))

        tk.Button(
            port_frm,
            text="Configure",
            command=lambda frm=self:_config_arduino(frm),
            padx=10,
            pady=5
        ).pack(side='left')

        self.arduino_status = tk.Label(arduino_frm)
        self.arduino_status.pack()

    def _create_file_widgets(self):

        tk.Label(
            self.right_side,
            text='File:'
        ).pack()

        # Create File Directory
        file_frame = tk.Frame(self.right_side)
        file_frame.pack()

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
            command=lambda frm=self:_config_file(frm)
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

        self.acquire_btn = tk.Button(
            btn_frm,
            text="Acquire",
            command=self.acquire,
            padx=10,
            pady=5
        ).pack(side='left', padx=10)

        btn_frm.pack(pady=30)

    def add_thumnail(self, name):
        self.thumbnails.append(tk.Label(self.thumbnails_frame))
        self.thumbnail_labels.append(tk.Label(self.thumbnails_frame, text=name))

    def _get_ports(self, event):
        self._port_combo.config(values=['Loading Ports...'])
        ports = pywfom.control.list_ports()
        ports.insert(0, self.arduino.port)
        self._port_combo.config(values=ports)

    def _change_port(self, event):

        self.arduino.set(
            port=event.widget.get().split(' - ')[0]
        )

    def _delete_camera(self):
        if i:
            frame.selected_frame = i

        self.cameras.pop(frame.selected_frame).close()
        frame.thumbnails.pop(frame.selected_frame).pack_forget()
        frame.thumbnail_labels.pop(frame.selected_frame).pack_forget()
        frame.selected_frame = 0

    def _update(self):

        self._draw_main_image()

        self._draw_thumnails()

        msg = "Ready" if not self.arduino.ERROR else self.arduino.ERROR
        self.arduino_status.config(text=msg)

        self.dir_name.config(text=self.file.directory)

        self.root.after(1, self._update)

    def _draw_main_image(self):

        if len(self.cameras) == 0:
            frame = pywfom.imaging.error_frame("No Cameras Configured")
            image = self.convert_frame(frame, (800,1000), True)
        else:
            # Draw main image
            cam = self.cameras[self.selected_frame]
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
        if len(self.cameras) == 0:
            return

        tn_height = self.root.winfo_height()/len(self.cameras)/3

        thumbnail_size = (tn_height, tn_height)

        for i, cam in enumerate(self.cameras):
            img = self.convert_frame(cam.frame, thumbnail_size, False)
            self.thumbnails[i].img = img
            self.thumbnails[i].config(image=img, borderwidth=3, relief="flat", bg="white")
            self.thumbnails[i].bind("<Button-1>",lambda event, idx=i: self.change_main_frame(event, idx))
            self.thumbnail_labels[i].pack()
            self.thumbnails[i].pack()

        self.thumbnails[self.selected_frame].config(borderwidth=10,relief="ridge", bg="green")

    def _add_camera(self):
        cam = pywfom.imaging.Camera()
        self.cameras.append(cam)
        self.add_thumnail(cam.name)
        self.selected_frame = len(self.cameras)-1
        _CameraConfig(self, self.root)

    def acquire(self):

        for cam in self.cameras:
            if cam.ERROR:
                tk.messagebox.showerror(
                    'Camera Error',
                    message=cam.ERROR
                )
                return

        if self.arduino.ERROR or self.file.ERROR:
            tk.messagebox.showerror(
                'Arduino Error',
                message=self.arduino.ERROR
            )
            return


        result = tk.messagebox.askyesno("pywfom", message="Start acquistion?")

        if result:
            self.file.write(self.arduino, self.cameras)
        else:
            pass

    def _shutdown(self):
        print("Closing pywfom...")
        [cam.close() for cam in self.cameras]
        self.arduino.close()
        self.file.close()

    def close(self, event=None):
        self._shutdown()
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

        cam = self.cameras[self.selected_frame]

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
        cam = self.cameras[self.selected_frame]
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

    def __init__(self, parent, config):

        # General Application Settings
        self.root = parent
        self.root.resizable(width=False, height=False)
        self.root.bind("<Escape>", self._close)
        self.root.title("WFOM Configuration")
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        _set_icon(self.root, 'configure')
        # Initiate each component's Class
        self.file = Writer(config=config["file"])
        self._create_file_widgets()
        self.arduino = Arduino(config["arduino"])
        self._create_arduino_widgets()
        self.cameras = [
            pywfom.imaging.DEVICES[cfg['device']](cfg) for cfg in config["cameras"]
        ]
        self._create_camera_widgets()

    def _create_file_widgets(self):
        tk.Label(self.root, text='File').grid(row=0, column=0, columnspan=3)
        for i, setting in enumerate(self.file.__dict__):
            if setting == 'ERROR':
                continue
            elif setting == 'directory':
                tk.Label(self.root, text=setting.title()).grid(row=i, column=0)
                self.path = tk.Label(self.root)
                self.path.grid(row=i, column=1)
                tk.Button(self.root,text='Browse').grid(row=i, column=2)
            else:
                tk.Label(self.root,text=setting.title()).grid(row=i,column=0)
                tk.Entry(self.root).grid(row=i,column=1)

    def _create_arduino_widgets(self):
        tk.Label(self.root, text='Arduino').grid(row=0, column=8, columnspan=2)

        tk.Label(
            self.root,
            text="Port: "
        ).grid(row=1, column=8)

        self.ports = ttk.Combobox(
            self.root
        )
        self.ports.insert(0,"Current Port ({0})".format(self.arduino.port))
        self.ports.config(state='readonly')
        self.ports.bind('<Button-1>', self._port_combo_select)
        self.ports.bind("<<ComboboxSelected>>", self._port_combo_update)
        self.ports.grid(row=1, column=9)

        tk.Button(  self.root,
                    text='Configure',
                    command=lambda frm=self:_config_arduino(frm)
        ).grid(row=2, column=8, columnspan=2)

        tk.Label(self.root, text='Status: ').grid(row=3, column=8)
        status = 'Ready' if not self.arduino.ERROR else "ERROR"
        lbl = tk.Label(self.root, text=status)
        if self.arduino.ERROR:
            lbl.bind('<Enter>', lambda event, msg=status:self._show_msg(event, msg))
        lbl.grid(row=4, column=9)

    def _create_camera_widgets(self):
        tk.Label(self.root, text='Cameras').grid(row=0, column=3, columnspan=4)

        tk.Label(self.root, text='Name').grid(row=1, column=3)
        tk.Label(self.root, text='Type').grid(row=1, column=4)
        tk.Label(self.root, text='Status').grid(row=1, column=5)

        for i, cam in enumerate(self.cameras):
            tk.Label(self.root, text=cam.name).grid(row=i+2, column=3)
            tk.Label(self.root, text=cam.device).grid(row=i+2, column=4)
            status = 'Ready' if not cam.ERROR else "ERROR"
            lbl = tk.Label(self.root, text=status)
            self.msg = tk.Label(self.root)
            if cam.ERROR:
                lbl.bind('<Enter>', lambda event, msg=status:self._show_msg(event, msg))
            lbl.grid(row=i+2, column=5)
            tk.Button(  self.root,
                        text='Remove').grid(row=i+2, column=6)
            tk.Button(  self.root,
                        text='Edit').grid(row=i+2, column=7)

    def _port_combo_select(self, event):

        self.ports.config(values=['Loading Ports...'])

        ports = list_ports()

        if len(ports) == 0:
            ports = ['No ports found']

        ports = ["{0} - {1}".format(p.device, p.description) for p in ports]

        self.ports.config(values=ports)

    def _port_combo_update(self, event):

        port = ''
        for let in event.widget.get():

            if let == '-':
                break
            else:
                port += let


        self.arduino.set('port', port[:-1])

    def _show_msg(self, event, msg):
        # TODO: Add error popup
        print(event.__dict__)

    def _hide_msg(self, event):
        # TODO: Remove error popup
        pass

    def _camera_config(self):
        pass

    def _delete_camera(self):
        pass

    def _add_camera(self):
        pass

    def _edit_camera(self):
        pass

    def _arduino_config(self):
        pass

    def _close(self, event=None):
        self.arduino.close()
        self.file.close()
        [cam.close() for cam in self.cameras]
        self.root.destroy()

class _CameraConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None, camera=None):

        super().__init__(master = master)

        if not camera:
            self.camera = parent.cameras[parent.selected_frame]
        else:
            self.camera = camera

        self.root = parent.root

        self._init_settings = {}
        for setting in pywfom.imaging.TYPES:
            self._init_settings[setting] = getattr(self.camera, setting)

        self.parent = parent
        _set_icon(self.root, 'configure')

        self.title("({0}) Settings".format(self.camera.name))

        self._create_widgets()

    def _create_widgets(self):

        setting_frm = tk.Frame(self)
        setting_frm.pack()

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

        button_frm = tk.Frame(self)
        button_frm.pack(pady=10)

        reset_btn = tk.Button(button_frm, text='Reset', command=self._reset)
        reset_btn.pack(side='left', padx=10)
        done_btn = tk.Button(button_frm, text='Done', command=self._close)
        done_btn.pack(side='left')

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

    def _close(self):
        _set_icon(self.root, 'icon')
        self.destroy()

class _ArduinoConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)

        self.parent = parent
        self.root = self.parent.root
        self.arduino = parent.arduino
        self.reset = self.arduino.__dict__.copy()
        _set_icon(self.root, 'configure')
        self.title("Arduino Settings")

        self._create_strobe_widgets()
        self._create_stim_widgets()
        self._create_daq_widgets()

    def _create_strobe_widgets(self):

        strobe_frm = tk.Frame(self)
        strobe_frm.pack()

        tk.Label(
            strobe_frm,
            text='Strobe Settings:').grid(row=0,column=0,columnspan=3)

        tk.Label(
            strobe_frm,
            text='Trigger'
        ).grid(row=1, column=0)

        trig = tk.Spinbox(
            strobe_frm,
            from_=0,
            to=40,
            width=2
        )
        trig.grid(row=1, column=1)
        trig.delete(0, 'end')
        trig.insert(0, self.arduino.strobing['trigger'])

        tk.Button(
            strobe_frm,
            text='Test'
        ).grid(row=1, column=2)

        for i, led in enumerate(self.arduino.strobing['leds']):

            name = tk.Entry(
                strobe_frm,
                width=7
            )
            name.grid(row=i+2, column=0)
            name.insert(0, led['name'])

            pin = tk.Spinbox(
                strobe_frm,
                from_=0,
                to=40,
                width=2
            )
            pin.grid(row=i+2, column=1)
            pin.delete(0, 'end')
            pin.insert(0, led['pin'])

            tk.Button(
                strobe_frm,
                text='Test'
            ).grid(row=i+2, column=2)

        tk.Button(
            strobe_frm,
            text='Add LED',
            command=self._add_led
        ).grid(row=i+3, column=0, columnspan=3)

    def _create_stim_widgets(self):

        stim_frm = tk.Frame(self)
        stim_frm.pack()

        tk.Label(
            stim_frm,
            text='Stim Settings:').grid(row=0,column=0,columnspan=4)

        count = 0

        for i, stim in enumerate(self.arduino.stim):

            tk.Label(
                stim_frm,
                text = "{0} ({1})".format(stim['name'], stim['type'])
            ).grid(row=i+1, column=0)

            tk.Button(
                stim_frm,
                text = 'Delete'
            ).grid(row=i+1, column=1)

            tk.Button(
                stim_frm,
                text = 'Edit'
            ).grid(row=i+1, column=2)

            tk.Button(
                stim_frm,
                text = 'Test'
            ).grid(row=i+1, column=3)

            count += 1

        tk.Button(
            stim_frm,
            text='Add Stim',
            command=self._add_stim
        ).grid(row=count+2, column=0, columnspan=4)

    def _create_daq_widgets(self):

        daq_frm = tk.Frame(self)
        daq_frm.pack()

        tk.Label(
            daq_frm,
            text='Data Acquisition'
        ).grid(row=0, column=0, columnspan=2)

        count = 0

        for i, daq in enumerate(self.arduino.data_acquisition):

            tk.Label(
                daq_frm,
                text = daq['name']
            ).grid(row=i+1, column=0)

            tk.Spinbox(
                daq_frm,
                from_=0,
                to=40,
                width=2
            ).grid(row=i+1, column=1)

            count+=1

        tk.Button(
            daq_frm,
            text='Add DAQ',
            command=self._add_daq
        ).grid(row=count+2, column=0, columnspan=2)

    def _callback(self):
        # TODO:
        pass

    def _add_led(self):
        # TODO:
        pass

    def _add_stim(self):
        # TODO:
        pass

    def _add_daq(self):
        # TODO:
        pass

class _FileConfig(tk.Toplevel):
    """docstring for FileConfig."""

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)
        self.root = parent.root
        self.file = parent.file
        self._create_widgets()

    def _create_widgets(self):

        for i, (k,v) in enumerate(self.file.__dict__.items()):

            if k == 'ERROR':
                continue
            else:

                tk.Label(self, text=k.title()).grid(row=i-1,column=0, sticky='e')

                var = tk.StringVar()
                var.set(v)

                if k == 'directory':
                    # TODO: Update dir on configuration
                    entry = tk.Label(self)
                    tk.Button(
                        self,
                        text="Browse",
                        padx=10,
                        pady=5,
                        command=lambda frm=self:_set_dir(frm)
                    ).grid(row=i-1,column=2)
                elif k == 'runs':
                    entry = tk.Spinbox(
                        self,
                        from_=1,
                        to=100,
                        width=3
                    )
                else:
                    entry = tk.Entry(self,width=10)

                entry.grid(row=i-1,column=1, sticky='w')
                entry.config(textvariable=var, justify='center')
                entry.bind('<FocusOut>', lambda event, k=k:self._callback(event,k))

    def _callback(self, event, setting):
        value = pywfom.file.TYPES[setting](event.widget.get())
        self.file.set(setting, value)
