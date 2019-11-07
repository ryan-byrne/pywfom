import serial, time, json

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, port):
        print("Attempting to Connect to Arduino at Serial Port: "+port)
        self.port = port
        self.map = ["Blue", "Green", "Lime", "Red"]
        try:
            self.ser = serial.Serial(
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
        print("Enabling Python Arduino Communication")
        self.ser.close()

    def enable(self):
        print("Enabling Python-Arduino Communication")
        try:
            self.ser = serial.Serial(
                port=self.port,\
                baudrate=115200,\
                parity=serial.PARITY_NONE,\
                stopbits=serial.STOPBITS_ONE,\
                bytesize=serial.EIGHTBITS,\
                    timeout=0)
            self.connected = 1
        except serial.SerialException as e:
            print("Can not enable the Arduino")
            print(e.strerror)
            self.connected = 0

    def set_strobe_order(self, strobe_order):
        order = ""
        for led in strobe_order:
            order += led[0]
        print("Setting the Strobe order on the Arduino to: "+order)
        self.ser.write((order+"\n").encode())

    def clear(self):
        self.ser.write("0000".encode())

    def strobe_gui(self):
        os.chdir("JSPLASSH")
        subprocess.call(["java", "-jar", "strobe.jar"])
        os.chdir("..")

    def stim_gui(self):
        os.chdir("JSPLASSH")
        subprocess.call(["java", "-jar", "stim.jar"])
        os.chdir("..")
