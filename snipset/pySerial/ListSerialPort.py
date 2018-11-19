#!/usr/bin/env python
#-*- coding: utf-8 -*-

import serial
import threading
from serial.tools.list_ports import comports
import time


listSerialPort = comports()


for port in listSerialPort:

    # serialPort = serial.Serial(port=port[0], baudrate=57600, parity=serial.PARITY_NONE,
    #                                 stopbits=serial.STOPBITS_ONE, timeout=0.5, rtscts=False)
    serialPort = serial.Serial(port=port[0], baudrate=57600, timeout=0.5, rtscts=False)
    #serialPort.open()
    serialPort.timeout = 2
    serialPort.write("?/\r\n")
    line = serialPort.readline()
    print(line)
    if line=="counter/\r\n":
        print("On l'a trouvé ! c'est le %s" % (port[0]))
        #print("le voici")
    serialPort.close()