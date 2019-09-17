# -*- coding: utf-8 -*-
from atcore import *
import numpy as np
from PIL import Image
import time

def main() :

    print("Single Scan Example")

    print("Intialising SDK3")
    sdk3 = ATCore() # Initialise SDK3

    print("  Opening camera ")
    hndl = sdk3.open(0);

    print("   Setting up acuisition")
    sdk3.set_enum_string(hndl, "PixelEncoding", "Mono32")


    imageSizeBytes = sdk3.get_int(hndl,"ImageSizeBytes")
    print("    Queuing Buffer (size",imageSizeBytes,")")
    height = sdk3.get_int(hndl, "AOIHeight")
    width = sdk3.get_int(hndl, "AOIWidth")
    print("    Image Dimensions: {0}x{1}".format(height, width))


    print("Cooling the Sensor")
    sdk3.set_bool(hndl, "SensorCooling", True)
    while sdk3.get_enum_string(hndl, "TemperatureStatus") != "Stabilised":
        print(u"Current Sensor Temperature: {0}{1}".format(round(sdk3.get_float(hndl, "SensorTemperature"),2), u"\u2103"), end="\r")
    
    buf = np.empty((imageSizeBytes,), dtype='B')
    sdk3.queue_buffer(hndl,buf.ctypes.data,imageSizeBytes)

    print("    Acquiring Frame")
    sdk3.command(hndl,"AcquisitionStart")
    (returnedBuf, returnedSize) = sdk3.wait_buffer(hndl);

    sdk3.command(hndl,"AcquisitionStop")

    img = Image.frombytes(data=buf, size=(height, width), mode="I")
    img.show()

main()
