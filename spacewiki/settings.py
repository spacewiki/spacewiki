"""Spacewiki settings"""
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///spacewiki.sqlite3')
SITE_NAME = 'SpaceWiki'
INDEX_PAGE = 'index'
UPLOAD_PATH = 'uploads'

ADMIN_EMAILS = None
TEMP_DIR = None

TWITTER_CARD_SITE = None

SECRET_SESSION_KEY = None

LOG_CONFIG = {
    'version': 1,
    'handlers': {
        'colorlog': {
            'class': 'colorlog.StreamHandler',
            'formatter': 'colorformat'
        }
    },
    'formatters': {
        'colorformat': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)s:%(name)s:%(message)s'
        }
    },
    'loggers': {
        'socketio': {'level': 'WARNING'},
        'engineio': {'level': 'WARNING'},
        'http': {'level': 'INFO'},
        'peewee': {'level': 'INFO'},
        'spacewiki.app': {'level': 'DEBUG'}
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['colorlog']
    }
}

try:
    from local_settings import *  # pylint: disable=unused-wildcard-import,wildcard-import
except ImportError:
    pass
