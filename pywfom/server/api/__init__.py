from flask import Blueprint

api = Blueprint("api", __name__)

from . import configure as api_configure
from . import directory as api_directory
from . import feed as api_feed
from . import find as api_find
