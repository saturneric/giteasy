from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
import os
from keygen import *
import window
from info import Info


class Branch(window.Window):
    def __init__(self, master):
        super().__init__(master)
        master.title("Branch Manager")
        super().set_height(350)
        super().set_width(480)
        super().set_position(350, 200)
        super().apply()

        self.master = master
        self.text = Text(self)
        self.list_btn = Button(self, width=12)
        self.add_btn = Button(self, width=12)
        self.checkout_btn = Button(self, width=12)
        self.merge_btn = Button(self, width=12)
        self.merge_list_btn = Button(self, width=12)
        self.delete_btn = Button(self, width=12)
        self.draw_widgets()
        self.branches = []
        self.current_branches = None
        self.info = None
        self.get_branches()

    def draw_widgets(self):
        self.text.grid(row=0,column=1,rowspan=8)
        self.list_btn["text"] = "List"
        self.checkout_btn["text"] = "Checkout"
        self.merge_btn["text"] = "Merge"
        self.merge_list_btn["text"] = "Merge List"
        self.delete_btn["text"] = "Delete"
        self.add_btn["text"] = "Add"

        self.list_btn["command"] = self.do_list
        self.add_btn["command"] = self.do_add
        self.checkout_btn["command"] = self.do_checkout
        self.merge_btn["command"] = self.do_merge
        self.merge_list_btn["command"] = self.do_merge_list
        self.delete_btn["command"] = self.do_delete

        self.list_btn.grid(row=0,column=0)
        self.add_btn.grid(row=1, column=0)
        self.checkout_btn.grid(row=2,column=0)
        self.merge_btn.grid(row=3, column=0)
        self.merge_list_btn.grid(row=4, column=0)
        self.delete_btn.grid(row=5, column=0)
        self.text.insert(INSERT, "Branch Manager Interface\n")
        self.text.insert(INSERT,"-----------------------------------\n")

    def get_branches(self):
        stdout = os.popen("git branch -v").read()
        self.current_branches = None
        self.branches = []
        lines = []
        str = ""
        for char in stdout:
            if char is '\n':
                lines.append(str)
                str = ""
            else:
                str += char

        for line in lines:
            branch_info = re.split(r"[ ]+",line)
            print(branch_info)
            if len(branch_info) > 3:
                if branch_info[0] is '*':
                    self.current_branches = branch_info[1]
                self.branches.append(branch_info[1])

    def do_merge_list(self):
        stdout = os.popen("git branch --merged").read()
        proc = subprocess.Popen("git branch --merged", shell=True,
                                stderr=subprocess.STDOUT,
                                stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate(timeout=3)
        self.text.insert(INSERT, "-----------------------------------\n")
        self.text.insert(INSERT, "Merged Branches\n")
        self.text.insert(INSERT, stdout.decode("utf-8") + "\n")
        self.text.insert(INSERT, "-----------------------------------\n")
        self.text.insert(INSERT, "Unmerged Branches\n")
        proc = subprocess.Popen("git branch --no-merged", shell=True,
                                stderr=subprocess.STDOUT,
                                stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate(timeout=3)
        self.text.insert(INSERT, stdout.decode("utf-8") + "\n")
        self.text.see(END)

    def do_list(self):
        stdout = os.popen("git branch -v").read()
        self.text.insert(INSERT, "-----------------------------------\n")
        self.text.insert(INSERT, stdout+"\n")
        self.text.see(END)

    def do_add(self):
        self.get_branches()
        self.info = Info(Tk())
        self.info.set_click(self.do_add_callback)

    def do_add_callback(self):
        stdout = os.popen("git branch {0}".format(self.info.information.get())).read()
        self.text.insert(INSERT, "-----------------------------------\n")
        self.text.insert(INSERT, "New Branch {0}\n".format(self.info.information.get()))
        self.text.insert(INSERT, stdout + "\n")
        self.text.see(END)
        self.info.master.protocol("WM_DELETE_WINDOW", self.destroy_info)
        self.info.master.destroy()
        self.info = None

    def do_checkout(self):
        self.get_branches()
        self.info = Info(Tk(), "Combobox")
        self.info.information["value"] = self.branches
        self.info.set_click(self.do_checkout_callback)

    def do_checkout_callback(self):
        stdout = os.popen("git checkout {0}".format(self.info.information.get())).read()
        self.text.insert(INSERT, "-----------------------------------\n")
        self.text.insert(INSERT, "Checkout Branch {0}\n".format(self.info.information.get()))
        self.text.insert(INSERT, stdout + "\n")
        self.text.see(END)
        self.info.master.protocol("WM_DELETE_WINDOW", self.destroy_info)
        self.info.master.destroy()
        self.info = None

    def do_merge(self):
        self.get_branches()
        self.info = Info(Tk(), "Combobox")
        branches_tmp = self.branches
        branches_tmp.remove(self.current_branches)
        self.info.information["value"] = branches_tmp
        self.info.set_click(self.do_merge_callback)

    def do_merge_callback(self):
        stdout = os.popen("git merge {0}".format(self.info.information.get())).read()
        self.text.insert(INSERT, "-----------------------------------\n")
        self.text.insert(INSERT, "Merge Branch From {0} To {1}\n"
                         .format(self.current_branches,self.info.information.get()))
        if len(stdout) > 4:
            self.text.insert(INSERT, stdout + "\n")
        else:
            self.text.insert(INSERT, "Merge Failed. Please check conflict.\n")
        self.text.see(END)
        self.info.master.protocol("WM_DELETE_WINDOW", self.destroy_info)
        self.info.master.destroy()
        self.info = None


    def do_delete(self):
        self.get_branches()
        self.info = Info(Tk(), "Combobox")
        self.info.information["value"] = self.branches
        self.info.set_click(self.do_delete_callback)

    def do_delete_callback(self):
        stdout = os.popen("git branch -d {0}".format(self.info.information.get())).read()
        self.text.insert(INSERT, "-----------------------------------\n")
        self.text.insert(INSERT, "Delete Branch {0}\n".format(self.info.information.get()))
        if self.info.information.get() == self.current_branches:
            self.text.insert(INSERT, "error: Cannot delete branch '{0}' checked out\n".format(self.current_branches))
        else:
            self.text.insert(INSERT, stdout + "\n")
        self.text.see(END)
        self.info.master.protocol("WM_DELETE_WINDOW", self.destroy_info)
        self.info.master.destroy()
        self.info = None

    def destroy_info(self):
        self.info.master.eval('::ttk::CancelRepeat')
        self.info.master.destroy()
        self.info = None


if __name__ == "__main__":
    bmgr = Branch(Tk())
    bmgr.mainloop()
