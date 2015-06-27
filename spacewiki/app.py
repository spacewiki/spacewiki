#!/usr/bin/env python
from argparse import ArgumentParser
from beaker.middleware import SessionMiddleware
from flask import Flask, g, render_template, request, redirect, Response, current_app
import logging
import peewee
import tempfile
import werkzeug
import werkzeug.exceptions

import model
import context
import uploads
import pages
import history
import specials

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config.from_object('spacewiki.settings')
app.register_blueprint(context.bp)
app.register_blueprint(model.bp)
app.register_blueprint(uploads.bp)
app.register_blueprint(pages.bp)
app.register_blueprint(history.bp)
app.register_blueprint(specials.bp)

if app.config['TEMP_DIR'] is None:
    app.config['TEMP_DIR'] = tempfile.mkdtemp(prefix='spacewiki')

app.wsgi_app = SessionMiddleware(app.wsgi_app, {
  'session.type': 'file',
  'session.cookie_expires': False,
  'session.data_dir': app.config['TEMP_DIR']
})

if app.config['ADMIN_EMAILS']:
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
        'spacewiki@localhost',
        app.config['ADMIN_EMAILS'], 'SpaceWiki error')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
