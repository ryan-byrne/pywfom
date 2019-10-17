from arduino import Arduino
from andor import Andor

if __name__ == '__main__':
    arduino = Arduino("COM4")
    camera = Andor()
    settings = {
                    "exposure":0.05,
                    "height":2048,
                    "width":2048,
                    "binning":"1x1",
                    "strobe_order":["Red", "Blue", "Lime", "Green"]
                    }
    arduino.set_strobe_order(settings["strobe_order"])
    camera.save = True
    if camera.connected > 0:
        camera.deploy_settings(settings, "resources/test")
        while True:
            camera.acquire()
