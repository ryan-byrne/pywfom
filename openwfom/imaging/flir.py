import cv2, threading, time, queue

try:
    import PySpin
except ModuleNotFoundError:
    print("\nPySpin is not installed")
    print("\nFollow the directions here to install it:")
    print("\nhttps://github.com/ryan-byrne/openwfom/wiki/Camera-Setup/_edit#installing-the-spinnaker-sdk\n")
    raise

class FlirError(Exception):
    pass

class Flir():
    """docstring for Flir."""

    def __init__(self, cam_num, verbose=False):

        print("Initializing FLIR Cameras...")

        self.system = PySpin.System.GetInstance()
        self.cameras = self.system.GetCameras()

        if 0 in [self.cameras.GetSize()]:
            self.close()
            raise FlirError("There are no FLIR Cameras attached")
        else:
            self.cam = self.cameras[cam_num]

    def init(self, idx):

        print("Initializing Camera {0}".format(idx))

        self.cameras[idx].Init()

    def close(self):
        self.cameras.Clear()
        self.system.ReleaseInstance()

    def capture(self, id, mode='time', val=0):

        if mode == 'frames':
            threading.Thread(target=self._capture_frames, args=(val,)).start()
        else:
            threading.Thread(target=self._capture_time, args=(val,)).start()


    def _capture_time(self, duration):

        self._start_acquisition()

        t0 = time.time()
        while (time.time()-t0) < duration:
            self.image = cam.GetNextImage(1000)

        self._end_acquisition()

    def _start_acquisition(self, cam):
        cam.BeginAcquisition()

    def _end_acquisition(self, cam):
        self.image.Release()
        cam.EndAcquisition()
        cam.DeInit()
        pass
