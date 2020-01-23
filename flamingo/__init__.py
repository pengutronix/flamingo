import os

from flamingo.core.plugins.plugin_manager import hook  # NOQA

_dirname = os.path.dirname(__file__)

VERSION = (0, 12, 1)
VERSION_STRING = '.'.join([str(i) for i in VERSION])
THEME_ROOT = os.path.join(_dirname, 'theme')
PROJECT_TEMPLATES_ROOT = os.path.join(_dirname, 'project_templates')

PROJECT_TEMPLATES_DATA_PATH = os.path.join(PROJECT_TEMPLATES_ROOT,
                                           'data.ini')
