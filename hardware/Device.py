


class Device(object):
    def __init__(self, mac_guiver, frameName="XY_Stage", mm_name=""):
        # self.mmc = mac_guiver.mmc
        if mac_guiver is not None:
            self.master = mac_guiver.root
        else:
            self.master = None
        self.mac_guiver = mac_guiver

        self.frameName = frameName
        self.mm_name = mm_name

        self.tag_label = ""

        self.initialized = False
        self.is_busy_ = False

    def create_GUI(self):
        pass

    def load_device(self, params=None):
        pass

    def close_device(self, params=None):
        pass