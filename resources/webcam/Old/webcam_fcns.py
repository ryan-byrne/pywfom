def preview_fcn(w,h):
    from SimpleCV import Camera, Display
    cam = Camera(0,{"width": w,"height": h})
    cam.live()

def writetovideo(w,h,frames,webcam_path):
    from SimpleCV import Camera, VideoStream
    import socket, time
    UDP_IP = "127.0.0.1"
    UDP_LISTEN_PORT = 65534
    UDP_WRITE_PORT = 65535
    MESSAGE = "Webcam Ready!"
    file=open("C:\Mohammed\SPLASSH_ANDOR_1003_with_webcam\python_scripts\message.txt","w")
    file.write((MESSAGE))
    file.close()
    print "Status: ", MESSAGE    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_LISTEN_PORT))
    cam = Camera(0,{"width": w,"height": h},threaded=True)
    img=cam.getImage()
    # vs = VideoStream("foo.avi",fps=60)
    # sock.sendto(MESSAGE, (UDP_IP, UDP_WRITE_PORT))
    data = sock.recvfrom(1024)
    start=time.time()
    for i in range(0,frames):
        # cam.getImage().save(vs)
        cam.getImage().save(webcam_path+str(i)+".jpg")
        # time.sleep(.005)
        # img=cam.getImage()
        # img.save(vs)
        # vs.writeFrame(img)
        # img.save(webcam_path+str(i)+".jpg")
    text_file=open(webcam_path+"True_Frame_Rate.txt","w")
    true_fr=(frames+1)/(time.time()-start)
    text_file.write("Frame Rate : %s" % true_fr)
    print("Frame Rate : %s" % true_fr)
    text_file.close()
    MESSAGE = "Webcam Done!"
    file=open("C:\Mohammed\SPLASSH_ANDOR_1003_with_webcam\python_scripts\message.txt","w")
    file.write((MESSAGE))
    file.close()    
    print "Status: ", MESSAGE
    sock.sendto(MESSAGE, (UDP_IP, UDP_WRITE_PORT))
