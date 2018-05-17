#!/usr/bin/env python
#-*- coding: utf-8 -*-



from XYStage import XYStage

class Standa_XY(XYStage):
    def __init__(self, macGuiver):
        super(Standa_XY, self).__init__(macGuiver, frameName="Standa_XY", mm_name="StandaXY")

    def loadDevice(self):
        """
        * Device name has form "xi-com:port" or "xi-net://host/serial" or "xi-emu://file".
		* In case of USB-COM port the "port" is the OS device name.
		* For example "xi-com:\\\.\COM3" in Windows or "xi-com:/dev/tty.s123" in Linux/Mac.

		Lokk in the gestionnaire de périphérique
        :return:
        """
        self.mmc.loadDevice(self.mm_name, "Standa8SMC4", "Standa8SMC4XY")

        self.mmc.setProperty(self.mm_name, "Port X", "xi-com:%5C%5C.%5CCOM6")
        self.mmc.setProperty(self.mm_name, "Port Y", "xi-com:%5C%5C.%5CCOM7")
        self.mmc.setProperty(self.mm_name, "UnitMultiplierX", "0.054")
        self.mmc.setProperty(self.mm_name, "UnitMultiplierY", "0.054")
        self.mmc.initializeDevice(self.mm_name)

    def moveAbsolute(self, posMicron):
        self.mmc.setXYPosition(self.mm_name, self.posMicron[0], self.posMicron[1])

    def moveRelative(self, posMicron):
        self.mmc.setRelativeXYPosition(self.mm_name, posMicron[0], posMicron[1])

    def waitForDevice(self):
        self.mmc.waitForDevice(self.mm_name)

    def stop(self):
        self.mmc.stop(self.mm_name)

