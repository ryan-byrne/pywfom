from flask import jsonify, Blueprint
from pywfom.devices.arduino import find_arduinos
from pywfom.devices.cameras import find_cameras

from pywfom.server.api import api

@api.route('find/<device>', methods=['GET'])
def api_find(device):
    if device == 'cameras':
        return jsonify(find_cameras())
    else:
        return jsonify(find_arduinos())
