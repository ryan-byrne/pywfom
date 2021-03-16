from flask import Flask, send_from_directory, render_template
import os, argparse

from flask import Flask, request, jsonify, Response, Blueprint
import cv2, pywfom

from pywfom.server.api import api


"""

"""

#@app.route('/')
#def serve():
#    return render_template('index.html')

SECRET_KEY = os.urandom(12).hex()

def test():
    app = Flask('pywfom')
    app.secret_key = SECRET_KEY
    app.register_blueprint(api, url_prefix='/api')
    app.run(debug=True)

def main():
    TEMPLATE_FOLDER = os.path.dirname(pywfom.__file__)+"/pywfom/client/build"
    app = Flask( 'pywfom',
        template_folder=TEMPLATE_FOLDER,
        static_folder='client/build/static'
    )
    app.secret_key = SECRET_KEY
    app.register_blueprint(api, url_prefix='/api')
    app.run(debug=True)
