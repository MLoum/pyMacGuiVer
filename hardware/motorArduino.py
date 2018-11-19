#!/usr/bin/env python
#-*- coding: utf-8 -*-

from Arduino import Arduino
import serial
import threading
from serial.tools.list_ports import comports

import Tkinter as tk
import ttk
from PIL import Image, ImageTk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# #matplotlib.use("TkAgg")
# import matplotlib.patches as patches
# import matplotlib.gridspec as gridspec
# from mpl_toolkits.mplot3d import Axes3D
# import time
import numpy as np


class Motor_arduino(Arduino):
    def __init__(self, mac_guiver, frameName="Arduino Counting", mm_name=""):
        super(Motor_arduino, self).__init__(mac_guiver, frameName="Motor - Arduino", mm_name="")
        self.threadMonitor = threading.Thread(name='arduinoRotationDLS', target=self.monitor)
        self.threadMonitor.setDaemon(True)
        self.isMonitor = True

        # FIXME
        self.change_com_port("COM4")
        self.initialized = self.load_device()
        if self.initialized == False:
            return

        self.create_GUI()

    def load_device(self, params=None):
        return super(Motor_arduino, self).load_device("rotation/\r\n")

    def create_GUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                   borderwidth=1)

        # img = Image.open("./Ressource/flecheUp.png")
        # self.tkimageUpArrow = ImageTk.PhotoImage(img)
        # b = tk.Button(self.frame, image=self.tkimageUpArrow, command=self.moveUp)
        # b.config(width="40", height="40")
        # b.grid(row=0, column=0)
        #
        # img = Image.open("./Ressource/flecheBas.png")
        # self.tkimageDownArrow = ImageTk.PhotoImage(img)
        # b = tk.Button(self.frame, image=self.tkimageDownArrow, command=self.moveDown)
        # b.config(width="40", height="40")
        # b.grid(row=1, column=0)
        #
        # img = Image.open("./Ressource/flecheLeft.png")
        # self.tkimageLeftArrow = ImageTk.PhotoImage(img)
        # b = tk.Button(self.frame, image=self.tkimageLeftArrow, command=self.moveLeft)
        # b.config(width="40", height="40")
        # b.grid(row=0, column=1)
        #
        # img = Image.open("./Ressource/flecheRight.png")
        # self.tkimageRightArrow = ImageTk.PhotoImage(img)
        # b = tk.Button(self.frame, image=self.tkimageRightArrow, command=self.moveRight)
        # b.config(width="40", height="40")
        # b.grid(row=1, column=1)

        label = ttk.Label(self.frame, text='angle')
        label.grid(row=0, column=0)
        self.angle_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.angle_sv, justify=tk.CENTER, width=7)
        e.grid(row=0, column=1)
        self.angle_sv.set('10')

        b = tk.Button(self.frame, text="+", command=self.button_plus)
        b.grid(row=0, column=2)

        b = tk.Button(self.frame, text="-", command=self.button_minus)
        b.grid(row=0, column=3)


        label = ttk.Label(self.frame, text='speed')
        label.grid(row=0, column=4)
        self.speed_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.speed_sv, justify=tk.CENTER, width=7)
        e.grid(row=0, column=5)
        self.speed_sv.set('100')

        # self.figure.canvas.mpl_connect('scroll_event', self.graphScrollEvent)
        # self.figure.canvas.mpl_connect('button_press_event', self.graph_button_press_event)
        # self.figure.canvas.mpl_connect('button_release_event', self.button_release_event)
        # self.figure.canvas.mpl_connect('motion_notify_event', self.motion_notify_event)

    def button_plus(self):
        self.rotate_positive(angle=float(self.angle_sv.get()))

    def button_minus(self):
        self.rotate_negative(angle=float(self.angle_sv.get()))

    def rotate_positive(self, angle):
        cmd = "r"
        if angle < 100:
            cmd += "0"
        if angle < 10:
            cmd += "0"

        cmd += str(angle)
        cmd += "/"
        self.send_command(cmd)

    def rotate_negative(self, angle):
        cmd = "b"
        if angle < 100:
            cmd += "0"
        if angle < 10:
            cmd += "0"

        cmd += str(angle)
        cmd += "/"
        self.send_command(cmd)


    def change_speed(self, speed):
        cmd = "s"
        if speed < 100:
            cmd += "0"
        if speed < 10:
            cmd += "0"

        cmd += str(speed)
        cmd += "/"
        self.send_command(cmd)