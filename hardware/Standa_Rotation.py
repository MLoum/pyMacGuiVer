#!/usr/bin/env python
#-*- coding: utf-8 -*-

import ctypes
import time
import platform

import os
import sys
import tempfile
import re

if sys.version_info >= (3, 0):
    import urllib.parse


from hardware.RotationStage import RotationStage

from standa.pyximc import *

class Standa_XY(RotationStage):
    def __init__(self, mac_guiver):
        self.lib = None
        self.device_id = None
        self.step_multiplier = 40
        super(Standa_XY, self).__init__(mac_guiver, frameName="Rotation_Standa", mm_name="Rotation_Standa")


    def load_device(self, params=None):
        """
        * Device name has form "xi-com:port" or "xi-net://host/serial" or "xi-emu://file".
		* In case of USB-COM port the "port" is the OS device name.
		* For example "xi-com:\\\.\COM3" in Windows or "xi-com:/dev/tty.s123" in Linux/Mac.

		Lokk in the gestionnaire de périphérique
        :return:
        """
        # self.mmc.loadDevice(self.mm_name, "Standa8SMC4", "Standa8SMC4XY")
        #
        # self.mmc.setProperty(self.mm_name, "Port X", "xi-com:%5C%5C.%5CCOM6")
        # self.mmc.setProperty(self.mm_name, "Port Y", "xi-com:%5C%5C.%5CCOM7")
        # self.mmc.setProperty(self.mm_name, "UnitMultiplierX", "0.054")
        # self.mmc.setProperty(self.mm_name, "UnitMultiplierY", "0.054")
        # self.mmc.initializeDevice(self.mm_name)

        self.mac_guiver.write_to_splash_screen("Loading Rotation standa")

        # Load library
        def __ximc_shared_lib(dll_path):
            try:
                # if platform.system() == "Linux":
                #     return CDLL("libximc.so")
                # elif platform.system() == "FreeBSD":
                #     return CDLL("libximc.so")
                # elif platform.system() == "Darwin":
                #     return CDLL("libximc.framework/libximc")
                # elif platform.system() == "Windows":
                #     return WinDLL("standa/libximc.dll")
                # else:
                #     return None
                return ctypes.WinDLL(dll_path)

            # except ImportError as err:
            #     self.mac_guiver.write_to_splash_screen(
            #         "Can't import pyximc module. The most probable reason is that you changed the relative location "
            #         "of the Standa_XY.py and pyximc.py files. See developers' documentation for details.",
            #         type="warn")
            #     return None
            except OSError as err:
                self.mac_guiver.write_to_splash_screen(
                    "Can't load libximc library. Please add all shared libraries to the appropriate places. It is "
                    "decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev "
                    "package.\nmake sure that the architecture of the system and the interpreter is the same",
                    type="warn")
                return None


         # TODO direct to the standa repertory for the dll
        cur_dir = os.path.abspath(os.path.dirname(__file__))
        # ximc_dir = os.path.join(cur_dir, "..", "..", "ximc")
        # ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
        ximc_dir = os.path.normpath(os.path.join(cur_dir, "standa"))
        ximc_package_dir = ximc_dir
        sys.path.append(ximc_package_dir)  # add ximc.py wrapper to python path

        # variable 'lib' points to a loaded library
        # note that ximc uses stdcall on win
        # if sys.platform in ("win32", "win64"):
        #     libdir = os.path.join(ximc_dir, sys.platform)
        #     os.environ["Path"] = libdir + ";" + os.environ["Path"]  # add dll

        # test if lib file exits
        ximc_file_path = os.path.normpath(os.path.join(ximc_dir, "libximc.dll"))
        file_exist = os.path.isfile(ximc_file_path)

        # The libximc.dll depends on other dll, and we need to change the working directory for the program to find them
        os.chdir(ximc_dir)

        self.lib = __ximc_shared_lib(ximc_file_path)
        root_path = os.path.dirname(sys.modules['__main__'].__file__)
        os.chdir(root_path)
        if self.lib is None:
            return False

        self.mac_guiver.write_to_splash_screen("ximc.dll found")

        # Clarify function types
        self.lib.enumerate_devices.restype = POINTER(device_enumeration_t)
        self.lib.get_device_name.restype = c_char_p

        # print("Library loaded")

        self.sbuf = create_string_buffer(64)
        self.lib.ximc_version(self.sbuf)
        # print("Library version: " + self.sbuf.raw.decode().rstrip("\0"))

        self.mac_guiver.write_to_splash_screen("Searching for devices. Wait 1 or 2 s")

        # Set bindy (network) keyfile. Must be called before any call to "enumerate_devices" or "open_device" if you
        # wish to use network-attached controllers. Accepts both absolute and relative paths, relative paths are resolved
        # relative to the process working directory. If you do not need network devices then "set_bindy_key" is optional.
        # In Python make sure to pass byte-array object to this function (b"string literal").
        # lib.set_bindy_key(os.path.join(ximc_dir, "win32", "keyfile.sqlite").encode("utf-8"))
        self.lib.set_bindy_key(os.path.join(ximc_dir, "keyfile.sqlite").encode("utf-8"))

        # This is device search and enumeration with probing. It gives more information about devices.
        probe_flags = EnumerateFlags.ENUMERATE_PROBE + EnumerateFlags.ENUMERATE_NETWORK
        enum_hints = b"addr=192.168.0.1,172.16.2.3"
        # enum_hints = b"addr=" # Use this hint string for broadcast enumerate
        self.devenum = self.lib.enumerate_devices(probe_flags, enum_hints)
        # print("Device enum handle: " + repr(self.devenum))
        # print("Device enum handle type: " + repr(type(self.devenum)))

        self.dev_count = self.lib.get_device_count(self.devenum)

        if self.dev_count == 0 :
            self.mac_guiver.write_to_splash_screen("No device found. Check connections", type="warn")
            return False

        self.mac_guiver.write_to_splash_screen("Device count: " + repr(self.dev_count))

        self.controller_name = controller_name_t()
        for dev_ind in range(0, self.dev_count):
            self.enum_name = self.lib.get_device_name(self.devenum, dev_ind)
            result = self.lib.get_enumerate_device_controller_name(self.devenum, dev_ind, byref(self.controller_name))
            if result == Result.Ok:
                self.mac_guiver.write_to_splash_screen("Enumerated device #{} name (port name): ".format(dev_ind) + repr(
                    self.enum_name) + ". Friendly name: " + repr(self.controller_name.ControllerName) + ".")

        self.open_name = None
        # if len(sys.argv) > 1:
        #     self.open_name = sys.argv[1]
        # elif self.dev_count > 0:
        #     self.open_name = self.lib.get_device_name(self.devenum, 0)
        # elif sys.version_info >= (3, 0):
        #     # use URI for virtual device when there is new urllib python3 API
        #     self.tempdir = tempfile.gettempdir() + "/testdevice.bin"
        #     if os.altsep:
        #         self.tempdir = self.tempdir.replace(os.sep, os.altsep)
        #     # urlparse build wrong path if scheme is not file
        #     uri = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
        #                                                            netloc=None, path=self.tempdir, params=None, query=None,
        #                                                            fragment=None))
        #     open_name = re.sub(r'^file', 'xi-emu', uri).encode()

        self.open_name_x = self.lib.get_device_name(self.devenum, 0)
        self.open_name_y = self.lib.get_device_name(self.devenum, 1)


        # if type(self.open_name) is str:
        self.open_name_x = self.open_name_x.encode()
        self.open_name_y = self.open_name_y.encode()

        self.mac_guiver.write_to_splash_screen("Open device " + repr(self.open_name_x))
        self.device_id_x = self.lib.open_device(self.open_name_x)
        self.mac_guiver.write_to_splash_screen("Device id: " + repr(self.device_id_x))

        self.mac_guiver.write_to_splash_screen("Open device " + repr(self.open_name_y))
        self.device_id_y = self.lib.open_device(self.open_name_y)
        self.mac_guiver.write_to_splash_screen("Device id: " + repr(self.device_id_y))

        return True


    def move_absolute(self, pos_angle_deg):
        """
        result t XIMC API command move ( device t id, int Position, int uPosition )
        Position position to move.
        uPosition part of the position to move, microsteps. Range: -255..255.

        Upon receiving the command ”move” the engine starts to move with pre-set parameters (speed, acceleration, retention),
        to the point specified to the Position, uPosition.
        For stepper motor uPosition sets the microstep, for DC motor this field is not used.

        :param pos_micron:
        :return:
        """
        nb_of_step = pos_angle_deg

        result = self.lib.command_move(self.device_id_x, nb_of_step, 0)
        return result


    def move_relative(self, pos_angle_deg):
        """
        result t XIMC API command move ( device t id, int Position, int uPosition )
        Position position to move.
        uPosition part of the position to move, microsteps. Range: -255..255.

        Upon receiving the command ”movr” engine starts to move with pre-set parameters (speed, acceleration, hold),
        left or right (depending on the sign of DeltaPosition) by the number of pulses specified in the fields DeltaPosition,
        uDeltaPosition.

        DeltaPosition shift from initial position
        uDeltaPosition part of the offset shift, microsteps. Range: -255..255.

        :param pos_micron:
        :return:
        """

        #TODO WHAT IS THE UNIT for DC Motor ???? -> counts
        nb_of_step = int(pos_angle_deg * self.step_multiplier)

        result = self.lib.command_movr(self.device_id_x, nb_of_step, 0)
        # self.get_position()
        # result = self.lib.command_move(self.device_id_x, self.posMicron[0] + pos_micron[0], 0)
        # result = self.lib.command_move(self.device_id_y, self.posMicron[1] + pos_micron[1], 0)
        print(result)
        # return result

    def continous_move(self):
        """
        result t XIMC API command_right ( device t id )
        Start continous moving to the right.

        result t XIMC API command_left ( device t id )

        Start continous moving to the left.

        :return:
        """
        #TODO
        pass


    def wait_for_device(self):
        """
        result t XIMC API command wait for stop ( device t id, uint32 t refresh interval ms )

        Status refresh interval. The function waits this number of milliseconds between
        get status requests to the controller. Recommended value of this parameter
        is 10 ms. Use values of less than 3 ms only when necessary - small refresh
        interval values do not significantly increase response time of the function, but
        they create substantially more traffic in controller-computer data channel.

        RESULT OK if controller has stopped and result of the first get status command
        which returned anything other than RESULT OK otherwise.

        :return:
        """
        self.is_busy_ = True
        interval = 10

        result = -1

        while result != 0:
            result_x = self.lib.command_wait_for_stop(self.device_id_x, interval)
            result = result_x

        self.is_busy_ = False

    def stop(self):
        """
        result t XIMC API command sstp ( device t id )
        Soft stop engine.
        The motor stops with deceleration speed.


        result t XIMC API command stop ( device t id )
        Immediately stop the engine, the transition to the STOP, mode key BREAK (winding short-circuited), the regime
        ”retention” is deactivated for DC motors, keeping current in the windings for stepper motors (with Power management
        settings).

        :return:
        """
        result = self.lib.command_stop(self.device_id_x)
        return result

    def is_busy(self):
        return self.is_busy_

    def close_device(self, params=None):
        result = self.lib.close_device(byref(cast(self.device_id_x, POINTER(c_int))))
        # self.lib.close_device(self.device_id_y)
        return result


    def get_position(self):
        # print("\nRead position")
        x_pos = get_position_t()
        result = self.lib.get_position(self.device_id_x, byref(x_pos))
        if result == Result.Ok:
            self.pos_angle_deg = x_pos.Position

        # print("Result: " + repr(result))
        #
        #     print("Position: {0} steps, {1} microsteps".format(x_pos.Position, x_pos.uPosition))
        # return x_pos.Position, x_pos.uPosition


    def get_info(self):
        print("\nGet device info")
        x_device_information = device_information_t()
        result = self.lib.get_device_information(self.device_id, byref(x_device_information))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Device information:")
            print(" Manufacturer: " +
                  repr(string_at(x_device_information.Manufacturer).decode()))
            print(" ManufacturerId: " +
                  repr(string_at(x_device_information.ManufacturerId).decode()))
            print(" ProductDescription: " +
                  repr(string_at(x_device_information.ProductDescription).decode()))
            print(" Major: " + repr(x_device_information.Major))
            print(" Minor: " + repr(x_device_information.Minor))
            print(" Release: " + repr(x_device_information.Release))

    def test_status(self):
        print("Get status\n")
        x_status = status_t()
        result = self.lib.get_status(self.device_id, byref(x_status))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Status.Ipwr: " + repr(x_status.Ipwr))
            print("Status.Upwr: " + repr(x_status.Upwr))
            print("Status.Iusb: " + repr(x_status.Iusb))
            print("Status.Flags: " + repr(hex(x_status.Flags)))

    def test_serial(self):
        print("\nReading serial")
        x_serial = c_uint()
        result = self.lib.get_serial_number(self.device_id, byref(x_serial))
        if result == Result.Ok:
            print("Serial: " + repr(x_serial.value))


    def get_speed(self):
        print("\nGet speed")
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller
        result = self.lib.get_move_settings(self.device_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        print("Read command result: " + repr(result))

        return mvst.Speed


    def test_set_speed(self, speed):
        print("\nSet speed")
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller
        result = self.lib.get_move_settings(self.device_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        print("Read command result: " + repr(result))
        print("The speed was equal to {0}. We will change it to {1}".format(mvst.Speed, speed))
        # Change current speed
        mvst.Speed = int(speed)
        # Write new move settings to controller
        result = self.lib.set_move_settings(self.device_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        print("Write command result: " + repr(result))



if __name__ == "__main__":

    class macGuiver():
        def __init__(self):
            self.mmc = None
            self.root = None

    macGuiver = macGuiver()
    standa = Standa_XY(macGuiver)
    standa.load_device()
