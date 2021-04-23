from flask import request, jsonify, session
from tqdm import tqdm
import traceback, json, time, os, datetime, threading, pywfom
import numpy as np

from . import api
from .. import models

from ...devices.arduino import Arduino
from ...devices.camera import Camera

DEFAULT_FILE = {
    "directory":os.environ['PYWFOM_DIR'] if 'PYWFOM_DIR' in os.environ else None,
    "number_of_runs":"",
    "run_length":"",
    "run_length_unit":"sec"
}

# ****** Create Controllable System ********

class _SystemException(Exception):
    pass


class _System(object):
    """docstring for _System."""

    def __init__(self):
        self.arduino = Arduino()
        self.cameras = []
        self.file = DEFAULT_FILE
        self.acquiring = False
        self.username = None
        self.mouse = None
        self.write_speed = 0
        self.primary_framerate = 0

    def benchmark_disk(self):
        pass

    def set_from_file(self, path):
        # Clear existing settings
        self.delete()
        # Start system from specified path, otherwise ignore
        with open(path, 'r') as f:
            settings = json.load(f)
            self.post(None, settings)
        f.close()

    def set_from_user_default(self, user, pwd):
        # Clear existing settings
        self.delete()
        self.username = user
        # Retrieve settings from MongoDB
        default = models.User.objects(username=user, password=pwd).get().default
        # Post the settings
        self.post(id=None, settings=json.loads(default.to_json()))

    def get(self, setting=None):

        resp = {
            "file":self.file,
            "cameras":[cam.json() for cam in self.cameras],
            "arduino":self.arduino.json() if self.arduino else {},
            "username":self.username,
            "mouse":self.mouse
        }
        if not setting:
            return resp
        elif setting in resp:
            return resp[setting]
        else:
            return self.cameras[int(setting)].json()

    def delete(self, id=None):

        if id == None:
            self.file = {}
            _ = self.arduino.close() if self.arduino else None
            self.arduino = None
            [cam.close() for cam in self.cameras]
            self.cameras = []
        elif id == 'file':
            self.file = {}
        elif id == 'arduino':
            _ = self.arduino.close() if self.arduino else None
            self.arduino = None
        elif id == 'cameras':
            [cam.close() for cam in self.cameras]
            self.cameras = []
        else:
            cam = self.cameras.pop(int(id))
            cam.close()

        return f"Successfully delete {id}", 200

    def put(self, id=None, settings={}):

        if id == 'file':
            self.file == settings
        elif id == 'arduino':
            if not self.arduino:
                return "Arduino is not initialized", 400
            else:
                self.arduino.set(**settings)
        elif id == 'mouse':
            self.mouse = settings
        else:
            self.cameras[int(id)].set(**settings)

        return self.get(id)

    def post(self, id=None, settings={}):

        if id == 'file':
            self.file = settings
        elif id == 'cameras':
            _newcam = Camera(**settings)
            self.cameras.append( _newcam )
            return _newcam.json()
        elif id == 'arduino':
            if self.arduino:
                return "Cannot POST to Initialized Arduino", 400
            else:
                self.arduino = Arduino(**settings)
        elif id == None:
            self.file = settings['file']
            self.cameras = [Camera(**config) for config in settings['cameras']]
            self.arduino = Arduino(**settings['arduino'])
        else:
            setattr(self, id, settings)

        return self.get(id)

    def stop_acquisition(self):
        self.acquiring = False

    def check_acquisition_settings(self):

        if self.acquiring:
            return ["All Good"]
        else:
            errors = []

            # Check run settings
            for key in ['run_length', 'run_length_unit', 'number_of_runs', 'directory']:
                if not self.file[key]:
                    errors.append(f"{key} is missing from file settings")

            # CAMERA SETTINGS
            _camera_settings = [cam.json() for cam in self.cameras]
            # Check number of cameras
            if len(_camera_settings) == 0:
                errors.append("No cameras have been added")
            # Assert proper number of primary cameras
            _primary_fr = [cam['framerate'] for cam in _camera_settings if cam['primary']]
            if len(_primary_fr) == 0:
                errors.append("You must specify a primary camera")
            elif len(_primary_fr) > 1:
                error.append("You can only specify one primary camera")
            else:
                self.primary_framerate = _primary_fr[0]
                _over = [cam['framerate'] < fr for cam in _camera_settings if not cam['primary']]
                # TODO: Ensure cameras aren't going over their maximum framerate


            # Check additional data settings
            for key in ['username', 'mouse']:
                if not getattr(self, key):
                    errors.append(f"{key} was not specified")

            return errors

    def start_acquisition(self):

        print("Starting an acquisition")

        path = os.path.join(self.file['directory'], datetime.datetime.now().strftime('%m_%d_%Y_%H%M%S'))

        os.mkdir(path)

        for cam in self.cameras:
            cam.acquiring = True

        for i in tqdm(range(int(self.file['number_of_runs'])), unit="run"):

            run = self._create_run()

            if not run:
                break
            else:
                os.mkdir(f"{path}/run{i}")

            rl, rlu = self.file['run_length'], self.file['run_length_unit']

            num_frames = self.primary_framerate*rl*{"sec":1,"min":60,"hr":3600}[rlu]
            for j in tqdm(range(int(num_frames)), leave=False, unit="frame"):
                # Place latest frame from each camera in dict
                frames = {
                    f"{cam.id}":cam.acquired_frames.get() for cam in self.cameras
                }
                # Create thread arguments
                args = (f"{path}/run{i}/frame{j}.npz", frames, run,)
                # Start a thread to write to file and mongodb
                threading.Thread(target=self._write_to_file, args=args).start()
            run.save()

        for cam in self.cameras:
            cam.acquiring = False

        return True, []

    def _create_run(self):
        # Check to see if MongoDB keys are valid
        try:
            mouse = models.Mouse.objects(name=self.mouse).get()
            user = models.User.objects(username=self.username).get()
            config = models.Configuration(
                file=self.file,
                arduino=self.arduino.json(),
                cameras=[cam.json() for cam in self.cameras]
            ).save()
            return models.Run(mouse=mouse,user=user,configuration=config,frames=[], timestamp=datetime.datetime.now())
        except Exception as e:
            traceback.print_exc()
            return None

    def _write_to_file(self, fname, frames, run):
        np.savez(fname, **frames)
        frame = models.Frame(file=fname)
        frame.save()
        run.frames.append(frame)

