#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time

from XYStage import XYStage

class dummy_XY(XYStage):
    def __init__(self, macGuiver):
        self.isBusy_ = False
        super(dummy_XY, self).__init__(macGuiver, frameName="Dummy_XY", mm_name="")

    def loadDevice(self):
        return True

    def moveAbsolute(self, posMicron):
        pass

    def moveRelative(self, posMicron):
        pass

    def waitForDevice(self):
        self.isBusy_ = True
        time.sleep(1)
        self.isBusy_ = False

    def stop(self):
        pass

    def isBusy(self):
        return self.isBusy_
