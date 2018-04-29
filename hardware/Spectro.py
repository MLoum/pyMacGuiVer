from Device import Device
import serial
import threading
from serial.tools.list_ports import comports
import Tkinter as tk
import ttk
import time
from PIL import Image, ImageTk

import threading


# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Spectro(Device):
    def __init__(self, macGuiver, frameName="spectro", mm_name=""):
        super(Spectro, self).__init__(macGuiver, frameName, mm_name)
        self.comPortInfo = "COM12"
        self.serialPort = serial.Serial(port="COM12", baudrate=9600, bytesize=8, parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE, timeout=0.5, rtscts=False)
        # print(self.serialPort)

    def createGUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                   borderwidth=1)

        label = ttk.Label(self.frame, text='wavelength (nm)')
        label.grid(row=0, column=0)

        # Choix de la longueur d'onde
        self.wl_sv = tk.StringVar()
        e = ttk.Entry(self.frame, textvariable=self.wl_sv, justify=tk.CENTER, width=7)
        e.grid(row=0, column=1)
        self.wl_sv.set('530')

        # Validation du choix de longueur d'onde et deplacement
        eb = tk.Button(self.frame, text="OK", command=self.changeWL)
        eb.grid(row=0, column=2, columnspan=1)

        # Choix du reseau
        label = ttk.Label(self.frame, text='grating')
        label.grid(row=1, column=0)
        self.r = tk.Spinbox(self.frame, values=(1, 4, 7))
        # Values 1 4 7 if gratings are on first turret
        self.r.grid(row=1, column=1)
        # Validation du choix de grating
        rb = tk.Button(self.frame, text="OK", command=self.changeGrating)
        rb.grid(row=1, column=2, columnspan=1)

    def waitForDevice(self):
        answer = 0
        cmd = ""
        self.serialPort.write(cmd)
        while self.serialPort.readline() != "1":
            self.serialPort.write(cmd)
            time.sleep(0.1)


    def changeWL(self):
        cmd = self.wl_sv.get() + " NM"
        # Can also use GOTO command or >NM coupled with MONO-?DONE to check if displacement is over
        self.serialPort.write(cmd)
        self.waitForDevice()
        # print(self.serialPort.readline())

    def changeGrating(self):
        cmd = self.r.get() + " GRATING"
        self.serialPort.write(cmd)
        # print(self.serialPort.readline())

    # def test(self):
    #     print("test")
    #     self.serialPort.write("GRATING?")

    # Pas de calibration pour l'instant on verra ensuite

    # def calibration(self):
    #     calFen = Tk()
    #     self.offset = tk.StringVar()
    #     e=ttk.Entry(calFen, textvariable=self.offset, justify=tk.CENTER, width=7)
    #     e.grid(row=0, column=0, columnspan=2)

    def loadDevice(self, params=None):
        pass
