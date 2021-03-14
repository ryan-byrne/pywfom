from flask import jsonify

from pywfom.server.api import api

@api.route('/directory/', methods=['GET'])
def api_directory():
    return(jsonify(directory="/pywfom/data"))
