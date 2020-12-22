import serial, os, time, sys, glob
import serial.tools.list_ports

def list_ports():
    return serial.tools.list_ports.comports()

class ArduinoError(Exception):
    pass

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, settings):

        # TODO: set stim settings
        # TODO:  test stim
        # # TODO: add encoder monitoring
        # TODO: Test data acquisition

        self.ERROR = None

        self.set(settings)

    def set(self, setting, value=None):

        self.stop()

        if type(setting).__name__ == "dict":
            for k, v in setting.items():
                self._set(k,v)
        else:
            self._set(setting,value)

        self.start()

    def _set(self, setting, value):

        setattr(self, setting, value)

        if setting == "port":
            self.connect_to_arduino(value)

        elif setting != "port" and not self.ser:
            # TODO: Remove this when things are working
            #return
            pass

        elif setting == "strobing":
            self._set_leds()
            self._set_trigger()

        elif setting == "stim":

            for stim in value:
                # Send command for setting stim pins (i.e. s5s6s)
                pass

    def _set_leds(self):
        """ Set led pin strobe array (i.e. p6p7p8p) """
        msg = "p"
        for led in self.strobing['leds']:
            print('setting led: {0}'.format(led['pin']))
            msg += "{0}p".format(led['pin'])
        self.ser.write(msg.encode())
        time.sleep(0.1)

    def _set_trigger(self):
        """ Send command for setting trigger pin (i.e. t3) """
        pin = self.strobing['trigger']
        print('setting trigger to: {0}'.format(pin))
        self.ser.write("t{0}".format(pin).encode())
        time.sleep(0.1)

    def toggle_led(self, pin):
        """ Turn on a specified LED """
        self.ser.write("T{0}".format(pin).encode())
        time.sleep(0.1)

    def toggle_strobing(self):
        """ Toggles strobing on the connected LEDs"""
        self.ser.write("S".encode())
        time.sleep(0.1)


    def connect_to_arduino(self, port):
        """ Connect to an Arduino at a specified COM Port"""
        try:
            print("Attempting to connect to Arduino at " + port)
            self.ser = serial.Serial(port=port , baudrate=115200)
            print("Successfully connected to Arduino at {0}".format(port))
            self.port = port
        except serial.serialutil.SerialException as e:
            self.ERROR = "Unable to connect to Arduino at "+port
            print(self.ERROR)
            self.ser = None

    def stop(self):

        try:
            self.ser.write("c".encode())
            time.sleep(0.1)
        except:
            return

    def start(self):
        pass

    def close(self):

        try:
            self.stop()
            self.ser.close()
        except:
            pass
