from flask import Response, jsonify, request
import json

from . import api
from .system import System
from .. import models
from ...devices.arduino import Arduino
from ...devices.camera import Camera

@api.route('/file/<name>', methods=["DELETE"])
def delete_configuration(name):
    # Delete the specified configuration
    pass

@api.route('/file/<name>', methods=["POST"])
def post_configuration(name):
    # Establish settings from specified configuration
    pass

@api.route('/file/configuration/<user>/<name>', methods=["GET"])
def get_configurations(user=None, name=None):
    # Return all saved configurations if name not specified
    if name == 'default':
        config = json.loads(models.User.objects(username=user)[0].default.to_json())
        config['username'] = user
        return config

@api.route('/file/<name>', methods=["PUT"])
def put_configuration(name):
    # Save a new configuration
    return jsonify("hello")
