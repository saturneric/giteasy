import paramiko
import re
import os

class ssh(object):
    ssh = paramiko.SSHClient();
    def __init__(self, hostname, path, user, passwd=None, sshkey=False):
        self.hostname = hostname;
        self.path = path;
        self.user = user;
        self.sshkey = sshkey;

        if sshkey == True:
            self.passwd = None;
            self.key = paramiko.RSAKey.from_private_key_file('/Users/huyibing/.ssh/id_rsa')
        else:
            self.passwd = passwd;

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def close(self):
        self.ssh.close();

    def run(self, cmd):
        print("CMD:", cmd)
        stdin, stdout, stderr = self.ssh.exec_command(cmd)

        stdout = list(stdout);
        stderr = list(stderr);
        return stdout, stderr;

    def check_error(self, stderr):
        if len(stderr) == 0:
            return True
        else:
            return False

    def connect(self,timeout):
        if self.sshkey:
            self.ssh.connect(hostname=self.hostname, port=22, username=self.user, pkey=self.key, timeout=timeout);
        else:
            self.ssh.connect(hostname=self.hostname, port=22, username=self.user, password=self.passwd, timeout=timeout);

    def __del__(self):
        self.close();

class git(ssh):
    projects = {}
    projects_list = []
    remotes = {}
    fix_name = None;

    def __init__(self, hostname, path, user, passwd):
        super().__init__(hostname, path, user, passwd);
        self.base_path = [False];
        self.connect(5);



    def globalinit(self,git_user,git_email):
        cmd = "git config --global user.email \"{0}\";".format(git_email);
        cmd += "git config --global user.name \"{0}\";".format(git_user);
        stdout, stderr = self.run(cmd)
        if self.check_error(stderr):
            print("Global setting successful.")
        else:
            print(stderr)
            raise ValueError("Args Abnormal")


    def baseinit(self):
        stdout, stderr = self.run("ls {}".format(self.path))
        if self.check_error(stderr):
            if "giteasy\n" in stdout:
                print("Directory already found.")
            else:
                stdout, stderr = self.run("mkdir {0}/{1}".format(self.path, "giteasy"))
                print("Create directory.")
            self.base_path = [True,"{0}/{1}".format(self.path, "giteasy")]
        else:
            raise ValueError("Home Path Abnormal")

    def create_project(self,name):
        if self.base_path[0]:
            stdout, stderr = self.run("mkdir {0}/{1}".format(self.base_path[1],name))
            if self.check_error(stderr):
                print("Succeed In Making Directory.")
                self.projects[name] = {"path" : "{0}/{1}".format(self.base_path[1],name), "branch" : []}
                cmd = "cd {0};".format(self.projects[name]["path"]);
                cmd += "git init;";
                cmd += "touch ReadME.md;";
                cmd += "git add *;"
                cmd += "git commit --message=init;";
                stdout, stderr = self.run(cmd)
                if self.check_error(stderr):
                    print("Succeed In Getting Repository.")
                else:
                    print(stderr)
                    raise ValueError("Target Path Abnormal")
            else:
                raise ValueError("Base Path Abnormal")
        else:
            raise UnboundLocalError("Init Base First")

    def update_projects(self):
        if self.base_path[0]:
            stdout, stderr = self.run("ls {0}".format(self.base_path[1]))
            if self.check_error(stderr):
                reform = re.compile("\w+")
                for project in stdout:
                    print("PROJECT",project)
                    project_name = reform.match(project).string.strip('\n')
                    self.projects[project_name] = {"path" : "{0}/{1}".format(self.base_path[1],project_name), "branch" : []}
            else:
                raise ValueError("Base Path Abnormal")

            self.list_projects();

        else:
            raise UnboundLocalError("Init Base First")

    def list_projects(self):
        for project in self.projects.keys():
            self.projects_list.append(project)
            print(project)

    def set_local(self,path):
        self.remotes = {};
        self.local_path = path;
        os.chdir(self.local_path);

    def add_remote(self,name="origin"):
        os.popen("git remote add {3} ssh://{0}@{1}:{2}/{4}/.git".format(self.user,self.hostname,self.base_path[1],name,self.fix_name))
        self.remotes[name] = {"name" : name, "url" : "ssh://{0}@{1}:{2}/{3}/.git".format(self.user,self.hostname,self.base_path[1],self.fix_name)}

    def fetch_remote(self,name):
        if name in self.remotes.keys():
            os.popen("git fetch {0}".format(name))

    def get_remote(self):
        retcode = re.compile(r"[\t, ]")
        for remote in os.popen("git remote -v").readlines():
            results = retcode.split(remote)
            for item in results:
                if item[0] not in self.remotes.keys():
                    self.remotes[item[0]] = {"name":item[0],"url":item[1]}



    def push_remote(self,name,branch):
        if branch in self.projects[self.fix_name]["branch"] and name in self.remotes.keys():
            os.popen("git push {0} {1}".format(name,branch))
        else:
            raise ValueError("Branch or Name Abnormal")

    def pull_remote(self,name,branch):
        if name in self.remotes.keys():
            os.popen("git pull {0} {1}".format(name,branch))
        else:
            raise ValueError("Remote Error")


    def fix(self,name):
        if name in self.projects_list:
            self.fix_name = name;
            stdout, stderr = self.run("cd {0}".format(self.projects[name]["path"]))
            if self.check_error(stderr):
                print("Fixed.")
                self.fix_cmd = "cd {0}".format(self.projects[name]["path"]) + ";";
            else:
                raise ValueError("Project Path Abnormal")

    def commit(self,message):
        if self.base_path[0]:
            stdout, stderr = self.run(self.fix_cmd+"git commit --message={0}".format(message))
        else:
            raise UnboundLocalError("Init Base First")

    def get_branch(self):
        if self.base_path[0] and  self.fix_name != None:
            stdout, stderr = self.run(self.fix_cmd+"git branch")
            if self.check_error(stderr):
                reform = re.compile("\w+",)
                for branch in stdout:
                    branch_name = reform.search("*master").group().strip('\n')
                    self.projects[self.fix_name]["branch"].append(branch_name)

                    if '*' in str(branch):
                        self.projects[self.fix_name]["active_branch"] = branch_name
            else:
                print(stderr)
                raise ValueError("Command Error")

    def list_branch(self):
        for project in self.projects.items():
            for branch in project[1]["branch"]:
                if branch == project[1]["active_branch"]:
                    print("(*)",branch)
                else:
                    print("   ",branch)


if __name__ == "__main__":
    compute = git("compute.bktus.com", "/home/git", "git", "123456")
    compute.globalinit(git_user = "saturneric", git_email = "eric.bktu@gmail.com")
    compute.baseinit();
    #compute.create_project("lcs")
    compute.update_projects();
    compute.list_projects();
    compute.fix("lcs");

    #compute.get_branch("lcs")
    compute.set_local("/Users/huyibing/Documents/code/test")
    #compute.add_remote();
    #compute.get_remote()
    compute.get_branch();
    compute.list_branch();
    print(compute.projects)

