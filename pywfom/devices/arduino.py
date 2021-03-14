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

    def __init__(self, port):
        self._serial = serial.Serial(port=port, timeout=3.0)

    def read(self):
        """

        Example Message: <pywfom_0.0.1><t1><l0,1,0,><d56,254,><s86>

        1) <pywfom_0.0.1> = Firmware Version (0.0.1)
        2) <t1> = Trigger Status (Should always be 1 when strobing)
        3) <l0,1,0,> = LED Status (Middle is on)
        4) <d56,254,> = DAQ (56 and 254)
        5) <s86> = Stim Position (86)

        """

    def test(self):
        if self._serial.readline()[:3] == b'<pw':
            return True
        else:
            return False

    def json(self):

        # Return Camera settings as a dictionary

        json_settings = {}

        for k, v in self.__dict__.items():
            if k[0] != '_':
                json_settings[k] = v

        return json_settings
