import pygame
import Tkinter as tk
from pygame.locals import *
import ttk
from PIL import Image, ImageTk

import threading
import time

class JoystickListener():
    def __init__(self, mac_guiver):
        self.mac_guiver = mac_guiver
        self.master = mac_guiver.root
        self.is_joy_listening = False
        self.list_control_to_monitor = []
        self.joy_inspect_delay = 0.05  # ms

        self.joystick = None
        pygame.init()
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        if self.joysticks is not None:
            self.joystick = self.joysticks[0]
            self.joystick.init()

        self.print_info_joystick()


    def joy_loop(self):
        while self.is_joy_listening == True:
            self.update_joy_status()
            time.sleep(self.joy_inspect_delay)

    def start_listening(self):
        self.joy_thread = threading.Thread(target=self.joy_loop)
        self.is_joy_listening = True
        # self.purgeMidi()
        self.joy_thread.start()

    def stop_listening(self):
        self.is_joy_listening = False

    def update_joy_status(self):
        for e in pygame.event.get():  # iterate over event stack
            print 'event : ' + str(e.type)
            if e.type == JOYAXISMOTION:  # 7
                for ctrl in self.list_control_to_monitor:
                    if ctrl.type == "axis":
                        x, y = self.joystick.get_axis(0), self.joystick.get_axis(1)
                        # print(x,y)
                        # up
                        if ctrl.num == 1 and y<-0.9:
                            self.set_gui_for_incoming_joy_cmd("axis_" + str(ctrl.num) + " : " + ctrl.name)
                            ctrl.callback()
                        # down
                        elif ctrl.num == -1 and y>0.9:
                            self.set_gui_for_incoming_joy_cmd("axis_" + str(ctrl.num) + " : " + ctrl.name)
                            ctrl.callback()
                        #left
                        if ctrl.num == 2 and x<-0.9:
                            self.set_gui_for_incoming_joy_cmd("axis_" + str(ctrl.num) + " : " + ctrl.name)
                            ctrl.callback()
                        #right
                        elif ctrl.num == -2 and x>0.9:
                            self.set_gui_for_incoming_joy_cmd("axis_" + str(ctrl.num) + " : " + ctrl.name)
                            ctrl.callback()





            elif e.type == JOYBALLMOTION:  # 8
                print 'ball motion'
            elif e.type == JOYHATMOTION:  # 9
                # x,y = self.joystick.get_hat(0)
                print 'hat motion'
            elif e.type == JOYBUTTONDOWN:  # 10

                for ctrl in self.list_control_to_monitor:
                    if ctrl.type == "button":
                        if self.joystick.get_button(ctrl.num):
                            self.set_gui_for_incoming_joy_cmd("button_" + str(ctrl.num) + " : " + ctrl.name)
                            ctrl.callback()

            elif e.type == JOYBUTTONUP:  # 11
                print 'button up'

    def print_info_joystick(self):
        if self.joystick is not None:
            self.id = self.joystick.get_id()
            self.name = self.joystick.get_name()
            self.numaxes = self.joystick.get_numaxes()
            self.numhats = self.joystick.get_numhats()
            self.numbuttons = self.joystick.get_numbuttons()

            print("id : ", self.joystick.get_id())
            print("name : ", self.joystick.get_name())
            print("numaxes : ", self.joystick.get_numaxes())
            print("numhats : ", self.joystick.get_numhats())
            print("numbuttons : ", self.joystick.get_numbuttons())

    def registerCallback(self, type="axis", num=0, name="", callBack=None):
        self.list_control_to_monitor.append(JoyCtrl(type, num, name, callBack))

    def createGUI(self):
        self.frame = tk.LabelFrame(self.master, text="Joy-Ctrl",
                                         borderwidth=1)

        self.label_joy_info_sv = tk.StringVar()
        self.label_midi_info = ttk.Label(self.frame, textvariable=self.label_joy_info_sv)
        self.label_midi_info.grid(row=0, column=0)

        img = Image.open("./Ressource/led-green-off.png")
        self.tkimage_led_green_off = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/led-green-on.png")
        self.tkimage_led_green_on = ImageTk.PhotoImage(img)

        self.label_LED_Incoming_joy = ttk.Label(self.frame, image=self.tkimage_led_green_off)
        self.label_LED_Incoming_joy.grid(row=0, column=1)

        self.button_toggle_listen = tk.Button(self.frame, text="Stop", command=self.toggleListen)
        self.button_toggle_listen.grid(row=0, column=2)

    def toggleListen(self):
        if self.is_joy_listening:
            self.button_toggle_listen.configure(text="Start")
            self.stop_listening()
        else:
            self.button_toggle_listen.configure(text="Stop")
            self.start_listening()

    def display_joy_ctrl(self, joy_cmd_name):
        self.label_LED_Incoming_joy.configure(image=self.tkimage_led_green_on)
        self.label_joy_info_sv.set(joy_cmd_name)
        time.sleep(0.2)
        self.label_LED_Incoming_joy.configure(image=self.tkimage_led_green_off)

    def set_gui_for_incoming_joy_cmd(self, joy_cmd_name):
        threading.Thread(target=self.display_joy_ctrl, args=(joy_cmd_name,)).start()


class JoyCtrl():
    def __init__(self, type_="axis", num=0, name="", callback=None):
        self.type = type_
        self.num = num
        self.name = name
        self.callback = callback


if __name__ == "__main__":
    joy_listener = JoystickListener(None)
    joy_listener.start_listening()
    while 1:
        pass
