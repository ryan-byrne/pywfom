from flask import Blueprint, jsonify
import json

from . import models

bp = Blueprint("viewer", __name__)

@bp.route('/runs/')
@bp.route('/runs/<user>')
def open_viewer(user=None):
    runs = []
    if user:
        user_id = models.User.objects(username=user).get()
        run_iter = models.Run.objects(user=user_id)
    else:
        run_iter = models.Run.objects()
    for run in run_iter:
        runs.append({
            "date":run.timestamp,
            "mouse":run.mouse.name,
            "config":json.loads(run.configuration.to_json())
        })
        print(run.mouse.name)
    return jsonify(runs)
