import logging
from threading import Lock
from spacewiki.hosted import model
from flask import current_app, session, request
from flask_login import current_user, login_user
import peewee
import spacewiki.app
import spacewiki.model
import spacewiki.auth

def db_name_for_subdomain(domain):
    try:
        space = model.Space.get(model.Space.domain == domain)
        return 'spacewiki_site_%s'%(space.slack_team_id.lower())
    except peewee.DoesNotExist:
        return None

def db_url_for_subdomain(domain):
    db_name = db_name_for_subdomain(domain)
    if db_name is None:
        return None
    return current_app.config['SPACE_DB_URL_PATTERN'] % (db_name)

def confirm_logged_in():
    common_user = session.get('_spacewikiio_auth_id', None)
    if common_user is not None:
        del session['_spacewikiio_auth_id']
        try:
            u = spacewiki.model.Identity.get(spacewiki.model.Identity.auth_id ==
                    common_user, spacewiki.model.Identity.auth_type == 'slack')
            login_user(u)
        except peewee.DoesNotExist:
            pass
    if not current_user.is_authenticated:
        spacewiki.auth.LOGIN_MANAGER.unauthorized()

def failed_auth():
    import app, routes
    hostedApp = app.create_app()
    hostedApp.config['LOGIN_NEEDED'] = True
    logging.debug("redirecting to failed app")
    return render_template('private.html')

def make_wiki_app(subdomain):
    import app
    hostedApp = app.create_app()
    with hostedApp.app_context():
        model.get_db()
        db_url = db_url_for_subdomain(subdomain)
        if db_url is None:
            logging.info("Spacewiki is not yet configured for %s.", subdomain)
            hostedApp.config['DEADSPACE'] = True
            return hostedApp
    app = spacewiki.app.create_app()
    app.before_request(confirm_logged_in)
    app.secret_key = hostedApp.secret_key
    app.config['DATABASE_URL'] = db_url
    app.config['SITE_NAME'] = subdomain
    app.config['UPLOAD_PATH'] = '/srv/spacewiki/uploads/%s'%(subdomain)
    app.config['ASSETS_CACHE'] = '/tmp/'
    app.logger.setLevel(logging.DEBUG)
    spacewiki.auth.LOGIN_MANAGER.unauthorized_handler(failed_auth)
    with app.app_context():
        spacewiki.model.syncdb()
    return app


class SubdomainDispatcher(object):
    def __init__(self, domain, create_app, create_default_app):
        self.domain = domain
        self.create_app = create_app
        self.create_default_app = create_default_app
        self.lock = Lock()
        self.instances = {}

    def get_application(self, host):
        logging.info("Got request for %s while serving %s", host, self.domain)
        host = host.split(':')[0]

        if not host.endswith(self.domain):
            return self.create_default_app()

        subdomain = host[:-len(self.domain)].rstrip('.')

        if subdomain == '':
            return self.create_default_app()

        with self.lock:
            app = self.instances.get(subdomain)
            if app is None:
                logging.info("Booting new application for %s", host)
                app = self.create_app(subdomain)
                self.instances[subdomain] = app
            return app

    def __call__(self, environ, start_response):
        app = self.get_application(environ['HTTP_HOST'])
        return app(environ, start_response)
