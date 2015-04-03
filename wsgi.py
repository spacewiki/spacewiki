import logging
import sys

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

from app import app as application
