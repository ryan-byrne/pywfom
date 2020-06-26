from openwfom.imaging import andor, flir, gui
from openwfom import arduino
import time, argparse, sys

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
    msg = "Duration (in sec), or # of frames of capture."
    parser.add_argument('val', nargs='?', type=int, default=0, help=msg)
    msg = "# of Camera Buffers to be used. (Default=10)"
    parser.add_argument('num_bfrs', type=int, nargs='?',default=10, help=msg)
    msg = "Sets capture to 'frames' mode."
    parser.add_argument('-f', '--frames', dest='frames', action='store_true', default=False, help=msg)
    msg = "Required if running with AndorSDK3's 'SimCam'"
    parser.add_argument('-t', '--test', dest='test', action='store_true', default=False, help=msg)
    msg = "Print additional text while running OpenWFOM."
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help=msg)
    args = parser.parse_args()

    return vars(args)

args = _get_args()

winname = "OpenWFOM"

t = args['test']
b = args['num_bfrs']
v = args['verbose']
val = float('inf') if args['val'] == 0 else args['val']

zyla = andor.Camera(0, t, b, v)
flirs = flir.Camera(v)
gui = gui.Frame("OpenWFOM")

t0 = time.time()

while (time.time() - t0) < val:

    if not gui.view(zyla.frame, flirs.frames):
        break

gui.close()
flirs.close()
zyla.shutdown()
