from flask import Flask, request, jsonify, Response
import cv2

from . import arduino, imaging

app = Flask(__name__)

class System(object):
    arduino = None
    cameras = []

# ********** Cameras ****************

@app.route('/find/cameras', methods=['GET'])
def find_cameras():
    return jsonify(imaging.find_cameras())

@app.route('/settings/camera/<index>/get', methods=['GET'])
def get_camera_settings(index):
    return(jsonify(System.cameras[index].get()))

@app.route('/settings/camera/<index>/set', methods=['POST'])
def set_camera_settings(index):
    System.cameras[index].set(request.get_json())

@app.route('/connect/camera/', methods=['POST'])
def connect_to_camera():
    data = request.get_json()
    for cam in System.cameras:
        if cam.index == data['index'] and cam.device == data['device']:
            return (jsonify(status='error',message='Device already exists.'))
    System.cameras.append(imaging.Camera(data['index'], data['device']))
    return(jsonify(status='success'))

@app.route('/close/camera/<index>', methods=['POST'])
def close_camera(index):
    System.cameras[int(index)].close()
    del System.cameras[int(index)]
    return(jsonify(status='success'))

def gen(cam):

    while True:
        img = cam.read()
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/feed/<index>', methods=['GET'])
def camera_feed(index):
    cam = System.cameras[int(index)]
    return Response(gen(cam),mimetype='multipart/x-mixed-replace; boundary=frame')

# ********** Arduino ****************

@app.route('/find/arduinos', methods=['GET'])
def find_arduinos():
    return jsonify(arduino.find())

@app.route('/connect/arduino', methods=['POST'])
def connect_to_arduino():
    # <pw0.0.1>
    settings = request.get_json()
    System.arduino = arduino.Arduino(settings['device'])
    result = System.arduino.test()
    if result[:3] != '<pw':
        return jsonify(status='error')
    else:
        return(jsonify(status='success', version=result[:7]))

@app.route('/settings/arduino/get', methods=['GET'])
def get_arduino_settings():
    return(jsonify('success'))

@app.route('/settings/arduino/set', methods=['POST'])
def set_arduino_settings():
    pass
