import serial
import threading
from serial.tools.list_ports import comports
import time


listSerialPort = comports()

serial_nb_to_detect = ""

for port in listSerialPort:
    print (port[0], port[1], port[2])
    serial_nb = port[2]
    if serial_nb == serial_nb_to_detect:
        print (port[0])

