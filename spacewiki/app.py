"""SpaceWiki Flask application"""

from flask import Flask
from flask_assets import Environment, Bundle

from spacewiki import context, model, \
        uploads,  assets, auth, middleware, api

def create_app(with_config=True):
    APP = Flask(__name__,
                static_folder='../static')

    APP.config.setdefault('INDEX_PAGE', 'index')

    if with_config:
        APP.config.from_object('spacewiki.settings')

    if 'LOG_CONFIG' in APP.config:
        logging.config.dictConfig(APP.config['LOG_CONFIG'])

    APP.register_blueprint(context.BLUEPRINT)
    APP.register_blueprint(model.BLUEPRINT)
    APP.register_blueprint(uploads.BLUEPRINT)
    APP.register_blueprint(api.BLUEPRINT)
    APP.register_blueprint(auth.BLUEPRINT)
    APP.json_encoder = model.ModelEncoder
    assets.ASSETS.init_app(APP)
    auth.LOGIN_MANAGER.init_app(APP)

    APP.wsgi_app = middleware.ReverseProxied(APP.wsgi_app)

    return APP
