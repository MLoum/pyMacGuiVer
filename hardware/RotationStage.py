#!/usr/bin/env python
#-*- coding: utf-8 -*-

from Device import Device

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog


# class addListPointDialog(SimpleDialog.SimpleDialog):
#     def __init__(self, master, title, pos):
#         self.xy = pos
#         super(addListPointDialog, self).__init__(master, title)
#
#     def body(self, master):
#
#         ttk.Label(master, text="X : ").grid(row=0)
#         ttk.Label(master, text="Y :").grid(row=1)
#         ttk.Label(master, text="name :").grid(row=3)
#
#         self.e1 = ttk.Entry(master)
#         self.e2 = ttk.Entry(master)
#         self.e3 = ttk.Entry(master)
#
#         #default value
#         self.e1.insert(tk.END, str(self.xy[0]))
#         self.e2.insert(tk.END, str(self.xy[1]))
#         self.e3.insert(tk.END, '')
#
#         self.e1.grid(row=0, column=1)
#         self.e2.grid(row=1, column=1)
#         self.e3.grid(row=2, column=1)
#
#         self.result = None
#         return self.e1 # initial focus
#
#     def validate(self):
#         try:
#             first = float(self.e1.get())
#             second = float(self.e2.get())
#             third = str(self.e3.get())
#             self.result = first, second, third
#         except ValueError:
#             tkMessageBox.showwarning(
#                 "Bad input",
#                 "Illegal values, please try again"
#             )
#             return 0
#
#     # def apply(self):



from PIL import Image, ImageTk

import threading
import time

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# #matplotlib.use("TkAgg")
# import matplotlib.patches as patches
# import matplotlib.gridspec as gridspec
# from mpl_toolkits.mplot3d import Axes3D
# import time
import numpy as np

