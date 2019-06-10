import time
from arduino import Arduino
from solis import Solis
from gui import Gui
from led import Led

def user_find_experiment_directory():
    print("Finding specified user directory")


if __name__ == '__main__':
    status = []
    # ------------------GUI---------------------
    Gui.open_GUI()
    # ------------------ARDUINO---------------------
    status.append(Arduino.check_arduino())
    # ------------------LED---------------------
    status.append(Led.check_led())
    # ------------------SOLIS---------------------
    status.append(Solis.check_for_SOLIS())
    # ------------------DIRECTORY---------------------
    user_find_experiment_directory()
    print(status)
