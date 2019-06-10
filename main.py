import psutil, time, subprocess
from arduino import Arduino

def check_for_SOLIS():
    print("Checking if SOLIS is running")
    return "AndorSolis.exe" in (p.name() for p in psutil.process_iter())


def open_GUI():
    print("Opening the Java GUI")
    subprocess.call(["java", "-jar","gui.jar"])
    pass

def user_find_experiment_directory():
    print("Finding specified user directory")


if __name__ == '__main__':
    # ------------------GUI---------------------
    open_GUI()
    # ------------------SOLIS---------------------
    if not check_for_SOLIS():
        print("SOLIS is not connected!")
        print("Opening SOLIS")
        subprocess.Popen(["C:\Program Files\Andor SOLIS\AndorSolis.exe"])
        while not ("AndorSolis.exe" in (p.name() for p in psutil.process_iter())):
            print("Waiting for SOLIS to open...")
    else:
        pass
    # ------------------DIRECTORY---------------------
    user_find_experiment_directory()
    # ------------------ARDUINO---------------------
    ard = Arduino()
    ard.initialize_arduino()
