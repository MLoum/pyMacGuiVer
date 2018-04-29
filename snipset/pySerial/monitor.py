#!/usr/bin/env python
#-*- coding: utf-8 -*-

import serial
import threading
from serial.tools.list_ports import comports
import time


listSerialPort = comports()
serialPort = serial.Serial(port="COM7", baudrate=57600, timeout=0.5, rtscts=False)

while True:
    serialPort.write("c/")
    print(serialPort.readline())


