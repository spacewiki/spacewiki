from spacewiki.app import create_app
import tempfile

def create_test_app():
    app = create_app(False)
    app.config['DATABASE_URL'] = 'sqlite:///'+tempfile.mkdtemp()+'/test.sqlite3'
    return app
