from flask_assets import Environment
from webassets.filter import register_filter
from webassets_browserify import Browserify
import os.path

register_filter(Browserify)

ASSETS = Environment()

ASSETS.from_yaml(os.path.sep.join((os.path.dirname(__file__), '..',
    'assets.yml')))
