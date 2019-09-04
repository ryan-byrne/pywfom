import time, subprocess, os, datetime, json, sys, string
from colorama import Fore, Style
from gui import Gui

os.system("cls")
Gui.banner("WFOM", "isometric1")
Gui.banner("WELCOME TO THE WFOM DASHBOARD", "contessa")

ERASE_LINE = '\x1b[2K'

from arduino import Arduino
from andor import Andor
from webcam import Webcam


if __name__ == '__main__':
    uni, mouse = Gui.open_GUI()
    hardware = [Arduino("COM4"), Andor(), Webcam()]
    for hw in hardware:
        name = hw.__class__.__name__
        if hw.connected == 0:
            print(Fore.RED + "Unable to Connect to {0}\n".format(name))
            print(Fore.RED + "Ensure {0} is Powered On, and no other programs are using it\n".format(name))
            Gui.restart()
            print(Style.RESET_ALL)
            os.execl(sys.executable, sys.executable, *sys.argv)
    print("Successsfully connected to Hardware")
