import shelve
from os import path

class Config:
    def __init__(self):
        self.shelf = None
        self.file_name = "config_shelve.ini"
        self.selected_hardware = []
        self.optical_filter_label = []
        self.load()

    def save(self):
        self.shelf = shelve.open(self.file_name, 'n')  # n for new
        self.shelf['selected_hardware'] = self.selected_hardware
        self.shelf['optical_filter_label'] = self.optical_filter_label
        self.shelf.close()

    def load(self):
        if not path.exists(self.file_name):
            self.save()
        self.shelf = shelve.open(self.file_name)

        # load for the controller
        self.selected_hardware = self.shelf['selected_hardware']
        self.optical_filter_label = self.shelf['optical_filter_label']

    def save_selected_hardware(self, hardware_dict):
        self.selected_hardware = []
        for key, value in hardware_dict.items():
            if value.get() == 1:
                self.selected_hardware .append(key)

        self.save()
