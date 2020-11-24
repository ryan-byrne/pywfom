import serial, os, time

class ArduinoError(Exception):
    pass

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, config=None):

        self.port = config['port']
        self.connect_to_arduino()

        for k, v in config.items():
            self.set(k, v)

        self.types = {
            "number_of_runs":int,
            "run_length":float,
            "pre_stim":float,
            "stim":float,
            "post_stim":float,
            "port":str,
            "strobing":list
        }

        self.error_msg = ""

    def set(self, param, value=None):
        if type(param).__name__ == "dict":
            for k, v in param.items():
                self._set(k,v)
        else:
            self._set(param,value)

    def toggle_led(self, pin):
        print("Toggling LED at Pin "+str(pin))

    def _set(self, param, value):

        if param == "port":
            # Restart arduino if port changes
            if self.port != value:
                self.ser.close()
                self.connect_to_arduino()



    def _clear(self):
        self.ser.write("0000".encode())
        self.strobe_order = []

    def _turn_on_strobing(self, strobe_order):
        print("Strobing the LEDs with the order: {0}".format(strobe_order))

        ord = ""

        for color in strobe_order:
            ord += color[0]

        # Send a 1-4 digit color code to Arduino i.e. RGBL
        self.ser.write(ord.encode())
        time.sleep(1)
        self.ser.write("S".encode())

    def _turn_off_strobing(self):
        print("Turning off the LED strobing...")
        self.ser.write("s".encode())

    def connect_to_arduino(self):
        try:
            print("Attempting to connect to Arduino at " + self.port)
            self.ser = serial.Serial(
                port=self.port,\
                baudrate=115200,\
                parity=serial.PARITY_NONE,\
                stopbits=serial.STOPBITS_ONE,\
                bytesize=serial.EIGHTBITS,\
                    timeout=0)
            time.sleep(1)
            self.error_msg = ""
            print("Successfully connected to Arduino at {0}".format(self.port))
        except serial.serialutil.SerialException:
            self.error_msg = "Unable to connect to Arduino at "+self.port
            self.ser = None
            print(self.error_msg)

    def shutdown(self):
        self._turn_off_strobing()
        self._clear()
        self._disable()
