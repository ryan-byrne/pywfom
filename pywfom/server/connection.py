from pywfom.server.api import api

@api.route('/api/connection', methods=['GET'])
def connection_state():
    pass

@api.route('/api/connection', methods=['POST'])
def connection_command():
    pass
