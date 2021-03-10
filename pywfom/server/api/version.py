from pywfom.server.api import api

# VERSION
@api.route('/api/version', methods=['GET'])
def version_info():
    pass
