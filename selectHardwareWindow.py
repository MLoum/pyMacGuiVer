import Tkinter as tk
import ttk


class SelectHardwareWindow():

    def __init__(self, root):
        self.root = root
        self.config = self.root.config

        self.hardware_dict = {
            'MCL XY': tk.IntVar(0),
            'Standa XY': tk.IntVar(0),
            'Arduino Counting': tk.IntVar(0),
            'XY Scanner': tk.IntVar(0),
            'Joystick control': tk.IntVar(0),
            'Elveflow OB1': tk.IntVar(0),
            'Fianium (Work In progress)': tk.IntVar(0),
            'Spectro (Work In progress)': tk.IntVar(0),
            'Arduino Pulser': tk.IntVar(0),
            'FPGA Nist': tk.IntVar(0),
            'Thorlabs Filter Slider': tk.IntVar(0),
            'Valve Manager': tk.IntVar(0),
        }
        self.create_widget()
        # self.top_level.deiconify()

    def create_widget(self):
        # self.top_level = tk.Toplevel(self.root.root)
        # self.top_level.title("Select hardware")

        # check last selected hardware from previous session
        for item in self.config.selected_hardware:
            self.hardware_dict[item].set(1)

        self.top_level = tk.LabelFrame(self.root.root, text="Select Hardware")
        self.top_level.pack()

        i = 0
        for key, value in self.hardware_dict.items():
            tk.Checkbutton(self.top_level, text=key, variable=value).grid(row=i, column=0)
            i += 1

        self.exit_button = tk.Button(self.top_level, text="OK", command=self.on_exit)
        self.exit_button.grid(row=i+1, column=0)

    def on_exit(self):
        # selection = {}
        # selection['MCL_XY'] = self.MCL_cb_iv.get()
        # selection['Standa_XY'] = self.standa_cb_iv.get()
        # selection['Arduino_counting'] = self.arduino_counting_cb_iv.get()
        # selection['scan-arduino-standa'] = self.scan_arduino_Standa_cb_iv.get()
        # selection['Fianium'] = self.fianium_cb_iv.get()
        # selection['Spectro'] = self.spectro_cb_iv.get()
        # selection['joy_crtl'] = self.joy_cb_iv.get()
        # selection["Elveflow OB1"] = self.OB1_cb_iv.get()
        # selection["Arduino_pulser"] = self.arduino_pulser_cb_iv.get()
        # selection["FPGA Nist"] = self.fpga_nist_cb_iv.get()
        # selection["Thorlabs_filter_select"] = self.Thorlabs_filter_select_cb_iv.get()
        # selection["Valve Manager"] = self.Valve_Manager_cb_iv.get()

        self.config.save_selected_hardware(self.hardware_dict)
        self.root.start_splash_screen(self.hardware_dict)
        self.top_level.destroy()
