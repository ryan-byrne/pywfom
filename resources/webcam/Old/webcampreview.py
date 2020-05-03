import cv2, time, os, re
from paramiko import SSHClient, AutoAddPolicy

def Connect(ip, username='pi', pw='lfoi'):
    '''ssh into the pi'''
    print('connecting to {}@{}...'.format(username, ip))
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(ip, username=username, password=pw)
    print('connection status =', ssh.get_transport().is_active())
    return ssh

def SendCommand(ssh, command, pw='password'):
    '''send a terminal/bash command to the ssh'ed-into machine '''
    print('sending a command... ', command)
    stdin, stdout, stderr = ssh.exec_command( command )
    if "sudo" in command:
        stdin.write(pw+'\n')
    stdin.flush()
    print('\nstout:',stdout.read())
    print('\nsterr:',stderr.read())

myssh = Connect(ip='129.236.163.116')
SendCommand(myssh, command='python wtest.py')
