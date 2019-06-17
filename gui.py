import subprocess, json
from pyfiglet import Figlet

class Gui():

    def __init__(self):
        pass

    def open_GUI():
        print("Waiting for UNI and Mouse Name")
        subprocess.call(["java", "-jar", "open.jar"])
        with open("JSPLASSH/settings.json") as f:
            settings = json.load(f)
            uni = settings["uni"]
            mouse = settings["mouse"]
        f.close()
        return uni, mouse

    def solis_GUI():
        print("Opening the Java GUI", end='\r')
        subprocess.call(["java", "-jar","solis.jar"])

    def exit():
        for i in [9,8,7,6,5,4,3,2,1]:
            print("Exiting in: ", sep=' ', end=': ')
            print(i, sep=' ', end='\r')
            time.sleep(1)
        sys.exit()

    def banner(text, font):
        custom_fig = Figlet(font=font, direction='auto', justify='auto', width=80)
        print(custom_fig.renderText(text))
