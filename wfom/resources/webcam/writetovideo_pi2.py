import time, os, serial, cv2
from multiprocessing import Process

def start_rotary():
    with open('C:\Mohammed\SPLASSH_Zyla_NEW\python_scripts\webcam_fcns\webcamparams.txt') as f:
        lines = f.readlines()
    runlength = int(round(float(lines[2])))+2
    lines = [x.strip() for x in lines]
    savepath = lines[3]
    run = lines[4]
    stim = lines[5]
    # open rotary COM port (2 for now)g
    try:
        ser = serial.Serial('COM2', 9600)
    except:
        print('port already open')
        return

    tstart = time.time()
    while (time.time()-tstart) < runlength:
        a = str(ser.read(15))
        ang = int(a.split('\\n')[1].split('\\r')[0])
        with open(savepath + '\\' + run + stim + '_rotary.txt', 'a') as text_file:
            text_file.write(str(ang)+','+str(time.time())+'\n')
    text_file.close()
    ser.close()

def start_webcam():
    with open('C:\Mohammed\SPLASSH_Zyla_NEW\python_scripts\webcam_fcns\webcamparams.txt') as f:
        lines = f.readlines()
    runlength = int(round(float(lines[2])))+2
    lines = [x.strip() for x in lines]
    savepath = lines[3]
    run = lines[4]
    stim = lines[5]
    cam = cv2.VideoCapture(0)
    out = cv2.VideoWriter(savepath + '\\' + run + stim + "_cam1.avi",cv2.VideoWriter_fourcc('M','J','P','G'),30,(640,480))
    tstart = time.time()
    i = 1
    times = []
    while (time.time() - tstart) < runlength:
        (grabbed, frame) = cam.read()
        out.write(frame)
        times.append(str(time.time()))
        i = i + 1
    with open(savepath + '\\' + run + stim + '_cam1.txt', 'a') as f:
        for item in times:
            f.write(item + ',')

    out.release()
    cam.release()
    f.close()
if __name__ == '__main__':
    p1 = Process(target=start_rotary)
    p1.start()
    p2 = Process(target=start_webcam)
    p2.start()
    p1.join()
    p2.join()