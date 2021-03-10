from pywfom.server.api import api

# LOGIN
@api.route('/api/login', methods=['POST'])
def api_login():
    pass

@api.route('/api/logout', methods=['POST'])
def api_logout():
    pass

@api.route('/api/currentuser', methods=['GET'])
def current_user():
    pass
