import subprocess, json

class Gui():

    def __init__(self):
        pass

    def open_GUI():
        print("Waiting for UNI and Mouse Name")
        subprocess.call(["java", "-jar", "open.jar"])
        with open("JSPLASSH/settings.json") as f:
            settings = json.load(f)
            uni = settings["uni"]
            mouse = settings["mouse"]
        f.close()
        return uni, mouse

    def solis_GUI():
        print("Opening the Java GUI", end='\r')
        subprocess.Popen(["java", "-jar","solis.jar"])
        pass
