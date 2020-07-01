from openwfom.control.arduino import Arduino
from openwfom import test
import time, argparse, sys, os

def _get_args():

    """
    This function simply checks for arguments when the script is called
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

    settings = gui.Settings()

    settings.set("stim")

def run_headless():

    from openwfom.imaging import andor, spinnaker
    from openwfom.viewing import gui
    from openwfom.file import Spool

    #zyla = andor.Capture(0)
    #arduino = Arduino()
    flirs = spinnaker.Capture()

def run():
    # Get command line options
    args = _get_args()
    # If test mode is run
    if args['test']:
        test.run()
    # Block prints if not verbose
    if not args['verbose']:
        sys.stdout = open(os.devnull, 'w')
    # Run with Solis UI if selected
    if args['solis']:
        run_solis()
    else:
        run_headless()

if __name__ == '__main__':
    run()
