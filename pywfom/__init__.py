import pkgutil, json
import tkinter as tk
from .imaging import Andor, Spinnaker, Webcam, Test
from .control import Arduino
from .viewing import Main
from .file import Writer

class System(object):

    """Class Wrapper for the OpenWFOM System"""

    def __init__(self, config=None):
        super(System, self).__init__()

        if not config:
            config = json.loads(pkgutil.get_data(__name__, 'utils/default.json'))
        else:
            config = json.load(open(config, 'r'))

        self.cameras = [DEVICES[cam['device']](cam) for cam in config['cameras']]
        self.arduino = Arduino(config['arduino'])
        self.file = Writer(config['file'])

    def view(self):
        """Module for launching the PyWFOM Viewing Frame"""
        root = tk.Tk()
        frame = Main(root, self)
        frame.root.mainloop()

DEVICES = {
    'andor':Andor,
    'spinnaker':Spinnaker,
    'webcam':Webcam,
    'test':Test
}
