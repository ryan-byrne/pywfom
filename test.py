from andor import Andor
from PIL import Image
import cv2

if __name__ == '__main__':
    camera = Andor()
    frames = camera.acquire(10, 0.0068)
    print(len(frames))
