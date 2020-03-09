

Settings
========

Naming Conventions
------------------

All settings should be uppercase. If a setting has no prefix or the prefix
``DEFAULT_`` you are free to change them. If a setting is prefixed ``CORE_`` it
is used to implement flamingo core features.

For example the variable ``CORE_PLUGINS`` holds a list of plugins that
implement parts of the meta data handling, handling of static files, hooks etc.
If you change this list, you should know what you are doing.

``DEFAULT_PLUGINS`` holds a selection of plugins the most users will need. If
you don't need them, you are free to clear or modify this list.

``PLUGINS`` holds a list of user activated plugins and is empty by default.

Overlaying Settings
-------------------

Most of flamingo command line tools come with an option ``-s`` for settings,
which can be one or more python files.

Let's say you have two settings files named ``settings.py`` und ``debug.py``.

.. code-block:: python

    # settings.py

    DEBUG = False

    PLUGINS = [
        'plugin1',
        'plugin2',
    ]


.. code-block:: python

    # debug.py

    DEBUG = True

    PLUGINS.append('debug_plugin')


If you call flamingo ``flamingo build -s settings.py debug.py``, ``debug.py``
will override ``settings.py`` like this:


.. code-block:: python

    # settings.py + debug.py

    DEBUG = True

    PLUGINS = [
        'plugin1',
        'plugin2',
        'debug_plugin',
    ]


Default Settings
----------------

Paths
~~~~~

.. data::

    CONTENT_ROOT = 'content'

    flamingo will search for content here recursivly

.. data::

    CONTENT_PATHS = []

    if set, flamingo will only parse the defined paths

.. data::

    OUTPUT_ROOT = 'output'

    flamingo will write the rendered HTML here

.. data::

    MEDIA_ROOT = 'output/media'

    flamingo will copy all media files used in content objects here

.. data::

    STATIC_ROOT = 'output/static'

    flamingo will copy all static files of activated themes here

Plugins
~~~~~~~

.. data::

    CORE_PLUGINS = [
        'flamingo.core.plugins.MetaDataProcessor',
        'flamingo.core.plugins.Hooks',
        'flamingo.core.plugins.Media',
        'flamingo.core.plugins.Static',
    ]

    these plugins implement basic flamingo features

    you can change this list if you are a developer and know what you are
    doing

.. data::

    DEFAULT_PLUGINS = [
        'flamingo.plugins.HTML',
        'flamingo.plugins.Yaml',
        'flamingo.plugins.reStructuredText',
        'flamingo.plugins.rstInclude',
        'flamingo.plugins.rstImage',
        'flamingo.plugins.rstFile',
    ]

    these plugins are the default selection of flaming plugins, the most users
    will need

    you are free to change this list

.. data::

    PLUGINS = []

    list of user installed plugins

.. data::

    CACHE_HOOKS = True

    control wether hooks should re discoverd on every hook run


Parsing
~~~~~~~

.. data::

    USE_CHARDET = False

    if enabled, `chardet <https://pypi.org/project/chardet/>`__ gets used to
    detect file types while parsing content files

.. data::

    FOLLOW_LINKS = True

    control if flamingo should follow filesystem links while searching for
    content files

.. data::

    DEDENT_INPUT = False

    control if flamingo should try to dedent a content file while parsing

.. data::

    HTML_PARSER_RAW_HTML = False

    if set to True the HTML parser won't process the HTML content of html
    content files


Templating
~~~~~~~~~~

.. data::

    TEMPLATING_ENGINE = 'flamingo.core.templating.Jinja2'

.. data::

    PRE_RENDER_CONTENT = True

    if set to True, templating syntax in content files is available

.. data::

    CORE_THEME_PATHS = [
        flamingo.THEME_ROOT,
    ]

.. data::

    THEME_PATHS = []

.. data::

    DEFAULT_TEMPLATE = 'page.html'

.. data::

    DEFAULT_PAGINATION = 25

.. data::

    EXTRA_CONTEXT = {}
