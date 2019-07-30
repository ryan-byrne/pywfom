import serial, time, os, sys, csv
import threading
import numpy as np
from serial.serialutil import SerialException
import seabreeze.spectrometers as sb

def arduino_connect():
    try:
        a = serial.Serial(
            port="COM4",\
            baudrate=9600,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
                timeout=0)
        time.sleep(3)
        print("Successfully connected to Arduino.")
        return(a)
    except SerialException:
        print("Unable to connect to Arduino")
        sys.exit()

def strobe_single_color(arduino, color, freq):
    t0 = time.time()
    if freq < 1:
        print("Leaving %s on." % (color))
        arduino.write(color[0].encode())
        time.sleep(duration)
        arduino.write(color[0].lower().encode())
        return
    print("Strobing %s at %s Hz" % (color, str(freq)))
    while time.time() - t0 < duration:
        arduino.write(color[0].encode())
        time.sleep(1/freq/2)
        arduino.write(color[0].lower().encode())
        time.sleep(1/freq/2)

def spectrometer_connect():
    print("Attempting to connect to Spectrometer.")
    devices = sb.list_devices()
    if len(devices) == 0:
        print("Unable to connect to Spectrometer")
        sys.exit()
    else:
        spec = sb.Spectrometer(devices[0])
        spec.integration_time_micros(delay*1000)
        print("Successfully connected to Spectrometer.")
        return(spec)

def read_all_wavelengths():
    d = {}
    i = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
    for l in leds.keys():
        d[l] = i[leds[l]]
    return(d)

def read_single_color(color, file):
    t0 = time.time()
    t = 0
    wavelengths = leds[color]
    bits = [int(wl*3.23-750) for wl in wavelengths]
    with open(file, "w") as f:
        while t < duration:
            t = time.time() - t0
            intensities = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)[bits]
            wavelengths = spec.wavelengths()[bits]
            i = sum(intensities)/len(intensities)
            f.write("%s,%s\n" % (str(t), str(i)))
            time.sleep(delay/1000)
    f.close()

def adjust_intensity(color, power):
    input("Switch the %s LED to 'CW' Mode. Then Press [ENTER]" % (color))
    p = (power/100)*20000
    print("Set the Intensity to %s" % (str(power)))
    set = False
    while not set:
        i = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)[leds[color]]
        diff = (i - p)
        print("Diff is: %s" % (str(diff)))
        if abs(diff/p) > 0.01:
            pass
        else:
            set = True
        time.sleep(1)
    input("Switch the %s LED to 'Trig' Mode. The press [ENTER]" % (color))

def make_save_file(color, power, freq):
    fname = "data/%s_%sp_%shz.csv" % (color, power, int(freq))
    print("Creating save file: %s" % (fname))
    with open(fname, "w+") as f:
        f.write("Time (s), Intensity\n")
    f.close()
    return(fname)

# SETTINGS
os.chdir("..")
freq = [1/300, 10, 25, 50] # in Hz
pow = [100, 50, 10] # % of Max LED power
leds = {    "GREEN":list(range(520,526)),
            "BLUE":list(range(490,494)),
            "RED":list(range(621,625)),
            "LIME":list(range(560,570)),
        }
        # Bit values for specified wavelength ranges
        # 1050/560 -> 1.875 bits/nm
duration = 300 # seconds
delay = 4 # milliseconds

spec = spectrometer_connect()

arduino = arduino_connect()

if __name__ == "__main__":

    p = "100"

    for f in freq:
        for color in leds.keys():
            arduino.write(color[0].encode())
            file = make_save_file(color, p, f)
            read_single_color(color, file)
            arduino.write(color[0].lower().encode())
