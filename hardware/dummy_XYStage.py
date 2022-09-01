#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time

from hardware.XYStage import XYStage

class dummy_XY(XYStage):
    def __init__(self, mac_guiver):
        super(dummy_XY, self).__init__(mac_guiver, frameName="Dummy_XY", mm_name="")
        self.is_busy_ = False

    def load_device(self):
        self.mac_guiver.write_to_splash_screen("Loading dummy XY stage", type="info")
        return True

    def move_absolute(self, pos_micron):
        pass

    def move_relative(self, pos_micron):
        pass

    def wait_for_device(self):
        self.is_busy_ = True
        time.sleep(0.2)
        self.is_busy_ = False

    def stop(self):
        pass

    def is_busy(self):
        return self.is_busy_
