from gui import Gui
from andor import Andor
from arduino import Arduino
import json, time, os, subprocess

def info():
    os.chdir("JSPLASSH")
    if os.path.isfile("settings.json"):
        os.remove("settings.json")
    subprocess.call(["java", "-jar", "info.jar"])
    os.chdir("..")

def make_directories():
    date = str(datetime.now())[:10]

    with open("JSPLASSH/settings.json") as f:
        settings = json.load(f)
        mouse = settings["info"]["mouse"]
    f.close()

    with open("JSPLASSH/archive.json", "r+") as f:
        archive = json.load(f)
        d = archive["mice"][mouse]["last_trial"]+1
        archive["mice"][mouse]["last_trial"] = d
        f.seek(0)
        json.dump(archive, f, indent=4)
        f.truncate()
    f.close()

    if not os.path.isdir(path + mouse + "_" + str(d)):
        path = path + mouse + "_" + str(d)
    else:
        path = path + mouse + "_" + str(d+1)

    print("Making directory: "+path)
    os.mkdir(path)
    print("Making directory: "+path+"/CCD")
    os.mkdir(path+"/CCD")
    print("Making directory: "+path+"/webcam")
    os.mkdir(path+"/webcam")

    print("Moving JSPLASSH/settings.json to "+path+"/settings.json")
    src = "JSPLASSH/settings.json"
    dst = path+"/settings.json"
    shutil.move(src, dst)
    return path

if __name__ == '__main__':
    andor = Andor(0)
    gui = Gui()
    arduino = Arduino("COM4")
    info()
    andor.camera_gui()
    arduino.strobe_gui()
