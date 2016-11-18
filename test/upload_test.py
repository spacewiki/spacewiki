from spacewiki import model
from spacewiki.app import APP as app
import unittest
import tempfile
import hashlib
from StringIO import StringIO
import os
from playhouse.test_utils import test_database
from peewee import SqliteDatabase

test_db = SqliteDatabase(':memory:')

class UploadTestCase(unittest.TestCase):
    def setUp(self):
        app.config['UPLOAD_PATH'] = tempfile.mkdtemp()
        self.app = app.test_client()

    def test_empty_upload(self):
        with test_database(test_db, [model.Attachment,
            model.AttachmentRevision, model.Page]):
          self.app.post('/index/attach', data={
            'file': (StringIO(''), 'empty.txt')
          })
          sha = hashlib.sha256()
          sha.update('')
          emptySha = sha.hexdigest()
          uploadedFile = os.path.join(app.config['UPLOAD_PATH'],
            model.Attachment.hashPath(emptySha, 'empty.txt'))

          self.assertTrue(os.path.exists(uploadedFile))
          resp = self.app.get('/index/file/empty.txt')
          self.assertEqual(resp.status_code, 200)
          self.assertEqual(resp.data, '')

    def test_simple_upload(self):
        with test_database(test_db, [model.Attachment,
            model.AttachmentRevision, model.Page]):
          self.app.post('/index/attach', data={
            'file': (StringIO('FOOBAR'), 'foo.bar')
          })
          sha = hashlib.sha256()
          sha.update('FOOBAR')
          emptySha = sha.hexdigest()
          uploadedFile = os.path.join(app.config['UPLOAD_PATH'],
            model.Attachment.hashPath(emptySha, 'foo.bar'))

          self.assertTrue(os.path.exists(uploadedFile))
          resp = self.app.get('/index/file/foo.bar')
          self.assertEqual(resp.status_code, 200)
          self.assertEqual(resp.data, 'FOOBAR')

    def test_upload_upate(self):
        with test_database(test_db, [model.Attachment,
            model.AttachmentRevision, model.Page]):
            self.app.post('/index/attach', data={
              'file': (StringIO('FOOBAR'), 'foo.bar')
            })
            self.app.post('/index/attach', data={
              'file': (StringIO('BARFOO'), 'foo.bar')
            })
            sha = hashlib.sha256()
            sha.update('BARFOO')
            emptySha = sha.hexdigest()
            uploadedFile = os.path.join(app.config['UPLOAD_PATH'],
              model.Attachment.hashPath(emptySha, 'foo.bar'))

            self.assertTrue(os.path.exists(uploadedFile))
            resp = self.app.get('/index/file/foo.bar')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.data, 'BARFOO')
