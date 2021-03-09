import serial, os, time, sys, glob, random, threading
from halo import Halo
import serial.tools.list_ports

# TODO: Create function which jsonifys settings to be sent

def list_ports():
    """Return a 2-item list of available COM Ports and their devices"""
    return [port.__dict__ for port in serial.tools.list_ports.comports()]

class Arduino():
    """ Methods pertaining to Communication with the Arduino


    .. code-block:: python

        from pywfom.control import Arduino, list_ports

        ports = list_ports() # Gather a list of available COM ports

        port, name = ports[0] # Select the first port

        ard = Arduino(port=port) # Connect to Arduino at specified port

        ard.toggle_led(5) # Turn on LED at pin 5

    """

    def __init__(self, config=None, **settings):

        # TODO:  test stim

        # Set default settings
        self.port, self.stim, self.data_acquisition, self.strobing =  "", [], [], []
        self.DAQ_MSG, self.ERROR, self._ser = "", "", None

        # Check for configuration dict, otherwise use kwargs
        settings = config if config else settings
        # Establish settings
        self.set(config=settings)


    def set(self, **settings):

        settings = settings['config'] if 'config' in settings else settings

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
            time.sleep(1)
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
        # <m2038.11_10_9_8_>

        msg = "<m{1}.{0}_>".format(
            "_".join([str(pin) for pin in self.stim[0]['pins']]),
            self.stim[0]['steps_per_revolution']
        )
        self._ser.write(msg.encode())
        time.sleep(0.1)

    def increase_step(self):
        self._ser.write("<+>".encode())

    def decrease_step(self):
        self._ser.write("<->".encode())

    def set_daq(self, pins=None):

        # <d4,5,6,>

        if not self._ser:
            return

        d = ','.join([str(daq['pin']) for daq in self.data_acquisition])
        self._ser.write("<d{0},>".format(d).encode())
        time.sleep(0.1)

    def read(self):
        # TODO: Uncomment when ready

        # 1d123,245,100,m200
        return "0d{0},{1},m200,".format( random.randint(0, 200) , random.randint(0, 200) )
        #return self._ser.readline()

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

        with Halo(text='Connecting to Arduino at Port: {0}'.format(port)) as spinner:
            try:
                self._ser = serial.Serial(port=port , baudrate=115200, timeout=2)
                spinner.succeed()
                self.port = port
                self.ERROR = None
            except serial.serialutil.SerialException as e:
                self.ERROR = "Unable to connect to Arduino at "+port
                spinner.fail(self.ERROR)
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

TYPES = {

}
