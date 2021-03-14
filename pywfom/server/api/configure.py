from flask import Blueprint, request, jsonify

from pywfom.devices.arduino import Arduino
from pywfom.devices.cameras import Camera

from pywfom.server.api import api
from pywfom.server import Devices, File

NAME = "Python Connection API"
DEVICE_MAP = [ Arduino, Camera ]

@api.route('/configure', methods=['GET'], defaults={'key':None})
@api.route('/configure/<key>', methods=['GET'])
def api_get_configuration(key=None):
    if key and key not in Devices:
        return jsonify(status='error', message='{0} was not initialized'.format(key))
    elif not key:
        return jsonify(
            status='success',
            devices=[Devices[key].json() for key in Devices.keys()],
            file=File
        )

@api.route('/configure', methods=['POST'])
def api_set_configuration():

    """

    command: ['open', 'close', 'set']
    device: ['arduino', 'jci2je8cjk']
    config: Configuration Settings (Object)

    """

    # Store data recieved from client
    data = request.get_json()
    # Set variables
    cmd, key, config = data['command'], data['device'], data['config']

    if cmd == 'open' and key in Devices.keys():
        # Catch if device has already been opened
        return (jsonify(
            status="error",
            message="Camera (id={0}) was already opened".format(key),
            type=NAME,
            devices=[Devices[key].json() for key in Devices.keys()]
        ))

    elif cmd in ['close', 'set'] and key not in Devices.keys():
        # Catch if device is not found
        return (jsonify(
            status="error",
            message="Camera (id={0}) has not been opened".format(key),
            type=NAME,
            devices=[Devices[key].json() for key in Devices.keys()]
        ))

    elif cmd == 'open':
        # Open a Camera or Arduino Object
        try:
            Devices[ key ] = DEVICE_MAP[0 if key == 'arduino' else 1](config=config)
            return jsonify(status="success", config=Devices[ key ].json())
        except Exception as e:
            return jsonify(status="error",message=e.message,type=NAME)

    elif cmd == 'close':
        # Close Camera or Arduino and delete instance
        try:
            Devices[ key ].close()
            del Devices[ key ]
            return jsonify(status="success")
        except Exception as e:
            print(e)
            return jsonify(status='error',message=e.message, type=NAME)

    elif cmd == 'set':
        # Set Camera or Arduino Settings
        try:
            Devices[ key ].set(config)
            return jsonify(status='success')
        except Exception as e:
            return jsonify(status='error',message=e.message, type=NAME)
