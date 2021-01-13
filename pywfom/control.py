import serial, os, time, sys, glob, random, threading
import serial.tools.list_ports

def list_ports():
    """Return a 2-item list of available COM Ports and their devices"""
    return serial.tools.list_ports.comports()

class Arduino():
    """ Methods pertaining to Communication with the Arduino


    .. code-block:: python

        from pywfom.control import Arduino, list_ports

        ports = list_ports() # Gather a list of available COM ports

        port, name = ports[0] # Select the first port

        ard = Arduino(port=port) # Connect to Arduino at specified port

        ard.toggle_led(5) # Turn on LED at pin 5

    """

    def __init__(self, port='COM1', **kwargs):

        # TODO:  test stim

        self.ERROR = None
        self.DAQ_MSG = ""

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
            self.set_leds()
            self.set_trigger()

        elif setting == "stim":
            self.set_stim()

        elif setting == 'data_acquisition':
            self.set_daq()

    def set_leds(self, pins=None):
        """ Set led strobe pins, an array of [2,3,4] sends `p2p3p4p` to the Arduino

        :param list_ pins: List of pins to be considered LED drivers
        """

        if not self._ser:
            return

        if not pins:
            leds = ','.join([str(led['pin']) for led in self.strobing['leds']])
        else:
            leds = ','.join(pins)
        self._ser.write("<l{0},>".format(leds).encode())
        time.sleep(0.1)

    def set_trigger(self, pin=None):
        """ Send command for setting trigger pin (i.e. t3) """

        if not self._ser:
            return

        if not pin:
            pin = self.strobing['trigger']
        else:
            self.strobing['trigger'] = pin

        self._ser.write("<t{0}>".format(pin).encode())
        time.sleep(0.1)

    def set_stim(self):
        # <m15,16,17,18,.200>

        if not self._ser:
            return

        msg = "<m{0},.{1}>".format(
            ",".join([str(pin) for pin in self.stim[0]['pins']]),
            self.stim[0]['steps_per_revolution']
        )
        self._ser.write(msg.encode())
        time.sleep(0.1)


    def set_daq(self, pins=None):
        if not self._ser:
            return
        d = ','.join([str(daq['pin']) for daq in self.data_acquisition])
        self._ser.write("<d{0},>".format(d).encode())
        time.sleep(0.1)

    def read(self):
        # TODO: Uncomment when ready
        #return self._ser.readline()
        return "0d{0},{1},m200,".format( random.randint(0, 200) , random.randint(0, 200) )

    def step(speed, steps):
        # <p60,200>
        if not self._ser:
            return
        self._ser.write("<p{0},{1}>".format(speed, steps))

    def toggle_led(self, pin):
        """ Turn on a specified LED """
        self._ser.write("<T{0}>".format(pin).encode())
        time.sleep(0.1)

    def start_strobing(self):
        """ Turns on strobing on the Arduino"""
        self._ser.write("<S>".encode())
        time.sleep(0.1)

    def stop_strobing(self):
        """ Turns off strobing on the Arduino"""
        self._ser.write("<s>".encode())
        time.sleep(0.1)

    def _connect(self, port):
        """ Connect to an Arduino at a specified COM Port"""
        try:
            print("Attempting to connect to Arduino at " + port)
            self._ser = serial.Serial(port=port , baudrate=115200)
            time.sleep(2)
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
            self._acquiring = False
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

OPTIONS = {
    'stim_types':[
        '2PinStepper',
        '4PinStepper'
    ]
}
