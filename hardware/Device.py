


class Device(object):
    def __init__(self, macGuiver, frameName="XY_Stage", mm_name=""):
        self.mmc = macGuiver.mmc
        self.master = macGuiver.root

        self.frameName = frameName
        self.mm_name = mm_name

        self.initialized = False

    def createGUI(self):
        pass

    def loadDevice(self, params=None):
        pass
