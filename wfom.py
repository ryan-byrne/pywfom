import time, subprocess, os, datetime, json, sys, string, pyautogui
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
    # Startup
    # 1. execute set parameters
    # 2. ready to preview? (y/n)
    # 3. begin SOLIS preview
    # 4. physical adjustments
    # 5. Press Enter to begin acquisition
    arduino = Arduino("COM4")
    camera = Andor(0)
    webcam = Webcam()
    gui.info()
    hardware = [arduino, camera, webcam]
    for hw in hardware:
        name = hw.__class__.__name__
        if hw.connected == 0:
            print(Fore.RED + "Unable to Connect to {0}\n".format(name))
            print(Fore.RED + "Ensure {0} is Powered On, and no other programs are using it\n".format(name))
            print(Style.RESET_ALL)
            gui.exit()
    i = 1
    while not os.path.isfile("JSPLASSH/settings.json"):
        spin = ["/", "|", "\\", "-"]
        print("Waiting for UNI and Mouse ID {0}".format(spin[i-1]), end='\r')
        time.sleep(0.5)
        if i > 3:
            i = 1
        else:
            i += 1
    while not gui.deployed:

    arduino.enable()
    camera.set_parameters(settings, path)
    arduino.set_strobe_order(settings["strobe_order"])
    camera.acquire()
