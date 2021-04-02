import serial.tools.list_ports as ports
import serial, time

def find_arduinos():
    arduinos = []
    port_dict = [port.__dict__ for port in ports.comports()]
    for port in port_dict:
        if not port['manufacturer'] or 'Arduino' not in port['manufacturer']:
            continue
        else:
            arduinos.append(port)
    return arduinos

class Arduino(object):
    """docstring for Arduino."""

    def __init__(self, **config):
        self.active = False
        [setattr(self, key, []) for key in ['leds','stim','daq']]
        [setattr(self, key, None) for key in ['trigger', '_serial', 'firmware_version', 'port']]
        self.trigger = None
        self.set(**config)

    def _connect_to_port(self, port):

        try:
            print("Connecting to Arduino at {}".format(port))
            self._serial = serial.Serial(port=port, baudrate=115200, timeout=3.0)
            time.sleep(2)
            print("Checking Arduino Firmware Version...")
            self._serial.write("<f>".encode())
            self.firmware_version = self._serial.readline().decode("utf-8")[:-2]
            print("Connected to Arduino. Firmware Version : {}".format(self.firmware_version))
        except serial.serialutil.SerialException as e:
            self._serial = None
            self.firmware_version = None

    def start(self):
        self.active = True
        while self.active:
            self.feed = self._read_serial_message()

    def _read_serial_message(self):
        """

        Example Message: <pywfom_0.0.1><t1><l0,1,0,><d56,254,><s86>

        1) <pywfom_0.0.1> = Firmware Version (0.0.1)
        2) <t1> = Trigger Status (Should always be 1 when strobing)
        3) <l0,1,0,> = LED Status (Middle is on)
        4) <d56,254,> = DAQ (56 and 254)
        5) <s86> = Stim Position (86)

        """
        return self._serial.readline()

    def close(self):
        self.active = False
        try:
            self._serial.close()
        except:
            pass

    def set(self, **settings):
        _msg = ""
        for setting, value in settings.items():
            if setting == 'port' and value != self.port:
                self._connect_to_port(value)
            elif not self._serial:
                return
            elif setting == 'trigger':
                _msg += "<t{}>".format(value)
            elif setting == 'leds':
                _msg += "<l{},>".format(','.join(str(led['pin']) for led in value))
            elif setting == 'daq':
                _msg += "<d{},>".format(','.join(str(daq['pin']) for daq in value))
            setattr(self, setting, value)

    def json(self):

        # Return Camera settings as a dictionary

        json_settings = {}

        for k, v in self.__dict__.items():
            if k[0] != '_':
                json_settings[k] = v

        return json_settings
