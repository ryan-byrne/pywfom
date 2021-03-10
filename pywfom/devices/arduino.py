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

    def test(self):
        if self._serial.readline()[:3] == b'<pw':
            return True
        else:
            return False
