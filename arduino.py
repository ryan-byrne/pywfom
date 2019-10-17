import serial, time, json
from gui import Gui

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, port):
        print("Attempting to Connect to Arduino at Serial Port: "+port)
        self.port = port
        self.map = ["Blue", "Green", "Lime", "Red"]
        try:
            self.arduino = serial.Serial(
                port=port,\
                baudrate=115200,\
                parity=serial.PARITY_NONE,\
                stopbits=serial.STOPBITS_ONE,\
                bytesize=serial.EIGHTBITS,\
                    timeout=0)
            self.connected = 1
        except serial.SerialException as e:
            print("Error connecting to Arduino")
            print(e.strerror)
            self.connected = 0

    def disable(self):
        self.arduino.close()

    def enable(self):
        try:
            self.arduino = serial.Serial(
                port=self.port,\
                baudrate=115200,\
                parity=serial.PARITY_NONE,\
                stopbits=serial.STOPBITS_ONE,\
                bytesize=serial.EIGHTBITS,\
                    timeout=0)
            self.connected = 1
        except serial.SerialException as e:
            print("Error connecting to Arduino")
            print(e.strerror)
            self.connected = 0

    def set_strobe_order(self, strobe_order):
        order = ""
        for led in strobe_order:
            order += led[0]
        print("Setting the Strobe order on the Arduino to: "+order)
        self.arduino.write(order.encode())
