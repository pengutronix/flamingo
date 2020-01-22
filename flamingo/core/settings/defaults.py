import flamingo

# plugins / hooks
CORE_PLUGINS_PRE = [
    'flamingo.core.plugins.layers.PreBuildLayers',
    'flamingo.core.plugins.MetaDataDefaults',
]

DEFAULT_PLUGINS = [
    'flamingo.plugins.HTML',
    'flamingo.plugins.Yaml',
    'flamingo.plugins.reStructuredText',
    'flamingo.plugins.rstInclude',
    'flamingo.plugins.rstImage',
    'flamingo.plugins.rstFile',
]

PLUGINS = []

CORE_PLUGINS_POST = [
    'flamingo.core.plugins.Media',
    'flamingo.core.plugins.Static',
    'flamingo.core.plugins.layers.PostBuildLayers',
]

SKIP_HOOKS = []

# parsing
USE_CHARDET = False
DEDENT_INPUT = False
FOLLOW_LINKS = True
HTML_PARSER_RAW_HTML = False

# templating
TEMPLATING_ENGINE = 'flamingo.core.templating.Jinja2'
PRE_RENDER_CONTENT = True
EXTRA_CONTEXT = {}

CORE_THEME_PATHS = [
    flamingo.THEME_ROOT,
]

THEME_PATHS = []

DEFAULT_TEMPLATE = 'page.html'
DEFAULT_IMAGE_TEMPLATE = 'image.html'
DEFAULT_GALLERY_TEMPLATE = 'gallery.html'
DEFAULT_CODE_BLOCK_TEMPLATE = 'code-block.html'
DEFAULT_PAGINATION = 25

JINJA2_TRACEBACKS = True
JINJA2_TRACEBACKS_CONTEXT_LINES = 3
JINJA2_TRACEBACKS_FILTER_PYTHON_CODE = True
JINJA2_TRACEBACKS_PYGMENTS = True

# build
SKIP_FILE_OPERATIONS = False

# content
CONTENT_ROOT = 'content'
CONTENT_PATHS = []

# output
OUTPUT_ROOT = 'output'
MEDIA_ROOT = 'media'
STATIC_ROOT = 'output/static'

# layers
PRE_BUILD_LAYERS = []
POST_BUILD_LAYERS = []

# live-server
LIVE_SERVER_RUNNING = False
LIVE_SERVER_IGNORE_PREFIX = []
LIVE_SERVER_RESETUP_ON_CODE_CHANGE = False
