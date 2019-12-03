from Device import Device
import ctypes
import os, sys
import threading
import Tkinter as tk
import ttk
from PIL import Image, ImageTk

class FPGA_nist(Device):
    FPGA_NO_CHANGE = 0
    FPGA_CLEAR = 1
    FPGA_DISABLE = 2
    FPGA_ENABLE = 4
    FPGA_GETDATA = 8

    def __init__(self, mac_guiver, frameName="FPGA Nist", mm_name=""):
        super(FPGA_nist, self).__init__(mac_guiver, frameName, mm_name)
        self.stats = ctypes.c_longlong * 16
        self.file_path = None
        self.nb_of_evt = 1000
        self.is_time_tagging = None
        self.initialized = self.load_device()
        if self.initialized == False:
            return
        self.mac_guiver.write_to_splash_screen("FPGA nist OK")

        self.create_GUI()

    def load_device(self, params=None):
        self.mac_guiver.write_to_splash_screen("Loading FPGA NIST")
        return True

        # Load library
        def __fpga_lib(dll_path):
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

        self.lib_fpga_dll = __fpga_lib(fpga_file_path)
        root_path = os.path.dirname(sys.modules['__main__'].__file__)
        os.chdir(root_path)
        if self.lib_fpga_dll is None:
            return False

        self.mac_guiver.write_to_splash_screen("Stats.dll found")

        self.FPGA_TimeTag_fct = self.lib_fpga_dll.FPGA_TimeTag
        # int FPGA_TimeTag(bool saveClicks, unsigned char  fpgaCommand, char* fileName, __int64* stats, int runs);
        self.FPGA_TimeTag_fct.argtypes = [ctypes.c_bool, ctypes.c_ubyte, ctypes.c_char_p, ctypes.POINTER(ctypes.c_longlong), ctypes.c_int]

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
        self.thread_monitor = threading.Thread(name='FGPA record', target=self.time_tag)
        self.thread_monitor.start()

    def time_tag(self):
        self.clear()
        self.lib_fpga_dll.FPGA_TimeTag(True, FPGA_nist.FPGA_ENABLE, self.file_path, self.stats, self.nb_of_evt)
        self.is_time_tagging = False
        self.label_LED_busy.configure(image=self.tkimage_off)

    def stop(self):
        if self.thread_monitor.is_alive():
            self.lib_fpga_dll.FPGA_TimeTag(False, FPGA_nist.FPGA_DISABLE, "", self.stats, 1)
            self.clear()
            self.thread_monitor.join(timeout=0.5)
        self.is_time_tagging = False
        self.label_LED_busy.configure(image=self.tkimage_off)


    def change_file_path(self, file_path):
        self.file_path = file_path.encode('utf8')

    def create_GUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                   borderwidth=1)

        img = Image.open("./Ressource/OffSmall.png")
        self.tkimage_off = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/OnSmall.png")
        self.tkimage_on = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/chooseFile.png")
        self.tkimage_open = ImageTk.PhotoImage(img)

        ttk.Label(self.frame, text='File Path').grid(row=0, column=0)

        self.file_path_sv = tk.StringVar(value="test.ttt")
        e = ttk.Entry(self.frame, textvariable=self.file_path_sv, justify=tk.CENTER, width=7).grid(row=0, column=1)
        # e.configure(state='readonly')

        tk.Button(self.frame, text='Open', image=self.tkimage_open, command=self.select_time_tag_file).grid(row=0, column=2)

        tk.Button(self.frame, text='Clear', command=self.clear).grid(row=0, column=3)
        tk.Button(self.frame, text='Start', command=self.start).grid(row=0, column=4)
        tk.Button(self.frame, text='Stop',  command=self.stop).grid(row=0, column=5)

        self.label_LED_busy = ttk.Label(self.frame, image=self.tkimage_off)
        self.label_LED_busy.grid(row=0, column=6)


    def select_time_tag_file(self):
        pass





