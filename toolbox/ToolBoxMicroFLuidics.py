#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt

class ToolBoxMicrofluidics():

    def __init__(self, master):
        self.master = master

        self.pad = 5
        self.font = "helvetica 12"

        self.top_level = tk.Toplevel(self.master)
        # self.top_level_navigation.bind("<Key>", self.mainGUI.pressed_key_shortcut)
        self.top_level.title("Microfluidics Tool box")
        self.frame_channel = tk.LabelFrame(self.top_level, text="Channel", borderwidth=1)
        self.frame_channel.pack(side="top", fill="both", expand=True)

        img = Image.open("./Ressource/microChannel.png")
        resized = img.resize((50, 34), Image.ANTIALIAS)
        self.tkimage_channel = ImageTk.PhotoImage(resized)

        ttk.Label(self.frame_channel, image=self.tkimage_channel, font=self.font).grid(row=0, column=0, padx=self.pad)

        ttk.Label(self.frame_channel, text='w (µm) :', font=self.font).grid(row=0, column=1, padx=self.pad)
        self.w_sv = tk.StringVar(value=150)
        e = ttk.Entry(self.frame_channel, textvariable=self.w_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=2, padx=self.pad)

        ttk.Label(self.frame_channel, text='h (µm) :', font=self.font).grid(row=0, column=3, padx=self.pad)
        self.h_sv = tk.StringVar(value=50)
        e = ttk.Entry(self.frame_channel, textvariable=self.h_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=4, padx=self.pad)

        # Solvent
        self.frame_solvent = tk.LabelFrame(self.top_level, text="Solvent", borderwidth=1)
        self.frame_solvent.pack(side="top", fill="both", expand=True)

        ttk.Label(self.frame_solvent, text='T (°C) :', font=self.font).grid(row=0, column=0, padx=self.pad)
        self.T_sv = tk.StringVar(value=20)
        e = ttk.Entry(self.frame_solvent, textvariable=self.T_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=1, padx=self.pad)


        ttk.Label(self.frame_solvent, text='viscosity (Pa.s) :', font=self.font).grid(row=0, column=2, padx=self.pad)
        self.viscosity_sv = tk.StringVar(value=0.001)
        e = ttk.Entry(self.frame_solvent, textvariable=self.viscosity_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=3, padx=self.pad)

        ttk.Label(self.frame_solvent, text='Volumic mass (kg/m^3) :', font=self.font).grid(row=0, column=4, padx=self.pad)
        self.volumic_mass_sv = tk.StringVar(value=1000)
        e = ttk.Entry(self.frame_solvent, textvariable=self.volumic_mass_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=5, padx=self.pad)

        ttk.Label(self.frame_solvent, text='Presets :', font=self.font).grid(row=0, column=6, padx=self.pad)
        self.cb_solvent_sv = tk.StringVar()
        self.cb = ttk.Combobox(self.frame_solvent, width=10, justify=tk.CENTER, textvariable=self.cb_solvent_sv, values='', font=self.font)
        self.cb['values'] = ('', 'Water', 'DMSO', 'acetonitrile', "DMF")
        self.cb.set('')
        self.cb.bind('<<ComboboxSelected>>', self.change_solvent)
        self.cb.grid(row=0, column=7, padx=self.pad)

        # Particle
        self.frame_particle = tk.LabelFrame(self.top_level, text="Particle", borderwidth=1)
        self.frame_particle.pack(side="top", fill="both", expand=True)

        ttk.Label(self.frame_particle, text='Radius (nm) :', font=self.font).grid(row=0, column=0, padx=self.pad)
        self.radius_particle_sv = tk.StringVar(value=1)
        e = ttk.Entry(self.frame_particle, textvariable=self.radius_particle_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=1, padx=self.pad)

        ttk.Label(self.frame_particle, text='D (m².s-1) :', font=self.font).grid(row=0, column=2, padx=self.pad)
        self.D_sv = tk.StringVar(value=1)
        e = ttk.Entry(self.frame_particle, textvariable=self.D_sv, justify=tk.CENTER, width=7, font=self.font)
        e.grid(row=0, column=3, padx=self.pad)
        e.configure(state='readonly')

        #Optics
        self.frame_optics = tk.LabelFrame(self.top_level, text="Optics", borderwidth=1)
        self.frame_optics.pack(side="top", fill="both", expand=True)

        ttk.Label(self.frame_optics, text='wavelength (nm) :', font=self.font).grid(row=0, column=0, padx=self.pad)
        self.wl_laser_sv = tk.StringVar(value=405)
        e = ttk.Entry(self.frame_optics, textvariable=self.wl_laser_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=1, padx=self.pad)

        ttk.Label(self.frame_optics, text='Numerical apperture (nm) :', font=self.font).grid(row=0, column=2, padx=self.pad)
        self.NA_objective_sv = tk.StringVar(value=1.2)
        e = ttk.Entry(self.frame_optics, textvariable=self.NA_objective_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=3, padx=self.pad)

        ttk.Label(self.frame_optics, text='Focal volume carac. size (nm) :', font=self.font).grid(row=0, column=4, padx=self.pad)
        self.focal_vol_size_sv = tk.StringVar(value=0)
        e = ttk.Entry(self.frame_optics, textvariable=self.focal_vol_size_sv, justify=tk.CENTER, width=7, font=self.font)
        e.configure(state='readonly')
        e.grid(row=0, column=5, padx=self.pad)


        # Flow
        self.frame_flow = tk.LabelFrame(self.top_level, text="Flow", borderwidth=1)
        self.frame_flow.pack(side="top", fill="both", expand=True)

        ttk.Label(self.frame_flow, text='Flow (µL/min) :', font=self.font).grid(row=0, column=0, padx=self.pad)
        self.flow_sv = tk.StringVar(value=1)
        e = ttk.Entry(self.frame_flow, textvariable=self.flow_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=1, padx=self.pad)

        ttk.Label(self.frame_flow, text='Reynolds (section carré):', font=self.font).grid(row=0, column=2, padx=self.pad)
        self.reynolds_sv = tk.StringVar(value=1)
        e = ttk.Entry(self.frame_flow, textvariable=self.reynolds_sv, justify=tk.CENTER, width=7, font=self.font)
        e.configure(state='readonly')
        e.grid(row=0, column=3, padx=self.pad)

        ttk.Label(self.frame_flow, text='Mean speed (µm/s):', font=self.font).grid(row=0, column=4, padx=self.pad)
        self.mean_speed_sv = tk.StringVar(value=1)
        e = ttk.Entry(self.frame_flow, textvariable=self.mean_speed_sv, justify=tk.CENTER, width=7, font=self.font)
        e.configure(state='readonly')
        e.grid(row=0, column=5, padx=self.pad)

        ttk.Label(self.frame_flow, text='Max speed (µm/s) :', font=self.font).grid(row=0, column=6, padx=self.pad)
        self.max_speed_sv = tk.StringVar(value=1)
        e = ttk.Entry(self.frame_flow, textvariable=self.max_speed_sv, justify=tk.CENTER, width=7, font=self.font)
        e.configure(state='readonly')
        e.grid(row=0, column=7, padx=self.pad)


        tk.Button(self.frame_flow, text="Flow map", command=self.calculate_flow_profile).grid(row=0, column=8, padx=self.pad)


        self.frame_diffusion = tk.LabelFrame(self.top_level, text="Diffusion", borderwidth=1)
        self.frame_diffusion.pack(side="top", fill="both", expand=True)

        ttk.Label(self.frame_diffusion, text='Diffusion time (s) :', font=self.font).grid(row=0, column=0, padx=self.pad)
        self.diff_time_sv = tk.StringVar(value=1)
        e = ttk.Entry(self.frame_diffusion, textvariable=self.diff_time_sv, justify=tk.CENTER, width=7, font=self.font)
        e.configure(state='readonly')
        e.grid(row=0, column=1, padx=self.pad)

        ttk.Label(self.frame_diffusion, text='Diffusion channel length (mm) :', font=self.font).grid(row=0, column=2, padx=self.pad)
        self.diff_length_sv = tk.StringVar(value=1)
        e = ttk.Entry(self.frame_diffusion, textvariable=self.diff_length_sv, justify=tk.CENTER, width=7, font=self.font)
        e.configure(state='readonly')
        e.grid(row=0, column=3, padx=self.pad)

        # Filling Time
        self.frame_filling = tk.LabelFrame(self.top_level, text="Tube Filling time", borderwidth=1)
        self.frame_filling.pack(side="top", fill="both", expand=True)


        ttk.Label(self.frame_filling, text='Tube ID (mm)', font=self.font).grid(row=0, column=0, padx=self.pad)
        self.tube_id_sv = tk.StringVar(value=0.51)
        e = ttk.Entry(self.frame_filling, textvariable=self.tube_id_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=1, padx=self.pad)

        ttk.Label(self.frame_filling, text='Tube length (cm)', font=self.font).grid(row=0, column=2, padx=self.pad)
        self.tube_length_sv = tk.StringVar(value=1)
        e = ttk.Entry(self.frame_filling, textvariable=self.tube_length_sv, justify=tk.CENTER, width=7, font=self.font)
        e.bind('<Return>', lambda e: self.recalculate())
        e.grid(row=0, column=3, padx=self.pad)

        ttk.Label(self.frame_filling, text='Filling time (s)', font=self.font).grid(row=0, column=4, padx=self.pad)
        self.filling_time_sv = tk.StringVar(value=0)
        e = ttk.Entry(self.frame_filling, textvariable=self.filling_time_sv, justify=tk.CENTER, width=7, font=self.font)
        e.configure(state='readonly')
        e.grid(row=0, column=5, padx=self.pad)

        self.recalculate()



    def change_solvent(self, e):
        if self.cb_solvent_sv.get() == "Water":
            self.viscosity_sv.set("0.001")
            self.volumic_mass_sv.set("1000")
        elif self.cb_solvent_sv.get() == "acetonitrile":
            self.viscosity_sv.set("0.000343")
            self.volumic_mass_sv.set("789")
        elif self.cb_solvent_sv.get() == "DMSO":
            self.viscosity_sv.set("0.002")
            self.volumic_mass_sv.set("1100")
        elif self.cb_solvent_sv.get() == "DMF":
            self.viscosity_sv.set("0.00092")
            self.volumic_mass_sv.set("969")
        self.recalculate()

    def calculate_flow_speed(self, y, z, w, h, eta, Q):
        """
        Calculate the flow speed from a rectangular Poiseuille flow
        :param y: vertical position in the channel 0 <= y <= h in µm
        :param z: lateral position in the channel 0 <= z <= w in µm
        :param w: width of the channel (µm)
        :param h: height of the channel (µm)
        :param eta: viscosity in Pa.s (SI)
        :param Q: flow in µL.min-1
        :return:
        """

        # From wikipédia formula,We compute the term G (i.e. constant pressure gradient), from the experimental value Q of the flow rate



        # From theorical microfluifics (Brus)
        sum_ = 0
        max_order_sum = 10

        for n in range(max_order_sum):
            if n%2 == 0:
                continue
            sum_ += 1/n**5 * 192/np.pi**5 * h/w * np.tanh(n * np.pi * w/(2*h))

        Q_SI = Q * 1E-9 / 60

        # G is the pressure gradient G = Delta P / L
        G = (12 * Q_SI * eta / (h**3 * w))  / (1 - sum_)

        # G is in Pa.m-1, but we are working with µm so we have to convert it
        G *= 1E-6

        sum_ = np.zeros_like(y, dtype=np.float64)
        for n in range(max_order_sum):
            if n%2 == 0:
                continue
            sum_ += 1/n**3 * (1 - np.cosh(n * np.pi * y / h)/np.cosh(n * np.pi * w / (2*h))) * np.sin(n * np.pi * z / h)

        v = 4 * h**2 * G / (np.pi**3 * eta) * sum_
        v = sum_
        return v



    def calculate_flow_profile(self):
        Ny = Nz = 51
        w = float(self.w_sv.get())
        h = float(self.h_sv.get())
        eta = float(self.viscosity_sv.get())
        Q = float(self.flow_sv.get())
        y = np.linspace(-w/2, w/2, Ny)
        z = np.linspace(0, h, Nz)
        YY, ZZ = np.meshgrid(y, z)
        max_order_sum = 10

        velocity_map = self.calculate_flow_speed(YY, ZZ, w, h, eta, Q)

        # cmap = plt.cm.jet, , levels=40
        plt.contourf(y, z, velocity_map)
        plt.xlabel("y / micron")
        plt.ylabel("z / micron")
        plt.colorbar()
        plt.savefig("velocity_map_w150_h50.png", dpi=400)
        plt.show()


    def recalculate(self):
        try:
            T = float(self.T_sv.get())
            w = float(self.w_sv.get())
            h = float(self.h_sv.get())
            eta = float(self.viscosity_sv.get())
            rho = float(self.volumic_mass_sv.get())
            r = float(self.radius_particle_sv.get())
            flow_mul_min = float(self.flow_sv.get())
            wl = float(self.wl_laser_sv.get())
            NA = float(self.NA_objective_sv.get())
            tube_id = float(self.tube_id_sv.get())
            tube_length = float(self.tube_length_sv.get())
        except ValueError:
            return False

        D = 1.38E-23 * (T+273) / (6*3.14*eta*r*1E-9)
        D_str_scientific = "{:.2e}".format(D)
        self.D_sv.set(D_str_scientific)

        # FIXME c'est pour un canal carré et non rectangulaire
        # Re = rho U w / eta where U is the mean speed U = Q / w**2
        flow_m3_s = flow_mul_min * 1E-9/60
        Re = rho * flow_m3_s/(eta * w*1E-6)
        self.reynolds_sv.set("%.2f" % Re)

        mean_speed = flow_m3_s / ((w*1-6)**2) * 1E6
        self.mean_speed_sv.set("%.2f" % mean_speed)



        max_speed = self.calculate_flow_speed(0, w/2, w, h, eta, flow_mul_min)


        tau = (w*1E-6)**2 / D
        self.diff_time_sv.set("%.2f" % tau)

        d_diff = flow_m3_s / D * 1000
        self.diff_length_sv.set("%.2f" % d_diff)

        # Optics
        focal_volume_carac_size = 1.22 * wl / NA
        self.focal_vol_size_sv.set("%.2f" % focal_volume_carac_size)

        # Filling time
        volume_m3 = np.pi*(tube_id*1E-3/2)**2*tube_length*1E-2
        filling_time = volume_m3 / flow_m3_s
        self.filling_time_sv.set("%.2f" % filling_time)
