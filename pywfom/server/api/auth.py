from flask import jsonify, Blueprint, request
import json

from . import api
from .system import system
from .. import models

@api.route('/auth/user/<username>')
def get_user(username):
    return "Hello User", 200

@api.route('/auth/register',methods=['POST'])
def register_user():
    data = request.get_json()
    keys = ['password','repassword','email','username','config']
    diff = [key for key in keys if key not in data.keys()]
    if len(diff) > 0:
        return f"Missing {', '.join(diff)}", 404
    elif data['password'] != data['repassword']:
        return "Passwords must match", 404
    elif len(models.User.objects(username=data['username'])) > 0:
        return f"User {data['username']} already exists", 404
    else:
        config = models.Configuration.objects(name=data['config']).get()
        user = models.User(username=data['username'], password=data['password'],default=config, configurations=[config])
        user.save()
        resp = json.loads(config.to_json())
        resp['username'] = data['username']
        return jsonify(resp)

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = models.User.objects(username=data['username'], password=data['password'])
    if len(user) == 0:
        return "Could not find a user with that name and password", 400
    else:
        system.username = data['username']
        return jsonify( system.get() )
