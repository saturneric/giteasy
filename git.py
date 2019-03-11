import re
import os
import ssh


class Git(ssh.SSH):
    projects = {}
    projects_list = []
    remotes = {}
    if_set_local = False
    if_global_init = False
    if_global_init_local = False
    if_base_init = False
    if_fix_project = False
    if_fix_local = False
    if_get_branches = False
    if_get_remote = False
    if_fetch_remote = False
    if_get_project = False
    if_connected = False

    def __init__(self, hostname, path, user, passwd):
        super().__init__(hostname, path, user, passwd)
        self.base_path = [False]
        self.connect(5)
        self.if_connected = True
        self.local_path = None
        self.fix_cmd = None
        self.fix_name = None
        self.git_user = None
        self.git_email = None

    def global_init(self, git_user, git_email):
        self.git_user = git_user
        self.git_email = git_email
        cmd = "git config --global user.email \"{0}\";".format(git_email)
        cmd += "git config --global user.name \"{0}\";".format(git_user)
        stdout, stderr = self.run(cmd)
        if self.check_error(stderr):
            print("Global Setting Successful.")
            self.if_global_init = True
        else:
            print(stderr)
            raise ValueError("Args Error")

    def base_init(self):
        if self.if_connected:
            stdout, stderr = self.run("ls {}".format(self.path))
            if self.check_error(stderr):
                if "giteasy\n" in stdout:
                    print("Directory Already Found.")
                else:
                    stdout, stderr = self.run("mkdir {0}/{1}".format(self.path, "giteasy"))
                    if self.check_error(stderr):
                        print("Create directory.")
                    else:
                        raise ValueError(stderr)
                self.base_path = [True, "{0}{1}".format(self.path, "giteasy")]
                self.if_base_init = True
            else:
                raise ValueError("Path Error")
        else:
            raise AttributeError("Connect First.")

    def create_project(self, name):
        if self.if_base_init:
            if os.path.exists("{0}/{1}.git".format(self.base_path[1], name)):
                print("Server Project Already Exist.")
            else:
                stdout, stderr = self.run("mkdir {0}/{1}.git".format(self.base_path[1], name))
                if self.check_error(stderr):
                    print("Succeed In Making Directory.")
                    self.projects[name] = {"path": "{0}/{1}".format(self.base_path[1], name), "branch": []}
                    cmd = "cd {0}.git;".format(self.projects[name]["path"])
                    cmd += "git init --bare;"
                    stdout, stderr = self.run(cmd)
                    if self.check_error(stderr):
                        print("Succeed In Getting Repository.")
                    else:
                        print(stderr)
                        raise ValueError("Target Path Abnormal")
                else:
                    raise ValueError("Path Error.")
        else:
            raise AttributeError("Set Base Path First.")

    def clone_project(self):
        if self.if_set_local and self.if_connected:
            os.chdir(self.local_path)
            os.popen("git clone ssh://{0}@{1}:{2}/{3}".format(self.user, self.hostname, self.base_path[1],
                                                                   self.fix_name))
        else:
            raise AttributeError("Connect & Set Local First.")

    def fix_project_local(self):
        if self.if_set_local and self.if_fix_project:
            os.chdir(os.path.join(self.local_path, self.fix_name))
            self.if_fix_local = True
        else:
            raise AttributeError("Set Local & Fix Project First.")

    def init_project_local(self, name):
        if self.if_set_local:
            os.chdir(self.local_path)
            try:
                os.mkdir(name)
            except FileExistsError:
                os.chdir(os.path.join(self.local_path, name))
                print("Local Project Already Exist.")
            os.chdir(os.path.join(self.local_path, name))
            cmd = "git init"
            readme = open(os.path.join(self.local_path, name,"ReadME.md"),"w")
            readme.write("#Default Project Introduction.#\n")
            readme.close()
            cmd += "git add *"
            cmd += "git commit --message=\"Initial Commit\""
            os.popen(cmd)
        else:
            raise AttributeError("Set Local First.")

    def global_init_local(self):
        cmd = "git config --global user.email \"{0}\"".format(self.git_email)
        print(os.popen(cmd).read())
        cmd = "git config --global user.name \"{0}\"".format(self.git_user)
        print(os.popen(cmd).read())
        self.if_global_init = True

    def update_projects(self):
        if self.base_path[0]:
            stdout, stderr = self.run("ls {0}".format(self.base_path[1]))
            if self.check_error(stderr):
                reform = re.compile("\w+")
                for project in stdout:
                    project_name = reform.match(project).string.strip('\n')
                    self.projects[project_name] = {"path": "{0}/{1}".format(self.base_path[1], project_name),
                                                   "branch": []}
                self.if_get_project = True
            else:
                raise ValueError("Base Path Abnormal")

            self.list_projects()

        else:
            raise UnboundLocalError("Init Base First")

    def list_projects(self):
        if self.if_get_project:
            for project in self.projects.keys():
                self.projects_list.append(project)
        else:
            raise AttributeError("Get Project First.")

    def set_local(self, path):
        if self.if_connected:
            self.remotes = {}
            self.local_path = path
            self.if_set_local = True
            os.chdir(self.local_path)
        else:
            raise AttributeError("Connect First.")
    def add_remote(self, name="origin"):
        if self.if_base_init and self.if_get_project and self.if_fix_project:
            stdout = os.popen("git remote add {3} ssh://{0}@{1}:{2}/{4}.git".format(self.user, self.hostname,
                                                                                    self.base_path[1],
                                                                                    name, self.fix_name)).read()
            self.remotes[name] = {"name": name,
                                  "url": "ssh://{0}@{1}:{2}/{3}.git".format(self.user, self.hostname, self.base_path[1],
                                                                            self.fix_name)}

            self.if_get_remote = True
            return stdout
        else:
            raise AttributeError("Get Project & Base Init & Fix Project First.")

    def fetch_remote(self, name):
        if self.if_fix_project and self.if_base_init and self.if_set_local:
            if name in self.remotes.keys():
                os.popen("git fetch {0}".format(name))
                self.if_fetch_remote = True
        else:
            raise AttributeError("Set Local & Fix Project & Base Init First.")

    def get_remote(self):
        if self.if_fix_project and self.if_base_init and self.if_set_local:
            ret_code = re.compile(r"[\t, ]")
            for remote in os.popen("git remote -v").readlines():
                results = ret_code.split(remote)
                results = list(results)
                if len(results) >= 1:
                    self.remotes = {}
                    for item in results:
                        if item[0] not in self.remotes.keys():
                            self.remotes[results[0]] = {"name": results[0], "url": results[1]}
                    self.if_get_remote = True
        else:
            raise AttributeError("Set Local & Fix Project & Base Init First.")

    def push_remote(self, name, branch):
        if self.if_fix_project and self.if_base_init and self.if_set_local \
                and self.if_get_remote:
            if name in self.remotes.keys():
                return os.popen("git push {0} {1}".format(name, branch)).read()
            else:
                raise ValueError("Name Abnormal")
        else:
            raise AttributeError("Set Local & Fix Project & Base Init & Get Remote First.")

    def pull_remote(self, name, branch):
        if self.if_fix_project and self.if_base_init and self.if_set_local \
                and self.if_get_remote:
            if name in self.remotes.keys():
                return os.popen("git pull {0} {1}".format(name, branch)).read()
            else:
                raise ValueError("Remote Error")
        else:
            raise AttributeError("Set Local & Fix Project & Base Init & Get Remote & Get Branches First.")

    def fix_project(self, name):
        if self.if_get_project and self.if_base_init:
            if name+".git" in self.projects_list:
                self.fix_name = name
                stdout, stderr = self.run("cd {0}".format(self.projects[name+".git"]["path"]))
                if self.check_error(stderr):
                    self.fix_cmd = "cd {0}".format(self.projects[name+".git"]["path"]) + ";"
                    self.if_fix_project = True
                else:
                    raise ValueError("Project Path Abnormal")
        else:
            raise AttributeError("Get Project & Base Init First.")

    def commit_local(self, message):
        if self.if_set_local and self.if_fix_local and self.if_base_init:
            if self.base_path[0]:
                stdout = os.popen("git commit --message={0}".format(message)).read()
                return stdout
            else:
                raise UnboundLocalError("Init Base First")
        else:
            raise AttributeError("Set Local & Fix Local & Base Init First.")

    def add(self):
        if self.if_set_local and self.if_fix_local and self.if_base_init:
            stdout = os.popen("git add *")
            return stdout
        else:
            raise AttributeError("Set Local & Fix Local & Base Init First.")

    def get_branch(self):
        if self.if_get_project and self.if_base_init and self.if_fix_local:
            stdout = os.popen("git branch").read()
            self.projects[self.fix_name+".git"]["branch"] = []
            reform = re.compile("\w+")
            for branch in stdout:
                branch_name = reform.search("*master").group().strip('\n')
                self.projects[self.fix_name+".git"]["branch"].append(branch_name)

                if '*' in str(branch):
                    self.projects[self.fix_name+".git"]["active_branch"] = branch_name
            self.if_get_branches = True
        else:
            raise AttributeError("Get Project & Base Init & Fix Local First.")

    def list_branch(self):
        if self.if_get_branches:
            for project in self.projects.items():
                for branch in project[1]["branch"]:
                    if branch == project[1]["active_branch"]:
                        print("(*)", branch)
                    else:
                        print("   ", branch)


if __name__ == "__main__":
    compute = Git("compute.bktus.com", "/home/git", "git", "123456")
    compute.global_init(git_user="saturneric", git_email="eric.bktu@gmail.com")
    compute.global_init_local()
    compute.base_init()
    # compute.create_project("lcs")
    compute.update_projects()
    compute.list_projects()
    compute.fix_project("lcs")
    compute.get_branch()
    compute.set_local("C:\\Users\\Saturneric\\Documents\\Code\\")
    # compute.init_project_local("test")
    compute.add_remote()
    compute.get_remote()
    compute.list_branch()
