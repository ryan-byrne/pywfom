import pkgutil, json
import tkinter as tk
from .imaging import Camera
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

        self.cameras = [Camera(config=cfg) for cfg in config['cameras']]
        self.arduino = Arduino(config=config['arduino'])
        self.file = Writer(config['file'])
