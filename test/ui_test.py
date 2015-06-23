from spacewiki.app import app
from spacewiki import model
import unittest
import tempfile

class UiTestCase(unittest.TestCase):
    def setUp(self):
        app.config['DATABASE'] = 'sqlite:///'+tempfile.mkdtemp()+'/test.sqlite3'
        with app.app_context():
          model.syncdb()
        self.app = app.test_client()

    def test_index(self):
        self.assertEqual(self.app.get('/').status_code, 200)

    def test_no_page(self):
        self.assertEqual(self.app.get('/missing-page').status_code, 200)

    def test_all_pages(self):
        self.assertEqual(self.app.get('/.all-pages').status_code, 200)

    def test_edit(self):
        self.assertEqual(self.app.get('/index/edit').status_code, 200)
