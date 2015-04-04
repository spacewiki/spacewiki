"""Spacewiki settings"""
DATABASE = 'spacewiki.sqlite3'
SITE_NAME = 'SpaceWiki'
INDEX_PAGE = 'Index'

try:
    from local_settings import * #pylint: disable=unused-wildcard-import,wildcard-import
except ImportError:
    pass
