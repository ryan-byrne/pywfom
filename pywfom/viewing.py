import numpy as np
import time, cv2, json, os
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

from pywfom import imaging
from pywfom.control import Arduino, list_ports
from pywfom.file import Writer

class Main(tk.Frame):

    def __init__(self, parent, config):

        # TODO: create option for default json
        # TODO: better arduino error handling

        self._startup(config)

        print("Opening Viewing Frame...")

        # General Application Settings
        self.root = parent
        self.root.resizable(width=False, height=False)
        self.root.bind("<Escape>", self.close)
        self.root.title("pywfom")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.set_icon()


        # Create Each Side of the Window
        self.right_side = tk.Frame(self.root)
        self.left_side = tk.Frame(self.root)
        self.right_side.pack(side="right")
        self.left_side.pack(side="left")

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

        # Create Canvas and subcanvas to add buttons
        self.canvas = tk.Canvas(    self.left_side,
                                    cursor="cross",
                                    width=1000,
                                    height=800)
        _sub_canvas = tk.Frame( self.canvas, cursor="arrow")
        self.canvas.create_window(200,10, window=_sub_canvas)
        self.canvas.pack()

        # Add widgets to subcanvas
        self.main_lbl = tk.Label(   _sub_canvas,
                                    font=("Helvetica", 14))
        self.main_lbl.pack(side='left')

        tk.Button(  _sub_canvas,
                    text='Edit',
                    command=self.edit_camera).pack(side='left')

        tk.Button(  _sub_canvas,
                    text='Remove',
                    command=self.delete_camera).pack(side='left')

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

        tk.Button()

    def _create_arduino_widgets(self):

        # Create frame
        arduino_frm = tk.Frame(self.right_side)
        arduino_frm.pack()

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

        # TODO: Add refresh button

        ttk.Combobox(
            port_frm,
            values=list_ports()
        ).pack(side='left')

        tk.Button(
            port_frm,
            text="Connect"
        ).pack(side='left')

        tk.Button(
            port_frm,
            text="Configure",
            command=self._config_arduino
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
            command=self._set_dir
        ).pack(side='left')

    def _create_buttons(self):

        # Create frame for buttons
        btn_frm = tk.Frame(self.right_side)

        # Create buttons
        tk.Button(
            btn_frm,
            text="Close",
            command=self.close
        ).pack(side='left')

        tk.Button(
            btn_frm,
            text="Save",
            command=self._save
        ).pack(side='left')

        tk.Button(
            btn_frm,
            text="Load",
            command=self._load
        ).pack(side='left')

        tk.Button(
            btn_frm,
            text="Acquire",
            command=self.acquire
        ).pack(side='left')

        btn_frm.pack()

    def set_icon(self, name="icon"):
        photo = tk.PhotoImage(
            file = os.path.dirname(imaging.__file__)+"/img/{0}.png".format(name)
        )
        self.root.iconphoto(False, photo)

    def add_thumnail(self, name):
        self.thumbnails.append(tk.Label(self.thumbnails_frame))
        self.thumbnail_labels.append(tk.Label(self.thumbnails_frame, text=name))

    def _update(self):

        self._draw_main_image()

        self._draw_thumnails()

        msg = "Ready" if not self.arduino.ERROR else self.arduino.ERROR
        self.arduino_status.config(text=msg)

        self.dir_name.config(text=self.file.directory)

        self.root.after(1, self._update)

    def _draw_main_image(self):

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
        thumbnail_size = (600/len(self.cameras), 150)

        for i, cam in enumerate(self.cameras):
            img = self.convert_frame(cam.frame, thumbnail_size, False)
            self.thumbnails[i].img = img
            self.thumbnails[i].config(image=img, borderwidth=10, relief="flat", bg="white")
            self.thumbnails[i].bind("<Button-1>",lambda event, idx=i: self.change_main_frame(event, idx))
            self.thumbnail_labels[i].pack()
            self.thumbnails[i].pack()

        self.thumbnails[self.selected_frame].config(borderwidth=10,relief="ridge", bg="green")

    def _set_dir(self):
        self.file.directory = tk.filedialog.askdirectory()

    def _save(self):

        _cameras = []

        for cam in self.cameras:

            _camera_settings = {}

            for setting in imaging.DEFAULT:
                _camera_settings[setting] = cam.get(setting)

            _cameras.append(_camera_settings)


        _config = {
            'file':self.file.__dict__,
            'arduino':self.arduino.__dict__,
            'cameras':_cameras
        }

        fname = filedialog.asksaveasfile(mode="w", parent=self.root, defaultextension=".json")

        if fname is None:
            return
        else:
            json.dump(_config, fname)
            fname.close()

    def _load(self):

        f = filedialog.askopenfile(parent=self.root)

        if not f:
            return

        config = json.load(f)
        f.close()

        self._shutdown()
        self._startup(config)

    def configure(self):
        self.set_icon("configure")
        Config(self, self.root)

    def edit_camera(self, i=None):

        if i:
            self.selected_frame = i

        self.set_icon("configure")
        CameraConfig(self, self.root)

    def delete_camera(self, i=None):

        print('deleting camera {0}'.format(i))

        if i:
            self.selected_frame = i

        self.cameras.pop(self.selected_frame).close()
        self.parent.thumbnails.pop(idx).grid_forget()
        self.parent.thumbnail_labels.pop(idx).grid_forget()
        self.selected_frame = 0

    def _config_arduino(self):
        ArduinoConfig(self, self.root)

    def acquire(self):

        result = tk.messagebox.askyesno("pywfom", message="Start acquistion?")

        if result:
            self.file.write(self.arduino, self.cameras)
        else:
            pass

    def _shutdown(self, event=""):
        print("Closing pywfom...")
        [cam.close() for cam in self.cameras]
        self.arduino.close()
        self.file.close()

    def _startup(self, config):
        # Initiate each component's Class
        self.cameras = [
            imaging.DEVICES[cfg['device']](cfg) for cfg in config["cameras"]
        ]
        self.arduino = Arduino(config["arduino"])
        self.file = Writer(config=config["file"])

    def close(self):
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

        x, y, he, wi = "offsetX", "offsetY", "height", "width"

        cam.set({
            he:int(h/self.scale),
            wi:int(w/self.scale),
            x:int(getattr(cam,x)+self.ix/self.scale),
            y:int(getattr(cam,y)+self.iy/self.scale)
        })

        self.ix, self.iy, self.x, self.y = 0,0,0,0

    def draw_rectangle(self, event):
        self.x, self.y = event.x, event.y

    def reset_aoi(self, event):
        cam = self.cameras[self.selected_frame]
        cam.set({
            "height":cam.get_max("height"),
            "width":cam.get_max("width"),
            "offsetX":1,
            "offsetY":1
        })

    def change_main_frame(self, event, idx):
        self.selected_frame = idx

    def convert_frame(self, frame, max_size, main):

        if frame.dtype == "uint16":
            frame = np.sqrt(frame).astype(np.uint8)
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

    # TODO: Edit to have a different screen configuration

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)

        self.parent = parent

        self.focus_force()

        self._create_camera_widgets()
        self._create_arduino_widgets()

    def _create_camera_widgets(self):

        camera_frame = tk.Frame(self)

        tk.Label(
            camera_frame,
            text="Camera Settings:"
        ).grid(row=0, column=0, columnspan=3)

        for i, cam in enumerate(self.parent.cameras):

            tk.Label(
                camera_frame,
                text="{0} ({1})".format(cam.name, cam.device)
            ).grid(row=i+1, column=0)

            tk.Button(
                camera_frame,
                text='Edit',
                command=lambda i=i:self.parent.edit_camera(i)
            ).grid(row=i+1,column=1)

            tk.Button(
                camera_frame,
                text='Remove',
                command=lambda i=i:self.parent.delete_camera(i)
            ).grid(row=i+1,column=2)

        camera_frame.pack()

    def _create_arduino_widgets(self):

        arduino_frame = tk.Frame(self)

        tk.Label(
            arduino_frame,
            text="Arduino Settings: "
        ).grid(row=0, column=0, columnspan=4)


        tk.Label(
            arduino_frame,
            text="Stim"
        ).grid(row=1, column=0)


        """
        for i, stim in enumerate(self.parent.arduino.stim):

            tk.Label(
                arduino_frame,
                text="{0} ({1})".format(stim['name'], stim['type']),
            ).grid(row=i+2, column=1)

            tk.Button(
                arduino_frame,
                text="Edit",
                command=lambda i=i:self.parent.edit_stim(i)
            ).grid(row=i+2, column=2)

            tk.Button(
                arduino_frame,
                text="Remove",
                command=lambda i=i:self.parent.remove_stim(i)
            ).grid(row=i+2, column=3)
        """

        arduino_frame.pack()

    def _create_file_widgets(self):
        file_frame = tk.Frame(self)

    def _edit_stim(self, i):
        # TODO: Populate
        pass

    def _remove_stim(self, i):
        # TODO: Populate
        pass

class CameraConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)

        self.camera = parent.cameras[parent.selected_frame]
        self.root = parent.root
        self.reset = self.camera.__dict__.copy()
        self.parent = parent
        self.parent.set_icon('configure')

        self.title("({0}) Settings".format(self.camera.name))

        self._create_widgets()

    def _create_widgets(self):

        for i, (k, v) in enumerate(self.camera.__dict__.items()):

            if k[0] == '_' or k not in imaging.DEFAULT:
                continue

            bin = tk.Frame(self)

            lbl = tk.Label(bin, text=k.title(), justify='left')


            if k in imaging.OPTIONS:
                entry = ttk.Combobox(
                    bin,
                    width=7,
                    values=imaging.OPTIONS[k],
                    justify='center'
                )
            elif k in ["framerate", 'name']:
                entry = tk.Entry(
                    bin,
                    width=10,
                    justify='center'
                )
            else:
                entry = tk.Spinbox(
                    bin,
                    width=5,
                    justify='center',
                    from_= self.camera.get_min(k),
                    to = self.camera.get_max(k)
                )
                entry.bind('<Button-1>', lambda event, k=k:self._callback(event,k))

            entry.delete(0,'end')
            entry.insert(0, str(v))

            bin.pack()
            lbl.pack(side='left',anchor=tk.W)
            entry.pack(side='left', anchor=tk.E)
            entry.bind('<FocusOut>', lambda event, k=k:self._callback(event,k))

        bin = tk.Frame(self)
        bin.pack(pady=10)
        reset_btn = tk.Button(bin, text='Reset', command=self._reset)
        reset_btn.pack(side='left', padx=10)
        done_btn = tk.Button(bin, text='Done', command=self._close)
        done_btn.pack(side='left')

    def _callback(self, event, setting):

        if setting == 'device' and self.camera.device != event.widget.get():

            _settings = {}
            for setting in imaging.DEFAULT:
                _settings[setting] = self.camera.get(setting)
            _settings['device'] = event.widget.get()

            self.parent.cameras[self.parent.selected_frame].close()
            self.parent.cameras[self.parent.selected_frame] = imaging.DEVICES[event.widget.get()](_settings)

        else:
            self.camera.set(setting, imaging.TYPES[setting](event.widget.get()))

    def _reset(self):
        # TODO: Reset settings in window
        _settings = {}
        for setting in imaging.DEFAULT:
            _settings[setting] = self.reset[setting]
        self.parent.cameras[self.parent.selected_frame].close()
        self.parent.cameras[self.parent.selected_frame] = imaging.DEVICES[_settings['device']](_settings)

    def _close(self):
        self.parent.set_icon('icon')
        self.destroy()

class ArduinoConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)

        self.parent = parent
        self.root = self.parent.root
        self.arduino = parent.arduino
        self.reset = self.arduino.__dict__.copy()
        self.parent.set_icon('configure')
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

        tk.Spinbox(
            strobe_frm,
            from_=0,
            to=40,
            width=2
        ).grid(row=1, column=1)

        tk.Button(
            strobe_frm,
            text='Test'
        ).grid(row=1, column=2)

        for i, led in enumerate(self.arduino.strobing['leds']):

            tk.Label(
                strobe_frm,
                text=led['name']
            ).grid(row=i+2, column=0)

            tk.Spinbox(
                strobe_frm,
                from_=0,
                to=40,
                width=2
            ).grid(row=i+2, column=1)

            tk.Button(
                strobe_frm,
                text='Test'
            ).grid(row=i+2, column=2)

    def _create_stim_widgets(self):

        stim_frm = tk.Frame(self)
        stim_frm.pack()

        tk.Label(
            stim_frm,
            text='Stim Settings:').grid(row=0,column=0,columnspan=4)

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

    def _create_daq_widgets(self):

        daq_frm = tk.Frame(self)
        daq_frm.pack()

        tk.Label(
            daq_frm,
            text='Data Acquisition'
        ).grid(row=0, column=0, columnspan=2)

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

