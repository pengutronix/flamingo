

Changelog
=========

`v1.9 <https://github.com/pengutronix/flamingo/compare/v1.8...v1.9>`_ (2022-11-22)
------------------------------------------------------------------------------------

Changes
~~~~~~~

* plugins/sphinx_themes: Make compatible to Sphinx>=5.02.
* plugins/feeds: Add support for Podcast-Style RSS feeds

Bugfixes
~~~~~~~~

* tests/plugin_git now works with output on systems with other languages than English.
* plugins/feeds: Set attributes that are mandatory for RSS feeds

`v1.8 <https://github.com/pengutronix/flamingo/compare/v1.7.1...v1.8>`_ (2021-05-12)
------------------------------------------------------------------------------------

Changes
~~~~~~~

* jinja2: Make integration compatible to jinja2 > 3.0.0
* tox: It's now possible to run a single test using ``tox -- <testname>``
* Release Workflow: Moved from a ``tox``-based to a ``make``-based workflow.
  We can now run ``make sdist`` and ``make _release`` to upload a new dist to pypi.

Breaking Changes
~~~~~~~~~~~~~~~~

* plugins/sphinx_themes: Update Sphinx to 4.5.0 and sphinx_rtd_theme to 1.0.0.
  After this change your ``settings.py`` needs to be altered according to
  https://github.com/pengutronix/flamingo/commit/4725f2ef94021b4eb49e497109c084a798d989af


`v1.7.1 <https://github.com/pengutronix/flamingo/compare/v1.7...v1.7.1>`_ (2021-12-16)
--------------------------------------------------------------------------------------

Bugfixes
~~~~~~~~

* plugins: Tags: titles in tag listing pages were fixed

  * Previously tag listing pages contained "None" if the template didn't set
    a proper title


`v1.7 <https://github.com/pengutronix/flamingo/compare/v1.6.1...v1.7>`_ (2021-12-02)
------------------------------------------------------------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

* plugins: reStructuredText: document_xform is now disabled by default

  * With this option enabled all articles with more than one heading are
    structured in sections, and all articles with less than two headings are
    not. This caused all sorts of CSS an structuring problems.

Bugfixes
~~~~~~~~

* plugins: SphinxThemes: handling of active menu items was fixed

  * Previously the menu was not expanded correctly in all cases


`v1.6.1 <https://github.com/pengutronix/flamingo/compare/v1.6...v1.6.1>`_ (2021-11-09)
--------------------------------------------------------------------------------------

Bugfixes
~~~~~~~~

* server: fix compatibility issues with aiohttp 3.8

* core: data model: NOT, OR, AND: fix compatibility problems between different
  python versions

* plugins: SphinxThemes: pin dependencies to a compatible versions


`v1.6 <https://github.com/pengutronix/flamingo/compare/v1.5...v1.6>`_ (2021-04-09)
----------------------------------------------------------------------------------

Changes
~~~~~~~

* shell: replace IPython with rlpython
* server: add a aiohttp-json-rpc replacement
* server: update aiohttp dependency
* server: set default watcher refresh interval to 1 second
* plugins: SphinxThemes: add support for multiple toctree captions
* plugins: SphinxThemes: add support for extra stylesheets and scripts
* plugins: setup ``flamingo.plugins.rstTable``
* doc: use official ReadTheDocs theme instead of fork


`v1.5 <https://github.com/pengutronix/flamingo/compare/v1.4...v1.5>`_ (2021-03-17)
----------------------------------------------------------------------------------

This release brings support for Shpinx themes, reStructuredText includes and 
various bugfixes and also drops support for Python 3.5


Breaking Changes
~~~~~~~~~~~~~~~~

* change range of supported Python versions to Python>3.5

* core: utils: html: extract_section_by_title got renamed to
  get_section_to_title

* plugins: Menu: Menu uses its own plugin namespace for resolving paths
  instead of the settings namespace now

  * all templates now have to use ``context.plugins.Menu.menu.main`` instead
    of ``context.settings.MENU.main``


Changes
~~~~~~~

* server: better support for ``related_paths`` keyword

* server: add ``--shutdown-timeout``

  * default in set to ``0.0`` (this fixes previous shutdown problems)

* plugins: add ``plugins.SphinxThemes``
* plugins: add ``plugins.rstInclude``
* plugins: Feeds: error messages are more human readable now

* plugins: reStructuredText: fix wrong line numbers in warnings and
  error messages

* plugins: Photoswipe: add support for SVGs
* plugins: Thumbnails: add support for SVGs


Bugfixes
~~~~~~~~

* plugins: rstImage: fix name clashes in meta data
* plugins: Feeds: fix link resolving in feed items
* plugins: reStructuredText: Container directive: fix namespace problems

* plugins: Thumbnails: fix thumbnail output paths

  * The previous naming scheme ``$FILE_NAME.thumb.$EXTENSION`` was not unique
    and lead to overriding of thumbnail. The new naming scheme is
    ``$FILE_NAME.thumb.$HASH.$EXTENSION``.


`v1.4 <https://github.com/pengutronix/flamingo/compare/v1.3...v1.4>`_ (2020-08-30)
----------------------------------------------------------------------------------

This release brings a changes and bugfixes for ``plugins.Time``


Breaking Changes
~~~~~~~~~~~~~~~~

* plugins: Time: add comparison between ``datetime.date`` and
  ``datetime.datetime`` objects

  * If a value in ``content['date']`` comes without a time string,
    ``datetime.datetime.min.time()`` gets used for comparisons


Bugfixes
~~~~~~~~

