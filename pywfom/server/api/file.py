from flask import Response, jsonify, request
import json

from pywfom.server.api import api
from pywfom.acquisition import current_acquisition

configs = {
    "hello":{
        "file":{},
        "arduino":{},
        "cameras":{}
    }
}

@api.route('/file', methods=["GET"])
def load_configurations():
    # Delete settings in the current session
    return jsonify(configs)

@api.route('/file', methods=["POST"])
def save_configurations():
    print(request.get_json())
    # Delete settings in the current session
    return jsonify("hello")
