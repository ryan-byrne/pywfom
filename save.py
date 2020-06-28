from openwfom import file
from openwfom.imaging import gui
import numpy as np
from sys import getsizeof
import time

file = file.Save()
frame = gui.Frame('save_test')

while True:

    imgs = {
        "zyla16":np.random.randint(0, 62000, (2000,2400), dtype='uint16'),
        "flir1":np.random.randint(0, 255, (2000,2400), dtype='uint8'),
        "flir2":np.random.randint(0, 255, (2000,2400), dtype='uint8'),
    }

    if not frame.view(imgs):
        break

    time.sleep(1/50)
