import argparse
from openwfom import wfom

def _get_args():

    """
    This function simply checks for arguments when the script is called
    and stores them in their corresponding variable.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-q", "--quiet",
                    action="store_true", dest="quiet", default=False,
                    help="Don't print status messages to stdout")

    parser.add_argument("-y", "--auto-yes",
                    action="store_true", dest="auto_yes", default=False,
                    help="Automatically accept errors and continue")

    parser.add_argument("-v", "--verbose",
                    action="store_true", dest="verbose", default=False,
                    help="Prints each message and records to a log file")

    args = parser.parse_args()


    return vars(args)

def run():
    args = _get_args()
    wfom.run(**args)

def test():
    args = _get_args()
    wfom.test(**args)

if __name__ == '__main__':
    test()
