import serial, re, time, datetime

runlength = 30
tstart = time.time();
filename = 'g:/rotaryfiles/'+str(time.time())+'_rotary.txt';

ser = serial.Serial('COM6', 19200)
while (time.time()-tstart) < runlength:
    ang = ser.read(10);
    with open(filename, 'a') as text_file:
                text_file.write(str(ang)+','+str(time.time())+'\n')
ser.close()
