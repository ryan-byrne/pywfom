from serial import Serial
from serial import serialutil

class Arduino():
    """docstring for Arduino."""

    def __init__(self):
        pass

    def check_arduino():
        try:
            arduinoData = Serial("COM4", "9600")
            return 1
        except serialutil.SerialException:
            return 0
