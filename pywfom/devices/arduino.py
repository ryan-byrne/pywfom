import serial.tools.list_ports as ports
import serial

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
        self.set(**config)
        self.active = False
        self.firmware_version = None
        self._serial = None

    def _connect_to_port(self, port):
        self._serial = serial.Serial(port=port, timeout=3.0)
        msg = self._serial.readline()[:3]
        self.firmware_version = None if msg[:3] != b'<py' else msg[7:12]

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
        self._serial.close()

    def set(self, **settings):
        [self._set(k,v) for k,v in settings.items()]

    def _set(self, setting, value):
        if setting == 'port':
            self._connect_to_port(value)


    def json(self):

        # Return Camera settings as a dictionary

        json_settings = {}

        for k, v in self.__dict__.items():
            if k[0] != '_':
                json_settings[k] = v

        return json_settings
