from flask import request, jsonify, session
import traceback

from . import api

from pywfom.devices.arduino import Arduino
from pywfom.devices.cameras import Camera

class System:
    arduino = None
    cameras = []
    file = {}

# ****** Create Responses ********

def _get_response(id):
    _settings = {
        'file':System.file,
        'arduino':System.arduino.json() if System.arduino else {},
        'cameras':[cam.json() for cam in System.cameras]
    }
    return jsonify(_settings[id] if id else _settings)


def _post_response(id, settings):
    if id == 'file':
        System.file = settings
        return jsonify(settings)
    elif id == 'arduino':
        System.arduino = Arduino(**settings)
        return jsonify(System.arduino.json())
    else:
        camera = Camera(**settings)
        System.cameras.append(camera)
        return jsonify([cam.json() for cam in System.cameras])

def _put_response(id, settings):
    if id == 'file':
        System.file = settings
        return jsonify(settings)
    elif id == 'arduino':
        System.arduino.set(**settings)
        return jsonify(System.arduino.json())
    else:
        System.cameras[id].set(**settings)
        return jsonify(System.cameras[id].json())

def _delete_response(id):
    if id == 'file':
        System.file = {}
    elif id == 'arduino':
        System.arduino.close()
    else:
        System.cameras[int(id)].close()
        del System.cameras[int(id)]
    return "Successfully closed {}".format(id), 200

# ************* ROUTING FUNCTIONS ******************
@api.route('/system', methods=['GET'])
@api.route('/system/<id>', methods=['GET'])
def get_settings(id=None):
    # Retrieve the current settings of the session
    return _get_response(id)

@api.route('/system', methods=['POST'])
@api.route('/system/<id>', methods=['POST'])
def post_settings(id=None):
    # Add settings to the current session
    return _post_response(id, request.get_json() )

@api.route('/system/<id>', methods=['PUT'])
def put_settings(id=None):
    # Adjust settings in the current session
    return _put_response(id, request.get_json() )

@api.route('/system', methods=["DELETE"])
@api.route('/system/<id>', methods=["DELETE"])
def delete_settings(id=None):
    # Delete settings in the current session
    return _delete_response(id)
