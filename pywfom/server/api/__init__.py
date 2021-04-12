from flask import Blueprint

api = Blueprint("api", __name__)

from . import system as api_system
from . import feed as api_feed
from . import devices as api_devices
from . import db as api_db
from . import auth as api_auth
