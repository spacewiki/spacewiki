"""Use this module as your wsgi application"""
import logging
import sys

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

from spacewiki.app import app as application #pylint: disable=unused-import
