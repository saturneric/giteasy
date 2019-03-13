import paramiko


class SSH(object):
    ssh = paramiko.SSHClient()

    def __init__(self, hostname, path, user, passwd=None, ssh_key=False):
        self.hostname = hostname
        self.path = path
        self.user = user
        self.ssh_key = ssh_key

        if ssh_key:
            self.passwd = None
            self.key = paramiko.RSAKey.from_private_key_file('/Users/huyibing/.ssh/id_rsa')
        else:
            self.passwd = passwd

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def close(self):
        self.ssh.close()

    def run(self, cmd):
        print("CMD:", cmd)
        stdin, stdout, stderr = self.ssh.exec_command(cmd)

        stdout = list(stdout)
        stderr = list(stderr)
        return stdout, stderr

    @staticmethod
    def check_error(stderr):
        if len(stderr) == 0:
            return True
        else:
            return False

    def connect(self, timeout):
        if self.ssh_key:
            self.ssh.connect(hostname=self.hostname, port=22, username=self.user, pkey=self.key,
                             timeout=timeout, look_for_keys=True)
        else:
            self.ssh.connect(hostname=self.hostname, port=22, username=self.user, password=self.passwd,
                             timeout=timeout, look_for_keys = True)

    def __del__(self):
        self.close()
