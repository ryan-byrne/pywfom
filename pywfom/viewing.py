import numpy as np
import time, cv2, json
import tkinter as tk
from pywfom import imaging
from tkinter import ttk, simpledialog, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

class Frame(tk.Frame):

    def __init__(self, parent, win_name, cameras=[], arduino={}, file={}):

        self.cameras = cameras
        self.arduino = arduino
        self.file = file

        self.root = parent
        self.root.bind("<Escape>", self.close)
        self.root.title(win_name)
        self.rect = None
        self.drawing = False
        self.selected_frame, self.ix, self.iy, self.x, self.y = 0,0,0,0,0
        self.offset_x, self.offset_y, self.scale = 0,0,0

        # Create widgets
        self.create_widgets()
        # Establish event bindings
        self.set_bindings()
        # Set each item on the grid
        self.set_grid()
        # Begin Updating the images
        self.update()

    def set_bindings(self):
        self.canvas.bind("<Button-1>", self.set_aoi_start)
        self.canvas.bind("<ButtonRelease-1>", self.set_aoi_end)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<Button-3>", self.reset_aoi)
        self.canvas.bind("<Button-2>", self.reset_aoi)

    def create_widgets(self):
        # Create image panels
        self.canvas = tk.Canvas(self.root, cursor="cross", width=1000, height=800)
        self.main_label = tk.Label(self.root)
        # Create Arduino Status
        self.arduino_status = tk.Label(self.root, text="Arduino Status")
        self.arduino_color = tk.Button(self.root, height=1, width=1)
        # Create File Directory
        self.dir_label = tk.Label(self.root, text="Save to:")
        self.dir_name = tk.Label(self.root)
        self.dir_button = tk.Button(self.root, text="Browse", command=self.set_dir)
        # Create buttons
        self.settings_btn = tk.Button(      self.root,
                                        text="Configure",
                                        command=self.view_settings)
        self.close_btn = tk.Button(     self.root,
                                        text="Quit",
                                        command=self.close)
        self.acquire_btn = tk.Button(  self.root,
                                        text="Acquire",
                                        command=self.acquire)
        # Create empty thumnails
        self.thumbnails, self.thumbnail_labels = [], []
        # Create thumbnails
        for cam in self.cameras:
            self.add_thumnail(cam.name)

    def add_thumnail(self, name):
        self.thumbnails.append(tk.Label(self.root))
        self.thumbnail_labels.append(tk.Label(self.root, text=name))

    def set_grid(self):
        self.main_label.grid(column=0, row=0,sticky=tk.NW)
        self.canvas.grid(row=0,column=0, rowspan=2*len(self.cameras)+2)
        for i, cam in enumerate(self.cameras):
            self.thumbnails[i].grid(row=i, column=1, padx=5, pady=10, columnspan=3)
            self.thumbnail_labels[i].grid(row=i, column=1, sticky=tk.NW)
        self.arduino_status.grid(row=len(self.cameras), column=1, columnspan=2, sticky="e")
        self.arduino_color.grid(row=len(self.cameras), column=3, sticky="w")
        self.dir_label.grid(row=len(self.cameras)+1, column=1)
        self.dir_name.grid(row=len(self.cameras)+1, column=2)
        self.dir_button.grid(row=len(self.cameras)+1, column=3)
        for i, btn in enumerate([self.close_btn, self.settings_btn, self.acquire_btn]):
            btn.grid(row=len(self.cameras)+2,column=i+1, padx=5, pady=10)

    def update(self):

        # TODO: Improve framerate of gui
        #   * when error message
        #   * when large frame (to be expected)

        t = time.time()

        cam = self.cameras[self.selected_frame]
        
        # Create main viewing frame
        image = self.convert_frame(cam.frame, (800,1000), True)

        h, w, fr = cam.Height, cam.Width, cam.AcquisitionFrameRate

        if self.cameras[self.selected_frame].error_msg == "":
            self.main_label.config(
                text="{0} ({1}): {2}x{3}, {4} fps".format(
                    cam.name,
                    cam.device.title(),
                    h,
                    w,
                    fr
                )
            )
        else:
            self.main_label.config(text="ERROR")

        self.canvas.config(height=image.height(), width=image.width())
        self.canvas.create_image(0,0,image=image,anchor="nw")
        self.canvas.delete(self.rect)
        if 0 in [self.ix, self.iy, self.x, self.y]:
            pass
        else:
            self.rect = self.canvas.create_rectangle(self.ix, self.iy, self.x, self.y, fill="", outline="green")
        self.canvas.image = image

        thumbnail_size = (600/len(self.cameras), 150)

        # Create subframes
        for i, cam in enumerate(self.cameras):
            img = self.convert_frame(cam.frame, thumbnail_size, False)
            self.thumbnails[i].img = img
            self.thumbnails[i].config(image=img, borderwidth=10, relief="flat", bg="white")
            self.thumbnails[i].bind("<Button-1>",lambda event, idx=i: self.change_main_frame(event, idx))
            (txt, color) = ("Ready", "Green") if cam.error_msg == "" else (cam.error_msg, "Red")

        color = "green" if self.arduino.error_msg == "" else "red"
        self.arduino_color.config(background=color)
        self.dir_name.config(text=self.file.directory)

        self.thumbnails[self.selected_frame].config(borderwidth=10,relief="ridge", bg="green")

        self.root.after(1, self.update)

    def set_dir(self):
        self.file.directory = tk.filedialog.askdirectory()

    def view_settings(self):
        SettingsWindow(self, self.root)

    def acquire(self):
        self.file.write(self.arduino, self.cameras)

    def close(self, event=""):
        self.root.destroy()

    def set_aoi_start(self, event):

        self.ix = event.x
        self.iy = event.y

    def set_aoi_end(self, event):

        # TODO: Fix issue with usb webcams

        self.x = event.x
        self.y = event.y
        w = self.x-self.ix
        h = self.y-self.iy

        if 0 in [w,h] or self.cameras[self.selected_frame].error_msg != "":
            self.ix, self.iy, self.x, self.y = 0,0,0,0
            return

        if w < 0:
            self.ix = self.x
            w = abs(w)
        if h < 0:
            self.iy = self.y
            h = abs(h)

        cam = self.cameras[self.selected_frame]

        if cam.device in ["spinnaker", "test", "webcam"]:
            x, y, he, wi = "OffsetX", "OffsetY", "Height", "Width"
        elif cam.device == "andor":
            # TODO: Account or Andor AOI being from the Top
            x, y, he, wi = "AOILeft", "AOITop", "AOIHeight", "AOIWidth"

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
            "Height":cam.get_max("Height"),
            "Width":cam.get_max("Width"),
            "OffsetX":0,
            "OffsetY":0
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


