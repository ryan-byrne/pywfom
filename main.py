import time, subprocess, os, datetime, json, sys, string
from arduino import Arduino
from andor import Andor
from webcam import Webcam
from gui import Gui


if __name__ == '__main__':

    # Welcome Banner
    Gui.banner("WFOM", "isometric1")
    Gui.banner("WELCOME TO SPLASSH", "contessa")

    # Testing hardware connections
    if 0 in [Andor.test_camera(), Arduino.test_arduino(), Webcam.test_webcam()]:
        Gui.exit()

    os.chdir("../..")

    # Initiate the Open Gui
    uni, mouse = Gui.open_GUI()

    try:
        path = Andor.create_camera_file_folder(mouse)
    except FileExistsError as e:
        print(e.with_traceback)
        Gui.exit()
    Gui.camera_GUI()
    sdk3, hndl = Andor.initialise_camera(path)
    #Andor.acquire(sdk3, hndl)
