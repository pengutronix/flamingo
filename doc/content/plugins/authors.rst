is_template: False


Authors
=======

This plugin creates overview content pages grouped by their authors.


Installation
------------

.. code-block:: python

    # settings.py

    PLUGINS = [
        'flamingo.plugins.Authors',
    ]


Usage
-----

To use ``authors`` you need to add a template to render the overview pages.

This example will render two pages: ``/authors/alice.html`` and
``/authors/bob.html``.

.. code-block:: rst

    # a content file can have one or more authors
    authors: Alice, Bob


    Hello World
    ===========

    Lorem ipsum

.. code-block:: html

    <!-- theme/authors.html -->

    {% extends "DEFAULT_TEMPLATE" %}

    <h1>Contents by {{ author }}</h1>
    <ul>
        {% for content in context.contents.filter(author=author) %}
            <li><a href="{{ content.url }}">{{ content.title }}</a></li>
        {% endfor %}
    </ul>
