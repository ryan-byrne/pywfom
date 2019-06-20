import serial, time, struct

class Arduino():
    """docstring for Arduino."""

    def __init__(self):
        pass


if __name__ == '__main__':
    ser = serial.Serial(
        port='COM7',\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=0)
    leds = ["1000", "0100", "0010", "0001"]
    fps = 50.70 # frames per seconds
    exp = 0.0068 # seconds
    delay = 0.5 # seconds
    len = 3 # seconds
    t0 = time.time()
    while (time.time() - t0) < len:
        for led in leds:
            ser.write(bytes(led, "utf-8"))
            time.sleep(1)
