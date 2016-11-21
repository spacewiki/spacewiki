#!/usr/bin/env python
from flask.ext.script import Manager, Shell, Server
from spacewiki.hosted import app, model
import logging
import colorlog

APP = app.create_app()
MANAGER = Manager(APP)
MANAGER.add_command('shell', Shell())
MANAGER.add_command('runserver', Server())

@MANAGER.command
def reset():
    model.get_db()
    model.Space.delete()
    syncdb()

@MANAGER.command
def syncdb():
    model.get_db()
    model.ADMIN_DATABASE.create_tables([model.Space], True)

if __name__ == "__main__":
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(name)s:%(message)s'))
    logging.root.addHandler(handler)
    APP.logger.setLevel(logging.DEBUG)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    logging.getLogger('http').setLevel(logging.WARNING)
    logging.getLogger('peewee').setLevel(logging.INFO)
    logging.root.setLevel(logging.DEBUG)

    MANAGER.run()
