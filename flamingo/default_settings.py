import flamingo

# plugins
CORE_PLUGINS = [
    'flamingo.core.plugins.MetaDataProcessor',
]

DEFAULT_PLUGINS = [
    'flamingo.core.plugins.HTML',
    'flamingo.core.plugins.reStructuredText',
    'flamingo.core.plugins.rstImage',
    'flamingo.core.plugins.rstFile',
]

PLUGINS = []

# templating
TEMPLATING_ENGINE = 'flamingo.core.templating.Jinja2'

CORE_THEME_PATHS = [
    flamingo.THEME_ROOT,
]

THEME_PATHS = []

DEFAULT_TEMPLATE = 'page.html'

DEFAULT_PAGINATION = 25

# content
CONTENT_ROOT = 'content'
CONTENT_PATHS = []

# output
OUTPUT_ROOT = 'output'
MEDIA_ROOT = 'output/media'
STATIC_ROOT = 'output/static'
