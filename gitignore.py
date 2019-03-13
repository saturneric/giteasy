from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
import os
from keygen import *
import window
from info import Info
from main import default_pwd


class Gitignore(window.Window):
    def __init__(self, master = None):
        self.master = master
        super().__init__(master)
        master.title("Git Ignore Manager")
        super().set_width(800)
        super().set_position(350, 200)

        super().apply()
        self.list = Listbox(self, width=18, height=30)
        self.list.bind("<<ListboxSelect>>", self.select_file)
        self.add_btn = Button(self)
        self.text = Text(self, width=75, height=35)
        self.save_btn = Button(self)
        self.pwd = default_pwd


        gitign_file = open(".gitignore","r")
        gitign_lines = gitign_file.readlines()
        self.gitign_text = ""
        if len(gitign_lines) == 0:
            self.gitign_text = "# ----Git Ignore File----\n"
        else:
            for line in gitign_lines:
                self.gitign_text += line
        gitign_file.close()

        self.draw_widgets()
        self.files = []
        self.set_list()
        self.current_index = None

    def select_file(self, *args):
        if len(self.files) > 0:
            self.current_index = self.list.curselection()[0]

    def add_file(self):
        if self.current_index is not None:
            file_data = open(os.path.join(sys._MEIPASS, self.files[self.current_index]),"r")
            for line in file_data.readlines():
                self.text.insert(INSERT, line)
            file_data.close()
            self.text.insert(INSERT, "\n# ----PART_END----\n\n\n")
            self.text.see(END)
        else:
            showinfo(message="Select one .gitignore file first.")

    def set_list(self):
        files = os.listdir(os.path.join(sys._MEIPASS))
        for file in files:
            file_info = os.path.splitext(file)
            if file_info[1] == ".gitignore":
                self.files.append(file)
            self.files.sort()
            for file in self.files:
                file_info = os.path.splitext(file)
                self.list.insert(END, file_info[0])


    def do_save(self):
        self.gitign_text = self.text.get(1.0, END)
        gitign_file = open(".gitignore", "w")
        gitign_file.write(self.gitign_text)
        gitign_file.close()
        showinfo(message="File Saved")



    def draw_widgets(self):
        self.save_btn["text"] = "Save"
        self.add_btn["text"] = "Add"
        self.save_btn["command"] = self.do_save
        self.add_btn["command"] = self.add_file
        self.save_btn.grid(row=1, column=1, sticky=E)
        self.add_btn.grid(row=1, column=0, sticky=E)
        self.text.grid(row=0, column=1)
        self.list.grid(row=0, column=0)
        self.text.insert(INSERT, self.gitign_text)

if __name__ == "__main__":
    gitign = Gitignore(Tk())
    gitign.mainloop()