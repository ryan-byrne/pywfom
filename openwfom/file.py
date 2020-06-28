import os, h5py

class Save(object):
    """docstring for File."""

    def __init__(self, path_to_dir=""):
        # Set Path to Files
        if path_to_dir == "":
            self.path = "C:\\wfom_data"
        else:
            self.path = path_to_dir

        self.save_to = "{0}\\test{1}".format(self.path, len(os.listdir(self.path)))

    def save(self, imgs):
        with h5py.File(self.save_to, 'w') as h5:
            pass

class Load(object):
    """docstring for File."""

    def __init__(self, path_to_dir=""):
        if os.path.exists(path_to_dir):
            pass
        # Set path to files
        self.path = path_to_dir
