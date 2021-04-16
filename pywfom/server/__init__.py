from flask import Flask, render_template
from mongoengine import connect, disconnect
import os, threading, webbrowser, pywfom, waitress
import numpy as np

from .api import api
from . import models, viewer
from .api.system import system

CLIENT_PATH = os.path.join(pywfom.__path__[0], "client/build/")

app = Flask('pywfom', static_folder=os.path.join(CLIENT_PATH,"static"), template_folder=CLIENT_PATH)
app.secret_key = os.urandom(12).hex()
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(viewer.bp, url_prefix='/viewer')

print('Connecting to MongoDB...')
connect(host="mongodb://localhost:27017/pywfom0")

@app.route('/')
def serve_main():
    return render_template('index.html')

def develop():
    app.run(debug=True)
    print('Disconnecting from MongoDB')
    disconnect()

def test():
    system.mouse = "cm105"
    system.username = "ryan"
    system.set_from_file("/Users/rbyrne/projects/pywfom/config.json")
    system.start_acquisition()
    system.delete()

def start():
    waitress.serve(app, host="0.0.0.0", port=8080)
    print('Disconnecting from MongoDB')
    disconnect()
