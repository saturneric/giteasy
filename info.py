from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
import window

class Info(window.Window):
    def __init__(self, master=None, type="Entry", title = "INFO"):
        super().__init__(master)
        master.title(title)
        if type is "Combobox":
            info_type = Combobox(self)
        else:
            info_type = Entry(self)
        self.information_label = Label(self)
        self.information = info_type
        self.ok = Button(self)
        self.draw_widgets()
        self.master = master

    def draw_widgets(self):
        self.information_label["text"] = "Info: "
        self.information_label.grid(row=0, column=0)
        self.information.grid(row=0, column=1)
        self.ok["text"] = "OK"
        self.ok.grid(row=0, column=2)

    def set_click(self, func):
        self.ok["command"] = func