import time, argparse, sys, os, json, pkgutil
import tkinter as tk
import numpy as np
import cv2
import pywfom

root = tk.Tk()

def _get_args():

    """
    This function simply checks for arguments when the script is

    and stores them in their corresponding variable.

    Example:

    wfom 0

    """

    parser = argparse.ArgumentParser(description="Command line tool for the pywfom library.")

    msg = "Run a diagnostic test of your pywfom installation."
    parser.add_argument('-t', '--test', dest='test', action='store_true', default=False, help=msg)

    msg = "Print additional text while running pywfom."
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help=msg)

    msg = "Option to run pywfom with Solis' built-in User Interface."
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

def _startup():
    # Get command line options
    args = _get_args()

    # Block prints if not verbose
    if not args['verbose']:
        sys.stdout = open(os.devnull, 'w')

    # Load Configuration
    with open(args['config'] if args['config'] else "config.json") as f:
        config = json.load(f)
    f.close()

    return args, config

def _test():
    wfom = pywfom.System()
    wfom.view()


def quickstart():
    wfom = pywfom.System()

def run():

    args = _get_args()

    if not args['verbose']:
        sys.stdout = open(os.devnull, 'w')

    if args['test']:
        _test()
    else:
        frame = viewing.Main(root, config)
        frame.root.mainloop()

def configure():

    args = _get_args()

    if not args['verbose']:
        sys.stdout = open(os.devnull, 'w')

    frame = viewing.Config(root, config)
    frame.root.mainloop()
