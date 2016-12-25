from spacewiki.app import create_app
from spacewiki import model
from spacewiki.test import create_test_app
import unittest

class UiTestCase(unittest.TestCase):
    def setUp(self):
        self._app = create_test_app()
        with self._app.app_context():
            model.syncdb()
        self.app = self._app.test_client()

    def test_index(self):
        self.assertEqual(self.app.get('/').status_code, 200)

    def test_no_page(self):
        self.assertEqual(self.app.get('/missing-page').status_code, 200)

    def test_all_pages(self):
        self.assertEqual(self.app.get('/.all-pages').status_code, 200)

    def test_edit(self):
        self.assertEqual(self.app.get('/index/edit').status_code, 200)
