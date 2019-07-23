import serial, time, os, sys, csv
import threading
import numpy as np
from graph import Graph
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
        time.sleep(1)
        print("Successfully connected to Arduino.")
        return(a)
    except SerialException:
        print("Unable to connect to Arduino")
        sys.exit()

def strobe_single_color(arduino, color, freq):
    t0 = time.time()
    print("Strobing %s at %s Hz" % (color, str(freq)))
    while time.time() - t0 < duration:
        arduino.write(color[0].encode())
        time.sleep(1/freq/2)
        arduino.write("C".encode())
        time.sleep(1/freq/2)

def spectrometer_connect():
    print("Attempting to connect to Spectrometer.")
    devices = sb.list_devices()
    if len(devices) == 0:
        print("Unable to connect to Spectrometer")
        sys.exit()
    else:
        spec = sb.Spectrometer(devices[0])
        spec.integration_time_micros(1000)
        print("Successfully connected to Spectrometer.")
        return(spec)

def read_all_wavelengths():
    d = {}
    i = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
    for l in leds.keys():
        d[l] = i[leds[l]]
    return(d)

def read_single_wavelength(color, file):
    t0 = time.time()
    t = 0
    with open(file, "w") as f:
        while t < duration:
            t = time.time() - t0
            i = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)[leds[color]]
            f.write("%s,%s\n" % (str(t), str(i)))
            time.sleep(delay/1000)
    f.close()

def adjust_intensity(color, power):
    input("Switch the %s LED to 'CW' Mode. Then Press [ENTER]" % (color))
    p = (power/100)*60000
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
    fname = "data/%s_%sp_%shz.csv" % (color, power, freq)
    print("Creating save file: %s" % (fname))
    with open(fname, "w") as f:
        f.write("Time (s), Intensity\n")
    return(fname)

# SETTINGS
os.chdir("..")
freq = [5, 10, 25, 50] # in Hz
pow = [100, 50, 10] # % of Max LED power
leds = {    "LIME":1061,
            "GREEN":962,
            "BLUE":848,
            "RED":1255}
duration = 1 # seconds
delay = 1 # milliseconds
data = {}

spec = spectrometer_connect()

arduino = arduino_connect()

if __name__ == "__main__":

    for color in ["RED"]:
        data[color] = {}
        for p in pow:
            data[color][p] = {}
            adjust_intensity(color, p)
            for f in freq:
                file = make_save_file(color, p, f)
                strobe = threading.Thread(  target=strobe_single_color,
                                            args=(arduino, color, f))
                read = threading.Thread(    target=read_single_wavelength,
                                            args=(color,file))
                strobe.start()
                read.start()
                strobe.join()
                read.join()
