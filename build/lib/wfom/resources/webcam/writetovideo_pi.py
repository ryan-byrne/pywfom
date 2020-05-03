import time, serial
from multiprocessing import Process
from paramiko import SSHClient, AutoAddPolicy
def start_rotary():
    with open('C:\Mohammed\SPLASSH_Zyla_NEW\python_scripts\webcam_fcns\webcamparams.txt') as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    runlength = int(round(float(lines[2])))
    filename = lines[4] + lines[5]
    savepath = lines[3] + '\\'
    # open rotary COM port
    ser = serial.Serial('COM2', 9600)

    while True:
        with open('C:\Mohammed\SPLASSH_Zyla_NEW\python_scripts\\rotarymessage.txt') as f:
            msg = f.read()
        if msg == '1':
            f.close()
            break

    tstart = time.time()
    while (time.time()-tstart) < runlength:
        a = str(ser.read(12))
        try:
            ang = int(a.split('\\n')[1].split('\\r')[0])
            with open(savepath+filename+'_rotary.txt', 'a') as text_file:
                text_file.write(str(ang)+','+str(time.time())+'\n')
        except:
                pass
    text_file.close()
    ser.close()

def start_webcam():
    with open('C:\Mohammed\SPLASSH_Zyla_NEW\python_scripts\webcam_fcns\webcamparams.txt') as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    runlength = int(round(float(lines[2])))
    tmp = lines[3][3:].replace('\\', '/') + '/'
    mouse = tmp.split('/')[0]
    run = tmp.split('/')[2]
    stim = lines[5]

    def Connect(ip, username='pi', pw='lfoi'):
        print('connecting to {}@{}...'.format(username, ip))
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(ip, username=username, password=pw)
        print('connection status =', ssh.get_transport().is_active())
        return ssh

    def SendCommand(ssh, command, pw='password'):
        print('sending a command... ', command)
        stdin, stdout, stderr = ssh.exec_command(command)
        if "sudo" in command:
            stdin.write(pw + '\n')
        stdin.flush()
        print('\nstout:', stdout.read())
        print('\nsterr:', stderr.read())

    myssh = Connect(ip='picam1.hillman.zi.columbia.edu')
    SendCommand(myssh, command='python w2.py revault/revault2/cmdata ' + mouse + '/' + run + ' ' + run + '_stim' + stim + ' ' + str(runlength))

if __name__ == '__main__':
    p1 = Process(target=start_rotary)
    p1.start()
    p2 = Process(target=start_webcam)
    p2.start()
    p1.join()
    p2.join()