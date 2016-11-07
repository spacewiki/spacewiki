"""Spacewiki settings"""
import os

DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///spacewiki.sqlite3')
SITE_NAME = 'SpaceWiki'
INDEX_PAGE = 'index'
UPLOAD_PATH = 'uploads'

ADMIN_EMAILS = None
TEMP_DIR = None

TWITTER_CARD_SITE = None

try:
    from local_settings import *  # pylint: disable=unused-wildcard-import,wildcard-import
except ImportError:
    pass
