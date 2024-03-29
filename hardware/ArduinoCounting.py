#!/usr/bin/env python
#-*- coding: utf-8 -*-

from hardware.Device import Device
from hardware.Arduino import Arduino
import serial
import threading
from serial.tools.list_ports import comports

import tkinter as tk
from tkinter import ttk
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

class ArduinoCouting(Arduino):
    def __init__(self, mac_guiver, frameName="Arduino Counting", mm_name=""):
        self.tag_label = "Arduino Counting"
        super(ArduinoCouting, self).__init__(mac_guiver, frameName="Counting Arduino", mm_name="")
        self.threadMonitor = threading.Thread(name='arduinoCountingMonitor', target=self.monitor)
        self.threadMonitor.setDaemon(True)
        self.isMonitor = False





        # FIXME
        self.change_com_port("COM10")
        self.initialized = self.load_device()
        if self.initialized == False:
            return
        self.mac_guiver.write_to_splash_screen("Opened with port %s" % (str(self.comPortInfo[0])))

        self.create_GUI()
        self.change_nb_of_point_in_history(150)
        self.change_integration_time(100)

    def load_device(self, params=None):
        self.mac_guiver.write_to_splash_screen("Loading Arduino Counting")
        return super(ArduinoCouting, self).load_device("counter/\r\n")

    def create_GUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                   borderwidth=1)

        img = Image.open("./Ressource/OffSmall.png")
        resized = img.resize((70, 70), Image.ANTIALIAS)
        self.tkimageOff = ImageTk.PhotoImage(resized)
        img = Image.open("./Ressource/OnSmall.png")
        resized = img.resize((70, 70), Image.ANTIALIAS)
        self.tkimageOn = ImageTk.PhotoImage(resized)



        self.lbOnOff = ttk.Label(self.frame, image=self.tkimageOff)
        # self.lbOnOff.config(width="40", height="40")
        self.lbOnOff.bind('<Button-1>', lambda e: self.on_button_on_off())
        self.lbOnOff.grid(row=0, column=0)

        # l = ttk.Label(self.frame, text="value", justify=tk.CENTER, width=7)
        # l.grid(row=0, column=2)
        self.current_value_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.current_value_sv, justify=tk.CENTER, width=7, font='Courier 65 bold')
        e.configure(state='readonly')
        e.grid(row=0, column=3)

        label = ttk.Label(self.frame, text='Int. Time (ms)', font='Courier 12')
        label.grid(row=1, column=0)
        self.intTime_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.intTime_sv, justify=tk.CENTER, width=7, font='Courier 15 bold')
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
        label.grid(row=2, column=0)
        self.sigma_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.sigma_sv, justify=tk.CENTER, width=7)
        e.grid(row=2, column=1)
        self.sigma_sv.set('0')

        self.frameHistory = tk.Frame(self.frame)
        self.frameHistory.grid(row=1, column=3, rowspan=5)

        self.figure = plt.Figure(figsize=(22, 7), dpi=60)
        self.ax = self.figure.add_subplot(111)

        self.ax.set_ylabel('time', fontsize=40)
        self.ax.set_ylabel('Photons', fontsize=40)

        self.ax.tick_params(axis='both', which='major', labelsize=40)
        self.ax.tick_params(axis='both', which='minor', labelsize=16)

        # self.change_nb_of_point_in_history(150)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frameHistory)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)


        label = ttk.Label(self.frame, text='Serial cmd')
        label.grid(row=3, column=0)
        self.send_command_entry_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.send_command_entry_sv, justify=tk.CENTER, width=20)
        e.bind('<Return>', lambda e: self.send_command_gui())
        e.grid(row=3, column=1)

        label = ttk.Label(self.frame, text='Serial Answer')
        label.grid(row=4, column=0)
        self.serial_answer_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.serial_answer_sv, justify=tk.CENTER, width=20)
        e.grid(row=4, column=1)


        b = tk.Button(self.frame, text="clear", command=self.clear_history)
        b.grid(row=5, column = 0)

        b = tk.Button(self.frame, text="Toggle LED", command=self.toggle_led)
        b.grid(row=5, column = 1)

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
                print(line)
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

    def count(self):
        """
        Cette fonction est bloquante contrairement à monitor.
        :return:
        """
        self.send_command("c/")
        line = self.serialPort.readline()
        try:
            i = int(line)
            return i
        except ValueError:
            # Handle the exception
            print("Pb Arduino Counting Transfert - not a number")
            return 0

    def send_command_gui(self):
        self.send_command(self.send_command_entry_sv.get())
        self.thread_send_cmd = threading.Thread(name='arduino_send_cmd', target=self.wait_answer_after_command)
        self.thread_send_cmd.start()

    def wait_answer_after_command(self):
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

    def clear_history(self):
        self.history[:] = 0
        self.idx_history = 0

    def toggle_led(self):
        cmd = "l/"
        self.send_command(cmd)


class dummy_counter(Device):
    def __init__(self, mac_guiver, frameName="DummyCounter", mm_name=""):
        super(dummy_counter, self).__init__(mac_guiver, frameName, mm_name)
        self.int_time_ms = 50.0
        self.load_device()

    def load_device(self, params=None):
        self.mac_guiver.write_to_splash_screen("Loading dummy counter", type="info")
        self.initialized = True
        return True

    def create_GUI(self):
        pass

    def count(self):
        time.sleep(self.int_time_ms/1000.0)
        return np.random.randint(50,10000)

    def change_integration_time(self, int_time_ms):
        self.int_time_ms = int_time_ms

