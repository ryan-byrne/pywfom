import time, subprocess, os, datetime, json, sys, string
from pyfiglet import Figlet
from datetime import datetime
from arduino import Arduino
from solis import Solis
from gui import Gui
from led import Led

def create_camera_file_folder(mouse):
    date = str(datetime.now())[:10]

    cpu_name = os.environ['COMPUTERNAME']
    # Check to make sure the proper computer is being used
    print("This computer's name is "+cpu_name)
    if cpu_name == "DESKTOP-TFJIITU":
        path = "S:/WFOM/data/"
    else:
        path = "C:/WFOM/data/"
        check = input("It looks like you are not using a designated work station. Would you like to continue? (y/n) ")
        if check == "y":
            pass
        else:
            exit()
    with open("JSPLASSH/archive.json", "r+") as f:
        archive = json.load(f)
        d = archive["mice"][mouse]["last_trial"]+1
        archive["mice"][mouse]["last_trial"] = d
        f.seek(0)
        json.dump(archive, f, indent=4)
        f.truncate()
    f.close()
    if not os.path.isdir(path + mouse + "_" + str(d)):
        path = path + mouse + "_" + str(d)
    else:
        path = path + mouse + "_" + str(d+1)
    print("Making directory: "+path)
    os.mkdir(path)
    print("Making directory: "+path+"/CCD")
    os.mkdir(path+"/CCD")
    print("Making directory: "+path+"/auxillary")
    os.mkdir(path+"/auxillary")
    print("Making directory: "+path+"/webcam")
    os.mkdir(path+"/webcam")
    return path

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

def deploy_settings(path):
    command = "move JSPLASSH/settings.json "+path
    os.system(command)

if __name__ == '__main__':
    banner("WFOM", "isometric1")
    banner("WELCOME TO SPLASSH", "contessa")
    uni, mouse = Gui.open_GUI()
    path = create_camera_file_folder(mouse)
    Gui.solis_GUI()
    update_status()
    deploy_settings(path)
