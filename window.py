from tkinter import *
from tkinter.messagebox import *
import git
import os


class Window(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.master = master
        self.master = master
        self.pack()
        self.width = 800
        self.height = 600
        self.position = [10, 10]

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_position(self, x=10, y=10):
        self.position = [x, y]

    def apply(self):
        self.master.geometry("{0}x{1}+{2}+{3}".format(self.width, self.height, self.position[0], self.position[1]))


class Info(Window):
    def __init__(self, master=None):
        super().__init__(master)
        self.information_label = Label(self)
        self.information = Entry(self)
        self.ok = Button(self)
        self.draw_widgets()

    def draw_widgets(self):
        self.information_label["text"] = "Info: "
        self.information_label.grid(row=0, column=0)
        self.information.grid(row=0, column=1)
        self.ok["text"] = "OK"
        self.ok.grid(row=0, column=2)

    def set_click(self, func):
        self.ok["command"] = func


class Main(Window):
    def __init__(self, master=None):
        super().__init__(master)
        self.connect = None
        self.hostname_label = Label(self)
        self.user_name_label = Label(self)
        self.password_label = Label(self)
        self.connection_status = Label(self)
        self.hostname = Entry(self)
        self.user_name = Entry(self)
        self.password = Entry(self)
        self.list_projects = Button(self)
        self.fix_project = Button(self)
        self.create_project = Button(self)
        self.broad = Text(self)
        self.fix_project_label = Label(self)
        self.local_path_label = Label(self)
        self.get_branch = Button(self)
        self.set_local = Button(self)
        self.add_remote = Button(self)
        self.list_remote = Button(self)
        self.clone_project = Button(self)
        self.pull = Button(self)
        self.push = Button(self)
        self.add = Button(self)
        self.commit = Button(self)
        self.fix_local = Button(self)
        self.info = None

        self.git = None
        self.draw_widget()

    def do_connect(self):
        try:
            self.git = git.Git(hostname=self.hostname.get(),
                               user=self.user_name.get(), passwd=self.password.get(),
                               path="/home/git/")
        finally:
            self.connection_status["text"] = "Failed"
            self.connection_status["fg"] = "red"
        self.connection_status["text"] = "Succeed"
        self.connection_status["fg"] = "green"
        try:
            self.git.base_init()
            self.git.update_projects()
            self.broad.insert(INSERT, "--------------------------\n")
            self.broad.insert(INSERT, "SSH Connection [Succeed]\n")
            self.broad.insert(INSERT, self.hostname.get()+"\n")
            self.broad.insert(INSERT, self.user_name.get()+"\n")
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return

    def do_list(self):
        try:
            self.git.list_projects()
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return
        self.broad.insert(INSERT, "--------------------------\n")
        self.broad.insert(INSERT, "Projects: \n")
        for project in self.git.projects.items():
            self.broad.insert(INSERT, "(*) "+project[0]+"\n")

    def new_project(self):
        self.info = Info(Tk())
        self.info.information_label["text"] = "Project Name: "
        self.info.set_click(self.new_project_callback)

    def do_fix_project(self):
        self.info = Info(Tk())
        self.info.information_label["text"] = "Project Name: "
        self.info.set_click(self.do_fix_project_callback)

    def new_project_callback(self):
        if self.info is not None:
            self.git.create_project(self.info.information.get())
            self.git.update_projects()
            self.info.master.destroy()
            self.info = None

    def do_fix_project_callback(self):
        if self.info is not None:
            try:
                self.broad.insert(INSERT, "--------------------------\n")
                self.broad.insert(INSERT, "Fixing Project {0} \n".format(self.info.information.get()))
                self.git.fix_project(self.info.information.get())
            except AttributeError as errinfo:
                showinfo(message=errinfo)
                return
            self.fix_project_label["text"] = "Fixed Project: {0}".format(self.info.information.get())
            try:
                self.git.get_remote()
                self.broad.insert(INSERT, "Get Remote...OK \n")
                if os.path.exists(os.path.join(self.git.local_path, self.git.fix_name)):
                    self.broad.insert(INSERT, "Check Local Project...OK \n")
                else:
                    self.do_clone_project()
                    self.broad.insert(INSERT, "Set Local Project...OK \n")

                self.do_fix_project_local()
                self.broad.insert(INSERT, "Fix Local Project...OK \n")
                self.git.get_branch()
                self.broad.insert(INSERT, "Get Local Project's Branches...OK \n")
                self.git.get_remote()
                self.broad.insert(INSERT, "Set Local Project's Remote...OK \n")
            except AttributeError as errinfo:
                showinfo(message=errinfo)
                return
            self.info.master.destroy()
            self.info = None

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

    def do_set_local(self):
        self.info = Info(Tk())
        self.info.information_label["text"] = "Local Path: "
        self.info.information.insert(END, "C:\\Users\\Saturneric\\Documents\\Code\\")
        self.info.set_click(self.do_set_local_callback)

    def do_set_local_callback(self):
        if self.info is not None:
            try:
                if os.path.exists(self.info.information.get()):
                    self.git.set_local(self.info.information.get())
                    self.broad.insert(INSERT, "--------------------------\n")
                    self.broad.insert(INSERT, "Set Local Path: {0}\n".format(self.info.information.get()))
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
            self.info.master.destroy()
            self.info = None

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

    def do_pull(self):
        try:
            stdout = self.git.pull_remote("origin", "master")
            self.broad.insert(INSERT, "--------------------------\n")
            self.broad.insert(INSERT, "{0}\n".format(stdout))

        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return

    def do_push(self):
        try:
            stdout = self.git.push_remote("origin", "master")
            self.broad.insert(INSERT, "--------------------------\n")
            self.broad.insert(INSERT, "{0}\n".format(stdout))
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return

    def do_add(self):
        try:
            stdout=self.git.add()
            self.broad.insert(INSERT, "--------------------------\n")
            self.broad.insert(INSERT, "{0}\n".format(stdout))
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return

    def do_fix_project_local(self):
        try:
            self.git.fix_project_local()
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
        except AttributeError as errinfo:
            showinfo(message=errinfo)
            return
        self.info.master.destroy()
        self.info = None

    def draw_widget(self):
        self.hostname_label["text"] = "Hostname: "
        self.hostname_label.grid(row=0, column=0)
        self.hostname.insert(END, "compute.bktus.com")
        self.hostname.grid(row=0, column=1)
        self.user_name_label["text"] = "Username: "
        self.user_name_label.grid(row=0, column=2)
        self.user_name.insert(END, "git")
        self.user_name.grid(row=0, column=3)
        self.password_label["text"] = "Password: "
        self.password_label.grid(row=0, column=4)
        self.password.grid(row=0, column=5)
        self.connection_status.grid(row=0, column=7)

        self.connect = Button(self)
        self.connect["text"] = "Connect"
        self.connect["command"] = self.do_connect
        self.connect.grid(row=0, column=6)

        self.list_projects["text"] = "List Projects"
        self.list_projects["command"] = self.do_list
        self.list_projects.grid(row=1, column=0)

        self.fix_project["text"] = " Fix Project "
        self.fix_project["command"] = self.do_fix_project
        self.fix_project.grid(row=2, column=0)

        self.create_project["text"] = "Create Project"
        self.create_project["command"] = self.new_project
        self.create_project.grid(row=1, column=1)

        self.fix_project_label["text"] = "Fixed Project: None"
        self.fix_project_label.grid(row=8, column=6)
        self.local_path_label["text"] = "Local Path: None"
        self.local_path_label.grid(row=9, column=0, columnspan=6)

        self.get_branch["text"] = "Get Branch"
        self.get_branch["command"] = self.do_get_branch
        self.get_branch.grid(row=3,column=0)

        self.set_local["text"] = "Set Local"
        self.set_local["command"]  = self.do_set_local
        self.set_local.grid(row=3, column=1)

        self.clone_project["text"] = "Clone Project"
        self.clone_project["command"] = self.do_clone_project
        self.clone_project.grid(row=2, column=1)

        self.add_remote["text"] = "Add Remote"
        self.add_remote["command"] = self.do_add_remote
        self.add_remote.grid(row=4, column=0)

        self.list_remote["text"] = "List Remote"
        self.list_remote["command"] = self.do_list_remote
        self.list_remote.grid(row=4, column=1)

        self.pull["text"] = "Pull"
        self.pull["command"] = self.do_pull
        self.pull.grid(row=5, column=0)

        self.push["text"] = "Push"
        self.push["command"] = self.do_push
        self.push.grid(row=5, column=1)

        self.add["text"] = "Add"
        self.add["command"] = self.do_add
        self.add.grid(row=6, column=0)

        self.commit["text"] = "Commit"
        self.commit["command"] = self.do_commit
        self.commit.grid(row=6, column=1)

        self.fix_local["text"] = "Fix Local"
        self.fix_local["command"] = self.do_fix_project_local
        self.fix_local.grid(row=7, column=0)

        self.broad.grid(row=1, column=2, columnspan=7, rowspan=6)


if __name__ == "__main__":
    root = Tk()
    main = Main(root)
    main.set_width(1150)
    main.apply()
    main.mainloop()


