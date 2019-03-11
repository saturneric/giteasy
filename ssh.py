import server
import subprocess
import os

class key(server.ssh):
    def __init__(self,hostname, path, user, passwd=None, sshkey=False):
        super().__init__(hostname=hostname, path=path, user=user, passwd=passwd, sshkey=sshkey)
        self.connect(5);

    def add_key(self):
        self.run("echo \"{0}\" >> ~/.ssh/authorized_keys".format(self.pub_key))

    def create_key(self):
        retcode = subprocess.Popen(["ssh-keygen", "-b 4096", "-t rsa"], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = retcode.communicate(input=b"\ny \n \n \n")

    def get_key(self):
        self.pub_key = os.popen("cat ~/.ssh/id_rsa.pub").read()




newkey = key("compute.bktus.com", "/home/git", "git", "123456",sshkey=False);
#newkey.create_key();
#newkey.get_key();
#newkey.add_key();