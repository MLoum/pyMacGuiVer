# coding: utf-8
from hardware.Device import Device
import ctypes
import os, sys
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import time
from PIL import Image, ImageTk

class FPGA_nist(Device):
    FPGA_NO_CHANGE = 0
    FPGA_CLEAR = 1
    FPGA_DISABLE = 2
    FPGA_ENABLE = 4
    # FPGA_GETDATA = 8  # only for counts firmware.

    def __init__(self, mac_guiver, frameName="FPGA Nist", mm_name=""):
        super(FPGA_nist, self).__init__(mac_guiver, frameName, mm_name)
        array_of_16_longlong  = ctypes.c_longlong * 32
        self.stats = array_of_16_longlong()
        # array_of_16_int  = ctypes.c_int * 32
        # self.stats = array_of_16_int()
        self.file_path = "test.ttt"
        self.nb_of_run = 500
        self.is_time_tagging = None
        self.initialized = self.load_device()
        if self.initialized == False:
            return
        self.mac_guiver.write_to_splash_screen("FPGA nist OK")
        self.nb_of_channel = 4
        self.counts_sv = []
        self.cps_sv = []
        self.previous_counts = [0,0,0,0]
        self.monitoring_delay = 1

        self.thread_time_tag = None
        self.thread_monitor = None

        self.create_GUI()

    def load_device(self, params=None):
        self.mac_guiver.write_to_splash_screen("Loading FPGA NIST")
        # return True

        # Load library
        def load_dll(dll_path):
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
                return ctypes.CDLL(dll_path)

            # except ImportError as err:
            #     self.mac_guiver.write_to_splash_screen(
            #         "Can't import pyximc module. The most probable reason is that you changed the relative location "
            #         "of the Standa_XY.py and pyximc.py files. See developers' documentation for details.",
            #         type="warn")
            #     return None
            except OSError as err:
                self.mac_guiver.write_to_splash_screen(
                    "Can't load the Stats FPGA library. Please add all shared libraries to the appropriate places.",
                    type="warn")
                return None

         # TODO direct to the standa repertory for the dll
        cur_dir = os.path.abspath(os.path.dirname(__file__))

        fpga_dir = os.path.normpath(os.path.join(cur_dir, "fpga"))
        fpga_package_dir = fpga_dir
        sys.path.append(fpga_package_dir)

        # variable 'lib' points to a loaded library
        # note that ximc uses stdcall on win
        # if sys.platform in ("win32", "win64"):
        #     libdir = os.path.join(ximc_dir, sys.platform)
        #     os.environ["Path"] = libdir + ";" + os.environ["Path"]  # add dll

        # test if lib file exits
        fpga_file_path = os.path.normpath(os.path.join(fpga_dir, "Stats.dll"))
        file_exist = os.path.isfile(fpga_file_path)

        # The libximc.dll depends on other dll, and we need to change the working directory for the program to find them
        os.chdir(fpga_dir)

        self.lib_fpga_dll = load_dll(fpga_file_path)
        root_path = os.path.dirname(sys.modules['__main__'].__file__)
        os.chdir(root_path)
        if self.lib_fpga_dll is None:
            return False

        self.mac_guiver.write_to_splash_screen("Stats.dll found")

        self.FPGA_TimeTag_fct = self.lib_fpga_dll.FPGA_TimeTag
        # int FPGA_TimeTag(bool saveClicks, unsigned char  fpgaCommand, char* fileName, __int64* stats, int runs);
        self.FPGA_TimeTag_fct.argtypes = [ctypes.c_bool, ctypes.c_ubyte, ctypes.c_char_p, ctypes.POINTER(ctypes.c_longlong), ctypes.c_int]

        # int FPGA_TimeTag(bool saveClicks, unsigned char fpgaCommand, char * fileName, int * stats, int runs);
        # self.FPGA_TimeTag_fct.argtypes = [ctypes.c_bool, ctypes.c_ubyte, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        """
        runs: integer number of USB queries the DLL should perform before returning the results to this
        LabVIEW VI. It is recommended to keep this number high enough to ensure that the LabVIEW
        interface isn’t jittery, but low enough that internal buffers in the FPGA don’t overflow with data
        (this takes a lot of data).
        
        saveData: boolean telling the DLL whether or not to save the data to file.
        
        fileName: string giving the full file name and path of the file in which data should be stored. If
        a file with the same name exists, data will be appended to that file.
        
        fpgaCommand: An unsigned byte containing a character representing a command to the FPGA.
        The commands accepted are detailed in Table 5.
        
        error in: error signal from previously executed VIs
        
        stats a 16-element array containing click and coincidence counts during the time since the last
        USB communication with the FPGA. The array contains starts, clicks on each channel, and the 
        various coincidences. The particular format of these data are detailed in the Sec. 6 section.
        
        function return: an integer giving the status of the output. 0 indicates no errors, while negative
        values indicate certain errors.
        """

        res = self.lib_fpga_dll.USB_Open()
        if res != 0:
            return False
        else:
            return True

    def clear(self):
        self.lib_fpga_dll.FPGA_TimeTag(False, FPGA_nist.FPGA_CLEAR, "", self.stats, 1)

    def start(self):

        self.is_time_tagging = True
        self.label_LED_busy.configure(image=self.tkimage_on)
        self.thread_time_tag = threading.Thread(name='FGPA record', target=self.time_tag)
        self.thread_monitor = threading.Thread(name='FGPA monitor', target=self.monitor)
        self.thread_time_tag.start()
        self.thread_monitor.start()

    def monitor(self):
        while self.is_time_tagging:
            self.monitor_display()
            time.sleep(self.monitoring_delay)

    def time_tag(self):
        self.clear()
        # self.lib_fpga_dll.FPGA_TimeTag(True, FPGA_nist.FPGA_ENABLE, "test.ttt", self.stats, self.nb_of_run)
        self.lib_fpga_dll.FPGA_TimeTag(False, FPGA_nist.FPGA_ENABLE, "", self.stats, 1)
        self.lib_fpga_dll.FPGA_TimeTag(True, FPGA_nist.FPGA_NO_CHANGE, self.file_path, self.stats, self.nb_of_run)
        self.lib_fpga_dll.FPGA_TimeTag(False, FPGA_nist.FPGA_DISABLE + FPGA_nist.FPGA_CLEAR, "", self.stats, 1)
        self.is_time_tagging = False
        self.label_LED_busy.configure(image=self.tkimage_off)

    def stop(self):
        if self.thread_time_tag.is_alive():
            self.lib_fpga_dll.FPGA_TimeTag(False, FPGA_nist.FPGA_DISABLE + FPGA_nist.FPGA_CLEAR, "", self.stats, 1)
            self.clear()
            self.thread_time_tag.join(timeout=0.5)
            self.thread_monitor.join(timeout=0.5)
        self.is_time_tagging = False
        self.label_LED_busy.configure(image=self.tkimage_off)


    def close_device(self, params=None):
        self.lib_fpga_dll.USB_Close()

    def change_file_path(self, file_path):
        # self.file_path = file_path.encode('utf8')
        self.file_path = file_path

    def create_GUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                   borderwidth=1)

        img = Image.open("./Ressource/led-green-off.png")
        self.tkimage_off = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/led-green-on.png")
        self.tkimage_on = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/chooseFile.png")
        self.tkimage_open = ImageTk.PhotoImage(img)

        ttk.Label(self.frame, text='File Path').grid(row=0, column=0)

        self.file_path_sv = tk.StringVar(value="test.ttt")
        e = ttk.Entry(self.frame, textvariable=self.file_path_sv, justify=tk.CENTER, width=75).grid(row=0, column=1)
        # e.configure(state='readonly')

        tk.Button(self.frame, text='Open', image=self.tkimage_open, command=self.select_time_tag_file).grid(row=0, column=2)

        ttk.Label(self.frame, text='nb of run').grid(row=1, column=0)

        self.frame_runs = tk.Frame(self.frame)
        self.frame_runs.grid(row=1, column=1)
        self.nb_of_run_current_sv = tk.StringVar(value=str(0))
        e = ttk.Entry(self.frame_runs, textvariable=self.nb_of_run_current_sv, justify=tk.CENTER, width=7)
        e.configure(state='readonly')
        e.grid(row=0, column=0)

        ttk.Label(self.frame_runs, text='/').grid(row=0, column=1)
        self.nb_of_run_sv = tk.StringVar(value=str(self.nb_of_run))
        e = ttk.Entry(self.frame_runs, textvariable=self.nb_of_run_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.change_nb_of_run())
        e.grid(row=0, column=2)


        tk.Button(self.frame, text='Clear', command=self.clear).grid(row=1, column=2)
        tk.Button(self.frame, text='Start', command=self.start).grid(row=1, column=3)
        tk.Button(self.frame, text='Stop',  command=self.stop).grid(row=1, column=4)

        self.label_LED_busy = ttk.Label(self.frame, image=self.tkimage_off)
        self.label_LED_busy.grid(row=1, column=5)


        self.frame_monitor = tk.LabelFrame(self.frame, text="monitor",
                                   borderwidth=1)
        self.frame_monitor.grid(row=0, column=6, rowspan=2)

        for i in range(self.nb_of_channel):
            ttk.Label(self.frame_monitor, text='Ch ' + str(i+1)).grid(row=0, column=i+1)
            self.counts_sv.append(tk.StringVar(value="0"))
            e = ttk.Entry(self.frame_monitor, textvariable=self.counts_sv[i], justify=tk.CENTER, width=7)
            e.configure(state='readonly')
            e.grid(row=1, column=i+1)
            self.cps_sv.append(tk.StringVar(value="0"))
            e = ttk.Entry(self.frame_monitor, textvariable=self.cps_sv[i], justify=tk.CENTER, width=7)
            e.configure(state='readonly')
            e.grid(row=2, column=i+1)

        ttk.Label(self.frame_monitor, text='Counts').grid(row=1, column=0)
        ttk.Label(self.frame_monitor, text='CPS').grid(row=2, column=0)


    def monitor_display(self):
        self.nb_of_run_current_sv.set(str(self.stats[0]))
        for i in range(self.nb_of_channel):
            self.counts_sv[i].set(str(self.stats[i+1]))
            self.cps_sv[i].set(str((self.stats[i+1] - self.previous_counts[i])/self.monitoring_delay))
            self.previous_counts[i] = self.stats[i+1]

    def select_time_tag_file(self):
        #TODO initial file
        # file_path = filedialog.asksaveasfile(title="ttt file name ?", initialdir=self.mac_guiver.save_dir, initialfile=initialfile)
        file_path = filedialog.asksaveasfile(title="ttt file name ?", initialdir=self.mac_guiver.save_dir)
        if file_path == None or file_path.name == '':
            return None
        else:
            self.file_path = file_path.name
            self.file_path_sv.set(self.file_path )

    def change_nb_of_run(self):
        self.nb_of_run = int(self.nb_of_run_sv.get())




