from flask import Flask, render_template
from mongoengine import connect, disconnect
import os, threading, webbrowser, pywfom, waitress
import numpy as np

from .api import api
from . import models

CLIENT_PATH = os.path.join(pywfom.__path__[0], "client/build/")

app = Flask('pywfom', static_folder=CLIENT_PATH+"/static", template_folder=CLIENT_PATH)
app.secret_key = os.urandom(12).hex()
app.register_blueprint(api, url_prefix='/api')

print('Connecting to MongoDB...')
connect(host="mongodb://localhost:27017/pywfom0")

@app.route('/')
def serve_page():
    return render_template('index.html')

def test():
    app.run(debug=True)
    print('Disconnecting from MongoDB')
    disconnect()

def start():
    waitress.serve(app, host="0.0.0.0", port=8080)
    print('Disconnecting from MongoDB')
    disconnect()
