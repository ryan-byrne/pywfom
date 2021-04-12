from flask import Flask, render_template
from mongoengine import connect, disconnect
import os, threading, webbrowser, pywfom
import numpy as np

from .api import api
from . import models

PATH_TO_PAGE = os.path.join(pywfom.__path__[0], "client/build/")

app = Flask('pywfom', static_folder=PATH_TO_PAGE+"/static", template_folder=PATH_TO_PAGE)
app.secret_key = os.urandom(12).hex()
app.register_blueprint(api, url_prefix='/api')

print('Connecting to MongoDB...')
connect(host="mongodb://localhost:27017/pywfom0")

@app.route('/')
def serve_page():
    return render_template('index.html')

def start():
    app.run(debug=True)
    print('Disconnecting from MongoDB')
    disconnect()
