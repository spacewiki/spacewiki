from flask_assets import Environment
from webassets.filter import register_filter
from webassets_browserify import Browserify

register_filter(Browserify)

ASSETS = Environment()

ASSETS.from_yaml('assets.yml')