#  ****** Initialize System System ********
system = _System()
# ************* System Settings API Calls ******************
@api.route('/system/settings', methods=['GET'])
@api.route('/system/settings/<id>', methods=['GET'])
def get_settings(id=None):
    # Retrieve the current settings of the session
    return jsonify( system.get(id) )

@api.route('/system/settings', methods=['POST'])
@api.route('/system/settings/<id>', methods=['POST'])
def post_settings(id=None):
    # Add settings to the current session
    return jsonify( system.post(id, request.get_json()) )

@api.route('/system/settings/<id>', methods=['PUT'])
def put_settings(id):
    # Adjust settings in the current session
    return jsonify( system.put(id, request.get_json()) )

@api.route('/system/settings', methods=["DELETE"])
@api.route('/system/settings/<id>', methods=["DELETE"])
def delete_settings(id=None):
    # Delete settings in the current session
    return system.delete(id)

@api.route('/system/acquisition', methods=["GET"])
def get_acquisition():
    return jsonify(system.check_acquisition_settings())

@api.route('/system/acquisition', methods=["DELETE"])
def stop_acquisition():
    return "Success", 200

@api.route('/system/acquisition', methods=['POST'])
def start_acquisition():
    try:
        system.start_acquisition()
        return "Success", 200
    except Exception as e:
        traceback.print_exc()
        return str(e), 404
