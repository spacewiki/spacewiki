from flask_assets import Environment

ASSETS = Environment()

ASSETS.from_yaml('assets.yml')
