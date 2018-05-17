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


class ArduinoCouting(Arduino):
    def __init__(self, macGuiver, frameName="Arduino Counting", mm_name=""):
        super(ArduinoCouting, self).__init__(macGuiver, frameName="Counting Arduino", mm_name="")
        self.threadMonitor = threading.Thread(name='arduinoCountingMonitor', target=self.monitor)
        self.threadMonitor.setDaemon(True)
        self.isMonitor = False

        self.initialized = self.loadDevice()
        if self.initialized == False:
            return

        self.createGUI()

    def loadDevice(self, params=None):
        return super(ArduinoCouting, self).loadDevice("counter/\r\n")

    def createGUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                   borderwidth=1)

        img = Image.open("./Ressource/OffSmall.png")
        self.tkimageOff = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/OnSmall.png")
        self.tkimageOn = ImageTk.PhotoImage(img)

        self.lbOnOff = ttk.Label(self.frame, image=self.tkimageOff)
        #self.lbOnOff.config(width="40", height="40")
        self.lbOnOff.bind('<Button-1>', lambda e: self.on_button_on_off())
        self.lbOnOff.grid(row=0, column=0)

        label = ttk.Label(self.frame, text='Int. Time (ms)')
        label.grid(row=1, column=0)
        self.intTime_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.intTime_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.change_integration_time_callback())
        e.grid(row=1, column=1)
        self.intTime_sv.set('100')

        label = ttk.Label(self.frame, text='Mean')
        label.grid(row=2, column=0)
        self.mean_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.mean_sv, justify=tk.CENTER, width=7)
        e.grid(row=2, column=1)
        self.mean_sv.set('0')

        label = ttk.Label(self.frame, text='Sigma')
        label.grid(row=3, column=0)
        self.sigma_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.sigma_sv, justify=tk.CENTER, width=7)
        e.grid(row=3, column=1)
        self.sigma_sv.set('0')

        self.frameHistory = tk.Frame(self.frame)
        self.frameHistory.grid(row=0, column=3, rowspan=3)

        self.figure = plt.Figure(figsize=(12, 4), dpi=50)
        self.ax = self.figure.add_subplot(111)

        self.change_nb_of_point_in_history(100)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frameHistory)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        self.send_command_entry_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.send_command_entry_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.send_command_gui())
        e.grid(row=0, column=4)

        self.serial_answer_sv = tk.StringVar()
        e = ttk.Label(self.frame, textvariable=self.serial_answer_sv, justify=tk.CENTER, width=7)
        e.grid(row=0, column=5)


        l = ttk.Label(self.frame, text="value", justify=tk.CENTER, width=7)
        l.grid(row=1, column=4)

        self.current_value_sv = tk.StringVar()
        label = ttk.Label(self.frame, textvariable=self.current_value_sv, justify=tk.CENTER, width=7)
        label.config(font=("Courier", 44))
        label.grid(row=1, column=5)


        # self.figure.canvas.mpl_connect('scroll_event', self.graphScrollEvent)
        # self.figure.canvas.mpl_connect('button_press_event', self.graph_button_press_event)
        # self.figure.canvas.mpl_connect('button_release_event', self.button_release_event)
        # self.figure.canvas.mpl_connect('motion_notify_event', self.motion_notify_event)

    def on_button_on_off(self):
        if self.isMonitor == False:
            self.lbOnOff.configure(image=self.tkimageOn)
            self.launch_monitor()
        else:
            self.stop_monitor()
            self.lbOnOff.configure(image=self.tkimageOff)

    def launch_monitor(self):
        self.send_command("m/")
        self.isMonitor = True
        self.threadMonitor = threading.Thread(name='arduinoCountingMonitor', target=self.monitor)
        self.threadMonitor.start()

    def stop_monitor(self):
        self.send_command("s/")
        if self.threadMonitor.is_alive():
            self.threadMonitor.join(timeout=0.5)
        self.isMonitor = False

    def monitor(self):
        while self.isMonitor == True:
            line = self.serialPort.readline()
            if line != "":
                #print(line)
                try:
                    i = int(line)
                    self.add_point_to_history(int(i))
                    self.current_value_sv.set(str(i))
                except ValueError:
                    # Handle the exception
                    print("Pb Arduino Counting Transfert - not a number")
            else:
                print("Arduino counting timeOut")
                #print (line.find("/"))

        #print("Ending thread ?")

    def send_command_gui(self):
        self.send_command(self.send_command_entry_sv.get())
        self.thread_send_cmd = threading.Thread(name='arduino_send_cmd', target=self.wait_asnwer_after_command)
        self.thread_send_cmd.start()

    def wait_asnwer_after_command(self):
        self.serial_answer_sv.set(self.serialPort.readline())


    def change_nb_of_point_in_history(self, nb_of_point):
        self.nb_of_point_in_history = nb_of_point
        self.history = np.zeros(nb_of_point)
        self.history_x = np.arange(self.nb_of_point_in_history)
        self.idx_history = 0
        self.ax.set_xlim(0, self.nb_of_point_in_history)

    def change_integration_time_callback(self):
        try:
            int_time = int(self.intTime_sv.get())
            self.change_integration_time(int_time)
        except ValueError:
            # Handle the exception
            print("Not a valid integration time")

    def change_integration_time(self, int_time_ms):
        cmd = "i"
        if int_time_ms < 10000:
            cmd += "0"
            if int_time_ms < 1000:
                cmd += "0"
            if int_time_ms < 100:
                cmd += "0"
            if int_time_ms < 10:
                cmd += "0"

        cmd += str(int_time_ms)
        cmd += "/"
        self.send_command(cmd)

    def add_point_to_history(self, point):
        if self.idx_history == self.nb_of_point_in_history-1:
            self.history[:] = 0
            self.idx_history = 0
        self.history[self.idx_history] = point
        self.idx_history += 1

        self.mean_sv.set(str(np.mean(self.history[0:self.idx_history])))
        self.sigma_sv.set(str(np.std(self.history[0:self.idx_history])))

        self.ax.clear()
        self.ax.set_xlim(0, self.nb_of_point_in_history)
        self.ax.plot(self.history_x[0:self.idx_history], self.history[0:self.idx_history], "ro")
        self.canvas.draw()



