import os, h5py, queue, threading, time
import numpy as np

class Spool(object):
    """docstring for File."""

    def __init__(self, mouse_name, base_dir="C:\\wfom_data", spool_len=100):
        self.spool_len = spool_len
        self._make_directories(mouse_name, base_dir)
        self._spools_to_save = queue.Queue()
        self._current_spool = {}
        threading.Thread(target=self._spooling_thread).start()

    def write(self, imgs):
        # Loop through each image and add it to the current spool
        for key in imgs:
            try:
                self._current_spool[key].append(imgs[key])
            except KeyError:
                self._current_spool[key] = [imgs[key]]
        # If the spool has reached its maximum length, queue it to be saved
        if len(self._current_spool[key]) == self.spool_len:
            # Queue the spool to be saved, then clear it
            self._spools_to_save.put(self._current_spool)
            self._current_spool = {}

    def _write_to_disk(self, spool):
        file_name = "{0}\\spool{1}.hdf5".format(self.path, len(os.listdir(self.path)))
        print(file_name)
        with h5py.File(file_name, 'w') as h5:
            for key in spool:
                h5.create_dataset(key, data=spool[key])
        h5.close()

    def _spooling_thread(self):
        self.active = True
        while self.active:
            while not self._spools_to_save.empty():
                spool = self._spools_to_save.get()
                threading.Thread(target=self._write_to_disk, args=(spool,)).start()
            time.sleep(0.001)

    def _make_directories(self, mouse_name, base_dir):
        # Make the base directory if it does not exist
        a = os.mkdir(base_dir) if not os.path.exists(base_dir) else None
        # Make the mouse directory if it does not exist
        mouse_dir = "{0}\\{1}".format(base_dir, mouse_name)
        a = os.mkdir(mouse_dir) if not os.path.exists(mouse_dir) else None
        # Create path for spool files, given number of runs already in folder
        self.path = "{0}\\run{1}".format(mouse_dir, len(os.listdir(mouse_dir)))
        # Make directory
        try:
            os.mkdir(self.path)
        except OSError:
            raise OSError("Folder {0} already exists, because you probably deleted a folder.\n\
             Don't do that!")

    def close(self):
        self.active = False
        print("Closing Spool...")
        while not self._spools_to_save.empty():
            self._write_to_disk(self._spools_to_save.get())
