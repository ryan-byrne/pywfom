from flask import request, jsonify, session
import traceback

from pywfom.server.api import api
from pywfom.server import Configuration

from pywfom.devices.arduino import Arduino
from pywfom.devices.cameras import Camera
from pywfom.file import File

_CLASS_MAP = {
    'arduino':Arduino,
    'file':File
}

def _session_response(id):
    return (session if not id else session[id])

# ****** Create Responses ********
def _get_response(id):
    if not id:
        # Get settings for everything in the session
        return jsonify({key:session[key] for key in session})
    elif id == 'cameras':
        return jsonify( {key:session[key] for key in session if key not in ['arduino', 'file']} )
    else:
        # Get settings from specific id
        return jsonify(session[id])

def _post_response(id, settings):
    try:

        if not id:
            # Post settings to everything in the session
            for key in settings.keys():
                if key in _CLASS_MAP:
                    Configuration[key] = _CLASS_MAP[key](**settings[key])
                    session[key] = Configuration[key].json()
                else:
                    Configuration[id] = Camera(**settings)
                    session[id] = Configuration[id].json()

        else:
            # Post settings to specific id
            Configuration[id] = _CLASS_MAP[id](**settings) if id in _CLASS_MAP else Camera(**settings)
            session[id] = Configuration[id].json()

        return _session_response(id)

    except Exception as e:
        traceback.print_exc()
        return "Unable to establish new settings", 400

def _put_response(id, settings):
    try:
        if not id:
            # Put settings for everything specified
            [ session[key].set(**settings[key]) for key in settings ]
        else:
            # Only put settings for specified id
            session[id].set(**settings[id])

        return _session_response(id)

    except Exception as e:
        return "Unable to establish settings in the Session", 400

def _delete_response(id):
    try:

        if not id:
            for key in list(session):
                session[key].close()
                session.pop(key, None)
        else:
            # Delete session variables only for specified id
            session[id].close()
            session.pop(id, None)

        return _session_response(id)

    except Exception as e:
        return "Unable to remove settings from session", 400

# ************* ROUTING FUNCTIONS ******************
@api.route('/settings', methods=['GET'])
@api.route('/settings/<id>', methods=['GET'])
def get_settings(id=None):
    # Retrieve the current settings of the session
    return _get_response(id)

@api.route('/settings', methods=['POST'])
@api.route('/settings/<id>', methods=['POST'])
def post_settings(id=None):
    # Add settings to the current session
    return _post_response(id, request.get_json() )

@api.route('/settings/<id>', methods=['PUT'])
def put_settings(id=None):
    # Adjust settings in the current session
    return _put_response(id, request.get_json() )

@api.route('/settings', methods=["DELETE"])
@api.route('/settings/<id>', methods=["DELETE"])
def delete_settings(id=None):
    # Delete settings in the current session
    return _delete_response(id)
