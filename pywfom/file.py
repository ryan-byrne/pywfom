import os, h5py, queue, threading, time
import numpy as np

class Writer2(object):
    """docstring for File."""

    def __init__(self, mouse_name, img_names, base_dir="C:\\openwfom\\data", spool_len=10):
        self.spool_len = spool_len
        self._make_directories(mouse_name, base_dir)
        self._img_names = img_names
        self._current_spool = []
        self._spool_count = 0
        self._done = False
        self._spool_queue = queue.Queue()
        threading.Thread(target=self._write_to_disk).start()

    def write(self, images):

        # Add the image to the current spool
        self._current_spool.append(images)

        # Check the length of the spool
        if len(self._current_spool) == self.spool_len:
            # If the spool is full, dump to file, clear memory
            self._spool_queue.put(self._current_spool)
            self._current_spool = []
        else:
            # Otherwise, return None
            return

    def _write_to_disk(self):

        while not self._done:
            spool = self._spool_queue.get()
            self._write_spool(spool)

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
             Don't do that!".format(self.path))
        print("Files to be saved to: {0}".format(self.path))

    def _write_spool(self, spool):

        self._spool_count += 1

        path_to_spool = self.path+"\\spool{0}".format(self._spool_count)
        t0 = time.time()
        with h5py.File(path_to_spool, "w") as h5:
            for i, frame in enumerate(spool):
                #print(i)
                grp = h5.create_group("frame{0}".format(i))
                for j, cam in enumerate(frame):
                    #print(j)
                    grp.create_dataset( self._img_names[j],
                                        data=cam)
        h5.close()
        time.sleep(0.01)

    def close(self):
        self._done = True

class Writer(object):
    """docstring for Writer."""

    def __init__(self, config):
        pass


class Reader(object):
    """docstring for Reader."""

    def __init__(self, run_dir):
        self.run_dir = run_dir

    def load(self):
        pass

    def view(self):
        for spool in os.listdir(self.run_dir):
            with h5py.File("{0}\\{1}".format(self.run_dir, spool), 'r') as h5:
                pass
