from __future__ import print_function
import Tkinter as tk
import ttk
from hardware import MCL_XY, Standa_XY, ArduinoCounting, ArduinoPulser, Spectro, dummy_XYStage, motorArduino, xy_scanner, OB1_MK3, fpga_nist, valveManager, FilterSlide
from Control import midiControl, joystick
from SplashScreen import SplashScreen
from selectHardwareWindow import SelectHardwareWindow
from config import Config
# import MMCorePy
from Menu import Menu
from toolbox import ToolBoxMicroFLuidics

import threading

# Built-in modules
import logging
import threading
import time


class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)

        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


class macGuiver():
    def __init__(self):
        self.root = tk.Tk()
        # self.mmc = None

        self.menu = Menu(self.root, self)

        self.is_hardware_loaded = False

        self.hardware_label_dict = {
            'MCL XY': MCL_XY.madLibCity_XY,
            'Standa XY': Standa_XY.Standa_XY,
            'Arduino Counting':  ArduinoCounting.ArduinoCouting,
            'XY Scanner': xy_scanner.XYScanner,
            'Joystick control': tk.IntVar(0),
            'Elveflow OB1': tk.IntVar(0),
            'Fianium (Work In progress)': tk.IntVar(0),
            'Spectro (Work In progress)': Spectro.Spectro,
            'Arduino Pulser': tk.IntVar(0),
            'FPGA Nist': tk.IntVar(0),
            'Thorlabs Filter Slider': tk.IntVar(0),
            'Valve Manager': tk.IntVar(0),
        }


        self.config = Config()
        self.listHardware = []
        # As for now, we don't need micromanager anymore.
        # self.launch_MicroManager()
        self.splash_screen = None
        # self.start_splash_screen()
        # self.root.update()

        self.save_dir = ""

        self.joystick_listener = None
        self.madLibCity_XY = None

        self.select_hardware_frame = SelectHardwareWindow(self)

        # We have to create a thread to update the GUI. Indeed, there is still no "main loop" for the tkinter app
        # but we already want to have some info on the harware initialization. Hence this small thread
        # thread_harware_init = threading.Thread(name='hardware_init_small_loop', target=self.hardware_init_small_loop)
        # thread_harware_init.start()

        self.root.protocol("WM_DELETE_WINDOW", self.onQuit)

    def hardware_init_small_loop(self):
        while self.is_hardware_loaded is False:
            self.root.update()
            time.sleep(0.5)

    def run(self):
        self.root.title("pyMacGUIver")
        self.root.deiconify()
        self.root.mainloop()

    def launch_MicroManager(self):
        try:
            # self.mmc = MMCorePy.CMMCore()
            # print(self.mmc.getVersionInfo())
            # print(self.mmc.getAPIVersionInfo())
            pass
        except:
            print("Can't launch micro-manager core.\n Exiting.")
            return


    def start_splash_screen(self, hardware_selection):
        self.splash_screen = SplashScreen(self)

        # Create textLogger
        self.splash_log_text_handler = TextHandler(self.splash_screen.txt)

        # Add the handler to logger
        self.splash_logger = logging.getLogger()
        self.splash_logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        self.splash_log_text_handler.setFormatter(formatter)
        self.splash_logger.addHandler(self.splash_log_text_handler)

        time.sleep(0.5)

        self.create_hardware(hardware_selection)
        self.splash_screen.set_exit_btn_ok()
        self.is_hardware_loaded = True

        # self.createMidiControl()



        self.create_gui()
        self.launch_ctrl()
        self.close_splash_screen()
        #self.midiListener.startListening()
        #self.createMenuCommands()
        #self.createShortCut()


    def write_to_splash_screen(self, msg, type="info"):
        if self.splash_screen is None:
            return
        if type == "info":
            self.splash_logger.info(msg)
        elif type == "debug":
            self.splash_logger.debug(msg)
        elif type == "warn":
            self.splash_logger.warn(msg)
        elif type == "critical":
            self.splash_logger.critical(msg)

    def close_splash_screen(self):
        pass


    def create_hardware(self, hardware_selection):

        if hardware_selection["MCL XY"].get() == 1:
            self.madLibCity_XY  = MCL_XY.madLibCity_XY(self)
            if self.madLibCity_XY.initialized:
                self.listHardware.append(self.madLibCity_XY)
        if hardware_selection["Standa XY"].get() == 1:
            self.standa_XY = Standa_XY.Standa_XY(self)
            if self.standa_XY.initialized:
                self.listHardware.append(self.standa_XY)
        if hardware_selection["Arduino Counting"].get() == 1:
            self.countingArduino = ArduinoCounting.ArduinoCouting(self)
            if self.countingArduino.initialized:
                self.listHardware.append(self.countingArduino)
        if hardware_selection["Elveflow OB1"].get() == 1:
            self.ob1 = OB1_MK3.OB1MK3(self)
            if self.ob1.initialized:
                self.listHardware.append(self.ob1)
        if hardware_selection["Arduino Pulser"].get() == 1:
            self.arduino_pulser = ArduinoPulser.ArduinoPulser(self)
            if self.arduino_pulser.initialized:
                self.listHardware.append(self.arduino_pulser)
        if hardware_selection["FPGA Nist"].get() == 1:
            self.fpga_nist = fpga_nist.FPGA_nist(self)
            if self.fpga_nist.initialized:
                self.listHardware.append(self.fpga_nist)
        if hardware_selection["Valve Manager"].get() == 1:
            self.valveManager = valveManager.ValveManager(self)
            if self.valveManager.initialized:
                self.listHardware.append(self.valveManager)

        if hardware_selection["Thorlabs Filter Slider"]:
            pass
            # self.filter_slide = FilterSlide.FilterSlide(self)
            # if self.filter_slide.initialized:
            #     self.listHardware.append(self.filter_slide)

        if hardware_selection["XY Scanner"].get() == 1:
            if self.standa_XY.initialized and self.countingArduino.initialized:
                self.xy_scanner = xy_scanner.XYScanner(self, self.standa_XY, self.countingArduino)
                if self.xy_scanner.initialized:
                    self.listHardware.append(self.xy_scanner)
                    # self.listHardware.append(self.dummy_XY)

        if hardware_selection["Spectro (Work In progress)"].get() == 1:
            self.spectro = Spectro.Spectro(self)
            self.listHardware.append(self.spectro)

        # if hardware_selection["Fianium"].get() == 1:
        #     pass

        # if hardware_selection["midi_crtl"]:
        #     self.create_midi_control()

        if hardware_selection["Joystick control"].get() == 1:
            self.create_joystick_control()
            self.listHardware.append(self.joystick_listener)



    def create_midi_control(self):
        self.midiListener = midiControl.MidiListener(self)
        self.register_midi_callback()
        self.midiListener.createGUI()

    def create_joystick_control(self):
        self.joystick_listener = joystick.JoystickListener(self)
        self.register_joy_callback()
        self.joystick_listener.createGUI()

    def create_gui(self):
        for device in self.listHardware:
            device.frame.pack()

        # self.dummy_XYStage.frame.pack()
        # self.madLibCity_XY.frame.pack()
        # # self.standa_XY.frame.pack()
        # if self.countingArduino.initialized:
        #     self.countingArduino.frame.pack()
        # # self.spectro.createGUI()
        # self.spectro.frame.pack()

        # self.midiListener.frame.pack()

    def launch_ctrl(self):
        if self.joystick_listener is not None:
            self.joystick_listener.start_listening()

    def register_midi_callback(self):
        self.midiListener.registerCallback(type="relative", name="MCL_X", midiCC=32, callBack=[self.dummy_XYStage.move_left, self.dummy_XYStage.move_right])
        self.midiListener.registerCallback(type="relative", name="MCL_Y", midiCC=33,
                                           callBack=[self.dummy_XYStage.move_down, self.dummy_XYStage.move_up])

        self.midiListener.registerCallback(type="relative", name="MCL_StepX_small", midiCC=40, inc=1, tkVariable=self.dummy_XYStage.stepX_sv, callBack=[self.dummy_XYStage.get_GUI_params, self.dummy_XYStage.get_GUI_params])
        self.midiListener.registerCallback(type="relative", name="MCL_StepY_small", midiCC=41, inc=1,
                                           tkVariable=self.dummy_XYStage.stepY_sv, callBack=[self.dummy_XYStage.get_GUI_params, self.dummy_XYStage.get_GUI_params])

        self.midiListener.registerCallback(type="relative", name="MCL_StepX_big", midiCC=48, inc=10, tkVariable=self.dummy_XYStage.stepX_sv, callBack=[self.dummy_XYStage.get_GUI_params, self.dummy_XYStage.get_GUI_params])
        self.midiListener.registerCallback(type="relative", name="MCL_StepY_big", midiCC=49, inc=10,
                                           tkVariable=self.dummy_XYStage.stepY_sv, callBack=[self.dummy_XYStage.get_GUI_params, self.dummy_XYStage.get_GUI_params])

    def register_joy_callback(self):


        if self.madLibCity_XY is not None:
            self.joystick_listener.registerCallback(type="button", num=0, name="MCL_dblStep",
                                                    callBack=self.madLibCity_XY.double_step)
            self.joystick_listener.registerCallback(type="button", num=1, name="MCL_halfStep",
                                                    callBack=self.madLibCity_XY.halve_step)

            self.joystick_listener.registerCallback(type="axis", num=1, name="MCL_up", callBack=self.madLibCity_XY.move_right)
            self.joystick_listener.registerCallback(type="axis", num=-1, name="MCL_down", callBack=self.madLibCity_XY.move_left)
            self.joystick_listener.registerCallback(type="axis", num=2, name="MCL_left", callBack=self.madLibCity_XY.move_down)
            self.joystick_listener.registerCallback(type="axis", num=-2, name="MCL_right", callBack=self.madLibCity_XY.move_up)


    def show_microfluidics_tool_box(self):
        ToolBoxMicroFLuidics.ToolBoxMicrofluidics(self.root)

    def onQuit(self):
        # paramFile = open('param.ini', 'w')
        # paramFile.write(self.saveDir)
        self.root.destroy()
        self.root.quit()




if __name__ == "__main__":
    macGuiver = macGuiver()
    macGuiver.run()