from flask_assets import Environment
from flask import Flask
from spacewiki.hosted import model, routes
from spacewiki.middleware import ReverseProxied
from slacker import Slacker
import peewee


def create_app():
    APP = Flask(__name__)
    APP.config.from_object('spacewiki.hosted.settings')
    ASSETS = Environment(APP)
    ASSETS.from_yaml("spacewiki-io-assets.yml")
    APP.secret_key = APP.config['SECRET_SESSION_KEY']
    APP.wsgi_app = ReverseProxied(APP.wsgi_app)

    APP.register_blueprint(routes.BLUEPRINT)
    APP.register_blueprint(model.BLUEPRINT)
    return APP
