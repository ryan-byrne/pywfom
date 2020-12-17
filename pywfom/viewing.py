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

        # Create+pack Arduino Widgets
        tk.Label(
            arduino_frm,
            text="Arduino: "
        ).pack(side='left')

        self.arduino_status = tk.Label(arduino_frm)
        self.arduino_status.pack(side='left')

        tk.Button(
            arduino_frm,
            text="Configure",
            command=self._config_arduino
        ).pack(side='left')

        arduino_frm.pack()

    def _create_file_widgets(self):

        # Create File Directory
        file_frame = tk.Frame(self.right_side)

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
        )

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
        pass

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

class Config(tk.Toplevel):

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

class SettingsConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)
        # TODO: Catch arduino error better
        self.ignore = [
            "_pointers",
            "settings",
            "methods",
            "system",
            "active",
            "camera",
            "frame",
            "default",
            "ser",
            "writing"
        ]

        # Get parent window, config settings, and types
        self.parent = parent
        self.cameras = parent.parent.cameras
        self.arduino = parent.parent.arduino
        self.file = parent.parent.file
        self.resizable(width=False, height=False)
        self.root = parent.root

        # Store initial settings in case of reset
        self.init_cameras = [cam.__dict__.copy() for cam in self.cameras]
        self.init_arduino = self.arduino.__dict__.copy()

        # Create Treeview
        self.tree = ttk.Treeview(self, columns=["A", "B"])
        self.tree.column("#0", width=90, anchor='center')
        self.tree.column("A", width=70, anchor='center')
        self.tree.column("B", width=50, anchor='center')
        self.tree.pack()
        self.title("Settings")

        # Add ability to edit
        self.tree.bind("<Double-Button-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.right_click)
        self.tree.bind("<Button-2>", self.right_click)

        self.populate_tree()

        self.create_buttons()

    def populate_tree(self):

        # Clear previous settings from the tree
        self.tree.delete(*self.tree.get_children())

        # Create tree branch for file info
        file = self.tree.insert("", 0, text="File")
        for i, values in enumerate(self.file.__dict__.items()):
            self.tree.insert(file,i, values=values)

        # Create Cameras tab
        cameras = self.tree.insert("", 1, text="Cameras")
        # Create tabs for each camera
        for i, cam in enumerate(self.cameras):
            cam_settings = {}
            parent = self.tree.insert(cameras, i, text=cam.name.title())
            # Add setting for each attribute
            for j, attr in enumerate(cam.__dict__.keys()):
                if attr in self.ignore:
                    continue
                else:
                    self.tree.insert(parent, j, values=(attr, getattr(cam, attr)))

        # Create Arduino Tab
        arduino = self.tree.insert("", 2, text="Arduino")
        # Go through each Arduino attribute
        for i, attr in enumerate(self.arduino.__dict__.keys()):
            if attr in self.ignore:
                continue
            elif attr == "ERROR":
                if not self.arduino.ERROR:
                    continue
                else:
                    self.tree.insert(arduino, i, text=self.arduino.ERROR)
            parent = self.tree.insert(arduino, i, text=attr)
            settings = getattr(self.arduino, attr)
            if attr == "port":
                self.tree.insert(parent, i, values=("Port", self.arduino.port))
            elif attr == "strobing":
                self.tree.insert(parent, 0, values=("Trigger", settings['trigger']))
                for j, led in enumerate(settings['leds']):
                    self.tree.insert(parent, j+1, values=(led["name"], led["pin"]))
            elif attr == "stim":
                for k, stim in enumerate(settings):
                    stim_parent = self.tree.insert(parent, k, text=stim["name"])
                    for m, setting in enumerate(stim):
                        self.tree.insert(stim_parent, m, values=(setting, stim[setting]))

    def create_buttons(self):
        reset = tk.Button(self, text="Reset", command=self.reset)
        save = tk.Button(self, text="Save", command=self.save)
        load = tk.Button(self, text="Load", command=self.load)
        cancel = tk.Button(self, text="Done", command=self.close)

        for i, btn in enumerate([cancel, reset, save, load]):
            btn.pack(side='right',pady=10, padx=10)

    def leds(self):
        LedConfig(self, self.root)

    def close(self):
        self.destroy()

    def reset(self):
        [self.cameras[i].set(settings) for i, settings in enumerate(self.init_cameras)]
        self.arduino.set(self.init_arduino)
        self.populate_tree()

    def on_double_click(self, event):

        item = self.tree.selection()[0]
        if not self.tree.parent(item) or self.tree.item(item)["text"] != "":
            return
        else:
            parent = self.tree.parent(item)
            self.edit_setting(item, parent)

    def right_click(self, event):

        # TODO: Focus on right clicked row

        item = self.tree.identify_row(event.y)
        parent = self.tree.parent(item)
        menu = tk.Menu(self.root, tearoff=0)

        if self.tree.item(item)['text'] in ["Arduino", "File"]:
            return
        elif "Cameras" == self.tree.item(parent)['text']:
            menu.add_command(label="Add Camera", command=lambda:self.add_setting(item, parent))
            menu.add_command(label="Delete Camera", command=lambda:self.delete_setting(item, parent))
        elif "Cameras" == self.tree.item(item)['text']:
            menu.add_command(label="Add Camera", command=lambda:self.add_setting(item, parent))
        elif "Stim" == self.tree.item(parent)['text']:
            menu.add_command(label="Add Stim", command=lambda:self.add_setting(item, parent))
            menu.add_command(label="Delete Stim", command=lambda:self.delete_setting(item, parent))
        elif "Stim" == self.tree.item(item)['text']:
            menu.add_command(label="Add Stim", command=lambda:self.add_setting(item, parent))
        elif "Strobing" == self.tree.item(parent)['text'] and "Trigger" != self.tree.item(item)['values'][0]:
            menu.add_command(label="Add LED", command=lambda:self.add_setting(item, parent))
            menu.add_command(label="Delete LED", command=lambda:self.delete_setting(item, parent))
        elif "Strobing" == self.tree.item(item)['text']:
            menu.add_command(label="Add LED", command=lambda:self.add_setting(item, parent))
        else:
            menu.add_command(label="Edit", command=lambda:self.edit_setting(item, parent))

        menu.tk_popup(event.x_root, event.y_root)

    def edit_setting(self, item_iid, parent_iid):

        parent = self.tree.item(parent_iid)['text']
        category = self.tree.item(self.tree.parent(parent_iid))['text']
        setting = self.tree.item(item_iid)['values'][0].lower()

        idx = self.tree.get_children(self.tree.parent(parent_iid)).index(parent_iid)

        new_value = None

        if setting in ["device", "master", "dtype", "port"]:
            combo = ComboboxSelectionWindow(self, self.root, setting)
            self.root.wait_window(combo)
            new_value = combo.value

        elif setting == "directory":
            new_value = tk.filedialog.askdirectory()

        elif setting in ["user", "mouse", "name"]:
            new_value = simpledialog.askstring(
                parent=self,
                title="Setting {0}:".format(setting),
                prompt=setting
            )
        elif setting in ["Height", "index", "Width", "OffsetX", "OffsetY", "runs", "pin", "trigger"]:
            new_value = simpledialog.askinteger(
                parent=self,
                title="Setting {0}:".format(setting),
                prompt=setting
            )
        elif setting in ["AcquisitionFrameRate", "pre_stim", "stim", "post_stim", "run_length"]:
            new_value = simpledialog.askfloat(
                parent=self,
                title="Setting {0}:".format(setting),
                prompt=setting
            )
        elif parent == "Strobing" and setting != "trigger":
            name = simpledialog.askstring(
                parent=self,
                title="Strobe LED",
                prompt="Choose a name for the LED:"
            )
            pin = simpledialog.askinteger(
                parent=self,
                title="Strobe LED",
                prompt="Choose a Pin on the Arduino:"
            )
            new_value = {"name":name,"pin":pin}


        if new_value == None:
            return

        for i, child_iid in enumerate(self.tree.get_children(parent_iid)):
            if child_iid == item_iid:
                self.tree.delete(item_iid)
                item = self.tree.insert(parent_iid, i, values=(setting, new_value))
                self.tree.see(item)
                cat = self.tree.item(self.tree.parent(parent_iid))['text'].lower()
                if cat == "arduino":
                    self.arduino.set(setting, new_value)
                else:
                    if setting == "device":
                        # Close current device and open a new one
                        self.cameras[idx].close()
                        self.cameras[idx] = imaging.DEVICES[new_value](self.cameras[idx])
                    else:
                        self.cameras[idx].set(setting, new_value)

    def add_setting(self, item_iid, parent_iid):

        cat = [self.tree.item(parent_iid)['text'], self.tree.item(item_iid)['text']]

        if "Cameras" in cat:
            self.cameras.append(imaging.Camera())
            self.parent.add_thumnail("default")
        elif "Stim" in cat:
            stims = getattr(self.arduino, 'stim')
            self.arduino.stim.append({
                "name":"default",
                "pre_stim":4.0,
                "stim":7.0,
                "post_stim":8.0
            })
        elif "Strobing" in cat:
            name = simpledialog.askstring(
                parent=self,
                title="Strobe LED",
                prompt="Choose a name for the LED:"
            )
            pin = simpledialog.askinteger(
                parent=self,
                title="Strobe LED",
                prompt="Choose a Pin on the Arduino:"
            )
            strobing = getattr(self.arduino, 'strobing')
            strobing["leds"].append({
                "name":name,
                "pin":pin
            })

        self.parent._pack_widgets()
        self.populate_tree()

    def delete_setting(self, item_iid, parent_iid):

        if len(self.tree.get_children(self.tree.parent(item_iid))) == 1:
            return

        idx = self.tree.get_children(self.tree.parent(item_iid)).index(item_iid)
        cat = [self.tree.item(parent_iid)['text'], self.tree.item(item_iid)['text']]

        if "Cameras" in cat:
            self.cameras.pop(idx).close()
            self.parent.thumbnails.pop(idx).grid_forget()
            self.parent.thumbnail_labels.pop(idx).grid_forget()
            self.parent.selected_frame = 0
        elif "Stim" in cat:
            stims = getattr(self.arduino, 'stim')
            stims.pop(idx)
        elif "Strobing" in cat:
            strobing = getattr(self.arduino, 'strobing')
            strobing['leds'].pop(idx-1)

        self.populate_tree()

class CameraConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)

        self.camera = parent.cameras[parent.selected_frame]
        self.root = parent.root
        self.reset = self.camera.__dict__.copy()
        self.parent = parent

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
        self.camera.set(setting, imaging.TYPES[setting](event.widget.get()))

    def _reset(self):
        self.camera.set(self.reset)

    def _close(self):
        self.parent.set_icon('icon')
        self.destroy()

class ArduinoConfig(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)

        self.reset = camera.__dict__.copy()
        self.arduino = parent.arduino

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
