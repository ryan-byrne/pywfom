import seabreeze.spectrometers as sb
import sys

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

delay = 3 # milliseconds
spec = spectrometer_connect()
count = 0
intensities = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
wavelengths = spec.wavelengths()
for wv in wavelengths:
    print(count, wv)
    count += 1
