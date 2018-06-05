#!/usr/bin/env python
#-*- coding: utf-8 -*-



from XYStage import XYStage

class madLibCity_XY(XYStage):
    def __init__(self, macGuiver):
        super(madLibCity_XY, self).__init__(macGuiver, frameName="MCL_XY", mm_name="MadLabXY")

    def loadDevice(self):
        try:
            self.mmc.loadDevice(self.mm_name, "MCL_MicroDrive", "MicroDrive XY Stage")
            self.mmc.initializeDevice(self.mm_name)
            return True
        except:
            print("MCL_XY ini pb")
            return False

    def moveAbsolute(self, posMicron):
        self.mmc.setXYPosition(self.mm_name, self.posMicron[0], self.posMicron[1])

    def moveRelative(self, posMicron):
        self.mmc.setRelativeXYPosition(self.mm_name, posMicron[0], posMicron[1])

    def waitForDevice(self):
        self.mmc.waitForDevice(self.mm_name)

    def stop(self):
        self.mmc.stop(self.mm_name)
