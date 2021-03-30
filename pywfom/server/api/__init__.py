from flask import Blueprint

api = Blueprint("api", __name__)

from . import settings as api_settings
from . import feed as api_feed
from . import devices as api_devices
from . import file as api_file
