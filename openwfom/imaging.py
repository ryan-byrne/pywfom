import PySpin, cv2
import matplotlib.pyplot as plt

class Andor():
    """docstring for Andor."""

    def __init__(self):
        pass

class Flir():
    """docstring for Flir."""

    def __init__(self):

        print("Initializing FLIR Cameras...")

        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()

        if 0 in [self.cam_list.GetSize()]:
            print("There are no FLIR Cameras attached")
            self.cam_list.Clear()
            self.system.ReleaseInstance()
            return False
        else:
            print("There are {0} FLIR Camera(s) attached".format(self.cam_list.GetSize()))

    def preview(self):

        print("Previewing FLIR Cameras")

        for enum, cam in enumerate(self.cam_list):

            cam.Init()
            cam.BeginAcquisition()

            while True:
                image = cam.GetNextImage(1000)
                cv2.imshow("%i" % enum, image.GetNDArray())
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            image.Release()
            cv2.destroyAllWindows()

            cam.EndAcquisition()
            cam.DeInit()



    def close(self):
        self.cam_list.Clear()
        self.system.ReleaseInstance()



if __name__ == '__main__':
    andor = Andor()
    flir = Flir()

    flir.preview()

    flir.close()
