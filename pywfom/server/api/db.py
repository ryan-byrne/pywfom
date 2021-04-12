from flask import Response, jsonify, request
import json, traceback

from . import api
from .. import models

@api.route('/db/<user>/', methods=["GET"])
@api.route('/db/<user>/<name>', methods=['GET'])
def get_configurations(user=None, name=None):
    # Return all saved configurations if name not specified
    if user == 'mice':
        return jsonify([mouse.name for mouse in models.Mouse.objects])
    elif user == 'mouse':
        models.Mouse(name=name).save()
        return "Success", 200
    elif not name:
        configs = models.User.objects(username=user)[0].configurations
        return jsonify([json.loads(config.to_json()) for config in configs])
    elif name == 'default':
        config = json.loads(models.User.objects(username=user)[0].default.to_json())
        config['username'] = user
        return config

@api.route('/db/<user>/<name>', methods=['POST'])
def make_new(user=None, name=None):
    # Return all saved configurations if name not specified
    # Create Configuration
    data = request.get_json()
    data.pop('username', None)
    try:
        config = models.Configuration(name=name, **data).save()
        user = models.User.objects(username=user).get()
        user.configurations.append(config)
        user.save()
        return "Success", 200
    except Exception as e:
        traceback.print_exc()
        return str(e), 400

@api.route('/db/<user>/<name>', methods=['PUT'])
def save_configuration_settings(user=None, name=None):
    # Return all saved configurations if name not specified
    data = request.get_json()
    data.pop('username', None)
    try:
        config = models.Configuration(name=name, **data).update()
        return "Success", 200
    except Exception as e:
        traceback.print_exc()
        return str(e), 400
