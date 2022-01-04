

Settings
========

Flamingo manages its settings in plain python files. Settings are project
specific and hold information like where the content files are stored, where
the output should be written to and which plugins are installed.


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

Let's say you have two settings files named ``settings.py`` and ``debug.py``.

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

.. setting::
    :name: DEFAULT_PLUGINS
    :path: flamingo.core.settings.defaults.DEFAULT_PLUGINS

    this are the default plugins

.. setting::
    :name: CONTENT_ROOT
    :path: flamingo.core.settings.defaults.CONTENT_ROOT

    flamingo will search for content here recursivly

.. setting::
    :name: CONTENT_PATHS
    :path: flamingo.core.settings.defaults.CONTENT_PATHS

    if set, flamingo will only parse the defined paths

.. setting::
    :name: OUTPUT_ROOT
    :path: flamingo.core.settings.defaults.OUTPUT_ROOT

    flamingo will write the rendered HTML here

.. setting::
    :name: MEDIA_ROOT
    :path: flamingo.core.settings.defaults.MEDIA_ROOT

    flamingo will copy all media files used in content objects here

.. setting::
    :name: STATIC_ROOT
    :path: flamingo.core.settings.defaults.STATIC_ROOT

    flamingo will copy all static files of activated themes here


Plugins
~~~~~~~

.. setting::
    :name: CORE_PLUGINS_PRE
    :path: flamingo.core.settings.defaults.CORE_PLUGINS_PRE

    these plugins implement basic flamingo features

    you can change this list if you are a developer and know what you are
    doing

.. setting::
    :name: DEFAULT_PLUGINS
    :path: flamingo.core.settings.defaults.DEFAULT_PLUGINS

    these plugins are the default selection of flaming plugins, the most users
    will need

    you are free to change this list

.. setting::
    :name: PLUGINS
    :path: flamingo.core.settings.defaults.PLUGINS

    list of user installed plugins

.. setting::
    :name: CORE_PLUGINS_POST
    :path: flamingo.core.settings.defaults.CORE_PLUGINS_POST

    these plugins implement basic flamingo features

    you can change this list if you are a developer and know what you are
    doing

.. setting::
    :name: SKIP_HOOKS
    :path: flamingo.core.settings.defaults.SKIP_HOOKS


Parsing
~~~~~~~

.. setting::
    :name: USE_CHARDET
    :path: flamingo.core.settings.defaults.USE_CHARDET

    if enabled, `chardet <https://pypi.org/project/chardet/>`__ gets used to
    detect file types while parsing content files

.. setting::
    :name: FOLLOW_LINKS
    :path: flamingo.core.settings.defaults.FOLLOW_LINKS

    control if flamingo should follow filesystem links while searching for
    content files

.. setting::
    :name: DEDENT_INPUT
    :path: flamingo.core.settings.defaults.DEDENT_INPUT

    control if flamingo should try to dedent a content file while parsing

.. setting::
    :name: HTML_PARSER_RAW_HTML
    :path: flamingo.core.settings.defaults.HTML_PARSER_RAW_HTML

    if set to True the HTML parser won't process the HTML content of html
    content files


Templating
~~~~~~~~~~

.. setting::
    :name: TEMPLATING_ENGINE
    :path: flamingo.core.settings.defaults.TEMPLATING_ENGINE

.. setting::
    :name: PRE_RENDER_CONTENT
    :path: flamingo.core.settings.defaults.PRE_RENDER_CONTENT

    if set to True, templating syntax in content files is available

.. setting::
    :name: CORE_THEME_PATHS
    :path: flamingo.core.settings.defaults.CORE_THEME_PATHS

.. setting::
    :name: THEME_PATHS
    :path: flamingo.core.settings.defaults.THEME_PATHS

.. setting::
    :name: DEFAULT_TEMPLATE
    :path: flamingo.core.settings.defaults.DEFAULT_TEMPLATE

.. setting::
    :name: DEFAULT_PAGINATION
    :path: flamingo.core.settings.defaults.DEFAULT_PAGINATION

.. setting::
    :name: EXTRA_CONTEXT
    :path: flamingo.core.settings.defaults.EXTRA_CONTEXT

.. setting::
    :name: JINJA2_EXTENSIONS
    :path: flamingo.core.settings.defaults.JINJA2_EXTENSIONS
