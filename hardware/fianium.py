#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time
import serial
from serial.tools.list_ports import comports
from hardware.Device import Device

class Fianium(Device):
    def __init__(self, macGuiver):
        self.isBusy_ = False
        super(Fianium, self).__init__(macGuiver, frameName="Dummy_XY", mm_name="")
        self.comPortInfo = "COM12"
        self.serialPort = serial.Serial(port="COM12", baudrate=19200, bytesize=8, parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE, timeout=0.5, rtscts=False)

    def loadDevice(self):
        return True

    def createGUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName, borderwidth=1)

    def changePower(self):
        pass

    def send_command(self, command):
        try:
            self.serialPort.write(command)
        except serial.portNotOpenError:
            print("Port non ouvert !")

    def read_result(self):
        msg = "timeout"
        msg = self.serialPort.readline()
        return msg

    def get_repetition_rate(self):
        cmd = "R?"
        self.send_command(cmd)
        msg = self.read_result()
        return msg

    def set_repetition_rate(self, repetition_rate):
        cmd = "R=" + str(repetition_rate)
        self.send_command(cmd)

    def set_laser_ctrl_mode(self, M):
        cmd = "R=" + str(M)
        self.send_command(cmd)


    def get_max_pump_power_Q(self):
        cmd = "R?"
        self.send_command(cmd)
        msg = self.read_result()
        self.S = float(msg)





    