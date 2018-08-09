import argparse
import os

from . import db
from . import shell

def main():
    defaultdb = os.path.join(os.path.expanduser('~'), ".bbc.db")
    parser = argparse.ArgumentParser()
    parser.add_argument('db', nargs='?', default=defaultdb, help="path of database file to use. Default: %(default)s")
    args = parser.parse_args()
    shell.run(db=db.DB(args.db))