class RotationStage(Device):
    def __init__(self, mac_guiver, frameName="XY_Stage", mm_name=""):
        self.frameName = frameName
        super(RotationStage, self).__init__(mac_guiver, frameName=self.frameName, mm_name=mm_name)

        self.pos_angle_deg = 0
        self.speed = 100
        self.step_deg = 1
        self.go_to_pos_deg = 0
        self.posHome_deg = 0

        self.posDict = {}
        self.listPosTreeView_iid = []

        self.initialized = self.load_device()
        if self.initialized:
            self.create_GUI()
            self.get_GUI_params()

    def load_device(self, params=None):
        pass
        # self.mmc.load_device("cam", "DemoCamera", "DCam")
        # self.mmc.initializeDevice("cam")

    def create_GUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                         borderwidth=1)

        img = Image.open("./Ressource/flecheLeft.png")
        self.tkimageLeftArrow = ImageTk.PhotoImage(img)
        b = tk.Button(self.frame, image=self.tkimageLeftArrow, command=self.move_left)
        b.config(width="40", height="40")
        b.grid(row=0, column=0)

        img = Image.open("./Ressource/flecheRight.png")
        self.tkimageRightArrow = ImageTk.PhotoImage(img)
        b = tk.Button(self.frame, image=self.tkimageRightArrow, command=self.move_right)
        b.config(width="40", height="40")
        b.grid(row=0, column=1)

        label = ttk.Label(self.frame, text='Step X(°)')
        label.grid(row=0, column=2)
        self.stepX_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.stepX_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.get_GUI_params())
        e.grid(row=0, column=3)
        self.stepX_sv.set('1')

        label = ttk.Label(self.frame, text='Dest (°)')
        label.grid(row=1, column=0)
        self.dest_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.dest_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.get_GUI_params())
        e.grid(row=1, column=1)
        self.stepX_sv.set('0')

        b = tk.Button(self.frame, text="Go to", command=self.goto)
        b.grid(row=1, column=2)

        label = ttk.Label(self.frame, text='Speed X(°/s)')
        label.grid(row=2, column=2)
        self.speedX_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.speedX_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.get_GUI_params())
        e.grid(row=2, column=3)
        self.speedX_sv.set('10')

        img = Image.open("./Ressource/led-green-off.png")
        self.tkimageLEDGreenOff = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/led-green-on.png")
        self.tkimageLEDGreenOn = ImageTk.PhotoImage(img)

        img = Image.open("./Ressource/led-red-off.png")
        self.tkimageLEDRedOff = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/led-red-on.png")
        self.tkimageLEDRedOn = ImageTk.PhotoImage(img)

        #TODO SetHome
        self.labelLEDMoving = ttk.Label(self.frame, image=self.tkimageLEDGreenOff)
        self.labelLEDMoving.grid(row=3, column=0)

        self.labelLED_ignored = ttk.Label(self.frame, image=self.tkimageLEDGreenOff)
        self.labelLED_ignored.grid(row=3, column=1)

        b = tk.Button(self.frame, text="STOP !", command=self.stop_cmd)
        b.grid(row=3, column=3)

        # self.frameNavigationGraph= tk.Frame(self.frame)
        # self.frameNavigationGraph.grid(row=0, column=6, rowspan=3)
        #
        # self.figure = plt.Figure(figsize=(3,3), dpi=50)
        # self.ax = self.figure.add_subplot(111)
        #
        # self.graphPositionExtension_micron = 1000
        #
        # self.canvas = FigureCanvasTkAgg(self.figure, master=self.frameNavigationGraph)
        # self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        #
        # self.figure.canvas.mpl_connect('scroll_event', self.graphScrollEvent)
        # self.figure.canvas.mpl_connect('button_press_event', self.graph_button_press_event)
        # # self.figure.canvas.mpl_connect('button_release_event', self.button_release_event)
        # # self.figure.canvas.mpl_connect('motion_notify_event', self.motion_notify_event)
        #
        # self.plot_position_on_graph()

        # #cursor =
        # self.pos_tree_view = ttk.Treeview(self.frame, height=7, columns=('PosX', 'PosY'), selectmode="browse")
        # self.pos_tree_view.grid(row=0, column=7, rowspan=3)
        # self.pos_tree_view.heading('#0', text='label', anchor=tk.CENTER, )
        # self.pos_tree_view.heading('#1', text='PosX', anchor=tk.CENTER)
        # self.pos_tree_view.heading('#2', text='PosY', anchor=tk.CENTER)
        # self.pos_tree_view.column('#1', stretch=tk.YES, minwidth=50, width=50)
        # self.pos_tree_view.column('#2', stretch=tk.YES, minwidth=50, width=50)
        # self.pos_tree_view.column('#0', stretch=tk.YES, minwidth=50, width=50)
        #
        # self.frame_tool_button_pos = tk.Frame(self.frame)
        # self.frame_tool_button_pos.grid(row=2, column=7, rowspan=3)

        # b = tk.Button(self.frame_tool_button_pos, text="+", command=self.add_pos)
        # b.grid(row=0, column=0)
        # b = tk.Button(self.frame_tool_button_pos, text="-", command=self.remove_pos)
        # b.grid(row=0, column=1)
        # b = tk.Button(self.frame_tool_button_pos, text="goTo", command=self.go_to_pos)
        # b.grid(row=0, column=2)
        # b = tk.Button(self.frame_tool_button_pos, text="SetHome", command=self.set_home)
        # b.grid(row=0, column=2)
        #
        # self.pos_tree_view.tag_bind('ttk', '<1>', self.pos_Selected)


    def stop_cmd(self):
        self.stop()

    def goto(self):
        self.get_GUI_params()
        self.launch_move(mode="absolute", pos_angle_deg=self.pos_angle_deg)

    def set_home(self):
        pass

    def get_GUI_params(self):
        # TODO check numeric and positive.
        self.step_deg = float(self.stepX_sv.get())
        self.speed = float(self.speedX_sv.get())
        self.go_to_pos_deg = float(self.dest_sv.get())

    # def graphScrollEvent(self, event):
    #     if event.button == 'up':
    #         self.graphPositionExtension_micron /= 2
    #     elif event.button == 'down':
    #         self.graphPositionExtension_micron *= 2
    #     self.plot_position_on_graph()


    # def graph_button_press_event(self, event):
    #     if event.dblclick:
    #         self.launch_move(mode="absolute", posMicron=[event.xdata, event.ydata])

    def move_absolute(self, pos_micron):
        pass

    def move_relative(self, pos_micron):
        pass

    def wait_for_device(self):
        pass

    def double_step(self):
        self.get_GUI_params()
        self.stepX_sv.set(str(self.step_deg * 2))
        self.get_GUI_params()

    def halve_step(self):
        self.get_GUI_params()
        self.stepX_sv.set(str(self.step_deg / 2))
        self.get_GUI_params()


    def get_position(self):
        pass

    # def plot_position_on_graph(self):
    #     self.ax.clear()
    #     self.ax.set_xlim(-self.graphPositionExtension_micron, self.graphPositionExtension_micron)
    #     self.ax.set_ylim(-self.graphPositionExtension_micron, self.graphPositionExtension_micron)
    #     self.ax.scatter(self.posHome[0], self.posHome[1])
    #     self.ax.scatter(self.posMicron[0], self.posMicron[1])
    #     self.canvas.draw()

    def launch_move(self, mode, posMicron):
        """
        THREAD !!
        """
        self.moveThread = threading.Thread(name='RotationStage', target=self.move, args=(mode, posMicron))
        self.moveThread.start()

    def is_busy(self):
        return False

    def blinkLED_ignored(self):
        self.labelLED_ignored.configure(image=self.tkimageLEDRedOn)
        time.sleep(0.2)
        self.labelLED_ignored.configure(image=self.tkimageLEDRedOff)

    def move(self, mode, pos_angle_deg):
        #FIXME
        # self.get_GUI_params()

        if self.is_busy():
            #ignore command
            threading.Thread(target=self.blinkLED_ignored).start()
            return

        if mode == "absolute":
            self.pos_angle_deg = pos_angle_deg
            self.move_absolute(pos_angle_deg)

        elif mode == "relative":
            self.move_relative(pos_angle_deg)
            self.pos_angle_deg += pos_angle_deg


        self.labelLEDMoving.configure(image=self.tkimageLEDGreenOn)
        self.wait_for_device()
        self.labelLEDMoving.configure(image=self.tkimageLEDGreenOff)

        # self.plot_position_on_graph()

    def stop(self):
        pass
