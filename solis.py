import psutil

class Solis():

    def __init__(self):
        pass

    def check_for_SOLIS():
        print("Checking if SOLIS is running")
        if "AndorSolis.exe" not in (p.name() for p in psutil.process_iter()):
            print("SOLIS is not connected!")
            return 0
        else:
            return 1
