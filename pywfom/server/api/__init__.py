from flask import Blueprint

api = Blueprint("api", __name__)

from . import settings as api_settings
from . import feed as api_feed
from . import find as api_find
