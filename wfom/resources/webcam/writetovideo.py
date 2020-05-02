import cv2, time, os
with open('C:\Mohammed\SPLASSH_Zyla_NEW\python_scripts\webcam_fcns\webcamparams.txt') as f:
    lines = f.readlines()
lines = [x.strip() for x in lines] 

w = int(lines[0])
h = int(lines[1])
frames = int(round(float(lines[2])))
webcam_path = lines[3]+'\\'+lines[4][0:5]+'webcam'+lines[5]+'\\'

if not os.path.exists(webcam_path):
    os.makedirs(webcam_path)
cam = cv2.VideoCapture(0)
start=time.time()
t = []
time.sleep(1)
for i in range(0,frames):
    print('collecting {} of {}'.format(str(i), str(frames)), end='\r')
    ts = time.time()
    t.append(time.time())
    (grabbed,frame) = cam.read()
    cv2.imwrite(webcam_path+str(i)+".jpg",frame)
    te = time.time()
with open(webcam_path+"t0.txt","w") as f:
    f.write(str(t))
text_file=open(webcam_path+"True_Frame_Rate.txt","w")
true_fr=(frames+1)/(time.time()-start)
text_file.write("Frame Rate : %s" % true_fr)
text_file.close()
