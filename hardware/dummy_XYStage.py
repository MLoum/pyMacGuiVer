#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time

from XYStage import XYStage

class dummy_XY(XYStage):
    def __init__(self, mac_guiver):
        super(dummy_XY, self).__init__(mac_guiver, frameName="Dummy_XY", mm_name="")

    def load_device(self):
        return True

    def move_absolute(self, pos_micron):
        pass

    def move_relative(self, pos_micron):
        pass

    def wait_for_device(self):
        self.is_busy = True
        time.sleep(1)
        self.is_busy = False

    def stop(self):
        pass

    def is_busy(self):
        return self.is_busy
