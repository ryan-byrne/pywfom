from andor import Andor
from arduino import Arduino
import json, time, os, subprocess
from datetime import datetime

if __name__ == '__main__':
    andor = Andor()
    arduino = Arduino("COM4")
    andor.info_gui()
    andor.camera_gui()
    arduino.strobe_gui()
    arduino.stim_gui()
    andor.set_parameters(False)
    arduino.turn_on_strobing()
    andor.acquire()
    arduino.turn_off_strobing()
