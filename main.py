import time, subprocess, os, datetime, json, sys, string
from colorama import Fore, Style
from gui import Gui

gui = Gui()

os.system("cls")
gui.banner("WFOM", "isometric1")
gui.banner("WELCOME TO THE WFOM DASHBOARD", "contessa")

from arduino import Arduino
from andor import Andor
from webcam import Webcam


if __name__ == '__main__':
    gui.open_gui()
    arduino = Arduino("COM4")
    camera = Andor()
    webcam = Webcam()
    hardware = [arduino, camera, webcam]
    for hw in hardware:
        name = hw.__class__.__name__
        if hw.connected == 0:
            print(Fore.RED + "Unable to Connect to {0}\n".format(name))
            print(Fore.RED + "Ensure {0} is Powered On, and no other programs are using it\n".format(name))
            print(Style.RESET_ALL)
            gui.exit()
    print("Successsfully connected to Hardware")
    while not os.path.isfile("JSPLASSH/settings.json"):
        print("Waiting for UNI and Mouse ID...", end='\r')
    print("settings.json successfully created")
    print("Temporarily disabling Python Arduino Communication")
    arduino.disable()
    settings = gui.camera_gui()
    print("Reconnecting to the Arduino")
    arduino.enable()
    camera.deploy_settings(settings)
