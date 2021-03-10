from . import api

# FIND
# FIND
@api.route('/api/find', methods=['GET'])
def find_devices():
    print(request.get_json())
    return jsonify("hello")
