from Device import Device
import serial
import threading
from serial.tools.list_ports import comports

class Arduino(Device):
    def __init__(self, mac_guiver, frameName="Arduino", mm_name=""):
        self.tag_label = "Arduino"
        super(Arduino, self).__init__(mac_guiver, frameName, mm_name)
        self.comPortInfo = None
        self.serialPort = serial.Serial(port=None, baudrate=57600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.5, rtscts=False)
        # self.threadPoll = threading.Thread(name='arduinoPoll', target=self.read_from_port)
        # self.threadPoll.setDaemon(True)
        self.comPortInfo = ["", "", ""]
        self.serial_number = None

    def load_device(self, params=None):
        #self.detectSerialPort(idString)
        # self.comPortInfo =["", "", ""]
        # self.comPortInfo[0] = "COM4"
        if self.comPortInfo  != None:
            self.serialPort.port = self.comPortInfo[0]
            try:
                self.serialPort.open()
            except serial.SerialException:
                #FIXME
                self.mac_guiver.write_to_splash_screen("Could not open the serial port", type="warn")
                return False
            return True
        else:
            return False

    def change_com_port(self, port):
        self.comPortInfo[0] = port

    def send_command(self, command):
        try:
            self.serialPort.write(command)
        except serial.portNotOpenError:
            print("Port non ouvert !")


    def read_result(self):
        self.answer = "timeout"
        self.answer = self.serialPort.readline()
        return self.answer

    def poll_arduino_for_answer(self):
        self.thread_poll = threading.Thread(name='arduino poll', target=self.read_result)
        self.thread_poll.start()

    def detect_serial_port(self, answerToDetect):
        self.comPortInfo =  None
        listSerialPort = comports()
        for port in listSerialPort:
           self.serialPort = serial.Serial(port=port[0], baudrate=57600, parity=serial.PARITY_NONE,
                                            stopbits=serial.STOPBITS_ONE, timeout=0.5, rtscts=False)
           self.send_command("?/")
           response = self.poll_arduino_for_answer()
           if response == answerToDetect:
               return

    def detect_serial_COM_port_via_serial_number(self, serial_number):
        self.comPortInfo =  None
        listSerialPort = comports()
        for port in listSerialPort:
            if serial_number in port[3]:
                return port[0]





