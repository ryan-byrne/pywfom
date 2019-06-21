import subprocess, json
from pyfiglet import Figlet

class Gui():

    def __init__(self):
        pass

    def open_GUI():

        """

        This method initiates the first SPLASSH GUI, which will specify the
        UNI of the user as well as the name of the mouse for the trial.

        Once the GUI is closed, the settings.json file is updated, and both the
        mouse name and UNI are passed back to the main function, where they will
        be used to create a file path.

        """

        print("Waiting for UNI and Mouse Name from GUI")
        subprocess.call(["java", "-jar", "open.jar"])
        with open("JSPLASSH/settings.json") as f:
            settings = json.load(f)
            uni = settings["uni"]
            mouse = settings["mouse"]
        f.close()
        print("Uni: "+uni)
        print("Mouse: "+mouse)
        return uni, mouse

    def solis_GUI():

        """

        This method opens the GUI which will update the settings.json with the
        specified camera parameters.

        """

        print("Opening the Java GUI")
        subprocess.call(["java", "-jar","solis.jar"])

    def exit():

        """

        This method simply provides an exit script for the main function.

        """

        for i in [9,8,7,6,5,4,3,2,1]:
            print("Exiting in: ", sep=' ', end=': ')
            print(i, sep=' ', end='\r')
            time.sleep(1)
        sys.exit()

    def banner(text, font):

        """

        Cool and completely unnecessary banners.

        """

        custom_fig = Figlet(font=font, direction='auto', justify='auto', width=80)
        print(custom_fig.renderText(text))
