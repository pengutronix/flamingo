.. image:: https://img.shields.io/travis/pengutronix/flamingo/master.svg
   :alt: Travis (.org) branch
   :target: https://travis-ci.org/pengutronix/flamingo
.. image:: https://img.shields.io/pypi/v/flamingo.svg
   :alt: pypi.org
   :target: https://pypi.org/project/flamingo

flamingo
========

Flamingo is a python3-based, `pelican <https://blog.getpelican.com/>`_-inspired
static site generator.


Basic Concepts
--------------

Flamingo aims to convert content written in a markup language into a static
website. To archive this the flamingo core parses a directory of markup files
and stores its content in an internal state called the ``context``. Plugins can
manipulate the internal state before the ``context`` is used to generate static
HTML using Jinja2 templates.

Default directory structure
---------------------------

The following listing shows the default directory structure flamingo
used if nothing else is configured:

.. code-block:: none

   |- settings.py
   |- content
   |- output
   |  |- static
   |- theme
   |  |- static
   |  |- templates

settings.py
...........

This file is loaded by flamingo on startup.
it can add, modify or remove the defaults provided by the core.


content
.......

This directory contains the markup files with the actual content for the
static site.
Flamingo will scan all directories recursively.
By default flamingo uses reStructuredText.

Content files must follow a special format:

.. code-block:: none

   id: example
   title: Title of this page
   output: file_where_this_is_written.html
   template: template_used.html
   
   
   First headline
   ==============
   
   The quick brown fox jumps over the lazy dog.

The first section of the file contains metadata of the file.
The next section contains the actual markup.
Both sections must be separated by a double newline.

For every file in the ``content`` directory a ``Content`` object in the
``context.contents`` -set is created.
All metadata are represented as items of the ``Content`` object.
The markdown section is represented in the special item ``content_body``.

theme
.....

This directory contains all elements related to the representation of the
content.
``theme/static`` can contain any static files that need to be present in the
output and are copied to ``output/static``.

``theme/templates`` contains the Jinja2-templates used to generate the
representation of the content.
If not defined by a plugin or the content itself ``page.html`` will be used
as a default template for all files in the ``content`` directory.

Inside the template the following objects are accessible:

* ``content`` -object itself: This is the content of the current file.
  Metadata is available via ``content.title`` etc.
  The actual content is available via ``content.content_body``.
* ``context``: Stores the complete state of the static site. The context object
  can be used to get information from other pages via filtering and slicing.

The following is an example that gives the latest 5 pages of all pages with
``type='blog'``:

.. code-block: none

   {% with entries=context.content.filter(type='blog').order_by('-date')[:5] %}
   {% for entry in entries %}
   {{ content.type }}: {{ content.url }}
   {% endfor %}
   {% endwith %}

Executing flamingo
----------------

Flamingo can be executed in three different ways:

* ``flamingo-build`` takes a given project and creates the static site.
* ``flamingo-shell`` loads all content and invokes an iPython-shell where the
  internal `context` is available.
* ``flamingo-server`` can be used while creating content for a website.
  In this mode flamingo builds the website and starts a webserver.
  Every time a file in ``content`` is changed it is automatically rebuild.
  ``http://localhost:8080`` can be used to access the website.
  ``http://localhost:8000/live-server`` can be used to access a version of the
  website that reloads the current page every time it has been rebuild by the
  server.
