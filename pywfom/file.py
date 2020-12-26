import os, h5py, queue, threading, time, shutil
import numpy as np

class Writer(object):

    def __init__(self, config):

        self.ERROR = None

        for k, v in config.items():
            self._set(k,v)

    def _make_run_directory(self, i):

        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        mouse_dir = os.path.join(self.directory, self.mouse)

        if not os.path.exists(mouse_dir):
            os.mkdir(mouse_dir)

        runs = len(os.listdir(mouse_dir))

        run_dir = os.path.join(self.directory, mouse_dir, "run"+str(runs))

        os.mkdir(run_dir)

        shutil.copy("config.json", run_dir+"/config.json")

        return run_dir, runs

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

    def _write_frame_file(self, fname, frames):
        t = time.time()
        np.savez(fname, frames)

    def _write(self, arduino, cameras):

        self.writing = True

        for i, cam in enumerate(cameras):
            if cam.master:
                master = i

        print("Acquiring {0} Frames per run ({1} Total)".format(run_frms, int(run_frms*num_runs)))

        # TODO: Master triggers the other cameras
        # TODO: Consolidate file writing code

        for i in range(this.number_of_runs):

            path, run = self._make_run_directory(i)
            run_frms = this.run_length*cameras[i].AcquisitionFrameRate
            num_frms = 0

            while num_frms < run_frms:

                frames = {cam.name: cam.frame for cam in cameras}

                fname = "{0}/frame{1}.npz".format(path, num_frms)

                threading.Thread(target=self._write_frame_file, args=(fname, frames,)).start()

                time.sleep(1/cameras[master].AcquisitionFrameRate)

                num_frms+=1

            print("Run {0} Complete".format(run))

        print("Acquisition Complete")

        self.writing = False

    def close(self):
        pass

class Reader(object):
    """docstring for Reader."""

    def __init__(self, run_dir):
        self.run_dir = run_dir

    def load(self):
        pass

    def view(self):
        pass

TYPES = {
    "user":str,
    "mouse":str,
    "directory":str,
    "runs": int,
    "run_length": float
}
