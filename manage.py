#!/usr/bin/env python
from flask.ext.script import Manager, Shell
import model
import logging

from app import app

manager = Manager(app)
manager.add_command("shell", Shell())
manager.add_command('db', model.MANAGER)

@manager.command
def runserver():
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app, use_debugger=True, use_reloader=True)

if __name__ == "__main__":
    logging.getLogger('peewee').setLevel(logging.INFO)
    logging.basicConfig(level=logging.DEBUG)

    manager.run()

