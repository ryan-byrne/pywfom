from openwfom.imaging import andor
import cv2, sys

def test_andor():

    zyla = andor.Camera(0, True)

    zyla.capture('time', 3)

    while zyla.active:

        cv2.imshow(zyla.serial_number, zyla.frame.astype('uint8'))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    zyla.shutdown()

if __name__ == '__main__':
    test_andor()
