from flask import Flask
from flask import request, jsonify

from . import arduino

app = Flask(__name__)
settings = {}

# List
# View
# Settings

@app.route('/setup/<device>/<function>',methods=['POST', 'GET'])
@app.route('/setup/<device>/<function>/<index>',methods=['POST', 'GET'])
def handle(device, function, index=None):
    # Devices: Arduino, Camera
    if device == 'arduino':
        # Arduino Setup Functions: set, get, list, connect, update
        if function == 'set':
            # TODO: Deploy settings to arduino
            print(request.get_json())
            return(jsonify(success='success'))
        elif function == 'list':
            return(jsonify(arduino.list_ports()))
        elif function == 'get':
            return(jsonify(settings={}))
    elif device == 'camera':
        # Camera Setup Functions
        pass
