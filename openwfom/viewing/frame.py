import numpy as np
import time, threading, cv2, json
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

class Frame(tk.Frame):

    def __init__(self, parent, win_name, cameras=[], arduino=None):

        self.cameras = cameras
        self.arduino = arduino

        self.root = parent
        self.root.bind("<Escape>", self.close)
        self.root.title(win_name)
        self.rect = None
        self.drawing = False
        self.selected_frame, self.ix, self.iy, self.x, self.y = 0,0,0,0,0
        self.offset_x, self.offset_y, self.scale = 0,0,0

        # Create image panels
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.main_label = tk.Label(self.root)
        self.main_label.grid(column=0, row=0,sticky=tk.NW)
        self.canvas.bind("<Button-1>", self.set_aoi_start)
        self.canvas.bind("<ButtonRelease-1>", self.set_aoi_end)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<Button-3>", self.reset_aoi)
        self.canvas.grid(row=0,column=0, rowspan=2*len(self.cameras)+3)


        # Create subframes for other cameras
        self.sub_frames,self.sub_labels,self.sub_status,self.sub_status_color = [], [], [], []

        for i, cam in enumerate(cameras):
            self.sub_frames.append(tk.Label(self.root))
            self.sub_labels.append(tk.Label(self.root, text=cam.name))
            self.sub_frames[i].grid(row=i, column=1, padx=5, pady=10, columnspan=3)
            self.sub_labels[i].grid(row=i, column=1, sticky=tk.NW)
            self.sub_status.append(tk.Label(self.root))
            self.sub_status[i].grid(row=i+len(self.cameras), column=2, columnspan=2, sticky=tk.NW)


        # Create status labels
        self.arduino_status = tk.Label(self.root, text="Arduino Status")
        self.arduino_color = tk.Button(self.root, height=1, width=1)
        self.arduino_status.grid(row=2*len(self.cameras)+1, column=1, columnspan=2, sticky="e")
        self.arduino_color.grid(row=2*len(self.cameras)+1, column=3, sticky="w")

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

        for i, btn in enumerate([self.close_btn, self.settings_btn, self.acquire_btn]):
            btn.grid(row=2*len(self.cameras)+2,column=i+1, padx=5, pady=10)

        # Begin Updating the images
        self.update()

    def update(self):

        # Create main viewing frame
        image = self.convert_frame(self.cameras[self.selected_frame].frame)
        max_dim = max(image.shape[0], image.shape[1])
        if max_dim < 750:
            self.scale = 750/max_dim
        elif max_dim > 1000:
            self.scale = 1000/max_dim
        else:
            self.scale = 1

        w, h = int(self.scale*image.shape[0]), int(self.scale*image.shape[1])
        img = ImageTk.PhotoImage(image = Image.fromarray(image).resize((h, w)))

        cam = self.cameras[self.selected_frame]

        if cam.type in ["spinnaker", "test"]:
            h, w = cam.Height, cam.Width
        else:
            h, w = cam.AOIHeight, cam.AOIWidth

        if self.cameras[self.selected_frame].error_msg == "":
            self.main_label.config(
                text="{0} ({1}): {2}x{3}".format(
                    cam.name,
                    cam.type.title(),
                    h,
                    w
                )
            )
        else:
            self.main_label.config(text="ERROR")

        self.canvas.config(height=img.height(), width=img.width())
        self.canvas.create_image(0,0,image=img,anchor="nw")
        self.canvas.delete(self.rect)
        if 0 in [self.ix, self.iy, self.x, self.y]:
            pass
        else:
            self.rect = self.canvas.create_rectangle(self.ix, self.iy, self.x, self.y, fill="", outline="green")
        self.canvas.image = img

        # Create subframes
        for i, cam in enumerate(self.cameras):
            image = self.convert_frame(cam.frame)
            img = ImageTk.PhotoImage(image = Image.fromarray(image).resize((250,250)))
            self.sub_frames[i].img = img
            self.sub_frames[i].config(image=img, borderwidth=10, relief="flat", bg="white")
            self.sub_frames[i].bind("<Button-1>",lambda event, idx=i: self.change_main_frame(event, idx))
            (txt, color) = ("Ready", "Green") if cam.error_msg == "" else (cam.error_msg, "Red")

        color = "green" if self.arduino.error_msg == "" else "red"
        self.arduino_color.config(background=color)

        self.sub_frames[self.selected_frame].config(borderwidth=10,relief="ridge", bg="green")

        self.root.after(1, self.update)

    def view_settings(self):
        SettingsWindow(self, self.root)

    def acquire(self):
        print("Acquiring")

    def close(self, event=""):
        self.root.destroy()

    def set_aoi_start(self, event):
        self.ix = event.x
        self.iy = event.y

    def set_aoi_end(self, event):

        self.x = event.x
        self.y = event.y
        w = self.x-self.ix
        h = self.y-self.iy

        if w < 0:
            self.ix = self.x
            w = abs(w)
        if h < 0:
            self.iy = self.y
            h = abs(h)

        cam = self.cameras[self.selected_frame]

        if cam.type == "spinnaker":
            x, y, he, wi = cam.OffsetX, cam.OffsetY, cam.Height, cam.Width
        elif cam.type == "andor":
            x, y, he, wi = cam.AOILeft, cam.AOITop, cam.AOIHeight, cam.AOIWidth

        cam.set({
            he:int(h/self.scale),
            wi:int(w/self.scale),
            x:int(x+self.ix/self.scale),
            y:int(y+self.iy/self.scale)
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

    def convert_frame(self, img):
        if img.dtype == "uint16":
            return np.sqrt(img).astype(np.uint8)
        else:
            return img

class SettingsWindow(tk.Toplevel):

    def __init__(self, parent=None, master=None):

        super().__init__(master = master)

        # Get parent window, config settings, and types
        self.root = parent.root
        self.cameras = parent.cameras
        self.arduino = parent.arduino

        # Create object to store settings
        self.settings = {}

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

        self.populate_tree()

        self.create_buttons()

    def populate_tree(self):

        # Clear previous settings from the tree
        self.tree.delete(*self.tree.get_children())

        # Create Cameras tab
        cameras = self.tree.insert("", 0, text="Cameras")
        # Create tabs for each camera
        for i, cam in enumerate(self.cameras):
            cam_settings = {}
            parent = self.tree.insert(cameras, i, text=cam.name.title())
            # Add setting for each attribute
            for j, attr in enumerate(cam.__dict__.keys()):
                if attr in ["pointers", "error_msg", "active", "paused", "system", "frame"]:
                    continue
                else:
                    self.tree.insert(parent, j, values=(attr, getattr(cam, attr)))

        # Create Arduino Tab
        arduino = self.tree.insert("", 1, text="Arduino")
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
        cancel = tk.Button(self, text="Cancel", command=self.close)
        save = tk.Button(self, text="Save", command=self.save)
        load = tk.Button(self, text="Load", command=self.load)
        apply = tk.Button(self, text="Apply", command=self.apply)

        for i, btn in enumerate([apply, save, load, cancel]):
            btn.pack(side='right',pady=10, padx=10)

    def close(self):
        self.settings = None
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

    def apply(self):

        for i, cam in enumerate(self.cameras):
            cam.set(self.settings['cameras'][i])
            self.cameras[i].settings = self.settings['cameras'][i]

        arduino = self.config["arduino"]
        for i, category in enumerate(self.settings["arduino"].keys()):
            if category == 'strobing':
                arduino.set("strobing", self.settings['arduino']['strobing'])
                self.config["arduino"].settings['strobing'] = self.settings["arduino"]['strobing']
            elif category == "port":
                arduino.set("port", self.settings['arduino']['port'])
            else:
                for setting in self.settings['arduino'][category].keys():
                    arduino.set(setting, self.settings['arduino'][category][setting])
                    self.config["arduino"].settings[category] = self.settings["arduino"][category]

    def on_double_click(self, event):

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
        if self.tree.item(parent)['text'] == "":
            return
        elif self.tree.item(parent)['text'] in ['Strobing', "Stim", "Run"]:
            add = tk.DISABLED
        else:
            add = tk.NORMAL
        menu = tk.Menu(self.root)
        menu.add_command(label="Add", command=lambda:self.add_setting(item, parent), state=add)
        menu.add_command(label="Edit", command=lambda:self.edit_setting(item, parent))
        menu.add_command(label="Delete", command=lambda:self.delete_setting(item, parent), state=add)
        menu.tk_popup(event.x_root, event.y_root)

    def add_setting(self, item_iid, parent_iid):
        parent = self.tree.item(parent_iid)['text']
        category = self.tree.item(self.tree.parent(parent_iid))['text']
        param = simpledialog.askstring(parent=self, title="Adding Setting:", prompt="Setting")
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
                    self.cameras[idx].set(cat, new_value)

    def delete_setting(self, item, parent):
        self.tree.delete(item)
