from flask import Response, jsonify, request
import json

from . import api
from .system import System
from .. import models
from ...devices.arduino import Arduino
from ...devices.camera import Camera

@api.route('/file/<user>/', methods=["GET"])
@api.route('/file/<user>/<name>', methods=['GET'])
def get_configurations(user=None, name=None):
    # Return all saved configurations if name not specified
    if not name:
        configs = models.User.objects(username=user)[0].configurations
        return jsonify([json.loads(config.to_json()) for config in configs])
    elif name == 'default':
        config = json.loads(models.User.objects(username=user)[0].default.to_json())
        config['username'] = user
        return config