class FileConfig(tk.Toplevel):

    def __init__(self, file, parent=None, master=None):

        super().__init__(master = master)

        self.reset = camera.__dict__.copy()

class LedConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)

        self.resizable(width=False, height=False)
        self.root = parent.root
        self.arduino = parent.parent.arduino
        self.title("LED Configuration")

        self.make_notice()
        self.make_buttons()

    def make_notice(self):
        lbl = tk.Label(
            master=self,
            text="1. Switch your LED drivers to\n'Constant Current (CM)' Mode"
        )
        pic = os.path.dirname(imaging.__file__)+"/img/driverDemo.png"
        img = ImageTk.PhotoImage(Image.open(pic))
        panel = tk.Label(master=self, image=img)
        panel.image = img

        lbl.pack()
        panel.pack()

    def make_buttons(self):
        lbl = tk.Label(
            master=self,
            text="2. Select an LED"
        )
        lbl.pack()
        for i, led in enumerate(self.arduino.strobing['leds']):
            btn = tk.Button(
                master=self,
                text=led['name'],
                command=lambda p=led['pin'] :self.arduino.toggle_led(p),
                height=3,
                width=20
            )
            btn.pack(pady=10)

class StimConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)
        self.resizable(width=False, height=False)
        self.root = parent.root
        self.arduino = parent.arduino
        self.title("Stim Configuration")

        self.make_notice()
        self.make_buttons()

    def make_notice(self):
        lbl = tk.Label(
            master=self,
            text="1. Switch your LED drivers to\n'Constant Current (CM)' Mode"
        )
        pic = os.path.dirname(pywfom.__file__)+"/img/driverDemo.png"
        img = ImageTk.PhotoImage(Image.open(pic))
        panel = tk.Label(master=self, image=img)
        panel.image = img

        lbl.pack()
        panel.pack()

    def make_buttons(self):
        lbl = tk.Label(
            master=self,
            text="2. Select an LED"
        )
        lbl.pack()
        for i, led in enumerate(self.arduino.strobing['leds']):
            btn = tk.Button(
                master=self,
                text=led['name'],
                command=lambda p=led['pin'] :self.arduino.toggle_led(p),
                height=3,
                width=20
            )
            btn.pack(pady=10)

class ComboboxSelectionWindow(tk.Toplevel):

    def __init__(self, parent=None, master=None, setting=None):

        super().__init__(master = master)
        self.root = parent.root
        self.title(setting.title())
        self.resizable(width=False, height=False)
        self.setting = setting
        self.options = {
            "device":[
                "spinnaker",
                "andor",
                "test",
                "webcam"
            ],
            "master":[
                True,
                False
            ],
            "dtype":[
                "uint16",
                "uint8"
            ],
            "port":["COM{0}".format(i) for i in range(10)]
        }
        self._create_widgets()

    def _create_widgets(self):

        self.combo = ttk.Combobox(master=self, values=self.options[self.setting])
        self.combo.current(1)
        self.combo.pack()
        self.done_btn = tk.Button(master=self, text="Done", command=self.callback)
        self.done_btn.pack()

    def callback(self):
        self.value = self.combo.get()
        self.destroy()
