#!/usr/bin/env python
#-*- coding: utf-8 -*-

from Device import Device

import Tkinter as tk
import tkMessageBox
import tkFileDialog


import ttk
from PIL import Image, ImageTk

import threading
import time

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# #matplotlib.use("TkAgg")
# import matplotlib.patches as patches
# import matplotlib.gridspec as gridspec
# from mpl_toolkits.mplot3d import Axes3D
# import time
import numpy as np

class XYScanner(Device):
    def __init__(self, mac_guiver, xyStage, counter, frameName="XY_Scanner", mm_name=""):
        self.frameName = frameName
        super(XYScanner, self).__init__(mac_guiver, frameName=self.frameName, mm_name=mm_name)

        self.xyStage = xyStage
        self.counter = counter

        self.stop_scan = False

        self.initialized = self.load_device()

        if self.initialized:
            self.create_GUI()
            # self.get_GUI_params()

    def load_device(self, params=None):
        if self.xyStage.initialized and self.counter.initialized:
            return True
        else:
            return False

    def create_GUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                         borderwidth=1)

        self.frame_cmd = tk.Frame(self.frame)
        self.frame_cmd.pack(fill='both', expand=1)


        label = ttk.Label(self.frame_cmd, text='Scan step (µm)')
        label.grid(row=0, column=0)
        self.scan_step_sv = tk.StringVar()
        e = ttk.Entry(self.frame_cmd, textvariable=self.scan_step_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.get_GUI_params())
        e.grid(row=0, column=1)
        self.scan_step_sv.set('25')

        label = ttk.Label(self.frame_cmd, text='nb of step X')
        label.grid(row=1, column=0)
        self.nb_step_X_sv = tk.StringVar()
        e = ttk.Entry(self.frame_cmd, textvariable=self.nb_step_X_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.get_GUI_params())
        e.grid(row=1, column=1)
        self.nb_step_X_sv.set('10')

        label = ttk.Label(self.frame_cmd, text='nb of step Y')
        label.grid(row=1, column=2)
        self.nb_step_Y_sv = tk.StringVar()
        e = ttk.Entry(self.frame_cmd, textvariable=self.nb_step_Y_sv, justify=tk.CENTER, width=7)
        e.bind('<Return>', lambda e: self.get_GUI_params())
        e.grid(row=1, column=3)
        self.nb_step_Y_sv.set('10')

        label = ttk.Label(self.frame_cmd, text='Scan size X (µm)')
        label.grid(row=1, column=4)
        self.size_X_sv = tk.StringVar()
        e = ttk.Entry(self.frame_cmd, textvariable=self.size_X_sv, justify=tk.CENTER, width=7)
        e.configure(state='readonly')
        e.grid(row=1, column=5)
        self.size_X_sv.set('250')

        label = ttk.Label(self.frame_cmd, text='Scan size X (µm)')
        label.grid(row=1, column=6)
        self.size_Y_sv = tk.StringVar()
        e = ttk.Entry(self.frame_cmd, textvariable=self.size_Y_sv, justify=tk.CENTER, width=7)
        e.configure(state='readonly')
        e.grid(row=1, column=7)
        self.size_Y_sv.set('250')

        label = ttk.Label(self.frame_cmd, text='Start pos X (µm)')
        label.grid(row=2, column=0)
        self.start_X_sv = tk.StringVar()
        e = ttk.Entry(self.frame_cmd, textvariable=self.start_X_sv, justify=tk.CENTER, width=7)
        e.grid(row=2, column=1)
        self.start_X_sv.set(str(self.xyStage.posMicron[0]))

        label = ttk.Label(self.frame_cmd, text='Start pos Y (µm)')
        label.grid(row=2, column=2)
        self.start_Y_sv = tk.StringVar()
        e = ttk.Entry(self.frame_cmd, textvariable=self.start_Y_sv, justify=tk.CENTER, width=7)
        e.grid(row=2, column=3)
        self.start_Y_sv.set(str(self.xyStage.posMicron[1]))

        b = tk.Button(self.frame_cmd, text="set current pos", command=self.set_current_pos)
        b.grid(row=2, column=4)
        b = tk.Button(self.frame_cmd, text="set around pos", command=self.set_around_pos)
        b.grid(row=2, column=5)


        label = ttk.Label(self.frame_cmd, text='Integration time (ms)')
        label.grid(row=3, column=0)
        self.integration_time_sv = tk.StringVar()
        e = ttk.Entry(self.frame_cmd, textvariable=self.integration_time_sv, justify=tk.CENTER, width=7)
        e.grid(row=3, column=1)
        self.integration_time_sv.set("100")

        b = tk.Button(self.frame_cmd, text="Save Image", command=self.save_scan_image)
        b.grid(row=3, column=2)


        b = tk.Button(self.frame_cmd, text="launch scan", command=self.launch_scan)
        b.grid(row=4, column=0)
        b = tk.Button(self.frame_cmd, text="STOP", command=self.do_stop_scan)
        b.grid(row=4, column=1)
        self.info_graph_sv = tk.StringVar()
        e = ttk.Entry(self.frame_cmd, textvariable=self.info_graph_sv, justify=tk.CENTER, width=45)
        e.configure(state='readonly')
        e.grid(row=4, column=2, columnspan=2)
        self.info_graph_sv.set('')

        self.frame_canvas = tk.Frame(self.frame)
        self.frame_canvas.pack(fill='both', expand=1)
        # self.frame_canvas.grid(row=0, column=5)

        self.figure = plt.Figure(figsize=(3,3), dpi=50)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_canvas)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        # self.figure.canvas.mpl_connect('scroll_event', self.graphScrollEvent)
        self.figure.canvas.mpl_connect('button_press_event', self.graph_button_press_event)
        # self.figure.canvas.mpl_connect('button_release_event', self.button_release_event)
        self.figure.canvas.mpl_connect('motion_notify_event', self.motion_notify_event)

        # Canvas to draw normalized image

        # Export canvas image to tiff or png.

        # Get default parameter
        self.get_GUI_params()


    def get_GUI_params(self):
        #TODO check positive and numeric
        self.nb_step_x, self.nb_step_y = int(self.nb_step_X_sv.get()), int(self.nb_step_Y_sv.get())
        self.step_size = float(self.scan_step_sv.get())
        self.size_X_sv.set(str(self.nb_step_x * self.step_size))
        self.size_Y_sv.set(str(self.nb_step_y * self.step_size))

        self.start_x, self.start_y = float(self.start_X_sv.get()), float(self.start_Y_sv.get())

        self.integration_time = float(self.integration_time_sv.get())
        self.change_integration_time()


    def change_integration_time(self):
        self.counter.change_integration_time(self.integration_time)

    def set_current_pos(self):
        # self.start_X_sv.set(str(self.xyStage.posMicron[0]))
        # self.start_Y_sv.set(str(self.xyStage.posMicron[1]))
        self.start_X_sv.set("0")
        self.start_Y_sv.set("0")

    def set_around_pos(self):
        """
        By default, upper left corner.
        :return:
        """
        x_start = - self.step_size * self.nb_step_x/2
        y_start = + self.step_size * self.nb_step_y/2
        self.start_X_sv.set(str(x_start))
        self.start_Y_sv.set(str(y_start))

    def do_stop_scan(self):
        self.stop_scan = True

    def save_scan_image(self):
        result = tkFileDialog.asksaveasfilename(title="File name for image")
        if result:
            fname = result
            self.figure.savefig(fname)

    def graph_button_press_event(self, event):
        # print('you pressed', event.button, event.xdata, event.ydata)
        x_pos = event.xdata * self.step_size
        y_pos = event.ydata * self.step_size
        if event.dblclick:
            result = tkMessageBox.askyesno("Python", "Would you like to move to x=%f, y=%f" % (x_pos, y_pos))
            if result:
                self.xyStage.move_absolute([x_pos, y_pos])

    def motion_notify_event(self, event):
        if event.xdata is not None and event.ydata is not None and  self.scan_data is not None :
            x_pos = int(event.xdata) * self.step_size
            y_pos = int(event.ydata) * self.step_size
            intensity = self.scan_data[int(event.xdata), int(event.ydata)]
            self.info_graph_sv.set("x: %d, y :%d, int : %d" % (x_pos, y_pos, intensity))


    def launch_scan(self):
        """
        THREAD !!
        """
        self.get_GUI_params()
        self.scan_thread = threading.Thread(name='XY_stage', target=self.scan)
        self.scan_thread.start()

    def scan(self):
        self.stop_scan = False

        #TODO Thread for the scan.

        #TODO set integration time.

        self.scan_data = np.zeros((self.nb_step_x, self.nb_step_y))

        # Move to start position
        # self.xyStage.move(mode="absolute", posMicron=[self.start_x, self.start_y])

        direction = 1
        for y in range(self.nb_step_y):
            print(y)
            if self.stop_scan:
                break
            for x in range(self.nb_step_x):
                if self.stop_scan:
                    break
                # move
                # Count is a blocking process
                self.scan_data[x, y] = self.counter.count()

                self.xyStage.move(mode="relative", posMicron=[self.step_size * direction, 0])
                self.xyStage.wait_for_device()

                self.refresh_canvas()
            direction = -direction
            self.xyStage.move(mode="relative", posMicron=[0, self.step_size])
            self.xyStage.wait_for_device()

        # return to initial position except if stop scan
        if not self.stop_scan:
            # self.xyStage.move(mode="absolute", posMicron=[self.start_x, self.start_y])
            # self.xyStage.wait_for_device()
            print("Scan Aborted")

        print("Scan Finished")

    def refresh_canvas(self):
        #TODO normalize cf  , norm= = colors.Normalize
        self.ax.clear()
        self.ax.imshow(self.scan_data, aspect="auto")
        self.canvas.draw()
        #TODO colorbar.
        # self.ax.color