import git
import subprocess
import os
import ssh


class Key(ssh.SSH):
    def __init__(self,hostname, path, user, password=None, ssh_key=False):
        super().__init__(hostname=hostname, path=path, user=user, passwd=password, ssh_key=ssh_key)
        self.connect(5)
        self.pub_key = None
        self.keygen = None
        self.local_path = "C:\\Users\\Saturneric\\"
        self.public_key_path = self.local_path+".ssh/id_rsa.pub"
        self.public_key = None

    def add_key(self):
        self.run("echo \"{0}\" >> ~/.ssh/authorized_keys".format(self.public_key))

    @staticmethod
    def create_key():
        ret_code = subprocess.Popen(["ssh-keygen", "-b 4096"], shell=True,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = ret_code.communicate(input=b"\n \n \n \n")

    def get_key(self):
        self.public_key = open(self.public_key_path, 'r').readline()


if __name__ == "__main__":
    new_key = Key("compute.bktus.com", "/home/git", "git", "123456", ssh_key=False)
    # new_key.create_key()
    new_key.get_key()
    print(new_key.public_key)
    new_key.add_key()
