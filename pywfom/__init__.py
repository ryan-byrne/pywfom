import argparse, json

from .server import start

from .server.api.system import system

def _get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['start', 'test', 'view'])
    parser.add_argument('path', nargs="?", default="")
    return parser.parse_args()

def main():
    args = _get_arguments()
    if args.command == 'test':
        # TODO:
        print('test')
    elif args.command == 'start':
        system.set_from_path(args.path)
        start()
    elif args.command == 'view':
        # TODO:
        print('view')
