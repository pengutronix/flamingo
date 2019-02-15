Changelog
=========


`v0.6.1 <https://github.com/pengutronix/flamingo/compare/v0.6...v0.6.1>`_ (2019-02-10)
--------------------------------------------------------------------------------------

**Bugfix release**

* Live-Server: IncrementalContext: fix missing hooks


`v0.6 <https://github.com/pengutronix/flamingo/compare/v0.5.1...v0.6>`_ (2019-02-08)
------------------------------------------------------------------------------------

* core: templating: Jinja2: add ``render`` and ``link`` functions
* Live-Server: reload page on rpc reconnect
* Live-Server: implement incremental builds


`v0.5.1 <https://github.com/pengutronix/flamingo/compare/v0.5...v0.5.1>`_ (2019-01-31)
--------------------------------------------------------------------------------------

* plugins: slugify tags but preserve original names
* core: utils: string: split: remove obsolete whitespaces


`v0.5 <https://github.com/pengutronix/flamingo/compare/v0.4.1...v0.5>`_ (2019-01-16)
------------------------------------------------------------------------------------

* flamingo: plugins: add plugin for redirect rules
* flamingo: core: context: typecast ``Content['content']`` empty string if None
* plugins: authors: fix content_keys
* plugins: authors: slugify links
* plugins: tags: make content_key uppercase because its a constant
* plugins: tags: add option to generate a tag page zero
* plugins: tags: fix content_keys
* plugins: tags: allow whitespaces in tag names
* core: utils: add library for string manipulation
* core: data model: ContentSet: add merges and removes
* plugins: i18n: remove old ``__not__`` syntax
* core: data model: make bitwise operations available in templates
* core: data model: implement Django like ``Q`` and ``F`` objects


`v0.4.1 <https://github.com/pengutronix/flamingo/compare/v0.4...v0.4.1>`_ (2018-12-21)
--------------------------------------------------------------------------------------

**Bugfix release**

* plugins: Feeds: fix ``updated`` field in feeds


`v0.4 <https://github.com/pengutronix/flamingo/compare/v0.3...v0.4>`_ (2018-12-20)
----------------------------------------------------------------------------------

* plugins: add plugin for RSS feeds
* plugins: Time: add strftime
* plugins: rst: add Pygments plugin
* Live-Server: use symlinks instead of copies for static files
* move non-core plugins to flamingo.plugins
* core: plugins: bootstrap3: YouTube: add privacy enhanced mode


`v0.3 <https://github.com/pengutronix/flamingo/compare/v0.2...v0.3>`_ (2018-12-17)
----------------------------------------------------------------------------------

* Live-Server: fix css in firefox
* core: utils: paginate: add docstring
* core: data model: values: prevent duplets when only one field name is given
* core: plugins: rst: RstParser: fix various parsing bugs
* core: plugins: add plugin for HTML5 time tags
* add .gitattributes to fix code vendoring
* README.rst: fix usage of hyphens


`v0.2 <https://github.com/pengutronix/flamingo/compare/v0.1...v0.2>`_ (2018-12-06)
----------------------------------------------------------------------------------

* server: log changing files
* core: context: build: only remove ``OUTPUT_ROOT`` if existing
* core: plugins: authors: fix content_keys; sort author names
* core: parsers: rst: split content in ``content_body`` and ``content_title``
* core: parsers: give all parsers full access to the current content object
* add vendor.yml to ignore 3rd party libraries
* README: fix typo


`v0.1 <https://github.com/pengutronix/flamingo/compare/v0.0...v0.1>`_ (2018-12-03)
----------------------------------------------------------------------------------

**Bugfix release**

* core: fix broken utils package


`v0.0 <https://github.com/pengutronix/flamingo/releases/tag/v0.0>`_ (2018-12-03)
--------------------------------------------------------------------------------

* Initial release
