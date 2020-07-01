from openwfom import file
from openwfom.imaging import gui
import numpy as np
from sys import getsizeof
import time, cv2

spool = file.Spool("test")
frame = gui.Frame('save_test')

zyla = cv2.VideoCapture(0)

while True:

    #t = time.time()
    print(zyla.read())
    """
    imgs = {
        "zyla16":zyla.read()[1],
        "flir1":np.random.randint(0, 255, (1000,1000), dtype='uint8'),
        "flir2":np.random.randint(0, 255, (1000,1000), dtype='uint8'),
    }
    """
