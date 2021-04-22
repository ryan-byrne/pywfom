import cv2, time, os
from datetime import datetime
from flask import Response, render_template_string
import numpy as np
import time

from . import api
from .system import system

def _generate_camera_feed(cam):
    while cam.active:
        frame = cv2.imencode('.jpg', cam.feed.get())[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@api.route('/feed/<id>', methods=['GET'])
def camera_feed(id):
    return Response(
        _generate_camera_feed(system.cameras[int(id)]),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def _generate_viewer_feed(id):
    path = "/Users/rbyrne/projects/pywfom/tmp/20210416144534/run0"
    img = np.load(f"{path}/frame5.npz")
    while True:
        for i, _ in enumerate(os.listdir(path)):
            img = np.load(f"{path}/frame{i}.npz")
            frame = cv2.imencode('.jpg', img['opencv2'])[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
