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
    run_simple('localhost', 5000, SessionMiddleware(app, {'session.type':
      'file'}), use_debugger=True)

if __name__ == "__main__":
    logging.getLogger('peewee').setLevel(logging.INFO)
    logging.basicConfig(level=logging.DEBUG)

    manager.run()

