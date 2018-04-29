# -*- coding: utf-8 -*-
"""
Created on Sat Mar 10 12:40:08 2012

@author: Matth
"""

import pygame.midi
import sys
import Tkinter as tk


def print_device_info():
    pygame.midi.init()
    _print_device_info()






def _print_device_info():
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print ("%2i: interface :%s:, name :%s:, opened :%s:  %s" %
               (i, interf, name, opened, in_out))

    """
    going = True
    while going:
        events = event_get()
        for e in events:
            if e.type in [QUIT]:
                going = False
            if e.type in [KEYDOWN]:
                going = False
            if e.type in [pygame.midi.MIDIIN]:
                print (e)

        if i.poll():
            midi_events = i.read(10)
            # convert them into pygame events.
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

            for m_e in midi_evs:
                event_post( m_e )

    del i
    pygame.midi.quit()

    """

print_device_info()


    pygame.midi.quit()
    print 'OK'


class prog_tk_UI(tk.Tk):
    def __init__(self, master=None):
        self.master = master
        tk.Tk.__init__(self, master)

        self.playDelay = 500
        self.stopPlay = False

        self.title('Test Midi')
        self.protocol("WM_DELETE_WINDOW",
                      self.onQuit)  # Exit when x pressed, notice that its the name of the function 'self.handler' and not a method call self.handler()

        pygame.midi.init()

        self.printDeviceInfo()

        self.midiInput = pygame.midi.Input(1)

        # Check if opened = 1
        #self.printDeviceInfo()

        b = tk.Button(self, text="Start Loop", width=6, command=self.startLoop)
        b.pack(side=tk.LEFT, padx=2, pady=2)

        b = tk.Button(self, text="Stop Loop", width=6, command=self.stopLoop)
        b.pack(side=tk.LEFT, padx=2, pady=2)

    def printDeviceInfo(self):
        for i in range(pygame.midi.get_count()):
            r = pygame.midi.get_device_info(i)
            (interf, name, input, output, opened) = r

            in_out = ""
            if input:
                in_out = "(input)"
            if output:
                in_out = "(output)"

            print ("%2i: interface :%s:, name :%s:, opened :%s:  %s" %
                   (i, interf, name, opened, in_out))

        print ("default input : % d" % pygame.midi.get_default_input_id())

    def startLoop(self):
        print("Start Loop")
        self.stopPlay = False
        self.midiLoop()

    def stopLoop(self):
        print("Stop Loop")
        self.stopPlay = True

    def midiLoop(self):
        if self.stopPlay == False:
            print("loop")
            self.after(self.playDelay, self.update)
            self.after(self.playDelay, self.midiLoop)

    def update(self):
        midi = self.midiInput.read(40)
        for event in midi:
            print event
            if event[0][0] != 248:
                print event

    def onQuit(self):
        self.destroy()
        self.quit()


def main():
    app = prog_tk_UI(master=None)
    app.title('my application')
    app.mainloop()


if __name__ == "__main__":
    main()