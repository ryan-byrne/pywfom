import subprocess

class Gui():

    def __init__(self):
        pass

    def open_GUI():
        print("Waiting for UNI")
        subprocess.call(["java", "-jar", "open.jar"])
        with open("uni.txt") as f:
            uni = f.read()
        f.close()
        return uni

    def solis_GUI():
        print("Opening the Java GUI", end='\r')
        subprocess.Popen(["java", "-jar","solis.jar"])
        pass
