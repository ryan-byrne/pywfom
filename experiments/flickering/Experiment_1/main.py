import serial, time

arduino = serial.Serial(
    port="COM4",\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

time.sleep(1)

if __name__ == "__main__":
    freq = [1, 5, 10, 100] # in Hz
    pow = [100, 50, 10, 5] # % of Max LED power
    leds = ["L", "G", "B", "R"]
    duration = 10 # seconds
    for led in leds:
        for f in freq:
            print("Flashing "+ led +" at " + str(f) + " Hz for " + str(duration) + " seconds")
            i = 0
            while i < duration/2*f:
                arduino.write(led.encode())
                time.sleep(1/f/2)
                arduino.write("C".encode())
                time.sleep(1/f/2)
                i += 1
