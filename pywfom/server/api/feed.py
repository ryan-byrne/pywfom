import cv2, time
from datetime import datetime
from flask import Response, render_template_string
import time

from . import api
from .system import System

def _generate_camera_feed(cam):
    while cam.active:
        frame = cv2.imencode('.jpg', cam.feed.get())[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def _generate_arduino_feed(ard):
    while ard.active:
        yield render_template_string("<p>Hello world<p>\n")

@api.route('/feed/<id>', methods=['GET'])
def camera_feed(id):
    if id == 'arduino':
        return Response(
            _generate_arduino_feed()
        )
    else:
        camera = System.cameras[int(id)]
        return Response(
            _generate_camera_feed(camera),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
