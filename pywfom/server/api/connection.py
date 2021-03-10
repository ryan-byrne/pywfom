from pywfom.server.api import api 

@app.route('/api/connection', methods=['GET'])
def connection_state():
    pass

@app.route('/api/connection', methods=['POST'])
def connection_command():
    pass
