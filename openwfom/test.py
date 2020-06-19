from imaging import flir, andor
import time, cv2

if __name__ == '__main__':
    zyla = andor.Camera(0)
    settings = {
        "PixelEncoding":"Mono16",
        "TiggerMode":"Software",
        "FastAOIFrameRateEnable":True,
        "AOIHeight":500,
        "AOIWidth":500,
        "CycleMode":"Continuous",
        "ExposureTime":0.001
    }

    zyla.set(settings)

    zyla.capture('frames', 1000)

    print(zyla.get("FrameRate"))

    while zyla.active:
        cv2.imshow(zyla.serial_number, zyla.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
          break

    zyla.shutdown()
