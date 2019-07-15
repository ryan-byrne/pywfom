import serial, time
from graph import Graph
from serial.serialutil import SerialException


# SETTINGS
freq = [10, 20, 50, 100] # in Hz
pow = [100, 50, 10, 5] # % of Max LED power
leds = ["LIME", "GREEN", "BLUE", "RED"]
duration = 5 # seconds

def arduino_connect():
    a = serial.Serial(
        port="COM4",\
        baudrate=9600,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=0)
    time.sleep(1)
    return(a)

if __name__ == "__main__":

    try:
        arduino = arduino_connect()
        print("Successfully connect to Arduino.")
    except SerialException:
        print("Could not connect to Arduino")
        arduino = ""

    for l in leds:
        input("Change Wavelength to "+l+" then press [ENTER]")
        for p in pow:
            input("Set the Power of "+l+" to "+str(p)+"% Saturation then press [ENTER]")
            input("Set the file BaseName to "+str(p)+"_sat_"+l+" then press [ENTER]")
            input("Begin the acquisition on OceanView. Then press [ENTER]")
            for f in freq:
                i = 0
                while i < duration*f:
                    print("Strobing "+l+" at "+f+"Hz")
                    arduino.write(l[0].encode())
                    time.sleep(1/f/2)
                    arduino.write("C".encode())
                    time.sleep(1/f/2)
                    i += 1
            input("End the acquisition on OceanView. Then press [ENTER]")
            # "100_sat_LIME_intensity_5.txt"
            filename = str(p) + "_sat_" + l + "_intensity_0.txt"
            Graph(filename)
