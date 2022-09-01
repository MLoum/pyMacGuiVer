#!/usr/bin/env python
#-*- coding: utf-8 -*-

from hardware.Device import Device
from hardware.ThorlabsElliptec import ThorlabsElliptec

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from tkinter import simpledialog

class FilterSlide(Device):

    def __init__(self, mac_guiver, frameName="Arduino Counting", mm_name=""):
        super(FilterSlide, self).__init__(mac_guiver, frameName="Filter Slider", mm_name="")

        self.nb_of_optical_filter = 8

        self.slider_up = ThorlabsElliptec(mac_guiver=mac_guiver, type_="Slider", frameName="", mm_name="")
        self.slider_down = ThorlabsElliptec(mac_guiver=mac_guiver, type_="Slider", frameName="", mm_name="")
        self.initialized = self.load_device()

        self.create_GUI()

    def load_device(self, params=None):
        self.mac_guiver.write_to_splash_screen("Loading Filter Slider")

        is_slider_up_ini = self.slider_up.load_device()
        is_slider_up_down = self.slider_down.load_device()

        return is_slider_up_ini and is_slider_up_down


    def create_GUI(self):
        self.frame = tk.LabelFrame(self.master, text=self.frameName,
                                   borderwidth=1)

        # img = Image.open("./Ressource/OffSmall.png")
        # self.tkimageOff = ImageTk.PhotoImage(img)
        # img = Image.open("./Ressource/OnSmall.png")
        # self.tkimageOn = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/edit.png")
        self.tkimage_edit = ImageTk.PhotoImage(img)

        self.frame_up = tk.LabelFrame(self.frame, text="up",
                                   borderwidth=1)

        self.frame_down = tk.LabelFrame(self.frame, text="down",
                                   borderwidth=1)

        self.button_sv = [tk.StringVar()]*self.nb_of_optical_filter
        self.fill_button_name_from_ini()

        def create_button(frame, number):
            b = tk.Button(frame, textvariable=self.button_sv[number], command=lambda: self.move_slider_up(number))
            b.grid(row=0, column=number)

        for i in range(4):
            create_button(self.frame_up, i)

        def create_label(frame, number):
            lb = ttk.Label(frame, image=self.tkimage_edit)
            lb.config(width="20", height="20")
            lb.bind('<Button-1>', lambda e: self.edit_label(number))
            lb.grid(row=1, column=number)

        for i in range(4):
            create_label(self.frame_up, i)

    def move_slider_up(self, number):
        #TODO
        pass

    def edit_label(self, number):
        answer = simpledialog.askstring("Filter Name", "What is the label for this optical filter ?",
                                        parent=self.frame)
        if answer is not None:
            self.button_sv[number].set(answer)

            # change ini file
            def fill_button_name_from_ini(self):
                with open("./pyMacGuiver.ini") as ini_file:
                    for num, line in enumerate(ini_file):
                        if "[Filter Slider]" in line:
                            for i in range(self.nb_of_optical_filter):
                                self.button_sv[i].set(ini_file.next())

    def fill_button_name_from_ini(self):
        with open("./pyMacGuiver.ini") as ini_file:
            for num, line in enumerate(ini_file):
                if "[Filter Slider]" in line:
                    for i in range(self.nb_of_optical_filter):
                        self.button_sv[i].set(ini_file.next())


    def change_com_port(self, port):
        pass

    def write(self):
        pass

    def read_until(self):
        pass



