from openwfom.imaging import andor
import cv2

def test_andor():

    zyla = andor.Camera(0)

    #zyla.capture('frames', 10)

    zyla.shutdown()

if __name__ == '__main__':
    test_andor()
