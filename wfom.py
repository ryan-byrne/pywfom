import time, argparse, sys, os, cv2
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

    msg = "The index of the camera you would like to connect to."
    parser.add_argument('cam_num', type=int, nargs='?',default=0, help=msg)

    msg = "Run a diagnostic test of your OpenWFOM installation."
    parser.add_argument('-t', '--test', dest='test', action='store_true', default=False, help=msg)

    msg = "Print additional text while running OpenWFOM."
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help=msg)

    msg = "Option to run OpenWFOM with Solis' built-in User Interface."
    parser.add_argument('-s', '--solis', dest='solis', action='store_true', default=False, help=msg)

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

def test():

    from openwfom.imaging.test import TestCamera
    from openwfom.viewing.test import Frame
    from openwfom.control.arduino import Arduino
    from openwfom.imaging import andor, spinnaker

    config = {
        "arduino":Arduino({
            "strobing":[
                "red",
                "green",
                "blue"
            ],
            "stim":{
                "pre_stim":5,
                "stim":15,
                "post_stim":4,
            },
            "run":{
                "number_of_runs":1,
                "running_time":21.00
            }
        }),
        "cameras":[
            spinnaker.Camera(0, "Flir1"),
            andor.Camera(0, "Zyla"),
            TestCamera("Zyla",(240,240),'uint16')
        ]

    }

    root = tk.Tk()
    frame = Frame(root, "OpenWFOM", config)
    frame.root.mainloop()

    for cam in config["cameras"]:
        cam.close()

if __name__ == '__main__':
    # Get command line options
    args = _get_args()
    # Block prints if not verbose
    if not args['verbose']:
        sys.stdout = open(os.devnull, 'w')
    # If test mode is run
    if args['test']:
        test()
    # Run with Solis UI if selected
    elif args['solis']:
        run_solis()
    else:
        run_headless()
