from gui import Gui
from andor import Andor
import json, time

if __name__ == '__main__':
    andor = Andor(0)
    gui = Gui()
    gui.info()
    gui.camera()
    old_settings = {"camera":{"fake"}}
    while not gui.deployed:
        with open("JSPLASSH/settings.json") as f:
            gui.settings = json.load(f)
        f.close()
        if "camera" not in gui.settings.keys():
            pass
        else:
            for k in gui.settings["camera"].keys():
                if len(old_settings.keys()) == 1 or gui.settings["camera"][k] != old_settings["camera"][k]:
                    print("Sending {0} to SOLIS!".format(k))
                    continue
        old_settings = gui.settings
        time.sleep(1)
    print("Settings deployed")
