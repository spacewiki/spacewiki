#!/usr/bin/env python
from flask.ext.script import Manager, Shell
from spacewiki import model
import logging
import sys
import os.path

sys.path.append(os.path.dirname(__file__))

from spacewiki.app import APP

MANAGER = Manager(APP)
MANAGER.add_command("shell", Shell())
MANAGER.add_command('db', model.MANAGER)

@MANAGER.command
def runserver():
    """Runs an HTTP server on *:5000"""
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, APP, use_debugger=True, use_reloader=True)

if __name__ == "__main__":
    logging.getLogger('peewee').setLevel(logging.INFO)
    logging.basicConfig(level=logging.DEBUG)

    MANAGER.run()
