

Tags
====

This plugin creates overview content pages grouped by their tags.


Installation
------------

.. code-block:: python

    # settings.py

    PLUGINS = [
        'flamingo.plugins.Tags',
    ]


Settings
--------

.. raw-setting::

    TAGS_GENERATE_PAGE_ZERO = True

    If set to ``True`` Tags will create an alias for ``tags/1.html`` with the
    url ``tags.html``


Usage
-----

This example will render two tag pages: ``/tags/hello.html`` and
``/tags/world.html`` and a overview page ``tags/1.html`` with ``hello`` and
``world`` listed.

.. code-block:: rst

    tags: hello, world


    Hello World
    ===========

    Lorem ipsum
