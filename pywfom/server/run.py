from flask import Flask, request, jsonify

from pywfom.devices.arduino import find_arduinos, Arduino
from pywfom.devices.cameras import find_cameras

app = Flask('pywfom')

class System(object):
    arduino = None
    cameras = []


@app.route('/api/find/<device>', methods=['GET'])
def api_find(device):
    if device == 'cameras':
        return jsonify(find_cameras())
    else:
        return jsonify(find_arduinos())

@app.route('/api/connection/<device>', methods=['POST'])
def api_connect(device):
    if device == 'camera':
        return(jsonify(status='success'))
    else:
        ard = Arduino(request.get_json()['device'])
        if ard.test():
            System.arduino = ard
            return(jsonify(status='success'))
        else:
            return(jsonify(status='error'))

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
