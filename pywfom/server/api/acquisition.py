from flask import jsonify, Blueprint
from pywfom.server.api import api

from ...system import System

@api.route('/acquisition', methods=['POST'])
def start_acquisition():
    # Retrieve the current settings of the session
    try:
        System.start_acquisition(System)
        return "Successfully started acquisition", 200
    except Exception as e:
        return str(e), 400

@api.route('/acquisition', methods=['DELETE'])
def stop_acquisition():
    # Retrieve the current settings of the session
    try:
        System.stop_acquisition(System)
        return "Successfully stopped acquisition", 200
    except Exception as e:
        return str(e), 400
