# coding=utf-8
from hardware.Device import Device
import threading, time
import os, sys
import ctypes
import tkinter as tk
from tkinter import ttk
# from tkinter import filedialog, messagebox, simpledialog
from hardware.ElveFlow import Elveflow64

class OB1MK3(Device):
    def __init__(self, mac_guiver, frameName="OB1MK3", mm_name=""):
        self.Instr_ID = None
        self.elveflow_dll = None
        self.Calib = None
        self.Calib_path = None
        self.calib_length = 1000
        self.presurres = [0, 0, 0, 0]
        self.flows = [0, 0, 0, 0]
        self.is_monitor, self.thread_monitor = None, None
        self.monitor_time_s = 0.5
        super(OB1MK3, self).__init__(mac_guiver, frameName, mm_name)
        # FIXME
        self.create_GUI()
        self.initialized = True

    def load_device(self, params=None):
        # FIXME
        return True

        cur_dir = os.path.abspath(os.path.dirname(__file__))
        elveflow_dir = os.path.normpath(os.path.join(cur_dir, "ElveFlow/DLL64"))

        sys.path.append(elveflow_dir)

        elveflowfile_path = os.path.normpath(os.path.join(elveflow_dir, "Elveflow64.dll"))
        file_exist = os.path.isfile(elveflowfile_path)

        # The Elveflow64.dll depends on other dll, and we need to change the working directory for the program to find them
        os.chdir(elveflow_dir)

        # Load library
        def load_dll(dll_path):
            try:
                return ctypes.CDLL(dll_path)

            # except ImportError as err:
            #     self.mac_guiver.write_to_splash_screen(
            #         "Can't import pyximc module. The most probable reason is that you changed the relative location "
            #         "of the Standa_XY.py and pyximc.py files. See developers' documentation for details.",
            #         type="warn")
            #     return None
            except OSError as err:
                self.mac_guiver.write_to_splash_screen(
                    "Can't load Eleveflow library",
                    type="warn")
                return None
        if file_exist:
            self.elveflow_dll = load_dll(elveflowfile_path)  # change this path
        else:
            self.mac_guiver.write_to_splash_screen(
                "Eleveflow dll not found, check hardware/OB1_MK3.py",
                type="warn")
            return


        self.Instr_ID = ctypes.c_int32()

        # self.mac_guiver.write_to_splash_screen("loading OB1-MK3 with the identifier : " + str(self.Instr_ID))
        # see User guide to determine regulator type NI MAX to determine the instrument name -> '01B7DFC9'.encode('ascii')

        # Elveflow Library
        # OB1 Device
        #
        # Initialize the OB1 device using device name and regulators type (see SDK
        # Z_regulator_type for corresponding numbers). It modify the OB1 ID (number
        # >=0). This ID can be used be used with other function to identify the
        # targed OB1. If an error occurs during the initialization process, the OB1
        # ID value will be -1.
        #

        # Regulator type :
        # Z_regulator_type_none               0
        # Z_regulator _type__0_200_mbar       1     Yellow
        # Z_regulator_type__0_2000_mbar       2     Blue
        # Z_regulator_type__0_8000_mbar       3     White
        # Z_regulator_type_m1000_1000_mbar    4     Purple
        # Z_regulator_type_m1000_6000_mbar    5     Orange

        X_OB1_Initialization = self.elveflow_dll.OB1_Initialization
        X_OB1_Initialization.argtypes = [ctypes.c_char_p, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint16, ctypes.POINTER(ctypes.c_int32)]
        error = X_OB1_Initialization('01B7DFC9'.encode('ascii'), 2, 2, 5, 5, ctypes.byref(self.Instr_ID))

        if self.Instr_ID == -1:
            print('error:-1')

        print('OB1 ID: %d' % self.Instr_ID.value)

        # Sensors
        # add one analog flow sensor
        # error = Elveflow64.OB1_Add_Sens(self.Instr_ID, 2, 1, 0, 0)
        # print('error add analog flow sensor:%d' % error)


        # Calibration
        self.Calib = (ctypes.c_double * self.calib_length)()  # always define array that way, calibration should have 1000 elements
        self.Calib_path = 'C:/Users/Public/Documents/Elvesys/ESI/bin/01B7DFC9.calib'
        self.Calib_path = os.path.normpath(self.Calib_path)

        # Default Calib
        # Elveflow Library
        # OB1-AF1 Device
        #
        # Set default Calib in Calib cluster, len is the Calib_Array_out array length
        #
        # use ctypes c_double*1000 for calibration array
        X_Elveflow_Calibration_Default = self.elveflow_dll.Elveflow_Calibration_Default
        X_Elveflow_Calibration_Default.argtypes = [ctypes.POINTER(ctypes.c_double * 1000), ctypes.c_int32]
        error = X_Elveflow_Calibration_Default(self.Calib, self.calib_length)

        # error = Elveflow64.Elveflow_Calibration_Default(ctypes.byref(self.Calib), self.calib_length)

        # # Existing
        # # Elveflow Library
        # # OB1-AF1 Device
        # #
        # # Load the calibration file located at Path and returns the calibration
        # # parameters in the Calib_Array_out. len is the Calib_Array_out array length.
        # # The function asks the user to choose the path if Path is not valid, empty
        # # or not a path. The function indicate if the file was found.
        # #
        # # use ctypes c_double*1000 for calibration array
        #
        # X_Elveflow_Calibration_Load = self.elveflow_dll.Elveflow_Calibration_Load
        # X_Elveflow_Calibration_Load.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_double * 1000), ctypes.c_int32]
        # error = X_Elveflow_Calibration_Load(self.Calib_path.encode('ascii'), ctypes.byref(self.Calib), self.calib_length)

        print('error: %f' % error)
        return True
        # error = Elveflow64.Elveflow_Calibration_Load(self.Calib_path.encode('ascii'), ctypes.byref(self.Calib), self.calib_length)


    def add_sensor(self, channel_1_to_4, SensorType_, Digital_or_Analog, FSens_Digit_Calib):
        # int32_t __cdecl OB1_Add_Sens(int32_t OB1_ID, int32_t Channel_1_to_4_, Z_sensor_type SensorType, Z_Sensor_digit_analog Digital_or_Analog, Z_Sensor_FSD_Calib FSens_Digit_Calib);
        """
        typedef uint16_t  Z_regulator_type;
        #define Z_regulator_type_none 0
        #define Z_regulator_type__0_200_mbar 1
        #define Z_regulator_type__0_2000_mbar 2
        #define Z_regulator_type__0_8000_mbar 3
        #define Z_regulator_type_m1000_1000_mbar 4
        typedef uint16_t  Z_sensor_type;
        #define Z_sensor_type_none 0
        #define Z_sensor_type_Flow_1_5_muL_min 1
        #define Z_sensor_type_Flow_7_muL_min 2
        #define Z_sensor_type_Flow_50_muL_min 3
        #define Z_sensor_type_Flow_80_muL_min 4
        #define Z_sensor_type_Flow_1000_muL_min 5
        #define Z_sensor_type_Flow_5000_muL_min 6
        #define Z_sensor_type_Press_70_mbar 7
        #define Z_sensor_type_Press_340_mbar 8
        #define Z_sensor_type_Press_1_bar 9
        #define Z_sensor_type_Press_2_bar 10
        #define Z_sensor_type_Press_7_bar 11
        #define Z_sensor_type_Press_16_bar 12
        #define Z_sensor_type_Level 13
        typedef uint16_t  Z_Sensor_digit_analog;
        #define Z_Sensor_digit_analog_Analog 0
        #define Z_Sensor_digit_analog_Digital 1
        typedef uint16_t  Z_Sensor_FSD_Calib;
        #define Z_Sensor_FSD_Calib_H2O 0
        #define Z_Sensor_FSD_Calib_IPA 1
        """
        error = Elveflow64.OB1_Add_Sens(self.Instr_ID, channel_1_to_4, SensorType_, Digital_or_Analog, FSens_Digit_Calib)

    def launch_calibration(self):
        Elveflow64.OB1_Calib(self.Instr_ID.value, self.Calib, 1000)
        error = Elveflow64.Elveflow_Calibration_Save(self.Calib_path.encode('ascii'), ctypes.byref(self.Calib), self.calib_length)
        print ('calib saved in %s' % self.Calib_path.encode('ascii'))

    def set_pressure(self, channel, pressure):
        channel = ctypes.c_int32(int(channel))
        pressure = ctypes.c_double(float(pressure))
        error = Elveflow64.OB1_Set_Press(self.Instr_ID.value, channel, pressure, ctypes.byref(self.Calib), 1000)

    def get_pressure(self, Channel_1_to_4, Acquire_Data1True0False):
        # int32_t __cdecl OB1_Get_Press(int32_t OB1_ID, int32_t Channel_1_to_4, int32_t Acquire_Data1True0False, double Calib_array_in[], double *Pressure, int32_t Calib_Array_len);
        pressure = 0
        error = Elveflow64.OB1_Get_Press(self.Instr_ID.value, Channel_1_to_4, Acquire_Data1True0False, ctypes.byref(self.Calib), ctypes.byref(pressure), self.calib_length)
        return pressure

    def get_sensor_data(self):
        pass

    def read_all(self):
        data_sens = ctypes.c_double()
        data_pressure = ctypes.c_double()

        # Elveflow Library
        # OB1 Device
        #
        #
        # Get the pressure of an OB1 channel.
        #
        # Calibration array is required (use Set_Default_Calib if required) and
        # return a double . Len correspond to the Calib_array_in length.
        #
        # If Acquire_data is true, the OB1 acquires ALL regulator AND ALL analog
        # sensor value. They are stored in the computer memory. Therefore, if several
        # regulator values (OB1_Get_Press) and/or sensor values (OB1_Get_Sens_Data)
        # have to be acquired simultaneously, set the Acquire_Data to true only for
        # the First function. All the other can used the values stored in memory and
        # are almost instantaneous.
        #
        # use ctypes c_double*1000 for calibration array
        # use ctype c_double*4 for pressure array

        X_OB1_Get_Press = self.elveflow_dll.OB1_Get_Press
        X_OB1_Get_Press.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_double * 1000), ctypes.POINTER(ctypes.c_double), ctypes.c_int32]
        error = X_OB1_Get_Press(self.Instr_ID.value, 1, 1, ctypes.byref(self.Calib), ctypes.byref(data_pressure),
                               self.calib_length) # Ch =1;  Acquire_data =1 -> Read all the analog value
        # error = Elveflow64.OB1_Get_Press(self.Instr_ID.value, 1, 1, ctypes.byref(self.Calib), ctypes.byref(data_pressure),
        #                       self.calib_length)  # Ch =1;  Acquire_data =1 -> Read all the analog value

        self.presurres[0] = data_pressure
        # NB pourquoi de 2 à 5, pourquoi pas 1 ? j'ai recopié le code de démo..., peut-être parce que l'on a déjà lu le 1
        for i in range(2, 5):
            # error = Elveflow64.OB1_Get_Press(self.Instr_ID.value, i, 0, ctypes.byref(self.Calib), ctypes.byref(data_pressure),
            #                                  self.calib_length)  # Ch = i;  Acquire_data =0 -> Use the value acquired in OB1_Get_Press
            error = X_OB1_Get_Press(self.Instr_ID.value, i, 0, ctypes.byref(self.Calib), ctypes.byref(data_pressure),
                                    self.calib_length)  # Ch =1;  Acquire_data =1 -> Read all the analog value
            self.presurres[i-1] = data_pressure.value

        # for i in range(1, 5):
        #     error = Elveflow64.OB1_Get_Sens_Data(self.Instr_ID.value, i, 0, ctypes.byref(
        #         data_sens))  # Ch = i;  Acquire_data =0 -> Use the value acquired in OB1_Get_Press
        #     self.flows[i - 1] = data_sens


    def launch_monitor(self):
        self.is_monitor = True
        self.thread_monitor = threading.Thread(name='OB1_monitor_thread', target=self.monitor)
        self.thread_monitor.start()

    def stop_monitor(self):
        if self.thread_monitor.is_alive():
            self.thread_monitor.join(timeout=0.5)
        self.is_monitor = False

    def monitor(self):
        while self.is_monitor == True:
            self.read_all()
            self.update_gui()
            time.sleep(self.monitor_time_s)
        self.is_monitor = False

    def update_gui(self):
        pass

    def create_GUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                         borderwidth=1)
        nb_of_channel = 4
        self.frames_channel = [None]*nb_of_channel
        self.frames_channel_p = [None] * nb_of_channel
        self.frames_channel_flow = [None] * nb_of_channel
        self.frames_channel_regulation = [None] * nb_of_channel

        self.regulation_vals = []
        self.regulation_etiqs = []

        self.list_sv_regulation = []
        self.list_sv_p_val = []
        self.list_label_p_val = []
        self.list_sv_p_enter = []
        self.list_entry_p_enter = []
        self.list_button_set_p = []

        self.list_sv_flow_val = []
        self.list_label_flow_val = []
        self.list_sv_flow_enter = []
        self.list_entry_flow_enter = []
        self.list_button_set_flow = []

        # self.frame_legend = tk.LabelFrame(self.frame, text="", borderwidth=1)
        # tk.Label(self.frame_legend, text="P (mBar)").grid(row=0, column=0)
        # tk.Label(self.frame_legend, text="Set P (mBar)").grid(row=1, column=0)
        # tk.Label(self.frame_legend, text="Flow (µL/min)").grid(row=2, column=0)
        # tk.Label(self.frame_legend, text="Set Flow (µL/min)").grid(row=3, column=0)
        # self.frame_legend.pack(side="left", fill='both', expand=1)

        color_bg_val = "gray73"
        # font_ = ("Helvetica", 16)
        font_ = "Helvetica 16 bold"
        font_b = "Helvetica 15"

        for i in range(4):
            self.frames_channel[i] = tk.LabelFrame(self.frame, text="Ch. " + str(i),
                                             borderwidth=1)




            # Pressure value
            self.frames_channel_p[i] = tk.LabelFrame(self.frames_channel[i], text="P (mBar)",
                                             borderwidth=1)
            self.frames_channel_p[i].pack(side="top", fill='both', expand=1)

            self.list_sv_p_val.append(tk.StringVar())
            self.list_label_p_val.append(
                tk.Label(self.frames_channel_p[i], text="0", justify=tk.CENTER, width=10, textvariable=self.list_sv_p_val[i], bg=color_bg_val, font=font_))
            self.list_label_p_val[i].grid(row=0, column=0, columnspan=2)

            # Set_pressure value
            self.list_sv_p_enter.append(tk.StringVar())
            self.list_entry_p_enter.append(
                tk.Entry(self.frames_channel_p[i], textvariable=self.list_sv_p_enter[i], justify=tk.CENTER,
                          width=7, font=font_))
            self.list_entry_p_enter[i].grid(row=1, column=0)
            self.list_button_set_p.append(tk.Button(master=self.frames_channel_p[i], text='set', font=font_b, command=lambda: self.gui_set_pressure(i, self.list_entry_p_enter[i])))
            self.list_button_set_p[i].grid(row=1, column=1)

            # Flow value
            self.frames_channel_flow[i] = tk.LabelFrame(self.frames_channel[i], text="Flow (µL/min)",
                                             borderwidth=1)
            self.frames_channel_flow[i].pack(side="top", fill='both', expand=1)

            self.list_sv_flow_val.append(tk.StringVar())
            self.list_label_flow_val.append(
                tk.Label(self.frames_channel_flow[i], text="0", justify=tk.CENTER, width=10, textvariable=self.list_sv_flow_val[i], bg=color_bg_val, font=font_))
            self.list_label_flow_val[i].grid(row=2, column=0, columnspan=2)

            # Set flow value
            self.list_sv_flow_enter.append(tk.StringVar())
            self.list_entry_flow_enter.append(
                tk.Entry(self.frames_channel_flow[i], textvariable=self.list_sv_flow_enter[i], justify=tk.CENTER,
                          width=7, font=font_))
            self.list_entry_flow_enter[i].grid(row=3, column=0)
            self.list_button_set_flow.append(tk.Button(master=self.frames_channel_flow[i], text='set', font=font_b, command=lambda: self.gui_set_flow(i, self.list_entry_p_enter[i])))
            self.list_button_set_flow[i].grid(row=3, column=1)

            # Regulation
            self.frames_channel_regulation[i] = tk.LabelFrame(self.frames_channel[i], text="Regulation",
                                             borderwidth=1)
            self.frames_channel_regulation[i].pack(side="top", fill='both', expand=1)


            self.regulation_vals.append(["Pressure", "Flow"])
            self.regulation_etiqs.append(["Pressure", "Flow"])
            self.list_sv_regulation.append(tk.StringVar())
            self.list_sv_regulation[i].set(self.regulation_vals[i][0])
            for j in range(len(self.regulation_vals[i])):
                b = ttk.Radiobutton(self.frames_channel_regulation[i], variable=self.regulation_vals[i], text=self.regulation_etiqs[i][j], value=self.regulation_vals[i][j])
                b.pack(side='top', expand=1)

            self.frames_channel[i].pack(side="left", fill='both', expand=1)

    def gui_set_pressure(self, channel, val_sv):
        pass

    def gui_set_flow(self, channel, val_sv):
        pass


    def process_error(self, error):
        if error == -8000:
            return "No Digital Sensor found"
        elif error==8001:
            return "No pressure sensor compatible with OB1 MK3"
        elif error==8002:
            return "No Digital pressure sensor compatible with OB1 MK3+"
        elif error==8003:
            return "No Digital Flow sensor compatible with OB1 MK3"
        elif error==8004:
            return "No IPA config for this sensor"
        elif error==8005:
            return "Sensor not compatible with AF1"
        elif error==8006:
            return "No Instrument with selected ID"

    def close_device(self, params=None):
        # Elveflow Library
        # OB1 Device
        #
        # Close communication with OB1
        #
        X_OB1_Destructor = self.elveflow_dll.OB1_Destructor
        X_OB1_Destructor.argtypes = [ctypes.c_int32]
        error = X_OB1_Destructor(self.Instr_ID.value)


if __name__ == "__main__":

    class macGuiver():
        def __init__(self):
            self.mmc = None
            self.root = None

    macGuiver = macGuiver()
    ob1 = OB1MK3(macGuiver)
    ob1.load_device()
    for i in range(20):
        ob1.read_all()
        print(ob1.presurres)
        time.sleep(0.5)
    ob1.close_device()