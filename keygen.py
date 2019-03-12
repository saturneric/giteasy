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
        self.local_path = "/Users/huyibing/"
        self.public_key_path = self.local_path+".ssh/id_rsa.pub"
        self.public_key = None

    def add_key(self):
        stdout, stderr = self.run("echo \"{0}\" >> ~/.ssh/authorized_keys".format(self.public_key))
        return stdout

    @staticmethod
    def create_key():
        if os.path.exists(os.path.join(os.environ["HOME"],".ssh","id_rsa.pub")):
            os.remove(os.path.join(os.environ["HOME"],".ssh","id_rsa.pub"))
            os.remove(os.path.join(os.environ["HOME"], ".ssh", "id_rsa"))

        print("Key Path:","{0}".format(os.path.join(os.environ["HOME"],".ssh","id_rsa")))
        ret_code = subprocess.Popen(["ssh-keygen", "-b 4096","-N ''", "-q",
                                     "-f {0}".format(os.path.join(os.environ["HOME"],".ssh","id_rsa")),
                                    ], shell=True,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = ret_code.communicate(input=b"\ny\n")
        return stdout.decode("utf-8")

    def get_key(self):
        self.public_key = open(self.public_key_path, 'r').readline()
        return self.public_key


if __name__ == "__main__":
    new_key = Key("compute.bktus.com", "/home/git", "git", "123456", ssh_key=False)
    # new_key.create_key()
    new_key.get_key()
    print(new_key.public_key)
    new_key.add_key()
