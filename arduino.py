import serial, time, json, os, subprocess, sys
from serial import Serial

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, port):
        print("Attempting to Connect to Arduino at Serial Port: "+port)
        self.port = port
        try:
            self.ser = serial.Serial(
                port=self.port,\
                baudrate=115200,\
                parity=serial.PARITY_NONE,\
                stopbits=serial.STOPBITS_ONE,\
                bytesize=serial.EIGHTBITS,\
                    timeout=0)
            time.sleep(3)
            self.connected = 1
            print("Successfully connected to Arduino at {0}".format(port))
        except serial.SerialException as e:
            print("Can not enable the Arduino")
            print(e.strerror)
            sys.exit()

    def disable(self):
        print("Enabling Python Arduino Communication")
        self.ser.close()

    def enable(self):
        print("Enabling Python-Arduino Communication")
        self.ser.open()
        time.sleep(3)

    def set_strobe_order(self):
        order = ""
        for led in self.strobe_order:
            order += led[0]
        print("Setting the Strobe order on the Arduino to: "+order)
        self.ser.write(order.encode())

    def clear(self):
        self.ser.write("0000".encode())

    def strobe_gui(self):
        print("Waiting to Recieve Strobe Settings from GUI...")
        self.disable()
        os.chdir("JSPLASSH")
        subprocess.call(["java", "-jar", "strobe.jar"])
        os.chdir("..")
        self.enable()
        with open("JSPLASSH/settings.json") as f:
            settings = json.load(f)
            print(settings)
            self.strobe_order = settings["strobe_order"]
        f.close()
        self.set_strobe_order()

    def stim_gui(self):
        print("Waiting to Recieve Stim Settings from GUI...")
        os.chdir("JSPLASSH")
        subprocess.call(["java", "-jar", "stim.jar"])
        os.chdir("..")

    def turn_on_strobing(self):
        self.ser.write("S".encode())

    def turn_off_strobing(self):
        self.ser.write("s".encode())

if __name__ == '__main__':
    arduino = Arduino("COM4")
    arduino.strobe_gui()
