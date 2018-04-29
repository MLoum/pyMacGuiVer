from Device import Device
import serial
import threading
from serial.tools.list_ports import comports

class Arduino(Device):
    def __init__(self, macGuiver, frameName="Arduino", mm_name=""):
        super(Arduino, self).__init__(macGuiver, frameName, mm_name)
        self.comPortInfo = None
        self.serialPort = serial.Serial(port=None, baudrate=57600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.5, rtscts=False)
        # self.threadPoll = threading.Thread(name='arduinoPoll', target=self.read_from_port)
        # self.threadPoll.setDaemon(True)

    def loadDevice(self, params=None):
        #self.detectSerialPort(idString)
        self.comPortInfo =["", "", ""]
        self.comPortInfo[0] = "COM3"
        if self.comPortInfo  != None:
            self.serialPort.port = self.comPortInfo[0]
            try:
                self.serialPort.open()
            except serial.SerialException:
                #FIXME
                print("Pas de port !")
                return False

            return True
        else:
            return  False

    def sendCommand(self, command):
        try:
            self.serialPort.write(command)
        except serial.portNotOpenError:
            print("Port non ouvert !")


    def readResult(self):
        msg = "timeout"
        msg = self.serialPort.readline()
        return msg

    def pollArduino(self):
        pass

    def detectSerialPort(self, answerToDetect):
        self.comPortInfo =  None
        listSerialPort = comports()
        for port in listSerialPort:
           self.serialPort = serial.Serial(port=port[0], baudrate=57600, parity=serial.PARITY_NONE,
                                            stopbits=serial.STOPBITS_ONE, timeout=0.5, rtscts=False)
           self.sendCommand("?/")
           response = self.pollArduino()
           if response == answerToDetect:
               return

    def detectSerialCOMPort_viaSerialNumber(self, serialNumber):
        self.comPortInfo =  None
        listSerialPort = comports()
        for port in listSerialPort:
            if serialNumber in port[3]:
                return port[0]





