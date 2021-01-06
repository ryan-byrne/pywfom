import serial, os, time, sys, glob
import serial.tools.list_ports

def list_ports():
    """Return a 2-item list of available COM Ports and their devices"""
    return serial.tools.list_ports.comports()

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, port='COM1', **kwargs):

        # TODO: set stim settings
        # TODO:  test stim
        # # TODO: add encoder monitoring
        # TODO: Test data acquisition

        self.ERROR = None

        config = kwargs if 'config' not in kwargs else kwargs['config']

        self.set(config=config)

    def set(self, **kwargs):

        settings = kwargs if 'config' not in kwargs else kwargs['config']

        for k, v in settings.items():

            if k[0] == '_' or k == 'ERROR':
                continue

            if not hasattr(self, k) or v != getattr(self, k):
                self._set(k,v)
            else:
                continue

    def _set(self, setting, value):

        setattr(self, setting, value)

        if setting == "port":
            self._connect(value)

        elif setting != 'port' and not self._ser:
            # Can't change settings to none port
            return

        elif setting == "strobing":
            self._set_leds()
            self._set_trigger()

        elif setting == "stim":

            for stim in value:
                # TODO: Set stim
                # Send command for setting stim pins (i.e. s5s6s)
                pass

        elif setting == 'data_acquisition':
            # TODO: Set DAQ
            pass

    def _set_leds(self, pins=None):
        """ Set led strobe pins, an array of [2,3,4] sends `p2p3p4p` to the Arduino

        :param list pins: List of pins to be considered LED drivers
        """
        msg = "p"
        for led in self.strobing['leds']:
            msg += "{0}p".format(led['pin'])
        self._ser.write(msg.encode())
        time.sleep(0.1)

    def _set_trigger(self, pin=None):
        """ Send command for setting trigger pin (i.e. t3) """
        pin = self.strobing['trigger']
        self._ser.write("t{0}".format(pin).encode())
        time.sleep(0.1)

    def toggle_led(self, pin):
        """ Turn on a specified LED """
        print("Turning on {0}".format(pin))
        self._ser.write("T{0}".format(pin).encode())
        time.sleep(0.1)

    def start_strobing(self):
        """ Turns on strobing on the Arduino"""
        self._ser.write("S".encode())
        time.sleep(0.1)

    def stop_strobing(self):
        """ Turns off strobing on the Arduino"""
        self._ser.write("S".encode())
        time.sleep(0.1)

    def _connect(self, port):
        """ Connect to an Arduino at a specified COM Port"""
        try:
            print("Attempting to connect to Arduino at " + port)
            self._ser = serial.Serial(port=port , baudrate=115200)
            print("Successfully connected to Arduino at {0}".format(port))
            self.port = port
            self.ERROR = None
        except serial.serialutil.SerialException as e:
            self.ERROR = "Unable to connect to Arduino at "+port
            print(self.ERROR)
            self._ser = None

    def stop(self):

        try:
            self._ser.write("c".encode())
            time.sleep(0.1)
        except:
            return

    def start(self):
        pass

    def close(self):

        try:
            self.stop()
            self._ser.close()
        except:
            pass
