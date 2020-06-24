from openwfom.imaging import andor, flir, gui
from openwfom import arduino
import time, argparse, sys, cv2

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

def get_settings():
    settings = {
        "CycleMode":"Continuous",
        "AOIBinning":"8x8",
        "AOIHeight":2000,
        "AOIWidth":2000
    }
    return settings

def init_andor():

    global args

    cam = andor.Camera(args['cam_num'], args['test'], args['num_bfrs'], args['verbose'])

    settings = get_settings()

    cam.set(settings)

    if args['frames']:
        mode = 'frames'
    else:
        mode = 'time'

    cam.capture(mode, args['val'])
    return cam

def init_flirs():

    global args

    flirs = flir.Flir(args['verbose'])

    flirs.start()

    return flirs

winname = "OpenWFOM"

zyla = andor.Camera(0, args['test'], args['num_bfrs'], args['verbose'])

while True:
    cv2.imshow(zyla.serial_number, zyla.frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

zyla.shutdown()
