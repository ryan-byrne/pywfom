import os, h5py, queue, threading, time
import numpy as np

class Writer(object):

    def __init__(self, config):
        for k, v in config.items():
            self._set(k,v)

    def set(self, param, value=None):
        if type(param).__name__ == "dict":
            for k,v in param.items():
                self._set(k,v)
        else:
            self._set(param,value)

    def _set(self, param, val):
        setattr(self, param, val)
        
    def write(self, arduino, cameras):

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

    def _make_run_directory(self, i):
        path = "{0}{1}//run{2}".format(self.directory, self.mouse, i)
        os.mkdir(path)
        return path

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
