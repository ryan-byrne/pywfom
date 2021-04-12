from flask import jsonify, Blueprint, request
import json

from . import api
from .system import system
from .. import models

@api.route('/auth/user/<username>')
def get_user(username):
    return "Hello User", 200

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = models.User.objects(username=data['username'], password=data['password'])
    if len(user) == 0:
        return "Could not find a user with that name and password", 400
    else:
        system.username = data['username']
        return jsonify( system.get() )
