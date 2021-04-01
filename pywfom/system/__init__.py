import json, os, pywfom

from pywfom.devices.arduino import Arduino
from pywfom.devices.cameras import Camera

DEFAULT_PATH = os.path.join(os.path.dirname(pywfom.__file__),'default.json')

with open(DEFAULT_PATH) as f:
    DEFAULT = json.load(f)

class System:
    file = DEFAULT['file']
    arduino = Arduino(**DEFAULT['arduino'])
    cameras = {
        key:Camera(id=key, **settings) for key, settings in DEFAULT['cameras'].items()
    }
