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

    def add_key(self):
        self.run("echo \"{0}\" >> ~/.ssh/authorized_keys".format(self.pub_key))

    def create_key(self):
        ret_code = subprocess.Popen(["ssh-keygen", "-b 4096", "-t rsa"], shell=True,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = ret_code.communicate(input=b"\ny \n \n \n")
        self.get_key()

    def get_key(self):
        self.pub_key = os.popen("cat ~/.ssh/id_rsa.pub").read()


if __name__ == "__main__":
    new_key = Key("compute.bktus.com", "/home/git", "git", "123456", ssh_key=False)
    # new_key.create_key()
    # new_key.get_key()
    # new_key.add_key()
