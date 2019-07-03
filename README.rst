

flamingo
========

.. image:: flamingo-web.org/theme/static/flamingo.svg
    :height: 128px
    :width: 128px

|

.. image:: https://img.shields.io/pypi/l/flamingo.svg
    :alt: pypi.org
    :target: https://pypi.org/project/flamingo
.. image:: https://img.shields.io/travis/com/pengutronix/flamingo/master.svg
    :alt: Travis branch
    :target: https://travis-ci.com/pengutronix/flamingo
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

Basically flamingo is a fancy converter, that turns RST, MD or HTML code into
HTML code.  It doesn't provides an editor, user management or a backup solution
like a CMS.

**Any part of flamingo is designed to be easy, not to be fast!**

Flamingo is full python and all operations run on python objects stored in RAM.


Getting Started
---------------

The simplest way to bootstrap a flamingo project is to use ``flamingo init``.
Flamingo does not enforce a specific project structure but comes with a number
of project templates.

A list of available project templates, their descriptions and variables is
available by running ``flamingo init -l``.

.. code-block:: text

    $ pip install flamingo
    $ flamingo init wobsite project_name="Wobsite"
    $ cd wobsite/
    $ make html

The content of ``wobsite`` will look like this:

.. code-block:: text

    wobsite/
    ├── content/          # flamingo will search for content here recursively
    ├── Makefile
    ├── overlay/          # here you can place files like a robots.txt or a
    │                       favicon.ico
    ├── plugins/          # place your plugins here
    ├── README.rst
    ├── REQUIREMENTS.txt  # list of all python dependencies
    ├── settings.py       # all settings are stored here
    └── theme/            # root of all HTML templates, CSS- and JS files

The new project comes with a
`gnu make <https://www.gnu.org/software/make/>`_ file, that handles flamingo
dependencies in a python virtualenv, setting the right python version and holds
command line options for building.

To build the project run ``make html``.

Flamingo comes with a interactive webserver for writing content and debugging.
Run ``make server`` and go to ``localhost:8080/live-server/`` with your
browser. Let server and browser run while writing your content. Flamingo
tracks file operations in ``content/``, rebuilds updated files and
refreshes the browser tab if needed.

Next Steps
----------

`Writing Content <flamingo-web.org/content/doc/writing_content.rst>`_

`Setup Markdown parser <flamingo-web.org/content/plugins/markdown.rst>`_

`Setup redirects to maintain historic links <flamingo-web.org/content/plugins/redirects.rst>`_

`Setup Internationalisation <flamingo-web.org/content/plugins/i18n.rst>`_

`Setup Tags <flamingo-web.org/content/plugins/tags.rst>`_

`Setup Author Pages <flamingo-web.org/content/plugins/authors.rst>`_
