from webassets.loaders import YAMLLoader
from flask_assets import Environment, Bundle

ASSETS = Environment()

ASSETS.from_yaml('assets.yml')
