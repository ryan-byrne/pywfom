from flask import Response, jsonify, request
import json

from . import api
from .system import System
from ..models import Configuration, User
from ...devices.arduino import Arduino
from ...devices.cameras import Camera

@api.route('/file/<name>', methods=["DELETE"])
def delete_configuration(name):
    # Delete the specified configuration
    pass

@api.route('/file/<name>', methods=["POST"])
def post_configuration(name):
    # Establish settings from specified configuration
    pass

@api.route('/file', methods=["GET"])
@api.route('/file/<name>', methods=["GET"])
def get_configurations(name=None):
    # Return all saved configurations if name not specified
    if name == 'default':
        return User.objects(name='ryan')[0].default.to_json()

@api.route('/file/<name>', methods=["PUT"])
def put_configuration(name):
    # Save a new configuration
    return jsonify("hello")
