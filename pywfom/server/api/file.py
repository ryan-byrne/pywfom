from flask import Response, jsonify, request
import json

from pywfom.server.api import api

configs = {
    "hello":{
        "file":{},
        "arduino":{},
        "cameras":{}
    }
}

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
    if name == None:
        return jsonify(configs)
    else:
        return jsonify(configs[name])

@api.route('/file/<name>', methods=["PUT"])
def put_configuration(name):
    # Save a new configuration
    return jsonify("hello")
