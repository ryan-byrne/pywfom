import time, subprocess, os, datetime, json, sys, string
from pyfiglet import Figlet
from datetime import datetime
from arduino import Arduino
from solis import Solis
from gui import Gui
from led import Led

def create_camera_file_folder():
    with open("settings.json") as f:
        settings = json.load(f)
    user = settings["uni"]
    date = str(datetime.now())[:10]
    path = "S:/cm_"+user+"_"+date
    runs = string.ascii_uppercase
    try:
        os.mkdir(path)
    except FileNotFoundError:
        print("Oh no! We couldn't make the directory: "+path+" \n\
        Are you using the right computer?")
        exit()
    except FileExistsError:
        try:
            os.mkdir(path+"/CCD/")
        except FileExistsError:
            num_of_runs = len(os.listdir(path+"/CCD/"))
            os.mkdir(path+"/CCD/"+"run"+runs[num_of_runs])
            return path+"/CCD/"+"run"+runs[num_of_runs]
    print("Error establishing path ("+path+") to store data")
    exit()



def exit():
    for i in [9,8,7,6,5,4,3,2,1]:
        print("Exiting in: ", sep=' ', end=': ')
        print(i, sep=' ', end='\r')
        time.sleep(1)
    sys.exit()


def banner(text, font):
    custom_fig = Figlet(font=font, direction='auto', justify='auto', width=80)
    print(custom_fig.renderText(text))

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
        with open("status.txt", "w+") as f:
            for s in status:
                f.write(str(s)+"\n")
        f.close()
        if 0 in status:
            pass
        else:
            ready = True
        time.sleep(1)

if __name__ == '__main__':
    banner("WFOM", "isometric1")
    banner("WELCOME TO SPLASSH", "contessa")
    run_path = create_camera_file_folder()
    Gui.open_GUI()
    Gui.solis_GUI()
    update_status()
