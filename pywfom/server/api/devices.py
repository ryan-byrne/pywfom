from flask import jsonify
from ...devices.arduino import find_arduinos
from ...devices.camera import find_cameras

from ..api import api

@api.route('devices/<device>', methods=['GET'])
def api_find(device):
    if device == 'cameras':
        return jsonify(find_cameras())
    else:
        return jsonify(find_arduinos())
