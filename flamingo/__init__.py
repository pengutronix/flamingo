import os

from flamingo.core.plugins.hooks import hook  # NOQA

VERSION = (0, 10, 1)
_dirname = os.path.dirname(__file__)
VERSION_STRING = '.'.join([str(i) for i in VERSION])
SERVER_STATIC_ROOT = os.path.join(_dirname, 'server/static')
THEME_ROOT = os.path.join(_dirname, 'theme')
PROJECT_TEMPLATES_ROOT = os.path.join(_dirname, 'project_templates')

PROJECT_TEMPLATES_DATA_PATH = os.path.join(PROJECT_TEMPLATES_ROOT,
                                           'data.ini')
