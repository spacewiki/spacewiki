from app import app
import unittest

class UiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        self.assertEqual(self.app.get('/').status_code, 200)

    def test_no_page(self):
        self.assertEqual(self.app.get('/missing-page').status_code, 200)

    def test_all_pages(self):
        self.assertEqual(self.app.get('/.all-pages').status_code, 200)

    def test_edit(self):
        self.assertEqual(self.app.get('/.edit/Index').status_code, 200)
        self.assertEqual(self.app.get('/.edit/').status_code, 404)
