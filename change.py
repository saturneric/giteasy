from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
import os
import window
import info


class Changes(window.Window):
    def __init__(self, master=None, broad=None):
        super().__init__(master)
        super().set_position(50,50)
        super().set_width(870)
        super().apply()
        master.title("Changes Manager")
        self.list = Listbox(self, width=35, height=30)
        self.text = Text(self, width=75, height=35)
        self.sb = Scrollbar(self)
        self.discard = Button(self, width=18)
        self.commit = Button(self, width=12)
        self.message = Entry(self, width=40)
        self.draw_widgets()
        self.change_files =[]
        self.discard_status = []
        self.list.bind("<<ListboxSelect>>",self.show_change)
        self.current_index = None
        self.broad = broad
        self.list_bak = []

    def draw_widgets(self):
        self.list.grid(row=0, column=0)
        self.text.grid(row=0, column=1)
        self.sb.grid(row=0, column=2, rowspan=2, sticky=W)
        self.text.config(yscrollcommand=self.sb)
        self.discard["command"] = self.discard_change
        self.discard['text'] = 'Discard'
        self.discard.grid(row=1, column=0, sticky=E)
        self.commit["text"] = "Commit"
        self.commit.grid(row=1, column=1, sticky=E)
        self.message.grid(row=1, column=1, sticky=W)
        self.message.insert(INSERT,"Default Commit.")
        self.commit["command"] = self.do_commit
        self.text.tag_configure('ADD',foreground="#00FF7F",font=('Verdana', 12))
        self.text.tag_configure('DEL', foreground="#DC143C",font=('Verdana', 12))
        self.text.tag_configure('INFO', foreground="#87CEEB",font=('Verdana', 12))
        self.text.tag_configure('TITLE', font=('Verdana', 12, 'bold'))
        self.text.tag_configure('DATA', font=('Verdana', 12))

    def discard_change(self):
        if self.current_index is not None:
            if self.discard_status[self.current_index]:
                os.popen("git checkout -- {0}".format(self.change_files[self.current_index]))
                self.discard_status[self.current_index] = False
                self.discard['text'] = 'Add'
            else:
                os.popen("git add {0}".format(self.change_files[self.current_index]))
                self.discard_status[self.current_index] = True
                self.discard['text'] = 'Discard'
        else:
            raise ValueError("Current_Index Is None.")

    def do_commit(self):
        stdout = os.popen("git commit --message=\"{0}\"".format(self.message.get())).read()
        self.broad.insert(INSERT, "--------------------------\n")
        self.broad.insert(INSERT, "{0}\n".format(stdout))
        self.broad.see(END)
        self.master.destroy()


    def show_change(self, *args):
        if len(self.list_bak) > 0:
            self.current_index = self.list.curselection()[0]
            if self.discard_status[self.current_index]:
                self.discard['text'] = 'Discard'
            else:
                self.discard['text'] = 'Add'

            stdout = os.popen("git diff --cached {0}".format(self.change_files[self.current_index])).read()
            self.text.delete('1.0', END)
            self.text.insert(INSERT,self.change_files[self.current_index]+"\n","TITLE")
            self.text.insert(INSERT, "-----------------------------------------------\n","TITLE")
            if_data = False
            lines = []
            str = ""
            for char in stdout:
                if char is not '\n':
                    str += char
                else:
                    lines.append(str)
                    str = ""
            for line in lines:
                if line[0] is '@':
                    if_data = True
                if line[0] is '+' and if_data:
                    self.text.insert(INSERT,line+"\n","ADD")
                elif line[0] is '-' and if_data:
                    self.text.insert(INSERT, line + "\n", "DEL")
                elif line[0] is '@':
                    self.text.insert(INSERT, line + "\n", "INFO")
                else:
                    if if_data:
                        self.text.insert(INSERT, line + "\n","DATA")
                    else:
                        self.text.insert(INSERT, line + "\n","TITLE")

            self.text.see(END)

    def set_list(self, list):
        for item in list:
            self.list.insert(END, item)
            self.list_bak =list
            ret_code = re.compile(r"[:]")
            tmp_ret = ret_code.split(item)
            self.change_files.append(tmp_ret[1])
            self.discard_status.append(True)