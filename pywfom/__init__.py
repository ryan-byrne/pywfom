import pkgutil, json
import pywfom.imaging
import pywfom.control
import pywfom.file
import pywfom.viewing

class System(object):

    """Class Wrapper for the OpenWFOM System"""

    def __init__(self, config=None):
        super(System, self).__init__()

        # Create a SimpleNamespace to store the configuration settings
        if not config:
            config = json.loads(pkgutil.get_data(__name__, 'utils/default.json'))
        else:
            config = json.load(open(config, 'r'))

        self.cameras = [imaging.DEVICES[cfg['device']](cfg) for cfg in config['cameras']]
        self.arduino = control.Arduino(config['arduino'])
