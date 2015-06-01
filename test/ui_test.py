from app import app
import model
import unittest

class UiTestCase(unittest.TestCase):
    def setUp(self):
        app.config['DATABASE'] = 'sqlite:///:memory:'
        with app.app_context():
          model.database.connect()
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
