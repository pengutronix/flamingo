PROJECT_NAME = 'flamingo'
CONTENT_ROOT = 'content'
OUTPUT_ROOT = 'output'

THEME_PATHS = [
    'theme',
]

PLUGINS = [
    'flamingo.plugins.rstPygments',
    'flamingo.plugins.Menu',
    'flamingo.plugins.ReadTheDocs',
    'flamingo.plugins.Git',
    'flamingo.plugins.Thumbnails',

    'plugins/rst_setting.py::rstSetting',
    'plugins/rst_table.py::rstTable',
]

POST_BUILD_LAYERS = [
    'overlay',
]
