class System():
    arduino = None
    cameras = []
    file = {}
    username = None
    acquiring = False
    def start_acquisition(self):
        print(self.acquiring)
    def stop_acquisition(self):
        print(self.acquiring)
    def get_acquisition_status(self):
        return {}
