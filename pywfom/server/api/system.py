from flask import request, jsonify, session
from tqdm import tqdm
import traceback, json, time, os, datetime, threading
import numpy as np

from . import api
from .. import models

from ...devices.arduino import Arduino
from ...devices.camera import Camera

# ****** Create Controllable System ********

class _SystemException(Exception):
    pass


class _System(object):
    """docstring for _System."""

    def __init__(self):
        self.arduino = None
        self.cameras = []
        self.file = {}
        self.acquiring = False
        self.username = None
        self.name = None
        self.mouse = None
        self.write_speed = 0

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
            "name":self.name,
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
            self.name = settings['name']
            self.username = settings['username']
        else:
            setattr(self, id, settings)

        return self.get(id)

    def stop_acquisition(self):
        self.acquiring = False

    def _check_system_settings(self):

        print("Checking System Settings...")

        errors = []
        _rlu, _rl, framerate, path, run = "sec",0.0,0.0,"", None

        # Check to see if the directory is configured
        try:
            _dir = os.environ['PYWFOM_DIR']
            _ = os.mkdir(_dir) if not os.path.exists(_dir) else None
            dt = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            path = _dir + '/' + dt
        except KeyError:
            errors.append("PYWFOM_DIR is not declared in the PATH")

        # Check run settings
        for key in ['run_length', 'run_length_unit', 'number_of_runs']:
            if key not in self.file:
                errors.append(f"{key} is missing from file settings")
            elif key == 'run_length':
                _rl = self.file['run_length']
            elif key == 'run_length_unit':
                _rlu = self.file['run_length_unit']

        _run_dur = {"sec":1.0,"min":60.0,"hr":3600.0}[_rlu]*float(_rl)
        # Check camera settings
        if len(self.cameras) == 0:
            errors.append("No cameras added.")
        framerate = [cam.json()['framerate'] for cam in self.cameras if cam.json()['primary']]
        if len(framerate) > 1:
            errors.append("More than one primary camera indicated.")
        elif len(framerate) == 0:
            framerate = 0.0
            errors.append("A primary camera must be indicated")
        else:
            framerate = framerate[0]


        for key in ['name', 'username', 'mouse']:
            if not getattr(self, key):
                errors.append(f"{key} was not specified")

        return path, int(framerate*_run_dur), errors

    def start_acquisition(self):

        print("Starting an acquisition")

        _path, _num_frms, _errors = self._check_system_settings()

        if len(_errors) > 0:
            print("\nERROR: Could not start acquisition due to the following errors:")
            [print(f"   * {err}") for err in _errors]
            print('')
            return False, _errors

        # Create save directory
        os.mkdir(_path)

        for cam in self.cameras:
            cam.acquiring = True

        for i in tqdm(range(int(self.file['number_of_runs'])), unit="run"):

            run = self._create_run()

            if not run:
                break
            else:
                os.mkdir(_path+f"/run{i}")
            for j in tqdm(range(_num_frms), leave=False, unit="frame"):
                # Place latest frame from each camera in dict
                frames = {
                    f"{cam.id}":cam.acquired_frames.get() for cam in self.cameras
                }
                # Create thread arguments
                args = (f'{_path}/run{i}/frame{j}.npz', frames, run)
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
            config = models.Configuration.objects(name=self.name).get() if self.name else None
            return models.Run(mouse=mouse,user=user,configuration=config,frames=[], timestamp=datetime.datetime.now())
        except Exception as e:
            traceback.print_exc()
            return None

    def _write_to_file(self, fname, frames, run):
        np.savez(fname, **frames)
        frame = models.Frame(file=fname)
        frame.save()
        run.frames.append(frame)

    def get_acquisition_status(self):
        return self.acquiring

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
    system.get_acquisition()

@api.route('/system/acquisition', methods=["DELETE"])
def stop_acquisition():
    return "Success", 200

@api.route('/system/acquisition', methods=['POST'])
def start_acquisition():
    result, errors = system.start_acquisition()
    if not result:
        return jsonify(errors), 404
    else:
        return "Success", 200
