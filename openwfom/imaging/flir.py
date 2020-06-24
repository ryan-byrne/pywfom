import numpy as np
import queue, threading

try:
    import PySpin
except ModuleNotFoundError:
    print("\nPySpin is not installed")
    print("\nFollow the directions here to install it:")
    print("\nhttps://github.com/ryan-byrne/openwfom/wiki/Camera-Setup/#installing-the-spinnaker-sdk\n")
    raise

class FlirError(Exception):
    pass

class Flir():
    """docstring for Flir."""

    def __init__(self, verbose=False):

        print("\nInitializing FLIR Cameras...")

        self._verbose = verbose

        self.system = PySpin.System.GetInstance()
        self.cameras = self.system.GetCameras()
        self.active = False

        if 0 in [self.cameras.GetSize()]:
            self.close()
            raise FlirError("There are no FLIR Cameras attached")
        else:
            print("There are {0} FLIR Camera(s) attached\n".format(self.cameras.GetSize()))

    def read(self, timeout=1000):

        imgs = []

        for i, cam in enumerate(self.cameras):

            t0 = time.time()
            image_result = cam.GetNextImage(timeout)
            print(time.time()-t0)

            if image_result.IsIncomplete():
                print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
                img = None
            else:
                w = image_result.GetWidth()
                h = image_result.GetHeight()
                data = image_result.GetData()
                img = np.reshape(data, (h,w))

            image_result.Release()

            imgs.append(img)

        return imgs

    def _update_frames(self, id):

        print("Reading frames from Flir {0}".format(id))

    def start(self):

        if self._verbose:
            print("Starting to Acquire Frames from FLIR Cameras...")

        for i, cam in enumerate(self.cameras):
            self.frames.append(queue.Queue(maxsize=100))

        self.active = True

        for i, cam in enumerate(self.cameras):
            cam.Init()
            cam.BeginAcquisition()
            threading.Thread(target=self._update_frames, args=(i,)).start()

    def close(self):

        if self._verbose:
            print("Closing FLIR Cameras...")

        self.active = False

        for cam in self.cameras:
            cam.EndAcquisition()
            cam.DeInit()

        self.cameras.Clear()
        self.system.ReleaseInstance()
