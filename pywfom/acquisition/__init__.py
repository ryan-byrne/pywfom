import pywfom, json, os, site

from pywfom.devices.cameras import Camera
from pywfom.devices.arduino import Arduino

_PATH = os.path.join(os.path.dirname(pywfom.__file__),'acquisition/default.json')

with open(_PATH) as f:
    DEFAULT_SETTINGS = json.load(f)

class Acquisition(object):

    def __init__(self, default=None, **settings):
        # TODO: Add default settings for missing
        settings = settings if not default else default
        self.file = settings['file']
        self.arduino = None if 'arduino' not in settings else Arduino(**settings['arduino'])
        self.cameras = {} if 'cameras' not in settings else {Cameras(**settings[id]) for id in settings['cameras']}

    def set(self, **settings):
        for k,v in settings.items():
            self.file[k] = v

current_acquisition = Acquisition(DEFAULT_SETTINGS)
