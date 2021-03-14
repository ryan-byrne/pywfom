import cv2
from flask import Response

from pywfom.server.api import api
from pywfom.server import Devices

def _generate_camera_feed(cam):
    while cam.feeding:
        img = cam.read()
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@api.route('/feed/<id>', methods=['GET'])
def camera_feed(id):
    if id == 'arduino':
        pass
    else:
        camera = Devices[id]
        return Response(
            _generate_camera_feed(camera),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
