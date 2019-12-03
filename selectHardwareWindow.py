import Tkinter as tk
import ttk


class SelectHardwareWindow():

    def __init__(self, root):
        self.root = root
        self.create_widget()
        # self.top_level.deiconify()

    def create_widget(self):
        # self.top_level = tk.Toplevel(self.root.root)
        # self.top_level.title("Select hardware")

        self.top_level = tk.LabelFrame(self.root.root, text="Select Hardware")
        self.top_level.pack()

        self.MCL_cb_iv = tk.IntVar()
        tk.Checkbutton(self.top_level, text="MCL XY", variable=self.MCL_cb_iv).grid(row=0, column=0)

        self.standa_cb_iv = tk.IntVar()
        checkbutton = tk.Checkbutton(self.top_level, text="Standa XY", variable=self.standa_cb_iv)
        checkbutton.grid(row=1, column=0)

        self.arduino_counting_cb_iv = tk.IntVar()
        tk.Checkbutton(self.top_level, text="Arduino Counting", variable=self.arduino_counting_cb_iv).grid(row=2, column=0)


        self.scan_arduino_Standa_cb_iv = tk.IntVar()
        tk.Checkbutton(self.top_level, text="XY Scanner", variable=self.scan_arduino_Standa_cb_iv).grid(row=3, column=0)


        self.OB1_cb_iv = tk.IntVar()
        tk.Checkbutton(self.top_level, text="Elveflow OB1", variable=self.OB1_cb_iv).grid(row=4, column=0)

        self.fianium_cb_iv = tk.IntVar()
        tk.Checkbutton(self.top_level, text="Fianium (Work In progress)", variable=self.fianium_cb_iv).grid(row=5, column=0)

        self.spectro_cb_iv = tk.IntVar()
        checkbutton = tk.Checkbutton(self.top_level, text="Spectro (Work In progress)", variable=self.spectro_cb_iv).grid(row=6, column=0)

        self.joy_cb_iv = tk.IntVar()
        tk.Checkbutton(self.top_level, text="Joystick control", variable=self.joy_cb_iv).grid(row=7, column=0)


        # self.spectro_cb_iv = tk.IntVar()
        # checkbutton = tk.Checkbutton(self.top_level, text="Spectro (Work In progress)", variable=self.spectro_cb_iv)
        # checkbutton.grid(row=5, column=0)

        self.arduino_pulser_cb_iv = tk.IntVar()
        tk.Checkbutton(self.top_level, text="Arduino Pulser", variable=self.arduino_pulser_cb_iv).grid(row=8, column=0)

        self.fpga_nist_cb_iv = tk.IntVar()
        tk.Checkbutton(self.top_level, text="FPGA Nist", variable=self.fpga_nist_cb_iv).grid(row=9, column=0)

        self.Thoralbs_filter_select_cb_iv = tk.IntVar()
        tk.Checkbutton(self.top_level, text="Thorlabs Filter Select", variable=self.Thoralbs_filter_select_cb_iv).grid(row=10, column=0)

        self.exit_button = tk.Button(self.top_level, text="OK", command=self.on_exit)
        self.exit_button.grid(row=11, column=0)

    def on_exit(self):
        selection = {}
        selection['MCL_XY'] = self.MCL_cb_iv.get()
        selection['Standa_XY'] = self.standa_cb_iv.get()
        selection['Arduino_counting'] = self.arduino_counting_cb_iv.get()
        selection['scan-arduino-standa'] = self.scan_arduino_Standa_cb_iv.get()
        selection['Fianium'] = self.fianium_cb_iv.get()
        selection['Spectro'] = self.spectro_cb_iv.get()
        selection['joy_crtl'] = self.joy_cb_iv.get()
        selection["Elveflow OB1"] = self.OB1_cb_iv.get()
        selection["Arduino_pulser"] = self.arduino_pulser_cb_iv.get()
        selection["FPGA Nist"] = self.fpga_nist_cb_iv.get()
        selection["Thoralbs filter select"] = self.Thoralbs_filter_select_cb_iv.get()
        self.root.start_splash_screen(selection)
        self.top_level.destroy()
