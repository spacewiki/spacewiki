from spacewiki.model import SlugField
from spacewiki import model
import unittest
import hypothesis
import string
import tempfile
from hypothesis.extra.fakefactory import FakeFactory
from spacewiki.app import APP as app

def makePath(s):
    return s.split('://', 1)[1].split('/', 1)[1]

Path = hypothesis.strategy(FakeFactory('url')).map(makePath)


class SlugTestCase(unittest.TestCase):
    def setUp(self):
        app.config['DATABASE'] = 'sqlite:///'+tempfile.mkdtemp()+'/test.sqlite3'
        with app.app_context():
            model.syncdb()
        self.app = app.test_client()

    def test_split_title(self):
        self.assertEqual(SlugField.split_title('foo'), ('', 'foo'))
        self.assertEqual(SlugField.split_title('foo/bar'), ('foo', 'bar'))

    def test_mangle_slug(self):
        self.assertEqual(SlugField.mangle_full_slug('foo/bar', 'Bar'), ('foo/bar/', 'Bar'))
        self.assertEqual(SlugField.mangle_full_slug('foo/bar', 'Baz'), ('foo/bar/', 'Baz'))
        self.assertEqual(SlugField.mangle_full_slug('', 'foo/bar'), ('foo/', 'bar'))

    def test_mid_edit_rename(self):
        resp = self.app.post('/test2', data={
          'title': 'not-a-test',
          'body': '',
          'author': '',
          'message': ''
        })

        self.assertEqual(resp.status_code, 302)

        with self.assertRaises(model.Page.DoesNotExist):
            model.Page.get(slug='test2')
