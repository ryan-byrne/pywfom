from flask import request, jsonify, session
import traceback

from pywfom.server.api import api

from pywfom.devices.arduino import Arduino
from pywfom.devices.cameras import Camera
from pywfom.acquisition import current_acquisition

def _session_response(id):
    return (jsonify(session) if not id else jsonify(session[id]))

# ****** Create Responses ********
def _get_response(id):

    if not id:
        # Get settings for everything in the session
        return jsonify({key:session[key] for key in session})
    elif id == 'file' and 'file' not in session:
        # If file is not in session, create it
        session['file'] = current_acquisition.file
        return jsonify(session['file'])
    elif id == 'cameras':
        # Return all session objects that are not arduino or file
        return jsonify( {key:session[key] for key in session if key not in ['arduino', 'file']} )
    else:
        # Get settings from specific id
        return jsonify(session[id])

def _post_response(id, settings):

    try:
        if not id:
            # Post settings to everything in the session
            pass
        elif id == 'arduino':
            current_acquisition.arduino = Arduino(**settings)
            session[id] = current_acquisition.arduino.json()
        elif id == 'file':
            current_acquisition.set(**settings)
            session[id] = current_acquisition.file
        else:
            current_acquisition.cameras[id] = Camera(**settings)
            session[id] = current_acquisition.cameras[id].json()

        return _session_response(id)

    except Exception as e:
        traceback.print_exc()
        return "Unable to establish new settings", 400

def _put_response(id, settings):
    try:
        if not id:
            return "Unable to PUT settings without a specified ID", 400
        elif id == 'file':
            current_acquisition.set(**settings)
            session['file'] = current_acquisition.file
        elif id == 'arduino':
            current_acquisition.arduino.set(**settings)
            session['arduino'] = current_acquisition.arduino.json()
        else:
            current_acquisition.cameras[id].set(**settings)
            session[id] = current_acquisition.cameras[id].json()

        return _session_response(id)

    except Exception as e:
        return "Unable to establish settings in the Session", 400

def _delete_response(id):
    try:

        if not id:
            # Delete and close arduino information from acquisition
            if current_acquisition.arduino:
                current_acquisition.arduino.close()
            current_acquisition.arduino = None
            # Delete and close camera information from acquisition
            if current_acquisition.cameras:
                [current_acquisition.cameras[key].close() for key in current_acquisition.cameras]
            current_acquisition.cameras = {}
            # Delete all cameras and arduino from session
            for key in list(session):
                if key != 'file':
                    session.pop(key, None)
        elif id == 'file':
            return "You are not allowed to delete file information", 405
        elif id == 'arduino':
            # Delete and close arduino information from acquisition
            current_acquisition.arduino.close()
            del current_acquisition['arduino']
            session.pop('arduino', None)
        else:
            current_acquisition.cameras[id].close()
            session.pop(id, None)

        return "Successfully cleared settings", 200

    except Exception as e:
        traceback.print_exc()
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
