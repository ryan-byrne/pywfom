import os, h5py, queue, threading, time
import numpy as np

class Writer(object):

    def __init__(self, config):

        for k, v in config.items():
            self._set(k,v)

    def _make_run_directory(self, i):

        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        mouse_dir = os.path.join(self.directory, self.mouse)

        if not os.path.exists(mouse_dir):
            os.mkdir(mouse_dir)

        runs = len(os.listdir(mouse_dir))

        run_dir = os.path.join(self.directory, mouse_dir, "run"+str(i+runs))

        os.mkdir(run_dir)

        return run_dir

    def set(self, param, value=None):
        if type(param).__name__ == "dict":
            for k,v in param.items():
                self._set(k,v)
        else:
            self._set(param,value)

    def _set(self, param, val):
        setattr(self, param, val)

    def write(self, arduino, camera):
        threading.Thread(target=self._write, args=(arduino, camera,)).start()

    def _write(self, arduino, cameras):

        self.writing = True

        for i, cam in enumerate(cameras):
            if cam.master:
                master = i

        num_frms = 0

        print("Acquiring Frames")

        for i in range(arduino.run["number_of_runs"]):
            path = self._make_run_directory(i)
            t = time.time()
            while num_frms < arduino.run["run_length"]:
                pass

        self.writing = False

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