class SettingsWindow(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)

        # Get parent window, config settings, and types
        self.parent = parent
        self.root = parent.root
        self.cameras = parent.cameras
        self.arduino = parent.arduino
        self.file = parent.file

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
                if attr in ["types", "error_msg", "active", "_camera", "frame"]:
                    continue
                else:
                    self.tree.insert(parent, j, values=(attr, getattr(cam, attr)))

        # Create Arduino Tab
        arduino = self.tree.insert("", 2, text="Arduino")
        # Go through each Arduino attribute
        for i, attr in enumerate(self.arduino.__dict__.keys()):
            if attr in ["error_msg", "types", "ser"]:
                continue
            parent = self.tree.insert(arduino, i, text=attr.title())
            if attr == "port":
                self.tree.insert(parent, i, values=("Port", self.arduino.port))
                continue
            settings = self.arduino.strobing if attr == "strobing" else getattr(self.arduino, attr).keys()
            for j, setting in enumerate(settings):
                if attr == "strobing":
                    values = ("", setting.upper())
                else:
                    values = (setting.replace("_", " ").title(), getattr(self.arduino, attr)[setting])
                self.tree.insert(parent, j, values=values)

    def create_buttons(self):
        reset = tk.Button(self, text="Reset", command=self.reset)
        save = tk.Button(self, text="Save", command=self.save)
        load = tk.Button(self, text="Load", command=self.load)
        cancel = tk.Button(self, text="Done", command=self.close)

        for i, btn in enumerate([cancel, reset, save, load]):
            btn.pack(side='right',pady=10, padx=10)

    def close(self):
        self.destroy()

    def save(self):

        f = filedialog.asksaveasfile(mode="w", parent=self, defaultextension=".json")
        if f is None:
            return
        json.dump(self.settings, f)
        f.close()

    def load(self):

        fname = filedialog.askopenfilename(parent=self)
        if fname == "":
            return
        with open(fname) as f:
            settings = json.load(f)
        f.close()

        self.settings = settings
        self.populate_tree()

    def reset(self):
        [self.cameras[i].set(settings) for i, settings in enumerate(self.init_cameras)]
        self.arduino.set(self.init_arduino)
        self.populate_tree()

    def on_double_click(self, event):

        # TODO: add dropdowns where possible

        item = self.tree.selection()[0]
        if not self.tree.parent(item) or self.tree.item(item)["text"] != "":
            return
        else:
            parent = self.tree.parent(item)
            self.edit_setting(item, parent)

    def right_click(self, event):

        item = self.tree.identify_row(event.y)
        self.tree.selection_set(item)
        parent = self.tree.parent(item)
        if self.tree.item(item)['text'] in ["Arduino", "File"]:
            return
        elif self.tree.item(item)['text'] == "Cameras":
            add = tk.NORMAL
            edit = tk.DISABLED
            delete = tk.DISABLED
        elif self.tree.item(parent)['text'] == "Cameras":
            add = tk.NORMAL
            edit = tk.DISABLED
            delete = tk.NORMAL
        elif self.tree.item(parent)['text'] in ["Stim", "Port", "Run", "Strobe"]:
            add = tk.DISABLED
            edit = tk.NORMAL
            delete = tk.DISABLED
        else:
            add = tk.DISABLED
            edit = tk.NORMAL
            delete = tk.DISABLED
        menu = tk.Menu(self.root)
        menu.add_command(label="Add", command=lambda:self.add_setting(item, parent), state=add)
        menu.add_command(label="Edit", command=lambda:self.edit_setting(item, parent), state=edit)
        menu.add_command(label="Delete", command=lambda:self.delete_setting(item), state=delete)
        menu.tk_popup(event.x_root, event.y_root)

    def add_setting(self, item_iid, parent_iid):

        if "Cameras" in [self.tree.item(parent_iid)['text'], self.tree.item(item_iid)['text']]:
            self.cameras.append(imaging.Camera())
            self.parent.add_thumnail("default")
            self.parent.set_grid()
            self.populate_tree()
            return

        parent = self.tree.item(parent_iid)['text']
        category = self.tree.item(self.tree.parent(parent_iid))['text']
        param = simpledialog.askstring(parent=self, title="Adding Setting:", prompt="Setting")
        if not param:
            return
        if param not in self.config[category].types.keys():
            messagebox.showerror("Adding Setting", "{0} is not a valid setting for: {1}".format(param, parent))
        if parent == "strobing":
            self.tree.insert(parent_iid, len(self.tree.get_children(parent_iid)), values=("", param))
            strobe_order = []
            for led in self.tree.get_children(parent_iid):
                strobe_order.append(self.tree.item(led)['values'][1])
            self.settings['arduino']['strobing'] = strobe_order
            return

        value = simpledialog.askstring(parent=self, title="Setting: {0}".format(param), prompt=param)
        self.tree.insert(parent_iid, len(self.tree.get_children(parent_iid)), values=(param, value))
        idx = self.tree.get_children(self.tree.parent(parent_iid)).index(parent_iid)
        if category == "arduino":
            self.settings['arduino'][parent][param] = value
        else:
            self.settings['cameras'][idx][param] = value

    def edit_setting(self, item_iid, parent_iid):
        parent = self.tree.item(parent_iid)['text']
        category = self.tree.item(self.tree.parent(parent_iid))['text']
        v = self.tree.item(item_iid)['values']
        new_value = simpledialog.askstring(parent=self, title="Setting {0}:".format(v[0]), prompt=v[0])
        if not new_value:
            return
        try:
            new_value = int(new_value)
        except ValueError:
            try:
                new_value = float(new_value)
            except ValueError:
                new_value = new_value

        idx = self.tree.get_children(self.tree.parent(parent_iid)).index(parent_iid)
        for i, child_iid in enumerate(self.tree.get_children(parent_iid)):
            if child_iid == item_iid:
                self.tree.delete(item_iid)
                self.tree.insert(parent_iid, i, values=(v[0], new_value))
                cat = self.tree.item(self.tree.parent(parent_iid))['text'].lower()
                if parent.lower() == "strobing":
                    self.arduino.set("strobing", new_value)
                    return
                elif parent.lower() == "port":
                    self.arduino.set("port", new_value)
                    return
                if cat == "arduino":
                    self.arduino.set(cat, new_value)
                else:
                    self.cameras[idx].set(v[0], new_value)

    def delete_setting(self, item_id):

        if len(self.tree.get_children(self.tree.parent(item_id))) == 1:
            return
        idx = self.tree.get_children(self.tree.parent(item_id)).index(item_id)

        self.cameras.pop(idx).close()
        self.parent.thumbnails.pop(idx).grid_forget()
        self.parent.thumbnail_labels.pop(idx).grid_forget()
        self.parent.selected_frame = 0
        self.populate_tree()

class ComboPopup(object):
    """docstring for ComboPopup."""

    def __init__(self, arg):
        super(ComboPopup, self).__init__()
        self.arg = arg
