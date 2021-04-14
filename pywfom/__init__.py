import argparse, json, getpass

from .server import start, test
from .server.api.system import system

def _get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['start', 'test', 'view'])
    parser.add_argument('--user', nargs='?')
    parser.add_argument('path', nargs="?", default="")
    return parser.parse_args()

def main():

    args = _get_arguments()

    if args.path != "":
        system.set_from_path(args.path)
    elif args.user:
        pwd = getpass.getpass(f"Enter Password for {args.user}: ")
        system.set_from_user_default(args.user, pwd)

    if args.command == 'test':
        test()
    elif args.command == 'view':
        pass
    elif args.command == 'acquire':
        system.set_from_file('/Users/rbyrne/projects/pywfom/config.json')
        e = system.start_acquisition()
    else:
        start()
