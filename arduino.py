from serial import Serial

class Arduino():
    """docstring for Arduino."""

    def __init__(self):
        pass

    def initialize_arduino(self):
        arduinoData = Serial("COM4", "9600")
        print(arduinoData)
