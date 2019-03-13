from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
import json
import git
import os
import window
from info import *
from change import  *
from sshtool import *
from branchmanager import *
from gitignore import *
import paramiko

default_pwd = os.getcwd()

class Main(window.Window):
    def __init__(self, master=None):
        super().__init__(master)
        master.title("GitEasy")
        self.style.configure("M.MButton",)
        self.connect = None
        self.hostname_label = Label(self, width=10)
        self.user_name_label = Label(self, width=12)
        self.password_label = Label(self, width=8)
        self.connection_status = Label(self, width=8)
        self.hostname = Entry(self, width=15)
        self.user_name = Entry(self, width=15)
        self.password = Entry(self, width=15, show="*")
        self.list_projects = Button(self, width=13)
        self.fix_project = Button(self, width=12)
        self.create_project = Button(self, width=12)
        self.broad = Text(self, width=85, height=30)
        self.fix_project_label = Label(self, width=15)
        self.local_path_label = Label(self, width=25)
        self.branches = Button(self, width=12)
        self.set_local = Button(self, width=12)
        self.add_remote = Button(self, width=12)
        self.list_remote = Button(self, width=12)
        self.clone_project = Button(self, width=13)
        self.project_status = Button(self, width=12)
        self.pull = Button(self, width=12)
        self.push = Button(self, width=12)
        self.add = Button(self, width=12)
        self.commit = Button(self, width=12)
        self.save = Button(self, width=15)
        self.ssh_tools = Button(self, width=12)
        self.gitignore = Button(self, width=12)
        self.info = None
        self.save_info = None

        self.git = None
        self.draw_widget()

        if os.path.exists(os.path.join(os.path.expanduser('~'),"save_data.json")):
            self.get_save_data()

    def get_save_data(self):
        save_file = open(os.path.join(os.path.expanduser('~'),"save_data.json"),"r")
        json_data = save_file.readline()
        save_infos = json.loads(json_data)
        self.save_info = save_infos[0]
        self.broad.insert(INSERT, "--------------------------\n")
        self.broad.insert(INSERT, "Get Saved Data\n")
        self.broad.insert(INSERT, "Hostname: {0}\n".format(self.save_info["hostname"]))
        self.broad.insert(INSERT, "User: {0}\n".format(self.save_info["user"]))
        self.broad.insert(INSERT, "Local Path: {0}\n".format(self.save_info["local_path"]))
        self.broad.insert(INSERT, "Fix Project: {0}\n".format(self.save_info["fix_project"]))

        self.user_name.insert(INSERT, self.save_info["user"])
        self.hostname.insert(INSERT, self.save_info["hostname"])
        self.password.insert(INSERT, self.save_info["password"])
        self.do_connect()

    def do_connect(self):
        if self.git is None:
            try:
                self.git = git.Git(hostname=self.hostname.get(),
                                   user=self.user_name.get(), passwd=self.password.get(),
                                   path="/home/git/")
            except paramiko.ssh_exception.AuthenticationException:
                self.connection_status["text"] = "Failed"
                showinfo(message="Authentication failed.")
                return

            except paramiko.ssh_exception.BadHostKeyException:
                self.connection_status["text"] = "Failed"
                showinfo(message="Bad HostKey.")
                return
            except paramiko.ssh_exception.SSHException:
                self.connection_status["text"] = "Failed"
                showinfo(message="There was any other error connecting or establishing an SSH session.")
                return
            except paramiko.socket.error:
                self.connection_status["text"] = "Failed"
                showinfo(message="A socket error occurred while connecting.")
                return

            self.connection_status["text"] = "Succeed"

            try:
                self.git.base_init()
                self.git.update_projects()
                self.broad.insert(INSERT, "--------------------------\n")
                self.broad.insert(INSERT, "SSH Connection [Succeed]\n")
                self.broad.insert(INSERT, "Hostame: "+self.hostname.get()+"\n")
                self.broad.insert(INSERT, "User: "+self.user_name.get()+"\n")
                if self.save_info is not None:
                    self.git.set_local(self.save_info["local_path"])
                    self.broad.insert(INSERT, "Set Local Path...OK" + "\n")
                    self.local_path_label["text"] = "Local Path:"+self.save_info["local_path"]

                    self.git.update_projects()
                    self.git.list_projects()
                    if self.save_info["fix_project"]+".git" in self.git.projects_list:
                        self.broad.insert(INSERT, "--------------------------\n")
                        self.broad.insert(INSERT, "Auto Fix Project ({0})\n".format(self.save_info["fix_project"] + ".git"))
                        self.git.fix_project(self.save_info["fix_project"])
                        self.fix_local_plus()
                        self.broad.see(END)
                        self.fix_project_label["text"] = "Fixed Project: {0}".format(self.save_info["fix_project"])

                self.broad.see(END)

            except AttributeError as errinfo:
                showinfo(message=errinfo)
                return

    def do_list(self):
        try:
            self.git.update_projects()
            self.git.list_projects()
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return
        self.broad.insert(INSERT, "--------------------------\n")
        self.broad.insert(INSERT, "Projects In Server: \n")
        for project in self.git.projects.items():
            self.broad.insert(INSERT, "(*) "+project[0]+"\n")
        self.broad.see(END)

    def new_project(self):
        self.info = Info(Tk())
        self.info.information_label["text"] = "New Project Name: "
        self.info.set_click(self.new_project_callback)

    def do_fix_project(self):
        if self.git.if_set_local:
            self.info = Info(Tk(),"Combobox")
            self.info.information_label["text"] = "Select Project: "
            self.info.information["value"] = self.git.projects_list
            if len(self.git.projects_list) > 0:
                self.info.information.current(0)

            self.info.set_click(self.do_fix_project_callback)
        else:
            showinfo(message="Please Set Local Path First.")

    def destroy_info(self):
        self.info.master.eval('::ttk::CancelRepeat')
        self.info.master.destroy()
        self.info = None

    def new_project_callback(self):
        if self.info is not None:
            try:
                self.git.create_project(self.info.information.get())
                self.git.update_projects()
            except AttributeError as errinfo:
                showinfo(message=errinfo)
                return

            self.broad.insert(INSERT, "--------------------------\n")
            self.broad.insert(INSERT, "New Project {0} \n".format(self.info.information.get()))
            self.broad.see(END)
            self.info.master.protocol("WM_DELETE_WINDOW", self.destroy_info)
            self.info.master.destroy()

    def do_fix_project_callback(self):
        if self.info is not None:
            try:
                self.broad.insert(INSERT, "--------------------------\n")
                fix_name_raw = self.info.information.get()
                fix_name = fix_name_raw[0:len(fix_name_raw)-4];
                self.broad.insert(INSERT, "Fixing Project {0} \n".format(fix_name))
                self.git.fix_project(fix_name)
            except AttributeError as errinfo:
                showinfo(message=errinfo)
                return
            self.fix_project_label["text"] = "Fixed Project: {0}".format(self.info.information.get())
            self.fix_local_plus()
            self.info.master.protocol("WM_DELETE_WINDOW", self.destroy_info)
            self.info.master.destroy()

    def fix_local_plus(self):
        try:
            if os.path.exists(os.path.join(self.git.local_path, self.git.fix_name)) and self.git.if_set_local:
                self.broad.insert(INSERT, "Check Local Project...OK \n")
            else:
                self.do_clone_project()
                self.broad.insert(INSERT, "Set Local Project...OK \n")

            self.do_fix_project_local()
            self.broad.insert(INSERT, "Fix Local Project...OK \n")
            self.git.get_remote()
            if "origin" not in self.git.remotes.keys():
                self.git.add_remote("origin")
            self.broad.insert(INSERT, "Get Local Project's Remote...OK \n")

            self.git.fetch_remote("origin")
            self.broad.insert(INSERT, "Fetch Server Project...OK \n")
            self.git.get_branch()
            self.broad.insert(INSERT, "Get Local Project's Branches...OK \n")
            self.broad.see(END)
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return

    def do_get_branch(self):
        try:
            self.git.get_branch()
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return
        self.broad.insert(INSERT, "--------------------------\n")
        self.broad.insert(INSERT, "Branches: \n")
        for branch in self.git.projects[self.git.fix_name+".git"]["branch"]:
            print(branch)
            self.broad.insert(INSERT, "(*) " + branch + "\n")
        self.broad.see(END)

    def do_set_local(self):
        self.info = Info(Tk())
        self.info.information_label["text"] = "Local Path: "
        self.info.information.insert(END, "")
        self.info.set_click(self.do_set_local_callback)

    def do_fix_project_local(self):
        try:
            self.git.fix_project_local()
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return

    def do_set_local_callback(self):
        if self.info is not None:
            try:
                if os.path.exists(self.info.information.get()):
                    self.git.set_local(self.info.information.get())
                    self.broad.insert(INSERT, "--------------------------\n")
                    self.broad.insert(INSERT, "Local Path: {0}\n".format(self.info.information.get()))
                    self.broad.see(END)
                else:
                    showinfo(message="{0} not exists.".format(self.info.information.get()))
                    return
            except AttributeError as errinfo:
                showinfo(message=errinfo)
                return
            except FileNotFoundError as errinfo:
                showinfo(message=errinfo)
                return
            self.local_path_label["text"] = "Local Path: {0}".format(self.info.information.get())
            self.info.master.protocol("WM_DELETE_WINDOW", self.destroy_info)
            self.info.master.destroy()

    def do_clone_project(self):
        self.git.init_project_local(self.git.fix_name)
        # self.git.add_remote()

    def do_add_remote(self):
        try:
            self.git.add_remote("origin")
        except AttributeError as errinfo:
            showinfo(errinfo)
            return

    def do_list_remote(self):
        try:
            self.git.get_remote()
        except AttributeError as errinfo:
            showinfo(errinfo)
            return
        self.broad.insert(INSERT, "--------------------------\n")
        self.broad.insert(INSERT, "Remotes: \n")
        for remote in self.git.remotes.items():
            print(remote)
            self.broad.insert(INSERT, "(*) " + remote[1]["name"] + " " + remote[1]["url"] + "\n")
        self.broad.see(END)

    def do_pull(self):
        try:
            self.git.get_branch()
            stdout = self.git.pull_remote("origin", self.git.projects[self.git.fix_name+".git"]["active_branch"])
            self.broad.insert(INSERT, "--------------------------\n")
            self.broad.insert(INSERT, "Pull Action\n")
            self.broad.insert(INSERT, "{0}\n".format(stdout))
            self.broad.see(END)
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return

    def do_push(self):
        try:
            self.git.get_branch()
            print("Active Branch:",self.git.projects[self.git.fix_name+".git"]["active_branch"])
            stdout = self.git.push_remote("origin", self.git.projects[self.git.fix_name+".git"]["active_branch"])
            self.broad.insert(INSERT, "--------------------------\n")
            self.broad.insert(INSERT, "Push Action\n")
            self.broad.insert(INSERT, "{0}\n".format(stdout))
            self.broad.see(END)
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return

    def do_add(self):
        if self.git is not None and self.git.if_fix_local:
            try:
                stdout=self.git.add()
                self.broad.insert(INSERT, "--------------------------\n")
                self.broad.insert(INSERT, "{0}\n".format(stdout))
                self.broad.see(END)
                self.changes_info = Changes(Tk(),self.broad)
                self.changes_info.set_list(self.git.get_changes())
            except AttributeError as errinfo:
                showinfo(message=errinfo)
                return
        else:
            showinfo(message="Connect and Fix Local Project First")

    def do_save(self):
        save_infos = []
        try:
            if self.git.if_set_local and self.git.if_connected:
                save_info = {}
                save_info["local_path"] = self.git.local_path
                save_info["user"] = self.git.ssh_user
                save_info["hostname"] = self.git.ssh_hostname
                save_info["password"] = self.git.passwd
                save_info["fix_project"] = self.git.fix_name
                save_infos.append(save_info)
                json_info = json.dumps(save_infos)
                save_file = open(os.path.join(os.path.expanduser('~'),"save_data.json"),"w")
                save_file.write(json_info)
                save_file.close()
                self.broad.insert(INSERT, "--------------------------\n")
                self.broad.insert(INSERT, "Data Information Saved\n")
                self.broad.insert(INSERT, "Path: "+os.path.join(os.path.expanduser('~'), "save_data.json"))
                self.broad.see(END)
            else:
                raise AttributeError("Please Connect And Set Local Path First.")
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return

    def do_commit(self):
        self.info = Info(Tk())
        self.info.information_label["text"] = "Local Path: "
        self.info.information.insert(END, "Default")
        self.info.set_click(self.do_commit_callback)

    def do_commit_callback(self):
        try:
            stdout=self.git.commit_local(self.info.information.get())
            self.broad.insert(INSERT, "--------------------------\n")
            self.broad.insert(INSERT, "{0}\n".format(stdout))
            self.broad.see(END)
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return
        self.info.master.destroy()
        self.info = None

    def do_status(self):
        self.broad.insert(INSERT, "--------------------------\n")
        self.broad.insert(INSERT, "{0}\n".format(self.git.status()))
        self.broad.see(END)

    def start_ssh_tools(self):
        if self.git is not None:
            self.ssh_interface = SSH_Tools(master=Tk(), broad=self.broad,
                                           hostname=self.git.ssh_hostname, user=self.git.ssh_user,
                                           passwd= self.git.passwd, path=self.git.path)
        else:
            showinfo(message="Connect First")

    def start_branch_manager(self):
        if self.git is not None and self.git.if_fix_local:
            self.branch_interface = Branch(master=Tk())
        else:
            showinfo(message="Connect and Fix Local Project First")

    def start_git_ignore(self):
        if self.git is not None and self.git.if_fix_local:
            self.git.set_ignore()
            self.gitignore_interface = Gitignore(master=Tk())
        else:
            showinfo(message="Connect and Fix Local Project First")

    def draw_widget(self):
        self.hostname_label["text"] = "Hostname: "
        self.hostname_label.grid(row=0, column=0, sticky=W)
        self.hostname.grid(row=0, column=1, sticky=W)
        self.user_name_label["text"] = "Username: "
        self.user_name_label.grid(row=0, column=2, sticky=W)
        self.user_name.grid(row=0, column=3, sticky=W)
        self.password_label["text"] = "Password: "
        self.password_label.grid(row=0, column=4, sticky=W)
        self.password.grid(row=0, column=5, sticky=W)
        self.connection_status.grid(row=9, column=6)

        self.connect = Button(self)
        self.connect["text"] = "Connect"
        self.connect["command"] = self.do_connect
        self.connect.grid(row=0, column=6)

        self.list_projects["text"] = "Server Projects"
        self.list_projects["command"] = self.do_list
        self.list_projects.grid(row=1, column=0)

        self.fix_project["text"] = "Fix Project"
        self.fix_project["command"] = self.do_fix_project
        self.fix_project.grid(row=2, column=0)

        self.create_project["text"] = "Create Project"
        self.create_project["command"] = self.new_project
        self.create_project.grid(row=1, column=1)

        self.fix_project_label["text"] = "Fixed Project: None"
        self.fix_project_label.grid(row=8, column=6, sticky=W)
        self.local_path_label["text"] = "Local Path: None"
        self.local_path_label.grid(row=9, column=0, columnspan=2, sticky=W)

        self.branches["text"] = "Branches"
        self.branches["command"] = self.start_branch_manager
        self.branches.grid(row=2,column=1)

        self.set_local["text"] = "Set Local Path"
        self.set_local["command"]  = self.do_set_local
        self.set_local.grid(row=7, column=1)

        # self.clone_project["text"] = "Clone Project"
        # self.clone_project["command"] = self.do_clone_project
        # self.clone_project.grid(row=2, column=1)

        # self.add_remote["text"] = "Add Remote"
        # self.add_remote["command"] = self.do_add_remote
        # self.add_remote.grid(row=4, column=0)

        # self.list_remote["text"] = "List Remote"
        # self.list_remote["command"] = self.do_list_remote
        # self.list_remote.grid(row=4, column=1)

        self.gitignore["text"] = "Git Ignore"
        self.gitignore["command"] = self.start_git_ignore
        self.gitignore.grid(row=4, column=1)

        self.pull["text"] = "Pull"
        self.pull["command"] = self.do_pull
        self.pull.grid(row=3, column=0)

        self.push["text"] = "Push"
        self.push["command"] = self.do_push
        self.push.grid(row=3, column=1)

        self.add["text"] = "Add"
        self.add["command"] = self.do_add
        self.add.grid(row=4, column=0)


        self.save["text"] = "Save Information"
        self.save["command"] = self.do_save
        self.save.grid(row=5, column=0)

        self.project_status["text"] = "Status"
        self.project_status["command"] = self.do_status
        self.project_status.grid(row=5, column=1)

        self.ssh_tools["text"] = "SSH Tools"
        self.ssh_tools["command"] = self.start_ssh_tools
        self.ssh_tools.grid(row=7, column=0)

        self.broad.grid(row=1, column=2, columnspan=7, rowspan=6)


if __name__ == "__main__":
    root = Tk()
    main = Main(root)
    main.set_width(930)
    main.set_height(560)
    main.apply()
    main.mainloop()