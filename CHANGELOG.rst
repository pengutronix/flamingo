

Changelog
=========

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
