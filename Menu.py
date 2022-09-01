import tkinter as tk
from tkinter import ttk

#https://stackoverflow.com/questions/673174/file-dialogs-of-tkinter-in-python-3
# from tkinter import filedialog, messagebox, simpledialog
import os


class Menu():
    def __init__(self, master, main_gui):
        self.master = master
        self.main_gui = main_gui
        self.create_menu()

    def create_menu(self):
        self.menuSystem = tk.Menu(self.master)

        # FILE#############
        self.menu_file = tk.Menu(self.menuSystem, tearoff=0)
        self.menu_file.add_command(label='Preferences', command=self.openPreferences)
        self.menu_file.add_command(label='Quit', command=self.quit)

        self.menuSystem.add_cascade(label="File", menu=self.menu_file)

        self.menu_toolbox = tk.Menu(self.menuSystem, tearoff=0)
        self.menu_toolbox.add_command(label='Microfluidics ToolBox', underline=1, command=self.open_microfluidics_toolbox)

        self.menuSystem.add_cascade(label="ToolBox", menu=self.menu_toolbox)

        self.master.config(menu=self.menuSystem)

    def quit(self):
        pass
        # result = messagebox.askquestion("Quit ?", "Are You Sure ?", icon='warning')
        # if result == 'yes':
        #     self.mainGUI.on_quit()


    def openPreferences(self, event):
        pass

    def open_microfluidics_toolbox(self):
        self.main_gui.show_microfluidics_tool_box()


