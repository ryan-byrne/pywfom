class System():
    arduino = None
    cameras = []
    file = {}
    _acquiring = False
    def start_acquisition(self):
        print(self._acquiring)
    def stop_acquisition(self):
        print(self._acquiring)
