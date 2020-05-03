import paramiko
ssh_client =paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname='enterprise.hillman.zi.columbia.edu',username='nic',password='M0nbas3')

ftp_client=ssh_client.open_sftp()
ftp_client.get('/local_mount/space/enterprise/4/Personal Folders/Jozsef/every_animal.dat','C:/users/jozsef/trythis.dat')
ftp_client.close()