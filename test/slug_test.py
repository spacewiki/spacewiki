from spacewiki.model import SlugField
from spacewiki import model
import unittest
import hypothesis
import string
import tempfile
from hypothesis.extra.fakefactory import FakeFactory
from spacewiki.app import create_app
from playhouse.test_utils import test_database
from peewee import SqliteDatabase

test_db = SqliteDatabase(':memory:')

def makePath(s):
    return s.split('://', 1)[1].split('/', 1)[1]

Path = hypothesis.strategy(FakeFactory('url')).map(makePath)


class SlugTestCase(unittest.TestCase):
    def setUp(self):
        self._app = create_app()
        self._app.config['DATABASE_URL'] = 'sqlite:///:memory:'
        self.app = self._app.test_client()

    def test_split_title(self):
        self.assertEqual(SlugField.split_title('foo'), ('', 'foo'))
        self.assertEqual(SlugField.split_title('foo/bar'), ('foo', 'bar'))

    def test_mangle_slug(self):
        self.assertEqual(SlugField.mangle_full_slug('foo/bar', 'Bar'), ('foo/bar/', 'Bar'))
        self.assertEqual(SlugField.mangle_full_slug('foo/bar', 'Baz'), ('foo/bar/', 'Baz'))
        self.assertEqual(SlugField.mangle_full_slug('', 'foo/bar'), ('foo', 'bar'))

    def test_mid_edit_rename(self):
        with test_database(test_db, [model.Page, model.Revision, model.Identity]):
            self.app.post('/test2', data={
                'title': 'test2',
                'slug': 'test2',
                'body': '',
                'author': '',
                'message': ''
            })
            resp = self.app.post('/test2', data={
              'title': 'not-a-test',
              'slug': 'not-a-test',
              'body': '',
              'author': '',
              'message': ''
            })

            self.assertEqual(resp.status_code, 302)

            with self.assertRaises(model.Page.DoesNotExist):
                model.Page.get(slug='test2')
