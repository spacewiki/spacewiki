import werkzeug.test
import unittest
from spacewiki import model
from spacewiki.app import app
import logging
import hypothesis
import tempfile
import string
from hypothesis.extra.fakefactory import FakeFactory

def makePath(s):
    return s.split('://', 1)[1].split('/', 1)[1]

Path = hypothesis.strategy(FakeFactory('url')).map(makePath)

FullUrl = hypothesis.strategy(FakeFactory('url'))

Domain = hypothesis.strategy(FakeFactory('domain_name'))

class SoftlinkParsingTestCase(unittest.TestCase):
    @hypothesis.given(Path)
    def test_parser_no_refer(self, s):
        req = werkzeug.test.EnvironBuilder(path=s)
        resp = model.Page.parsePreviousSlugFromRequest(req, 'index')
        self.assertEqual(req.lastSlug, None)

    @hypothesis.given(Path, FullUrl)
    def test_parser_extern_refer(self, page, refer):
        req = werkzeug.test.EnvironBuilder(
            path=page,
            headers={
                'Referer': refer
            }
        )
        resp = model.Page.parsePreviousSlugFromRequest(req, 'index')
        self.assertEqual(req.lastSlug, None)

    @hypothesis.given(Path, Path, Domain, Path)
    def test_parser_page_refer(self, page, referPage, host, prefix):
        req = werkzeug.test.EnvironBuilder(
            path=prefix+page,
            headers={'Referer': 'http://'+host+prefix+referPage, 'Host': host},
            base_url='http://'+host+prefix
        ).get_request()
        resp = model.Page.parsePreviousSlugFromRequest(req, referPage)
        self.assertEqual(req.lastSlug, referPage)

class SoftlinkTestCase(unittest.TestCase):
    def setUp(self):
        app.config['DATABASE'] = 'sqlite:///'+tempfile.mkdtemp()+'/test.sqlite3'
        with app.app_context():
            model.syncdb()
            model.Page.create(title='page', slug='page')
            model.Page.create(title='index', slug='index')
        self.app = app.test_client()

    @hypothesis.given(Path, Path, Domain, Path)
    def test_create_softlink(self, src, dest, host, prefix):
        if src == dest:
            return

        self.app.get(
            prefix+dest,
            headers={
              'Referer': 'http://'+host+prefix+src,
              'Host': host
            },
            base_url = 'http://'+host+prefix
        )

        self.assertTrue(
          model.Softlink.select() \
            .join(model.Page, on=model.Softlink.src) \
            .where(
                model.Page.slug == src, 
            ).join(model.Page, on=model.Softlink.dest) \
            .where(
                model.Page.slug == dest,
            ).exists()
        )
