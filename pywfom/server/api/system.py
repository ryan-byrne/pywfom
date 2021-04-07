from flask import request, jsonify, session
import traceback

from . import api

from ...devices.arduino import Arduino
from ...devices.camera import Camera

from ...system import System

# ****** Create Responses ********

def _get_response(id):
    _settings = {
        'file':System.file,
        'arduino':System.arduino.json() if System.arduino else {},
        'cameras':[cam.json() for cam in System.cameras]
    }
    return jsonify(_settings[id] if id else _settings)

def _post_response(id, settings):

    if id == None:
        System.file = settings['file']
        # Send create new Arduino
        if System.arduino:
            return "Arduino is already initialized. It must be empty to POST", 403
        else:
            System.arduino = Arduino(**settings['arduino'])
        # Add new cameras
        if len(System.cameras) > 0:
            return "Camera array must be empty before POST", 403
        else:
            System.cameras = [Camera(**cam) for cam in settings['cameras']]
        return jsonify({
            "file":System.file,"arduino":System.arduino.json(),"cameras":[cam.json() for cam in System.cameras]
        })
    elif id == 'file':
        System.file = settings
        return jsonify(settings)
    elif id == 'arduino':
        _ = System.arduino.close() if System.arduino else None
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
        if not System.arduino:
            return "System Arduino has not been initialized", 400
        else:
            return jsonify(System.arduino.json())
    else:
        System.cameras[id].set(**settings)
        return jsonify(System.cameras[id].json())

def _delete_response(id):
    if id == None:
        System.file = {}
        if System.arduino:
            System.arduino.close()
        System.arduino = None
        [System.cameras.pop(i).close() for i in range(len(System.cameras))]
    elif id == 'file':
        System.file = {}
    elif id == 'arduino':
        if System.arduino:
            System.arduino.close()
        System.arduino = None
    else:
        System.cameras.pop(int(id)).close()
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
def put_settings(id):
    # Adjust settings in the current session
    return _put_response(id, request.get_json() )

@api.route('/system', methods=["DELETE"])
@api.route('/system/<id>', methods=["DELETE"])
def delete_settings(id=None):
    # Delete settings in the current session
    return _delete_response(id)
