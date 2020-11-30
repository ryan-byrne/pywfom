import serial, os, time

class ArduinoError(Exception):
    pass

class Arduino():
    """ Methods pertaining to Communication with the Arduino """

    def __init__(self, port=None, config=None):

        # Starting Arduino at specified port
        self.port = config['port'] if not port else port
        self.connect_to_arduino()

        self.set(config)

        self.types = {
            "number_of_runs":int,
            "run_length":float,
            "pre_stim":float,
            "stim":float,
            "post_stim":float,
            "port":str,
            "strobing":list
        }

        self.error_msg = ""

    def set(self, param, value=None):
        if type(param).__name__ == "dict":
            for k, v in param.items():
                self._set(k,v)
        else:
            self._set(param,value)

    def toggle_led(self, pin):
        print("Toggling LED at Pin "+str(pin))

    def _set(self, param, value):

        setattr(self, param, value)

        if param == "port" and self.port != value:
            self.ser.close()
            self.connect_to_arduino()
        else:
            return

        if not self.ser:
            return

        if param == "strobing":
            # Send command for setting trigger pin (i.e. T3)
            self.ser.write("T{0}".format(value['trigger']).encode())
            for led in value['leds']:
                # Send command for led pin (i.e. l11)
                self.ser.write("l{0}".format(led['pin']).encode())

        elif param == "stim":
            for stim in value['stim']:
                # Send command for setting stim pins (i.e. p5_6)
                self.ser.write(stim['pins'].join("_"))
                # Send command for setting stim (i.e. )
                self.ser.write("{0}_{1}_{2}".format(
                        stim['pre_stim'],
                        stim['stim'],
                        stim['post_stim']
                    ).encode()
                )
        elif param == "run":
            return

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

    def shutdown(self):
        self.ser.write("c".encode())
        self.ser.close()
