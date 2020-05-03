import time
t = time.time()
import serial, re, datetime, cv2
with open('C:\Mohammed\SPLASSH_Zyla_NEW\python_scripts\webcam_fcns\webcamparams.txt') as f:
    lines = f.readlines()
lines = [x.strip() for x in lines]
filename = savepath+lines[3].split("\\")[1]+'_'+lines[4]+lines[5]+'_rotary.txt'
ser = serial.Serial('COM6', 9600)
tstart = time.time()
tlag = time.time()-t

