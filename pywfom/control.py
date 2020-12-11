import serial, os, time

class ArduinoError(Exception):
    pass

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, settings):

        self.set(settings)

        self.error_msg = ""

    def set(self, setting, value=None):

        print("(arduino) Adjusting settings...")

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
            # Send command for setting trigger pin (i.e. T3)
            self.ser.write("t{0}".format(value['trigger']).encode())
            msg = "l"
            for led in value['leds']:
                # Set led pin strobe array (i.e. l6l7l8l)
                msg += "{0}l".format(led['pin'])
            self.ser.write(msg.encode())

        elif setting == "stim":
            # TODO: Set stim
            return
            for stim in value['stim']:
                # Send command for setting stim pins (i.e. s5s6s)
                self.ser.write(stim['pins'].join("_"))
                # Send command for setting stim (i.e. )
                self.ser.write("{0}_{1}_{2}".format(
                        stim['pre_stim'],
                        stim['stim'],
                        stim['post_stim']
                    ).encode()
                )
        setattr(self, setting, value)

    def toggle_led(self, pin):
        self.ser.write("T{0}".format(pin).encode())

    def toggle_strobing(self):
        self.ser.write("S".encode())

    def connect_to_arduino(self):
        try:
            print("Attempting to connect to Arduino at " + self.port)
            self.ser = serial.Serial(
                port=self.port,\
                baudrate=115200,\
                parity=serial.PARITY_NONE,\
                stopbits=serial.STOPBITS_ONE,\
                bytesize=serial.EIGHTBITS,\
                    timeout=0)
            time.sleep(1)
            self.error_msg = ""
            print("Successfully connected to Arduino at {0}".format(self.port))
        except serial.serialutil.SerialException:
            self.error_msg = "Unable to connect to Arduino at "+self.port
            self.ser = None
            print(self.error_msg)

    def stop(self):

        try:
            self.ser.write("C".encode())
        except:
            return

    def start(self):
        pass

    def close(self):
        self.ser.write("C".encode())
        self.ser.close()
