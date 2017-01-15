from spacewiki.test import create_test_app
import werkzeug.test
import unittest
from spacewiki import model
from spacewiki.app import create_app
from spacewiki.auth import tripcodes
import logging
from hypothesis import given, assume
from hypothesis.strategies import text, composite, lists
import tempfile
import string
from playhouse.test_utils import test_database
from peewee import SqliteDatabase

test_db = SqliteDatabase(':memory:')

@composite
def FullUrl(draw):
    return 'https://'+draw(Domain())+'/'+draw(Path())

@composite
def Path(draw):
    return '/'.join(draw(lists(PathSegment())))

@composite
def PathSegment(draw):
    return draw(text(alphabet=string.letters, min_size=1))

@composite
def Domain(draw):
    return '.'.join(draw(lists(DomainSegment(), min_size=2)))

@composite
def DomainSegment(draw):
    return draw(text(alphabet=string.letters,min_size=1))+draw(text(alphabet=string.letters+string.digits))

class SoftlinkParsingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()

    @given(Path())
    def test_parser_no_refer(self, s):
        req = werkzeug.test.EnvironBuilder(path=s)
        resp = model.Page.parsePreviousSlugFromRequest(req, 'index')
        self.assertEqual(req.lastSlug, None)

    @given(Path(), FullUrl())
    def test_parser_extern_refer(self, page, refer):
        req = werkzeug.test.EnvironBuilder(
            path=page,
            headers={
                'Referer': refer
            }
        )
        resp = model.Page.parsePreviousSlugFromRequest(req, 'index')
        self.assertEqual(req.lastSlug, None)

    @given(Path(), Path(), Domain(), Path())
    def test_parser_page_refer(self, page, referPage, host, prefix):
        with self.app.app_context():
            req = werkzeug.test.EnvironBuilder(
                path=prefix+page,
                headers={'Referer': '/'.join(('http://'+host, prefix, referPage)), 'Host': host},
                base_url='http://'+'/'.join((host, prefix))
            ).get_request()
            resp = model.Page.parsePreviousSlugFromRequest(req, referPage)
            self.assertEqual(req.lastSlug, referPage)

class SoftlinkTestCase(unittest.TestCase):
    def setUp(self):
        self._app = create_test_app()
        self.app = self._app.test_client()

    @given(Path(), Path(), Domain())
    def test_create_softlink(self, src, dest, host):
        assume(src != dest)
        assume(src != '' and dest != '')

        with test_database(test_db, [model.Softlink, model.Page, model.Revision,
            model.Identity, model.Attachment]):
            startPage = model.Page.create(title='index', slug=src)
            endPage = model.Page.create(title='page', slug=dest)
            with self._app.app_context():
                startPage.newRevision('', '', tripcodes.new_anon_user())
                endPage.newRevision('', '', tripcodes.new_anon_user())

            req = self.app.get(
                '/'+dest,
                headers={
                  'Referer': 'http://'+host+'/'+src,
                },
                base_url = 'http://'+host+'/'
            )

            self.assertEqual(req.status_code, 200)

            self.assertTrue(
              model.Softlink.select() \
                .where(
                    model.Softlink.src == startPage,
                    model.Softlink.dest == endPage
                ).exists()
            )
