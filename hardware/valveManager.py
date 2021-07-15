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

class ValveManager(Arduino):
    def __init__(self, mac_guiver, frameName="Arduino Counting", mm_name=""):
        super(ValveManager, self).__init__(mac_guiver, frameName="Valve Manager", mm_name="")

        # FIXME
        self.change_com_port("COM8")
        self.initialized = self.load_device()
        if self.initialized == False:
            return
        self.mac_guiver.write_to_splash_screen("Opened with port %s" % (str(self.comPortInfo[0])))
        self.nb_of_valve = 8
        self.valve_state = [False] * self.nb_of_valve
        self.label_on_off = [None] * self.nb_of_valve
        self.create_GUI()

    def load_device(self, params=None):
        self.mac_guiver.write_to_splash_screen("Loading Valve manager")
        return True
        # return super(ValveManager, self).load_device("valve/\r\n")

    def create_GUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                   borderwidth=1)

        self.frame_arduino = tk.Frame(self.frame)
        # self.frame_arduino.pack(side=tk.LEFT)
        self.frame_arduino.grid(row=0, column=0)

        img = Image.open("./Ressource/led-green-off.png")
        self.tkimageLEDGreenOff = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/led-green-on.png")
        self.tkimageLEDGreenOn = ImageTk.PhotoImage(img)

        img = Image.open("./Ressource/led-red-off.png")
        self.tkimageLEDRedOff = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/led-red-on.png")
        self.tkimageLEDRedOn = ImageTk.PhotoImage(img)

        ttk.Label(self.frame_arduino, text='Port :').grid(row=0, column=0)
        self.comPort_sv = tk.StringVar(value='COM8')
        tk.Entry(self.frame_arduino, textvariable=self.comPort_sv, justify=tk.CENTER, width=7).grid(row=0, column=1)
        tk.Button(self.frame_arduino, text="Connect", command=self.connect).grid(row=0, column=2)
        self.arduino_connected_sv = tk.StringVar(value='offline')
        ttk.Label(self.frame_arduino, textvariable=self.arduino_connected_sv).grid(row=0, column=3)

        self.label_LED_connected = ttk.Label(self.frame_arduino, image=self.tkimageLEDGreenOff)
        self.label_LED_connected.grid(row=0, column=4)

        self.cmd_sv = tk.StringVar()
        ttk.Label(self.frame_arduino, text='Cmd :').grid(row=1, column=0)
        tk.Entry(self.frame_arduino, textvariable=self.cmd_sv, justify=tk.CENTER, width=7).grid(row=1, column=1)
        tk.Button(self.frame_arduino, text="Send", command=self.send_cmd).grid(row=1, column=2)
        self.cmd_answer_sv = tk.StringVar()
        e = tk.Entry(self.frame_arduino, textvariable=self.cmd_answer_sv, justify=tk.CENTER, width=10)
        e.grid(row=2, column=1)
        e.configure(state='readonly')

        self.frame_switch = tk.Frame(self.frame)
        # self.frame_switch.pack(side=tk.LEFT)
        self.frame_switch.grid(row=0, column=1)

        img = Image.open("./Ressource/OffSmall.png")
        self.tkimageOff = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/OnSmall.png")
        self.tkimageOn = ImageTk.PhotoImage(img)

        for i in range(self.nb_of_valve):
            self.label_on_off[i] = ttk.Label(self.frame_switch, image=self.tkimageOff)
            #self.lbOnOff.config(width="40", height="40")
            ttk.Label(self.frame_switch, text=str(i)).grid(row=0, column=i)
            self.label_on_off[i].bind('<Button-1>', lambda e: self.on_button_on_off(i))
            self.label_on_off[i].bind('<Button-1>', self.on_button_on_off)
            self.label_on_off[i].grid(row=1, column=i)



    def connect(self):
        self.change_com_port(self.comPort_sv.get())
        is_connected = self.load_device()
        if(is_connected):
            self.arduino_connected_sv.set("connected")
            self.label_LED_connected.configure(image=self.tkimageLEDGreenOn)
        else:
            self.arduino_connected_sv.set("offline")
            self.label_LED_connected.configure(image=self.tkimageLEDGreenOff)

    def send_cmd(self):
        cmd = self.cmd_sv.get()
        self.send_cmd(cmd)
        self.thread_wait_and_display_answer = threading.Thread(name='valve manager send cmd', target=self.wait_and_display_answer)
        self.thread_wait_and_display_answer.start()

    def wait_and_display_answer(self):
        msg = self.read_result()
        self.cmd_answer_sv.set(msg)

    def on_button_on_off(self, event):
        print(event)
        number = 0
        for i, widget in enumerate(self.label_on_off):
            if event.widget == widget:
                number = i
                break
        self.valve_state[number] = not(self.valve_state[number])
        if self.valve_state[number] == True:
            self.label_on_off[number].configure(image=self.tkimageOn)
            self.open_valve(number)
        else:
            # self.stop_monitor()
            self.label_on_off[number].configure(image=self.tkimageOff)
            self.close_valve(number)


    def oscillate_valve(self, number_valve, period_ms, nb_of_oscillation):
        cmd = "O" + str(number_valve) + "-" + str(period_ms) + "-" + str(nb_of_oscillation) + "/"
        self.send_cmd(cmd)
        pass


    def open_valve(self, number):
        # H for HIGH
        cmd = "H" + str(number) + "/"
        self.send_command(cmd)

    def open_all_valves(self):
        # A for All
        cmd = "A1/"
        self.send_command(cmd)

    def close_all_valves(self,):
        # A for All
        cmd = "A0/"
        self.send_command(cmd)

    def close_valve(self, number):
        # L for Low
        cmd = "L" + str(number) + "/"
        self.send_command(cmd)