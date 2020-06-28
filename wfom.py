from openwfom.imaging import andor, spinnaker, arduino, gui
from openwfom import file
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

    a = vars(args)

    val = float('inf') if a['val'] == 0 else a['val']

    return a['test'], a['num_bfrs'], a['verbose'], val

t, b, v, val = _get_args()

if not v:
    sys.stdout = open(os.devnull, 'w')

zyla = andor.Capture(0, t, b)
flirs = spinnaker.Capture(t)
frame = gui.Frame("OpenWFOM")

t0 = time.time()

while (time.time() - t0) < val:

    imgs = {
        "Zyla":zyla.frame,
        "Flir1":flirs.frames[0],
        "Flir2":flirs.frames[1],
    }

    if not frame.view(imgs):
        break

    time.sleep(1/50)

settings = zyla.get(["AOIHeight","AOIWidth","AOIStride","ImageSizeBytes"])

print(settings)

frame.close()
flirs.shutdown()
zyla.shutdown()
