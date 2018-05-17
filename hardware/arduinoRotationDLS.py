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


class ArduinoRotationDLS(Arduino):
    def __init__(self, macGuiver, frameName="Arduino Counting", mm_name=""):
        super(ArduinoCouting, self).__init__(macGuiver, frameName="Counting Arduino", mm_name="")
        self.threadMonitor = threading.Thread(name='arduinoRotationDLS', target=self.monitor)
        self.threadMonitor.setDaemon(True)
        self.isMonitor = True

        self.initialized = self.loadDevice()
        if self.initialized == False:
            return

        self.createGUI()

    def loadDevice(self, params=None):
        return super(ArduinoCouting, self).loadDevice("counter/\r\n")

    def createGUI(self):
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

        img = Image.open("./Ressource/Off.png")
        self.tkimageOff = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/On.png")
        self.tkimageOn = ImageTk.PhotoImage(img)

        self.lbOnOff = ttk.Label(self.frame, image=self.tkimageOff)
        #self.lbOnOff.config(width="40", height="40")
        self.lbOnOff.bind('<Button-1>', lambda e: self.on_buttonOnOff())
        self.lbOnOff.grid(row=0, column=0)

        label = ttk.Label(self.frame, text='Int. Time (ms)')
        label.grid(row=1, column=0)
        self.intTime_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.intTime_sv, justify=tk.CENTER, width=7)
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

        # label = ttk.Label(self.frame, text='Speed Y(µm/s)')
        # label.grid(row=1, column=4)
        # self.speedY_sv = tk.StringVar()
        # e = ttk.Entry(self.frame, textvariable=self.speedY_sv, justify=tk.CENTER, width=7)
        # e.grid(row=1, column=5)
        # self.speedY_sv.set('500')

        self.frameHistory = tk.Frame(self.frame)
        self.frameHistory.grid(row=0, column=3, rowspan=3)

        self.figure = plt.Figure(figsize=(12, 4), dpi=50)
        self.ax = self.figure.add_subplot(111)

        self.changeNbOfPointInHistory(100)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frameHistory)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        # self.figure.canvas.mpl_connect('scroll_event', self.graphScrollEvent)
        # self.figure.canvas.mpl_connect('button_press_event', self.graph_button_press_event)
        # self.figure.canvas.mpl_connect('button_release_event', self.button_release_event)
        # self.figure.canvas.mpl_connect('motion_notify_event', self.motion_notify_event)

    def on_buttonOnOff(self):
        if self.isMonitor == False:
            self.lbOnOff.configure(image=self.tkimageOn)
            self.launchMonitor()
        else:
            self.stopMonitor()
            self.lbOnOff.configure(image=self.tkimageOff)

    def launchMonitor(self):
        self.send_command("m/")
        self.isMonitor = True
        self.threadMonitor = threading.Thread(name='arduinoCountingMonitor', target=self.monitor)
        self.threadMonitor.start()

    def stopMonitor(self):
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
                    self.addPointToHistory(int(i))
                except ValueError:
                    # Handle the exception
                    print("Pb Arduino Counting Transfert - not a number")

                #print (line.find("/"))

        #print("Ending thread ?")

    def changeNbOfPointInHistory(self, nbOfPoint):
        self.nbOfPointInHistory = nbOfPoint
        self.history = np.zeros(nbOfPoint)
        self.history_x = np.arange(self.nbOfPointInHistory)
        self.idx_history = 0
        self.ax.set_xlim(0,self.nbOfPointInHistory)

    def changeIntegrationTime(self, intTimeMs):
        cmd = "i"
        if intTimeMs < 10000:
            cmd += "0"
            if intTimeMs < 1000:
                cmd += "0"
            if intTimeMs < 100:
                cmd += "0";
            if intTimeMs < 10:
                cmd += "0";

        cmd += intTimeMs
        cmd += "/"
        self.send_command(cmd)


    def addPointToHistory(self, point):
        if self.idx_history == self.nbOfPointInHistory-1:
            self.history[:] = 0
            self.idx_history = 0
        self.history[self.idx_history] = point
        self.idx_history += 1

        self.mean_sv.set(str(np.mean(self.history[0:self.idx_history])))
        self.sigma_sv.set(str(np.std(self.history[0:self.idx_history])))

        self.ax.clear()
        self.ax.set_xlim(0, self.nbOfPointInHistory)
        self.ax.plot(self.history_x[0:self.idx_history], self.history[0:self.idx_history], "ro")
        self.canvas.draw()



