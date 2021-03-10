import serial.tools.list_ports as ports
import serial

def find():
    arduinos = []
    port_dict = [port.__dict__ for port in ports.comports()]
    for port in port_dict:
        if not port['manufacturer'] or 'Arduino' not in port['manufacturer']:
            continue
        else:
            arduinos.append(port)
    return arduinos

def connect(port):
    ser = serial.Serial(port=port)
    print(ser)

class Arduino(object):
    """docstring for Arduino."""

    def __init__(self, port):
        self._serial = serial.Serial(port=port, timeout=3.0)

    def test(self):
        return self._serial.readline()
