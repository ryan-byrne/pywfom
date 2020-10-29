import time, argparse, sys, os, json
import numpy as np
import tkinter as tk

def _get_args():

    """
    This function simply checks for arguments when the script is

    and stores them in their corresponding variable.

    Example:

    wfom 0

    """

    parser = argparse.ArgumentParser(description="Command line tool for the OpenWFOM library.")

    msg = "Run a diagnostic test of your OpenWFOM installation."
    parser.add_argument('-t', '--test', dest='test', action='store_true', default=False, help=msg)

    msg = "Print additional text while running OpenWFOM."
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help=msg)

    msg = "Option to run OpenWFOM with Solis' built-in User Interface."
    parser.add_argument('-s', '--solis', dest='solis', action='store_true', default=False, help=msg)

    msg = "Use previously saved configuration (.json) file"
    parser.add_argument(    '-c',
                            '--config',
                            dest='config',
                            type=str,
                            nargs='?',
                            default="",
                            help=msg
                            )
    args = vars(parser.parse_args())

    return args

def run_solis():

    from openwfom.viewing import gui
    from openwfom.control.arduino import Arduino

    solis = gui.Solis()
    arduino = Arduino()
    flirs = spinnaker.Capture(1)

def run_headless():

    from openwfom.control.arduino import Arduino
    from openwfom.imaging import andor, spinnaker
    from openwfom.viewing import gui
    from openwfom import file

    # Open a preview frame
    frame = gui.Frame("OpenWFOM")

    # Initialise each OpenWFOM component
    arduino = Arduino()
    flirs = spinnaker.Capture(1)
    zyla = andor.Capture(0)

    # Loop while each component is active
    while True:

        images = {
            "Flir1":flirs.frames[0],
            "Zyla":zyla.frame
        }

        print(images)

        if not frame.view(images) or not arduino.active:
            break


    arduino.shutdown()
    zyla.shutdown()
    flirs.shutdown()
    frame.close()

def main(config=None):

    from openwfom.imaging.test import TestCamera
    from openwfom.viewing.frame import Frame
    from openwfom.control.arduino import Arduino
    from openwfom.imaging import andor, spinnaker

    if not config:
        config={
            "arduino":Arduino(),
            "cameras":[
                andor.Camera(),
                spinnaker.Camera()
            ]
        }

    root = tk.Tk()
    frame = Frame(root, "OpenWFOM", config)
    frame.root.mainloop()

    for cam in config["cameras"]:
        cam.close()

def test():
    pass

if __name__ == '__main__':

    # Get command line options
    args = _get_args()

    # Block prints if not verbose
    if not args['verbose']:
        sys.stdout = open(os.devnull, 'w')

    # Load
    if args["config"] != "":
        with open(args['config']) as f:
            config = json.load(f)
        f.close()
        main(config)
    else:
        main()
