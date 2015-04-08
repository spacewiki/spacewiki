import model
from app import app
import unittest
import tempfile
import hashlib
from StringIO import StringIO
import os

class UploadTestCase(unittest.TestCase):
    def setUp(self):
        app.config['UPLOAD_PATH'] = tempfile.mkdtemp()
        self.app = app.test_client()
        self.app.post('/index', data={'body': '', 'message': ''})

    def test_empty_upload(self):
      self.app.post('/index/attach', data={
        'file': (StringIO(''), 'empty.txt')
      })
      sha = hashlib.sha256()
      sha.update('')
      emptySha = sha.hexdigest()
      uploadedFile = os.path.join(app.config['UPLOAD_PATH'],
        emptySha+'-empty.txt')

      self.assertTrue(os.path.exists(uploadedFile))
      self.assertEqual(self.app.get('/index/file/empty_txt').data, '')

    def test_simple_upload(self):
      self.app.post('/index/attach', data={
        'file': (StringIO('FOOBAR'), 'foo.bar')
      })
      sha = hashlib.sha256()
      sha.update('FOOBAR')
      emptySha = sha.hexdigest()
      uploadedFile = os.path.join(app.config['UPLOAD_PATH'],
        emptySha+'-foo.bar')

      self.assertTrue(os.path.exists(uploadedFile))
      self.assertEqual(self.app.get('/index/file/foo_bar').data, 'FOOBAR')
