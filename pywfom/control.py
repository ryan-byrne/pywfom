import serial, os, time

class ArduinoError(Exception):
    pass

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, settings):

        self.set(settings)

        self.error_msg = ""

    def set(self, setting, value=None):

        

        self.stop()

        if type(setting).__name__ == "dict":
            for k, v in setting.items():
                self._set(k,v)
        else:
            self._set(setting,value)

        self.start()

    def _set(self, setting, value):

        if setting == "port":
            self.port = value
            self.connect_to_arduino()

        elif setting != "port" and not self.ser:
            return

        elif setting == "strobing":
            self._set_leds(value['leds'])
            self._set_trigger(value['trigger'])

        elif setting == "stim":
            # TODO: Set stim
            return
            for stim in value['stim']:
                # Send command for setting stim pins (i.e. s5s6s)
                self.ser.write(stim['pins'].join("_"))
                time.sleep(0.1)
                # Send command for setting stim (i.e. )
                self.ser.write("{0}_{1}_{2}".format(
                        stim['pre_stim'],
                        stim['stim'],
                        stim['post_stim']
                    ).encode()
                )
                time.sleep(0.1)
        setattr(self, setting, value)

    def _set_leds(self, leds):
        """ Set led pin strobe array (i.e. p6p7p8p) """
        msg = "p"
        for led in leds:
            msg += "{0}p".format(led['pin'])
        self.ser.write(msg.encode())

    def _set_trigger(self, pin):
        """ Send command for setting trigger pin (i.e. t3) """
        self.ser.write("t{0}".format(pin).encode())

    def toggle_led(self, pin):
        """ Turn on a specified LED """
        self.ser.write("T{0}".format(pin).encode())

    def toggle_strobing(self):
        """ Toggles strobing on the connected LEDs"""
        self.ser.write("S".encode())

    def connect_to_arduino(self):
        """ Connect to an Arduino at a specified COM Port"""
        try:
            print("Attempting to connect to Arduino at " + self.port)
            self.ser = serial.Serial(port=self.port , baudrate=115200)
            time.sleep(2)
            self.error_msg = ""
            print("Successfully connected to Arduino at {0}".format(self.port))
        except serial.serialutil.SerialException:
            self.error_msg = "Unable to connect to Arduino at "+self.port
            self.ser = None
            print(self.error_msg)

    def stop(self):

        try:
            self.ser.write("c".encode())
            time.sleep(0.1)
        except:
            return

    def start(self):
        pass

    def close(self):
        self.stop()
        self.ser.close()
