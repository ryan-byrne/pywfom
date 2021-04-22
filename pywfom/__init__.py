import argparse, json, getpass

from .server import start, develop, test
from .server.api.system import system

def _get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['start', 'develop', 'view', 'test'])
    parser.add_argument('--user', nargs='?')
    parser.add_argument('path', nargs="?", default="")
    return parser.parse_args()

def main():

    args = _get_arguments()

    if args.path != "":
        system.set_from_path(args.path)
    elif args.user:
        system.username = args.user
    if args.command == 'develop':
        develop()
    elif args.command == 'test':
        test()
    elif args.command == 'acquire':
        system.set_from_file('/Users/rbyrne/projects/pywfom/config.json')
        e = system.start_acquisition()
    else:
        start()
