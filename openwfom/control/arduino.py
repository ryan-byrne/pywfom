import serial, os, time

class ArduinoError(Exception):
    pass

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, config=None):

        for k, v in config.items():
            setattr(self, k, v)

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

        self.connect_to_arduino()

    def _disable(self):
        print("Disabling Python <-> Arduino Communication")
        self.ser.close()

    def _enable(self):
        print("Enabling Python <-> Arduino Communication")
        self.ser.open()
        time.sleep(1)

    def set(self, param, value):

        setattr(self, param, value)

        if param == "port":
            if not self.ser:
                self.port = value
                self.connect_to_arduino()
            else:
                self.ser.close()
                self.connect_to_arduino()

        if not self.ser:
            return

        if param == 'strobing':
            order = ""
            for led in value:
                order += led[0]
            print("Setting the Strobe order on the Arduino to: "+order)
            self.ser.write(order.encode())

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

    def _list_com_ports(self):
        """ Lists serial port names
            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        ports = ['COM%s' % (i + 1) for i in range(256)]
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

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
