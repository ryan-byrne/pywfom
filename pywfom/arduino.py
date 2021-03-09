import serial.tools.list_ports as ports

def list_ports():
    return [ports.__dict__ for port in ports.comports() if "Arduino" in port.description]

class Arduino(object):

    def __init__(self):
        pass
