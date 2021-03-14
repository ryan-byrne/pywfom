from flask import Flask, send_from_directory, render_template
import os, argparse

from flask import Flask, request, jsonify, Response, Blueprint
import cv2

from pywfom.server.api import api


"""
TEMPLATE_FOLDER = "/Users/rbyrne/projects/pywfom/env/lib/python3.9/site-packages/pywfom-0.0.1-py3.9.egg/pywfom/client/build"
app = Flask( 'pywfom',
    template_folder=TEMPLATE_FOLDER,
    static_folder='client/build/static'
)
"""

app = Flask('pywfom')
app.register_blueprint(api, url_prefix='/api')

#@app.route('/')
#def serve():
#    return render_template('index.html')

def main():
    app.run(debug=True)
