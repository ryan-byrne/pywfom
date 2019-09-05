from gui import Gui
import os

if __name__ == '__main__':
    Gui.open_GUI()
    while not os.path.isfile("JSPLASSH/settings.json"):
        print("Waiting for settings file", end="\r")
