from spacewiki.app import create_app
from spacewiki import model
from spacewiki.test import create_test_app
from spacewiki.auth import tripcodes
import unittest

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self._app = create_test_app()
        with self._app.app_context():
            model.syncdb()
        self.app = self._app.test_client()

    def test_index(self):
        self.assertEqual(self.app.get('/').status_code, 404)
        newPage = model.Page.create(slug='index', title='Index')
        with (self._app.app_context()):
            newPage.newRevision('', '', tripcodes.new_anon_user())

        self._app.config['INDEX_PAGE'] = 'test'
        self.assertEqual(self.app.get('/').status_code, 404)
        self.assertEqual(self.app.get('/index').status_code, 200)

        newPage = model.Page.create(slug='test', title='Test')
        with (self._app.app_context()):
            newPage.newRevision('', '', tripcodes.new_anon_user())

        self.assertEqual(self.app.get('/').status_code, 200)

    def test_content_type_responses(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual('application/json', resp.headers['Content-Type'])

        resp = self.app.get('/', headers={'Accept': 'text/html'})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual('text/html', resp.headers['Content-Type'])

        newPage = model.Page.create(slug='index', title='Index')
        with (self._app.app_context()):
            newPage.newRevision('', '', tripcodes.new_anon_user())

        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual('application/json', resp.headers['Content-Type'])

        resp = self.app.get('/', headers={'Accept': 'text/html'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual('text/html', resp.headers['Content-Type'])

    def test_identities(self):
        resp = self.app.get('/_/identity/')
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get('/_/identity/logout')
        self.assertEqual(resp.status_code, 200)
