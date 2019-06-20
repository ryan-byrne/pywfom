import serial
from time import sleep

class Arduino():
    """docstring for Arduino."""

    def __init__(self):
        pass


if __name__ == '__main__':
    ser = serial.Serial(
        port='COM4',\
        baudrate=9600,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=0)
    while True:
        print(ser.isOpen())
        sleep(1)
