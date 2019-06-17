from serial import Serial
from serial import serialutil

class Arduino():
    """docstring for Arduino."""

    def __init__(self):
        pass

    def check_arduino():
        try:
            arduinoData = Serial("COM6", "9600")
            return 1
        except serialutil.SerialException:
            print("Arduino is not connected...", end='\r')
            return 0
