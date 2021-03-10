from pywfom.server.api import api

# SERVER
@api.route('/api/server', methods=['GET'])
def server_info():
    pass
