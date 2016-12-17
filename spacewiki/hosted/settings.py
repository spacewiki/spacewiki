SLACK_KEY = None
SLACK_SECRET = None
SPACE_DB_URL_PATTERN = 'postgres:///%s'
ADMIN_DB_URL = 'postgres:///spacewiki'
DEADSPACE = False
LOGIN_NEEDED = False

try:
    from local_hosted_settings import *
except ImportError:
    pass
