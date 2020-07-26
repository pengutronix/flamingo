

Changelog
=========

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
