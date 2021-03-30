from flask import Flask, request, jsonify, Response, Blueprint, render_template
import cv2, os, argparse, pywfom

from pywfom.server.api import api

SECRET_KEY = os.urandom(12).hex()

def _get_arguments():
    parser = argparse.ArgumentParser(
        description="Command Line Interface for the pyWFOM System"
    )
    parser.add_argument('-t', '--test',
        dest='test', action='store_true', help="Run pyWFOM in Test Mode"
    )
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
        help="Run the API Server in Debugging Mode"
    )
    return parser.parse_args()

def main():

    args = _get_arguments()

    if args.test:
        app = Flask('pywfom')
    else:
        TEMPLATE_FOLDER = os.path.dirname(pywfom.__file__)+"/client/build"
        app = Flask( 'pywfom',
            template_folder=TEMPLATE_FOLDER,
            static_folder='client/build/static'
        )
        @app.route('/')
        def index():
            return render_template('index.html')

    app.secret_key = SECRET_KEY
    app.register_blueprint(api, url_prefix='/api')
    app.run(debug=args.debug)
