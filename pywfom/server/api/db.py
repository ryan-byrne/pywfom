from flask import Response, jsonify, request
import json, traceback

from . import api
from .. import models

@api.route('/db/default/<user>', methods=["GET"])
def get_default(user=None):
    config = json.loads(models.User.objects(username=user)[0].default.to_json())
    config['username'] = user
    return config

@api.route('/db/default/<user>/<name>', methods=["PUT"])
def put_default(user=None, name=None):
    print(user, name)
    data = request.get_json()
    data.pop('username', None)
    config = models.Configuration.objects(name=name).get()
    config.update(**data)
    user = models.User.objects(username=user).get()
    user.update(default=config)
    return jsonify(config.to_json())

@api.route('/db/default/<user>/<name>', methods=["POST"])
def post_default(user=None, name=None):
    data = request.get_json()
    data.pop('username', None)
    config = models.Configuration(name=name, **data).save()
    user = models.User.objects(username=user).get()
    user.update(default=config)
    return jsonify(config.to_json())

@api.route('/db/configurations/<user>', methods=["GET"])
@api.route('/db/configurations/<user>/<name>', methods=['GET'])
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

@api.route('/db/configurations/<user>/<name>', methods=['POST'])
def make_new(user=None, name=None):
    # Return all saved configurations if name not specified
    # Create Configuration
    data = request.get_json()
    data.pop('username', None)
    data['arduino'].pop('firmware_version',None)
    data['arduino'].pop('active',None)
    try:
        config = models.Configuration(name=name, **data).save()
        user = models.User.objects(username=user).get()
        user.configurations.append(config)
        user.save()
        return "Success", 200
    except Exception as e:
        traceback.print_exc()
        return str(e), 400

@api.route('/db/configurations/<user>/<name>', methods=['PUT'])
def save_configuration_settings(user=None, name=None, default=None):
    # Return all saved configurations if name not specified
    data = request.get_json()
    data.pop('username', None)
    data['arduino'].pop('firmware_version',None)
    data['arduino'].pop('active',None)
    try:
        config = models.Configuration.objects(name=name)[0]
        config.update(**data)
        return "Success", 200
    except Exception as e:
        traceback.print_exc()
        return str(e), 400
