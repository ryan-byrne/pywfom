from openwfom.imaging import andor
import cv2

def test_andor():
    zyla = andor.Camera(0, True)
    settings = {
        "PixelEncoding":"Mono16"
    }
    zyla.set("PixelEncoding","Mono16")
    zyla.capture('time', 10)
    while zyla.active:
        cv2.imshow(zyla.serial_number, zyla.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    zyla.shutdown()

if __name__ == '__main__':
    test_andor()
