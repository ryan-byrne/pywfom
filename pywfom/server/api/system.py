from flask import request, jsonify, session
import traceback, json

from . import api
from .. import models

from ...devices.arduino import Arduino
from ...devices.camera import Camera

# ****** Create Controllable System ********
class _System(object):
    """docstring for _System."""

    def __init__(self):
        self.arduino = None
        self.cameras = []
        self.file = {}
        self.acquiring = False
        self.username = None

    def set_from_path(self, path):
        # Clear existing settings
        self.delete()
        # Start system from specified path, otherwise ignore
        with open(path, 'r') as f:
            settings = json.load(f)
            self.post(settings)
        f.close()

    def set_from_user_default(self, user):
        # Clear existing settings
        self.delete()
        # Retrieve settings from MongoDB
        default = models.User.objects(username=user).get().default
        # Post the settings
        self.post(id=None, settings=json.loads(default.to_json()))

    def get(self, setting=None):
        resp = {
            "file":self.file,
            "cameras":[cam.json() for cam in self.cameras],
            "arduino":self.arduino.json() if self.arduino else {},
            "username":self.username
        }
        if not setting:
            return resp
        else:
            return resp[setting]

    def delete(self, id=None):

        if id == None:
            print("clearing all")
            self.file = {}
            _ = self.arduino.close() if self.arduino else None
            self.arduino = None
            [cam.close() for cam in self.cameras]
            self.cameras = []
        elif id == 'file':
            self.file = {}
        elif id == 'arduino':
            _ = self.arduino.close() if self.arduino else None
            self.arduino = None
        elif id == 'cameras':
            [cam.close() for cam in self.cameras]
            self.cameras = []
        else:
            cam = self.cameras.pop(int(id))
            cam.close()

        return "Successfully cleared system", 200

    def put(self, id=None, settings={}):

        if id == 'file':
            self.file == settings
        elif id == 'arduino':
            if not self.arduino:
                return "Arduino is not initialized", 400
            else:
                self.arduino.set(**settings)
        else:
            self.cameras[id].set(**settings)

        return self.get(id)

    def post(self, id=None, settings={}):

        if id == 'file':
            self.file == settings
        elif id == 'cameras':
            self.cameras.append( Camera(**settings) )
        elif id == 'arduino':
            if self.arduino:
                return "Cannot POST to Initialized Arduino", 400
            else:
                self.arduino = Arduino(**settings)
        elif id == None:
            self.file = settings['file']
            self.cameras = [Camera(**config) for config in settings['cameras']]
            self.arduino = Arduino(**settings['arduino'])

        return self.get(id)

    def stop_acquisition(self):
        self.acquiring = False

    def start_acquisition(self):
        self.acquiring = True

    def get_acquisition_status(self):
        return self.acquiring
#  ****** Initialize System System ********
system = _System()
# ************* System Settings API Calls ******************
@api.route('/system/settings', methods=['GET'])
@api.route('/system/settings/<id>', methods=['GET'])
def get_settings(id=None):
    # Retrieve the current settings of the session
    return jsonify( system.get(id) )

@api.route('/system/settings', methods=['POST'])
@api.route('/system/settings/<id>', methods=['POST'])
def post_settings(id=None):
    # Add settings to the current session
    return jsonify( system.post(id, request.get_json()) )

@api.route('/system/settings/<id>', methods=['PUT'])
def put_settings(id):
    # Adjust settings in the current session
    return jsonify( system.put(id, request.get_json()) )

@api.route('/system/settings', methods=["DELETE"])
@api.route('/system/settings/<id>', methods=["DELETE"])
def delete_settings(id=None):
    # Delete settings in the current session
    return system.delete(id)
# ************* System Acquisition API Calls ******************
@api.route('/system/acquisition', methods=["GET"])
def get_acquisition(id=None):
    # Delete settings in the current session
    return jsonify( system.get_acquisition_status() )

@api.route('/system/acquisition', methods=["POST"])
def post_acquisition(id=None):
    # Delete settings in the current session
    return jsonify( system.start_acquisition() )

@api.route('/system/acquisition', methods=["DELETE"])
def delete_acquisition(id=None):
    # Delete settings in the current session
    return jsonify( system.stop_acquisition() )
