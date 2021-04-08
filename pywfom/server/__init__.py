from flask import Flask
from mongoengine import connect, disconnect
import os

from .api import api

app = Flask('pywfom')
app.secret_key = os.urandom(12).hex()
app.register_blueprint(api, url_prefix='/api')

# TODO: Get credentials from HTTP
#pwd = os.environ['MONGODB_PASSWORD']

print('Connecting to MongoDB...')
# TODO: Add individual credentials
connect(host="mongodb://localhost:27017/pywfom0")

def run_server():
    app.run(debug=True)
    print('Disconnecting from MongoDB')
    disconnect()

def test_server():
    print('test server')
