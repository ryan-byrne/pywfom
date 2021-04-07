from flask import Blueprint

api = Blueprint("api", __name__)

from . import system as api_system
from . import feed as api_feed
from . import devices as api_devices
from . import file as api_file
from . import acquisition as api_acquisition
