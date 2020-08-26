from tkinter import Frame, BOTH, Button
from tkinter.filedialog import askdirectory
from tkinter.simpledialog import askinteger
from tkinter import messagebox

import time
import sys
import os
import glob
import datetime
import getpass
import shutil
import copy

class GuiMainFrame(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.init_window()

    # Creation of init_window
    def init_window(self):

        self.pack(fill=BOTH, expand=1)

        # Create the Quit button
        self.quitButton = Button(self, bg="red", text="Exit", command=quit, width=3)

        # Place the Quit Button on the top right corner
        self.quitButton.place(x=570, y=0)
