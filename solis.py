import psutil

class Solis():

    def __init__(self):
        pass

    def check_for_SOLIS():
        if "AndorSolis.exe" not in (p.name() for p in psutil.process_iter()):
            print(" "*100, end="\r")
            print("SOLIS is Not Running!", end='\r')
            return 0
        else:
            return 1
