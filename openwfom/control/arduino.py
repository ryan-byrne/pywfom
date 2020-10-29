import serial, os, time

class ArduinoError(Exception):
    pass

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, settings=None):

        if not settings:
            self.settings = {
                "port":[os.environ.get("WFOM_ARDUINO")],
                "strobing":[],
                "stim":{},
                "run":{
                    "number_of_runs":1,
                    "run_length":5.00
                }
            }
        else:
            self.settings = settings

        self.types = {
            "number_of_runs":int,
            "run_length":float,
            "pre_stim":float,
            "stim":float,
            "post_stim":float,
            "port":list,
            "strobing":list
        }

        self.error_msg = ""


        if not self.settings["port"][0]:
            print("There was an error connecting to the Arduino")
            print("Be sure you've followed the tutorial below:")
            link = "https://github.com/ryan-byrne/openwfom/wiki/Arduino-Setup/"
            print("\n{0}\n".format(link))
            raise ArduinoError()
        print("Attempting to Connect to Arduino at Serial Port: "+self.settings["port"][0])
        try:
            self.connect_to_arduino()
        except serial.SerialException as e:
            self.error_msg = "ERROR: Unable to connect to the Arduino at {0}".format(self.settings["port"][0])
            self.active = False
            raise ArduinoError(msg)

    def _disable(self):
        print("Disabling Python <-> Arduino Communication")
        self.ser.close()

    def _enable(self):
        print("Enabling Python <-> Arduino Communication")
        self.ser.open()
        time.sleep(1)

    def set(self, param, value):

        self.settings[param] = value

        if param == 'strobing':
            order = ""
            for led in value:
                order += led[0]
            print("Setting the Strobe order on the Arduino to: "+order)
            self.ser.write(order.encode())
        elif param == "port":
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

        self.ser = serial.Serial(
            port=self.settings["port"][0],\
            baudrate=115200,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
                timeout=0)
        time.sleep(1)
        self.error_msg = ""
        print("Successfully connected to Arduino at {0}".format(self.settings["port"][0]))
        self.active = True

    def shutdown(self):
        self._turn_off_strobing()
        self._clear()
        self._disable()
