import numpy as np
import cv2

class Webcam():

    def __init__(self):
        print("Attempting to Connect to the Webcam")
        self.connected = 1
