#!/usr/bin/env python
#-*- coding: utf-8 -*-

from Device import Device
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
import time

class ArduinoPulser(Arduino):
    def __init__(self, mac_guiver, frameName="Arduino Counting", mm_name=""):
        super(ArduinoPulser, self).__init__(mac_guiver, frameName="Counting Arduino", mm_name="")

        # FIXME
        self.change_com_port("COM8")
        self.initialized = self.load_device()
        if self.initialized == False:
            return
        self.mac_guiver.write_to_splash_screen("Opened with port %s" % (str(self.comPortInfo[0])))

        self.create_GUI()

    def load_device(self, params=None):
        self.mac_guiver.write_to_splash_screen("Loading Arduino Counting")
        return super(ArduinoPulser, self).load_device("counter/\r\n")

    def create_GUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                   borderwidth=1)

        img = Image.open("./Ressource/led-green-off.png")
        self.tkimageLEDGreenOff = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/led-green-on.png")
        self.tkimageLEDGreenOn = ImageTk.PhotoImage(img)

        img = Image.open("./Ressource/led-red-off.png")
        self.tkimageLEDRedOff = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/led-red-on.png")
        self.tkimageLEDRedOn = ImageTk.PhotoImage(img)

        ttk.Label(self.frame, text='Port :').grid(row=0, column=0)
        self.comPort_sv = tk.StringVar(value='COM8')
        tk.Entry(self.frame, textvariable=self.comPort_sv, justify=tk.CENTER, width=7).grid(row=0, column=1)
        tk.Button(self.frame, text="Connect", command=self.connect).grid(row=0, column=2)
        self.arduino_connected_sv = tk.StringVar(value='offline')
        ttk.Label(self.frame, textvariable=self.arduino_connected_sv).grid(row=0, column=3)

        self.label_LED_connected = ttk.Label(self.frame, image=self.tkimageLEDGreenOff)
        self.label_LED_connected.grid(row=0, column=4)

        ttk.Label(self.frame, text='Inter pulse (ms) :').grid(row=0, column=5)
        self.interpulse_sv = tk.StringVar(value='100')
        e = tk.Entry(self.frame, textvariable=self.interpulse_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.change_interpulse_duration())
        e.grid(row=0, column=6)

        ttk.Label(self.frame, text='Pulse duration (au)').grid(row=0, column=7)
        self.pulse_duration_sv = tk.StringVar(value='10')
        e  = tk.Entry(self.frame, textvariable=self.pulse_duration_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.change_pulse_duration())
        e.grid(row=0, column=8)

        tk.Button(self.frame, text="Pulse", command=self.start_pulse).grid(row=0, column=9)
        tk.Button(self.frame, text="Stop", command=self.stop_pulse).grid(row=0, column=10)

        self.label_LED_pulsing = ttk.Label(self.frame, image=self.tkimageLEDRedOff)
        self.label_LED_pulsing.grid(row=0, column=11)

    def connect(self):
        self.change_com_port(self.comPort_sv.get())
        is_connected = self.load_device()
        if(is_connected):
            self.arduino_connected_sv.set("connected")
            self.label_LED_connected.configure(image=self.tkimageLEDGreenOn)
        else:
            self.arduino_connected_sv.set("offline")
            self.label_LED_connected.configure(image=self.tkimageLEDGreenOff)

    def change_interpulse_duration(self):
        interpulse_ms = int(self.interpulse_sv.get())
        cmd = "i"   # i for interpulse
        if interpulse_ms < 10000:
            cmd += "0"
            if interpulse_ms < 1000:
                cmd += "0"
            if interpulse_ms < 100:
                cmd += "0"
            if interpulse_ms < 10:
                cmd += "0"

        cmd += str(interpulse_ms)
        cmd += "/"
        self.send_command(cmd)

    def change_pulse_duration(self):
        pulse_duration_ua = int(self.pulse_duration_sv.get())
        cmd = "d"   # d for duration
        if pulse_duration_ua < 10000:
            cmd += "0"
            if pulse_duration_ua < 1000:
                cmd += "0"
            if pulse_duration_ua < 100:
                cmd += "0"
            if pulse_duration_ua < 10:
                cmd += "0"

        cmd += str(pulse_duration_ua)
        cmd += "/"
        self.send_command(cmd)


    def start_pulse(self):
        self.send_command("p/")
        self.label_LED_pulsing.configure(image=self.tkimageLEDRedOn)

    def stop_pulse(self):
        self.send_command("s/")
        self.label_LED_pulsing.configure(image=self.tkimageLEDRedOff)



