from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
import os
from keygen import *
import window


class SSH_Tools(window.Window,Key):
    def __init__(self, hostname, user, passwd, path, master=None, broad=None):
        window.Window.__init__(self,master)
        master.title("SSH Manager")
        Key.__init__(self,hostname=hostname, user=user, password=passwd, path=path)
        self.broad = broad
        self.hostname = hostname
        self.user = user
        self.add_btn = Button(self, width=12)
        self.set_btn = Button(self, width=12)
        self.check_btn = Button(self, width=12)
        self.draw_window()

    def do_add_key(self):
        stdout = self.create_key()
        self.broad.insert(INSERT, "--------------------------\n")
        self.broad.insert(INSERT, "{0}\n".format(stdout))
        self.broad.see(END)

    def do_set_key(self):
        stdout = self.get_key()
        self.broad.insert(INSERT, "--------------------------\n")
        self.broad.insert(INSERT, "{0}\n".format(stdout))
        stdout = self.add_key()
        self.broad.see(END)

    def do_check_key(self):
        ret_code = subprocess.Popen("ssh -o StrictHostKeyChecking=no -T {0}@{1}".format(self.user, self.hostname),
                                    shell=False,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE
                                    )
        stdout, stderr = ret_code.communicate(input=b"\x03")
        self.broad.insert(INSERT, "--------------------------\n")
        self.broad.insert(INSERT, "{0}\n".format(stdout.decode("utf-8")))
        self.broad.see(END)


    def draw_window(self):
        self.add_btn["text"] = "New Key"
        self.set_btn["text"] = "Set Key"
        self.check_btn["text"] = "Check Key"

        self.add_btn["command"] = self.do_add_key
        self.set_btn["command"] = self.do_set_key
        self.check_btn["command"] = self.do_check_key
        self.add_btn.grid(row=0,column=0)
        self.set_btn.grid(row=1, column=0)
        self.check_btn.grid(row=2, column=0)

