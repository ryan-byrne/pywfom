from flask import jsonify
from pywfom.devices.arduino import find_arduinos
from pywfom.devices.camera import find_cameras

from pywfom.server.api import api

@api.route('devices/<device>', methods=['GET'])
def api_find(device):
    if device == 'cameras':
        return jsonify(find_cameras())
    else:
        return jsonify(find_arduinos())
