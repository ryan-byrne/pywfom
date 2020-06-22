from openwfom.imaging import andor
import cv2, time, argparse
import numpy as np

def _get_args():

    """
    This function simply checks for arguments when the script is called
    and stores them in their corresponding variable.

    Example:

    wfom 0

    """

    parser = argparse.ArgumentParser()

    parser.add_argument('cam_num', type=int, nargs='?',default=0)
    parser.add_argument('val', nargs='?', default=0)
    parser.add_argument('num_bfrs', type=int, nargs='?',default=10)
    parser.add_argument('-f', '--frames', dest='frames', action='store_true', default=False)
    parser.add_argument('-t', '--test', dest='test', action='store_true', default=False)
    args = parser.parse_args()


    return vars(args)

def get_settings():
    settings = {
        "CycleMode":"Continuous",
        "PixelEncoding":"Mono16",
        "AOIBinning":"8x8",
        "AOIHeight":2000,
        "AOIWidth":2000,
    }
    return settings

def run():

    args = _get_args()

    zyla = andor.Camera(args['cam_num'], args['test'], args['num_bfrs'])

    settings = get_settings()

    zyla.set(settings)

    if args['frames']:
        mode = 'frames'
    else:
        mode = 'time'

    zyla.capture(mode, 10)

    while zyla.active or not zyla.frames.empty():
        frame = zyla.frames.get()
        time.sleep(0.001)

    zyla.shutdown()

# python -c "from wfom import run;run()"
if __name__ == '__main__':
    run()
