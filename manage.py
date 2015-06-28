#!/usr/bin/env python
from flask.ext.script import Manager, Shell, Server
from spacewiki import model
import logging
import sys
import os.path

sys.path.append(os.path.dirname(__file__))

from spacewiki.app import APP

MANAGER = Manager(APP)
MANAGER.add_command('db', model.MANAGER)
MANAGER.add_command('runserver', Server())
MANAGER.add_command("shell", Shell())

if __name__ == "__main__":
    logging.getLogger('peewee').setLevel(logging.INFO)
    logging.basicConfig(level=logging.DEBUG)

    MANAGER.run()
