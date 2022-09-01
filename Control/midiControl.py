# -*- coding: utf-8 -*-
"""
Created on Thu Jan 03 14:21:34 2013

@author: biomis_m
"""

import pygame.midi
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import threading
import time



class MidiListener():
    def __init__(self, macGuiver):
        self.macGuiver = macGuiver
        self.master = macGuiver.root
        self.isMidiListening = False
        self.list_control_to_monitor = []
        self.midiInspectDelay = 0.05  # ms

        # WARNING This code does not take in account midi channel. Consquently, only 127 control can be used simultaneouslly.

        # FIXME System Dependent !!!!!!

        pygame.midi.init()


        #FIXME
        self.numInputMidi = 1

        r = pygame.midi.get_device_info(self.numInputMidi)
        (interf, name, input, output, opened) = r

        if input:
            self.midiInput = pygame.midi.Input(self.numInputMidi, 100)  # buffer_size 1
        else:
            print ("Input Midi non valide. Mettre les mains dans le code...")

        self._print_device_info()

        # self.midiStatusRange = range(0, 192)  # Status for Control/Mode change
        # self.midiLoop()
        #print 'FIN MIDI'

    def add_a_Control(self, tkVariable, min_, max_, midiCC, midiCC_inc, callBack=None):
        self.list_control_to_monitor.append(MidiTkControl(tkVariable, min_, max_, midiCC, midiCC_inc, callBack))

    def midiLoop(self):
        while self.isMidiListening == True:
            self.updateMidiStatus()
            time.sleep(self.midiInspectDelay)
        # if self.midiLoopStop == False:
        #     self.after(self.midiInspectDelay, self.updateMidiStatus)
        #     self.after(self.midiInspectDelay, self.midiLoop)

    def startListening(self):
        self.midiThread = threading.Thread(target=self.midiLoop)
        self.isMidiListening = True
        self.purgeMidi()
        self.midiThread.start()

    def purgeMidi(self):
        self.midiInput.read(100)

    def stopListening(self):
        self.isMidiListening = False

    def updateMidiStatus(self):
        try:
            midi = self.midiInput.read(100)
        # except pygame.midi.MidiException:
        #     print("Overflow")
        except Exception as exception:
            #There is sometimes some bufferOverflow when some knob are turned too fast. We catch and ignore them
            print(type(exception).__name__ )
            return

        # [[status,data1,data2,data3],timestamp],...]
        #print (midi)

        #Test on n'execute que le dernier ?
        if len(midi) != 0:
            lastEvent = midi[-1]
            CCname = lastEvent[0][1]
            #print (CCname)
            for control in self.list_control_to_monitor:
                if control.modifyMidiCC == CCname:
                    control.midiValue = lastEvent[0][2]
                    self.setGuiforIncomingMidi(control.name)
                    control.act()

    def registerCallback(self, type="relative", name="", tkVariable=None, min_=0, max_=0, inc=1, midiChannel=1, midiCC=0, callBack=None):
        self.list_control_to_monitor.append(MidiTkControl(type, name, tkVariable, min_, max_, inc, midiChannel, midiCC, callBack))

    def _print_device_info(self):
        for i in range(pygame.midi.get_count()):
            r = pygame.midi.get_device_info(i)
            (interf, name, input, output, opened) = r

            in_out = ""
            if input:
                in_out = "(input)"
            if output:
                in_out = "(output)"

            text = ("%2i: interface :%s:, name :%s:, opened :%s:  %s" % (i, interf, name, opened, in_out))
            print (text)
            # self.txt.insert(tk.END, text)

    def createGUI(self):
        self.frame = tk.LabelFrame(self.master, text="MidiCtrl",
                                         borderwidth=1)

        self.labelMidiInfo_sv = tk.StringVar()
        self.labelMidiInfo = ttk.Label(self.frame, textvariable=self.labelMidiInfo_sv)
        self.labelMidiInfo.grid(column=0)

        img = Image.open("./Ressource/led-green-off.png")
        self.tkimageLEDGreenOff = ImageTk.PhotoImage(img)
        img = Image.open("./Ressource/led-green-on.png")
        self.tkimageLEDGreenOn = ImageTk.PhotoImage(img)

        self.label_LED_IncomingMidi = ttk.Label(self.frame, image=self.tkimageLEDGreenOff)
        self.label_LED_IncomingMidi.grid(column=1)


        self.buttonToggleListen = tk.Button(self.frame, text="Start", command=self.toggleListen)
        self.buttonToggleListen.grid(column=3)

    def toggleListen(self):
        if self.isMidiListening:
            self.buttonToggleListen.configure(text="Start")
            self.stopListening()
        else:
            self.buttonToggleListen.configure(text="Stop")
            self.startListening()



    def displayMidi(self, midiCmdName):
        self.label_LED_IncomingMidi.configure(image=self.tkimageLEDGreenOn)
        self.labelMidiInfo_sv.set(midiCmdName)
        time.sleep(0.2)
        self.label_LED_IncomingMidi.configure(image=self.tkimageLEDGreenOff)

    def setGuiforIncomingMidi(self, midiCmdName):
        threading.Thread(target=self.displayMidi, args=(midiCmdName,)).start()


class MidiTkControl():
    """
    Fait un mapping entre une valeur et une donnée midi. tkVariable permet de relier au GUI
    """
    def __init__(self, type="relative", name="", tkVariable=None, min_=0, max_=0, inc=1, midiChannel=1, midiCC=0, callBack=None):
        self.modifyMidiCC = midiCC
        self.inc = inc
        self.name = name
        self.midiChannel = midiChannel

        self.type = type

        self.currentValue = 0
        self.currentInc = 0.1

        self.tkVariable = tkVariable
        if tkVariable is not None:
            self.value = float(tkVariable.get())
        else:
            self.value = 0
        self.midiValue= None
        # self.value = None
        self.min = min_
        self.max = max_

        if self.type == "case":
            #FIXME les cases dans quelle arguments de la fonction ?
            self.nbOfCase = len(self.inc)
        self.callBack = callBack

    def act(self):
        if self.type=="relative":
            if self.midiValue == 1:
                if self.tkVariable is not None:
                    self.tkVariable.set(str(self.getValue(incIsPositive=True)))
                if self.callBack is not None:
                    self.callBack[0]()

            elif self.midiValue == 127:
                if self.tkVariable is not None:
                    self.tkVariable.set(str(self.getValue(incIsPositive=False)))
                if self.callBack is not None:
                    self.callBack[1]()

        elif self.type=="absolute":
            #actualize gui and call the callback
            self.tkVariable.set(str(self.getValue()))
            self.callBack[0]()


    def getValue(self, incIsPositive=True):
        # MidiValue est entre 0 et 127
        if self.type == "relative":
            if incIsPositive:
                self.value +=  self.inc
            else:
                self.value -= self.inc

            return self.value

        elif self.type == "absolute":
            return self.min + float(self.midiValue) / 127.0 * self.max
        elif self.type == "case":
            caseNumber = int(float(self.midiValue) / 127.0 * self.nbOfCase)

    def actualiseValue(self, midiValue):
        print ("midiValue : ", midiValue)
        print ("self.currentInc : ", self.currentInc)
        value = self.getValue(midiValue)
        print ("value : ", value)
        self.tkVariable.set(str(value))

    def actualiseInc(self, incValue):
        self.currentInc = incValue

    def _print(self):
        return "tkVariable =" + str(self.tkVariable) + "\n" + "MidiCC : " + str(self.modifyMidiCC) + "\n"


if __name__ == "__main__":
    midiListener = MidiListener(None)
    midiListener.startListening()
    while True:
        pass

