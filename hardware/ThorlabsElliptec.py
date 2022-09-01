from hardware.Device import Device
import serial as s
import serial.tools.list_ports as lp

class ThorlabsElliptec(Device):
    """
    Based on https://github.com/cdbaird/TL-rotation-control

    The current position of the device (Position 0 ['0'], Position 1 ['31'], Position 2 ['62'], Position 3 ['93'],) is displayed in the 'Position' field.
    The slider will only move between these four positions. If the device is already at a particular position when the associated button is pushed, the command will be ignored.

    """

    def __init__(self, mac_guiver, type_="Slider", frameName="Slider", mm_name=""):
        super(ThorlabsElliptec, self).__init__(mac_guiver, frameName, mm_name)

        self.comPortInfo = None
        self.serial_port = s.Serial(port=None, baudrate=9600, bytesize=8, parity='N', timeout=2)
        self.COM_port = "COM5"
        self.serial_number = None
        self.type = type_

        self.error_codes = {
            '0': 'Status OK',
            '1': 'Communication Timeout',
            '2': 'Mechanical Timeout',
            '3': 'Command Error',
            '4': 'Value Out of Range',
            '5': 'Module Isolated',
            '6': 'Module Out of Isolation',
            '7': 'Initialisation Error',
            '8': 'Thermal Error',
            '9': 'Busy',
            '10': 'Sensor Error',
            '11': 'Motor Error',
            '12': 'Out of Range',
            '13': 'Over Current Error',
        }

        self.get_ = {
            'info': b'in',
            'status': b'gs',
            'position': b'gp',
            'stepsize': b'gj'
        }

        self.set_ = {
            'stepsize': b'sj',
            'isolate': b'is'
        }

        self.mov_ = {
            'home': b'ho',
            'forward': b'fw',
            'backward': b'bw',
            'absolute': b'ma',
            'relative': b'mr'
        }

        self.initialized = self.load_device()


    def load_device(self, params=None):
        self.mac_guiver.write_to_splash_screen("Loading Elliptec")
        self.serial_port.port = self.COM_port
        try:
            self.serial_port.open()
        except s.SerialException:
            #FIXME
            self.mac_guiver.write_to_splash_screen("Could not open the serial port", type="warn")
            return False
        self._get_motor_info()
        self.conv_factor = float(self.info['Range']) / float(self.info['Pulse/Rev'])
        self.range = self.info['Range']
        self.counts_per_rev = self.info['Pulse/Rev']
        return True

    def write(self, data):
        self.serial_port.write(data)

    def read_until(self, terminator):
        self.serial_port.read_until(terminator)

    def find_ports(self):
        avail_ports = []
        for port in lp.comports():
            if port.serial_number:
                # print(port.serial_number)
                try:
                    p = s.Serial(port.device)
                    p.close()
                    avail_ports.append(port)
                except (OSError, s.SerialException):
                    print('%s unavailable.\n' % port.device)
                # pass
        return avail_ports

    def _get_motor_info(self):
        # instruction = cmd['info']
        self.info = self._send_command(self.get_['info'])

    def _send_command(self, instruction, msg=None, address=b'0'):
        command = address + instruction
        if msg:
            command += msg
        # print(command)
        self.write(command)
        response = self.read_until(terminator=b'\n')
        # print(response)
        return self.parse(response)

    def do_(self, req='home', data='0', addr='0'):
        try:
            instruction = self.mov_[req]
        except KeyError:
            print('Invalid Command: %s' % req)
        else:
            command = addr.encode('utf-8') + instruction
            if data:
                command += data.encode('utf-8')

            self.request = command
            self.write(command)
            self.response = self.read_until(terminator=b'\n')
            self.status = self.parse(self.response)
            self.move_check(self.status)

    def set_(self, req='', data='', addr='0'):
        try:
            instruction = self.set_[req]
        except KeyError:
            print('Invalid Command')
        else:
            command = addr.encode('utf-8') + instruction
            if data:
                command += data.encode('utf-8')

            self.write(command)
            # print(command)
            response = self.read_until(terminator=b'\n')
            # print(response)
            self.status = self.parse(response)
            self.error_check(self.status)

    def get_(self, req='status', data='', addr='0'):
        try:
            instruction = self.get_[req]
        except KeyError:
            print('Invalid Command')
        else:
            command = addr.encode('utf-8') + instruction
            if data:
                command += data.encode('utf-8')

            self.write(command)
            # print(command)
            response = self.read_until(terminator=b'\n')
            print(response)
            self.status = self.parse(response)
            self.error_check(self.status)

    def parse(self, msg):
        if (not msg.endswith(b'\r\n') or (len(msg) == 0)):
            print('Status/Response may be incomplete!')
            return None
        msg = msg.decode().strip()
        code = msg[1:3]
        try:
            addr = int(msg[0], 16)
        except ValueError:
            raise ValueError('Invalid Address: %s' % msg[0])

        if (code.upper() == 'IN'):
            info = {'Address': str(addr),
                    'Motor Type': msg[3:5],
                    'Serial No.': msg[5:13],
                    'Year': msg[13:17],
                    'Firmware': msg[17:19],
                    'Thread': self.is_metric(msg[19]),
                    'Hardware': msg[20],
                    'Range': (int(msg[21:25], 16)),
                    'Pulse/Rev': (int(msg[25:], 16))}
            return info

        elif ((code.upper() == 'PO') or code.upper() == 'BO'):
            pos = msg[3:]
            return (code, (self.s32(int(pos, 16))))

        elif (code.upper() == 'GS'):
            errcode = msg[3:]
            return (code, str(int(errcode, 16)))

        else:
            return (code, msg[3:])

    def error_check(self, status):
        if not status:
            print('Status is None')
        elif (status[0] == "GS"):
            if (status[1] != '0'):  # is there an error?
                err = self.error_codes[status[1]]
                print('ERROR: %s' % err)
            else:
                print('Status OK')

    def move_check(self, status):
        if not status:
            print('Status is None')
        elif status[0] == 'GS':
            self.error_check(status)
        elif ((status[0] == "PO") or (status[0] == "BO")):
            print('Move Successful')
        else:
            print('Unknown response code %s' % status[0])

    def get_msg_code(self, msg):
        print('WARNING: get_msg_code does not work correctly. Don\'t use it!')
        code = [c for c in msg if not c.isdigit()]
        return ''.join(code)

    def is_metric(self, num):
        if (num == '0'):
            thread_type = 'Metric'
        elif (num == '1'):
            thread_type = 'Imperial'
        else:
            thread_type = None

        return thread_type

    def s32(self, value):  # Convert 32bit signed hex to int
        return -(value & 0x80000000) | (value & 0x7fffffff)




