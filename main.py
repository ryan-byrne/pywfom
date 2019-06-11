import time, subprocess
from multiprocessing import Process, Queue
from arduino import Arduino
from solis import Solis
from gui import Gui
from led import Led

def create_camera_file_folder():
    print("Finding specified user directory")

def update_status():
    ready = False
    while not ready:
        status = []
        # ------------------ARDUINO---------------------
        status.append(Arduino.check_arduino())
        # ------------------LED---------------------
        status.append(Led.check_led())
        # ------------------SOLIS---------------------
        status.append(Solis.check_for_SOLIS())
        with open("JSPLASSH/status.txt", "w+") as f:
            for s in status:
                f.write(str(s)+"\n")
        f.close()
        if 0 in status:
            pass
        else:
            ready = True
        time.sleep(1)

if __name__ == '__main__':
    Gui.open_GUI()
    update_status()
