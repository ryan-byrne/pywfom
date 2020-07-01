import serial, os

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self):
        self.port = os.environ.get("WFOM_ARDUINO")
        if not self.port:
            raise EnvironmentError("WFOM_ARDUINO variable is not set in the PATH.\n\
            Follow the tutorial below to add it:\n\
            ")
        print("Attempting to Connect to Arduino at Serial Port: "+self.port)
        try:
            self.ser = serial.Serial(
                port=self.port,\
                baudrate=115200,\
                parity=serial.PARITY_NONE,\
                stopbits=serial.STOPBITS_ONE,\
                bytesize=serial.EIGHTBITS,\
                    timeout=0)
            time.sleep(1)
            print("Successfully connected to Arduino at {0}".format(self.port))
        except serial.SerialException as e:
            msg = "Unable to connect to the Arduino at {0}. Ensure that it is plugged in.".format(self.port)
            raise ConnectionError(msg)

    def _disable(self):
        print("Disabling Python <-> Arduino Communication")
        self.ser.close()

    def _enable(self):
        print("Enabling Python <-> Arduino Communication")
        self.ser.open()
        time.sleep(1)

    def _set_strobe_order(self):
        order = ""
        for led in self.strobe_order:
            order += led[0]
        print("Setting the Strobe order on the Arduino to: "+order)
        self.ser.write(order.encode())

    def _clear(self):
        self.ser.write("0000".encode())

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
