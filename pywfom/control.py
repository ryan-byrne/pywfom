import serial, os, time, sys, glob

def list_ports():

    if sys.platform.startswith('win'):
        _ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux'):
        _ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        _ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    _available = []

    for port in _ports:

        if "Bluetooth" in port:
            continue

        try:
            s = serial.Serial(port=port)
            _available.append(port)
            s.close()
        except serial.SerialException:
            continue

    return _available

class ArduinoError(Exception):
    pass

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, settings):

        # TODO: set stim settings
        # TODO:  test stim
        # # TODO: add encoder monitoring

        self.ERROR = None

        self.set(settings)

    def set(self, setting, value=None):

        self.stop()

        if type(setting).__name__ == "dict":
            for k, v in setting.items():
                self._set(k,v)
        else:
            self._set(setting,value)

        self.start()

    def _set(self, setting, value):

        if setting == "ERROR":
            return

        elif setting == "port":
            self.connect_to_arduino(value)

        elif setting != "port" and not self.ser:
            # TODO: Remove this when things are working
            #return
            pass

        elif setting == "strobing":
            self._set_leds(value['leds'])
            self._set_trigger(value['trigger'])

        elif setting == "stim":
            # TODO: Set stim
            for stim in value['stim']:
                # Send command for setting stim pins (i.e. s5s6s)
                pass

        setattr(self, setting, value)

    def _set_leds(self, leds):
        """ Set led pin strobe array (i.e. p6p7p8p) """
        msg = "p"
        for led in leds:
            msg += "{0}p".format(led['pin'])
        self.ser.write(msg.encode())

    def _set_trigger(self, pin):
        """ Send command for setting trigger pin (i.e. t3) """
        self.ser.write("t{0}".format(pin).encode())

    def toggle_led(self, pin):
        """ Turn on a specified LED """
        self.ser.write("T{0}".format(pin).encode())

    def toggle_strobing(self):
        """ Toggles strobing on the connected LEDs"""
        self.ser.write("S".encode())

    def connect_to_arduino(self, port):
        """ Connect to an Arduino at a specified COM Port"""
        try:
            print("Attempting to connect to Arduino at " + port)
            self.ser = serial.Serial(port=port , baudrate=115200)
            time.sleep(2)
            print("Successfully connected to Arduino at {0}".format(port))
            self.port = port
        except serial.serialutil.SerialException as e:
            self.ERROR = "Unable to connect to Arduino at "+port
            print(self.ERROR)
            self.ser = None

    def stop(self):

        try:
            self.ser.write("c".encode())
            time.sleep(0.1)
        except:
            return

    def start(self):
        pass

    def close(self):

        try:
            self.stop()
            self.ser.close()
        except:
            pass
