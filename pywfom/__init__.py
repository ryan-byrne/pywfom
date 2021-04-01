from flask import Flask, render_template
import argparse, os, json, webbrowser

from .server.api import api
from pywfom.system import System

def _get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['start'])
    parser.add_argument('path', nargs="?", default="")
    return parser.parse_args()


def main():
    args = _get_arguments()
    app = Flask('pywfom')
    app.secret_key = os.urandom(12).hex()
    app.register_blueprint(api, url_prefix='/api')
    app.run(debug=True, use_reloader=False)
