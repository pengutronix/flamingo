flamingo
========

.. image:: doc/static/flamingo.svg
    :height: 128px
    :width: 128px

|

.. image:: https://img.shields.io/pypi/l/flamingo.svg
    :alt: pypi.org
    :target: https://pypi.org/project/flamingo
.. image:: https://img.shields.io/travis/pengutronix/flamingo/master.svg
    :alt: Travis (.org) branch
    :target: https://travis-ci.org/pengutronix/flamingo
.. image:: https://img.shields.io/pypi/pyversions/flamingo.svg
    :alt: pypi.org
    :target: https://pypi.org/project/flamingo
.. image:: https://img.shields.io/pypi/v/flamingo.svg
    :alt: pypi.org
    :target: https://pypi.org/project/flamingo
.. image:: https://img.shields.io/codecov/c/github/pengutronix/flamingo.svg
    :alt: codecov.io
    :target: https://codecov.io/gh/pengutronix/flamingo/
.. image:: https://img.shields.io/lgtm/alerts/g/pengutronix/flamingo.svg
    :alt: lgtm.com
    :target: https://lgtm.com/projects/g/pengutronix/flamingo/
.. image:: https://img.shields.io/lgtm/grade/python/g/pengutronix/flamingo.svg
    :alt: lgtm.com
    :target: https://lgtm.com/projects/g/pengutronix/flamingo/


What flamingo is and what it is not
-----------------------------------

Flamingo is a python3-based, `pelican <https://blog.getpelican.com/>`_-inspired
static site generator. This means you can only create content
that doesn't require a dynamic backend, while users visit your site.

For example: If you want your site to have login for editing or comments or
even the current time, flamingo is the wrong tool.

Basically flamingo is a fancy converter, that turns RST code into HTML code.
It doesn't provides an editor, user management or a backup solution like a CMS.

**Any part of flamingo is designed to be easy, not to be fast!**

Flamingo is full python and all operations run on python objects stored in RAM.


Getting Started
---------------

FIXME


Topics
------

- `Recipes for usage and optimization <doc/recipes.rst>`_
- `Settings <doc/settings.rst>`_
- `Data model <doc/data_model.rst>`_
- `Writing content <doc/writing_content.rst>`_
- `Writing themes <doc/writing_themes.rst>`_
- `Writing plugins <doc/writing_plugins.rst>`_
- `Using the Live-Server <doc/live-server.rst>`_
- `Using an interactive shell <doc/interactive-shell.rst>`_
- `Contributing and testing <doc/contributing.rst>`_
- `Changelog <CHANGELOG.rst>`_


Available plugins
-----------------

- `Authors <doc/plugins/authors.rst>`_
- `Tags <doc/plugins/tags.rst>`_
- `I18N <doc/plugins/i18n.rst>`_
- `Layers <doc/plugins/layers.rst>`_
- `Redirects <doc/plugins/redirects.rst>`_
- `Feeds <doc/plugins/feeds.rst>`_
- `Time <doc/plugins/time.rst>`_
- `rstBootstrap3 <doc/plugins/rst_bootstrap3.rst>`_
- `rstPygments <doc/plugins/rst_pygments.rst>`_


Helpful links
-------------

- `reStructuredText quick-reference <http://docutils.sourceforge.net/docs/user/rst/quickref.html>`_
- `Django / Making queries <https://docs.djangoproject.com/en/2.1/topics/db/queries/>`_
