import werkzeug.test
import unittest
import model
from app import app
import logging

class SoftlinkTestCase(unittest.TestCase):
    def setUp(self):
        model.setURI('sqlite:///:memory:')
        model.syncdb()
        model.Page.create(title='page', slug='page')
        model.Page.create(title='index', slug='index')
        self.app = app.test_client()

    def test_parser_no_refer(self):
        req = werkzeug.test.EnvironBuilder('/')
        resp = model.Page.parsePreviousSlugFromRequest(req, 'index')
        self.assertEqual(req.lastSlug, None)

    def test_parser_extern_refer(self):
        req = werkzeug.test.EnvironBuilder('/', headers={'Referer': \
            'http://example.com/'})
        resp = model.Page.parsePreviousSlugFromRequest(req, 'index')
        self.assertEqual(req.lastSlug, None)

    def test_parser_index_refer(self):
        req = werkzeug.test.EnvironBuilder('http://example.com/index', headers={'Referer': \
            'http://example.com/', 'Host': 'example.com'},
            base_url='http://example.com/').get_request()
        resp = model.Page.parsePreviousSlugFromRequest(req, 'index')
        self.assertEqual(req.lastSlug, 'index')

    def test_parser_page_refer(self):
        req = werkzeug.test.EnvironBuilder('http://example.com/index', headers={'Referer': \
            'http://example.com/referring-page', 'Host': 'example.com'},
            base_url='http://example.com/').get_request()
        resp = model.Page.parsePreviousSlugFromRequest(req, 'index')
        self.assertEqual(req.lastSlug, 'referring-page')

    def test_parser_subdir(self):
        req = werkzeug.test.EnvironBuilder('http://example.com/wiki/index', headers={'Referer': \
            'http://example.com/wiki/referring-page', 'Host': 'example.com'},
            base_url='http://example.com/wiki/').get_request()
        resp = model.Page.parsePreviousSlugFromRequest(req, 'index')
        self.assertEqual(req.lastSlug, 'referring-page')

    def test_parser_subdir(self):
        req = werkzeug.test.EnvironBuilder('http://example.com/wiki/index', headers={'Referer': \
            'http://example.com/wiki/referring-page', 'Host': 'example.com'},
            base_url='http://example.com/wiki/').get_request()
        resp = model.Page.parsePreviousSlugFromRequest(req, 'index')
        self.assertEqual(req.lastSlug, 'referring-page')
