import Tkinter as tk
from hardware import MCL_XY, Standa_XY, ArduinoCounting, Spectro, dummy_XYStage, motorArduino
from Control import midiControl
import MMCorePy

class macGuiver():
    def __init__(self):
        self.root = tk.Tk()
        self.mmc = None
        self.listHardware = []
        self.launch_MicroManager()
        self.start_splash_screen()
        self.createHardware()

        # self.createMidiControl()

        self.createGUI()
        self.close_splash_screen()
        #self.midiListener.startListening()
        #self.createMenuCommands()
        #self.createShortCut()
        self.root.protocol("WM_DELETE_WINDOW", self.onQuit)

    def run(self):
        self.root.title("pyMacGUIver")
        self.root.deiconify()
        self.root.mainloop()

    def launch_MicroManager(self):
        try:
            self.mmc = MMCorePy.CMMCore()
            print(self.mmc.getVersionInfo())
            print(self.mmc.getAPIVersionInfo())
        except:
            print("Can't launch micro-manager core.\n Exiting.")
            return

    def start_splash_screen(self):
        pass

    def close_splash_screen(self):
        pass

    def createHardware(self):
        # self.dummy_XYStage = dummy_XYStage.dummy_XY(self)

        self.madLibCity_XY  = MCL_XY.madLibCity_XY(self)
        if self.madLibCity_XY.initialized:
            self.listHardware.append(self.madLibCity_XY)


        # self.standa_XY  = Standa_XY.Standa_XY(self)
        # self.listHardware.append(self.standa_XY)

        # self.spectro = Spectro.Spectro(self)
        # self.listHardware.append(self.spectro)
        #

        self.countingArduino = ArduinoCounting.ArduinoCouting(self)
        if self.countingArduino.initialized:
            self.listHardware.append(self.countingArduino)
            # TODO print info to splash screen

        # self.rotation_arduino_dls = motorArduino.Motor_arduino(self)
        # if self.rotation_arduino_dls.initialized:
        #     self.listHardware.append(self.rotation_arduino_dls)


    def createMidiControl(self):
        self.midiListener = midiControl.MidiListener(self)
        self.registerMidiCallback()
        self.midiListener.createGUI()

    def createGUI(self):
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

    def registerMidiCallback(self):
        self.midiListener.registerCallback(type="relative", name="MCL_X", midiCC=32, callBack=[self.dummy_XYStage.moveLeft, self.dummy_XYStage.moveRight])
        self.midiListener.registerCallback(type="relative", name="MCL_Y", midiCC=33,
                                           callBack=[self.dummy_XYStage.moveDown, self.dummy_XYStage.moveUp])

        self.midiListener.registerCallback(type="relative", name="MCL_StepX_small", midiCC=40, inc=1, tkVariable=self.dummy_XYStage.stepX_sv, callBack=[self.dummy_XYStage.get_GUI_params, self.dummy_XYStage.get_GUI_params])
        self.midiListener.registerCallback(type="relative", name="MCL_StepY_small", midiCC=41, inc=1,
                                           tkVariable=self.dummy_XYStage.stepY_sv, callBack=[self.dummy_XYStage.get_GUI_params, self.dummy_XYStage.get_GUI_params])

        self.midiListener.registerCallback(type="relative", name="MCL_StepX_big", midiCC=48, inc=10, tkVariable=self.dummy_XYStage.stepX_sv, callBack=[self.dummy_XYStage.get_GUI_params, self.dummy_XYStage.get_GUI_params])
        self.midiListener.registerCallback(type="relative", name="MCL_StepY_big", midiCC=49, inc=10,
                                           tkVariable=self.dummy_XYStage.stepY_sv, callBack=[self.dummy_XYStage.get_GUI_params, self.dummy_XYStage.get_GUI_params])



    def onQuit(self):
        # paramFile = open('param.ini', 'w')
        # paramFile.write(self.saveDir)
        self.root.destroy()
        self.root.quit()


if __name__ == "__main__":
    macGuiver = macGuiver()
    macGuiver.run()