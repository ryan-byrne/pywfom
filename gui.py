import subprocess

class Gui():

    def __init__(self):
        pass

    def open_GUI():
        subprocess.call(["java", "-jar", "open.jar"])

    def solis_GUI():
        print("Opening the Java GUI", end='\r')
        subprocess.Popen(["java", "-jar","solis.jar"])
        pass
