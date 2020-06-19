import cv2
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

    def __init__(self):

        print("Initializing FLIR Cameras...")

        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()

        if 0 in [self.cam_list.GetSize()]:
            self.cam_list.Clear()
            self.system.ReleaseInstance()
            raise FlirError("There are no FLIR Cameras attached")
        else:
            print("There are {0} FLIR Camera(s) attached".format(self.cam_list.GetSize()))

    def close(self):

        self.cam_list.Clear()
        self.system.ReleaseInstance()

    def capture(self, id):

        print("Previewing FLIR Camera {0}".format(id))

        cam = self.cam_list[id]

        cam.Init()
        cam.BeginAcquisition()

        while True:
            image = cam.GetNextImage(1000)

            cv2.imshow("%i" % id, image.GetNDArray())
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        image.Release()
        cv2.destroyAllWindows()

        cam.EndAcquisition()
        cam.DeInit()