* plugins: Time: wrong implicit type casting of time object

  * Previously it could happen that ``datetime.datetime`` objects got
    mistakenly type casted to ``datetime.date`` objects


`v1.3 <https://github.com/pengutronix/flamingo/compare/v1.2.2...v1.3>`_ (2020-07-26)
------------------------------------------------------------------------------------

This release brings bugfixes, performance improvements and long anticipated
development features like directory-listing and configurable directory-indexing


Breaking Changes
~~~~~~~~~~~~~~~~

* core: set ``content['output']`` to ``/dev/null`` when ``output``
  and ``path`` are not set

  * This saves loop iterations when rendering output

* server: consolidate command line args

  * Previously the command line used terms like ``--disable-$FEATURE`` which
    lead to double negation in code. Also it made it hard to change defaults.

* plugins: Feeds: use ``title`` or ``content_title`` for feed items

  * This emulates flamingos behavior on how to search for a content files title

* plugins: reStructuredText: split plugin in multiple modules

* plugins: rstLink: remove obsolete option ``find_name``

  * This option never made sense: If you provide a link name, it is obvious
    that flamingo don't has to search for one. If you don't provide one,
    setting ``find_name=False`` can only result in a crash.

* plugins: remove plugins.rst.rstFile

  * Since plugins.rst.rstLink has support for downloadable files, this plugin
    is obsolete


Changes
~~~~~~~

* core: data model: Q: skip unnecessary lookups; cache lookups

  * This can (depending on your use cases) have a significant impact on your
    projects performance

* core: context: add hook template_context_setup

  * This makes it possible to inject context changes to any template

* core: context: add ``media_content`` property
* core: plugin manager: add tab completion for shell

* plugins: rstLink: add support for downloads
* server: BuildEnvironment: add api to await rebuilds
* server: share server options live between frontend and backend
* server: ContentExporter: add directory listing
* server: frontend: add better tab- and shortcut handling
* server: add sync variant of ``await_unlock()``

* tests: setup server tests
* tests: add tests for plugins.Git
* tests: add tests for plugins.Thumbnails
* tests: core: settings: add overlay tests
* tests: add tests for plugins.rst.rstLink
* tests: add layer tests


Bugfixes
~~~~~~~~

* core: context: build: run hook ``pre_build`` hook after initial cleanup

  * pre build layers were pretty much broken by design before

* server: cli: fix log filtering

  * ``--loggers`` was never processed properly

* server: meta data: use overlay data instead of original data
* server: meta data: mask overlay types

  * Previously this lead to confusing output in the ``Meta Data`` tab in
    flamingo server

* core: types: OverlayObject: fix duplicates in ``__dir__()``

* plugins: reStructuredText: fix caching issues for directives and roles

  * Previous versions of the reStructuredText plugin use the reStructuredText
    upstreams directive cache, which is fine til you try to overload a
    directive twice. This lead to confusing results when running tests.



`v1.2.2 <https://github.com/pengutronix/flamingo/compare/v1.2.1...v1.2.2>`_ (2020-05-04)
----------------------------------------------------------------------------------------

Changes
~~~~~~~

* tests: plugins: Markdown: test image tag rendering


Bugfixes
~~~~~~~~

* core: utils: html: ``process_media_links()``: fix broken media meta data

  This fixes broken image tags in Markdown files



`v1.2.1 <https://github.com/pengutronix/flamingo/compare/v1.2...v1.2.1>`_ (2020-04-29)
--------------------------------------------------------------------------------------

Bugfixes
~~~~~~~~

* plugins: reStructuredText: rstFile: fix broken links



`v1.2 <https://github.com/pengutronix/flamingo/compare/v1.1...v1.2>`_ (2020-04-25)
----------------------------------------------------------------------------------

Changes
~~~~~~~

* server: exporter: search for a ``index.html`` if an empty directory is requested

Bugfixes
~~~~~~~~

* server: frontend: fix rpc race condition while iframe setup

* plugins: Redirects: fix empty HTML files

  In early versions of flamingo page contents were stored in
  ``content['content']``.  Now they are stored in ``content['content_body']``.



`v1.1 <https://github.com/pengutronix/flamingo/compare/v1.0...v1.1>`_ (2020-03-29)
----------------------------------------------------------------------------------

Changes
~~~~~~~

* core: plugins: PluginManager: make ``THEME_PATHS`` a property

  This makes dynamically generated theme paths by plugin hooks possible

* server: frontend: show an error message if JavasCript is disabled

* plugins: reStructuredText: make system message removing configurable by
  ``settings.RST_REMOVE_SYSTEM_MESSAGES_FROM_OUPUT``

* core: context: add ``resolve_content_path()`` for resolving relative and
  absolute content paths

* core: templating: Jinja2: make Jinja2 extensions configurable by
  ``settings.JINJA2_EXTENSIONS``

* core: templating: Jinja2: rewrite ``link()`` method

  * use ``context.resolve_content_path()`` instead of custom path resolving
  * add ``LinkError`` class for better error reporting in Live-Server
  * make i18n path resolving configurable

* plugins: reStructuredText: add rstLink

  This plugin adds a Sphinx like docutils role for internal and external links

Bugfixes
~~~~~~~~

* core: plugins: Layers: Check if directories exist before using them

* core: data model: fix ``endswith`` lookup

  Til this point ``__endswith`` lookups ran ``<str>.startswith()`` due a
  copy-paste error.

* server: frontend: return an ``404`` error on directory listing request
  instead of crashing



`v1.0 <https://github.com/pengutronix/flamingo/releases/tag/v1.0>`_ (2020-03-19)
--------------------------------------------------------------------------------

* First stable release
