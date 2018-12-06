import os

VERSION = (0, 2)
VERSION_STRING = '.'.join([str(i) for i in VERSION])
SERVER_STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'server')
THEME_ROOT = os.path.join(os.path.dirname(__file__), 'theme')
