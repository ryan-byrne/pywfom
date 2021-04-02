from flask import request, jsonify, session
import traceback

from . import api

from pywfom.system import System
from pywfom.devices.arduino import Arduino
from pywfom.devices.cameras import Camera

# ****** Create Responses ********

def _get_response(id):
    _settings = {
        'file':System.file,
        'arduino':System.arduino.json(),
        'cameras':{key:cam.json() for key, cam in System.cameras.items()}
    }

    return jsonify(_settings[id] if id else _settings)


def _post_response(id, settings):
    if id == 'file':
        System.file = settings
        return jsonify(setting)
    elif id == 'arduino':
        System.arduino = Arduino(**settings)
        return jsonify(System.arduino.json())
    else:
        System.cameras[id] = Camera(**settings)
        return jsonify(System.cameras[id].json())

def _put_response(id, settings):
    if id == 'file':
        System.file = settings
        return jsonify(setting)
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
        System.cameras[id].close()
        del System.cameras[id]
    return "Successfully closed {}".format(id), 200

# ************* ROUTING FUNCTIONS ******************
@api.route('/settings', methods=['GET'])
@api.route('/settings/<id>', methods=['GET'])
def get_settings(id=None):
    # Retrieve the current settings of the session
    return _get_response(id)

@api.route('/settings', methods=['POST'])
@api.route('/settings/<id>', methods=['POST'])
def post_settings(id=None):
    # Add settings to the current session
    return _post_response(id, request.get_json() )

@api.route('/settings/<id>', methods=['PUT'])
def put_settings(id=None):
    # Adjust settings in the current session
    return _put_response(id, request.get_json() )

@api.route('/settings', methods=["DELETE"])
@api.route('/settings/<id>', methods=["DELETE"])
def delete_settings(id=None):
    # Delete settings in the current session
    return _delete_response(id)
