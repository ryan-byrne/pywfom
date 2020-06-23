from openwfom.imaging import andor, flir
import cv2, time, argparse, sys
import numpy as np

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

def get_settings():
    settings = {
        "CycleMode":"Continuous",
        "AOIBinning":"8x8",
        "AOIHeight":2000,
        "AOIWidth":2000
    }
    return settings

def init_andor(args):

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
    flirs = flir.Flir()

    for i, cam in enumerate(flirs.cameras):
        flirs.init(i)

    print(flirs.cameras)

def draw_aoi(event, x, y, flags, param):

    global drawing, ix, iy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x,y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cv2.rectangle(frame, )
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        w = x - ix
        h = y - iy
        print("{0}x{1} Rectangle, with origin at {2},{3}".format(h, w, ix, iy))

# python -c "from wfom import run;run()"
drawing = False
ix, iy = -1, -1

args = _get_args()

#flirs = init_flirs()

zyla = init_andor(args)

while zyla.active:
    zyla_img = zyla.get_next_image()
    cv2.imshow(zyla.serial_number, zyla_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        zyla.active = False
        break
cv2.destroyAllWindows()
zyla.shutdown()
