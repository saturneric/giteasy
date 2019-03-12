from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *


class Window(Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.style = Style()
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



