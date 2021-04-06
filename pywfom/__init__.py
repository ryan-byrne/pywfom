from flask import Flask, render_template
import argparse, os, json, webbrowser

from pywfom.server import run_server, test_server

def _get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['start', 'test'])
    parser.add_argument('path', nargs="?", default="")
    return parser.parse_args()

def main():
    args = _get_arguments()
    if args.command == 'test':
        test_server()
    elif args.command == 'start':
        run_server()
