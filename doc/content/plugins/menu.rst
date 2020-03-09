is_template: False


Menu
====

This plugin is used to generate simple menus.


Installation
------------

.. code-block:: python

    # settings.py

    PLUGINS = [
        'flamingo.plugins.Menu',
    ]


Usage
-----

.. code-block:: python

    # settings.py

    MENU = [
        ['Section 1', [
            ['Article 1', 'section-1/article-1.rst'],
            ['Article 2', 'section-1/article-2.rst'],
        ],
        ['Section 2', [

            # menu items can contain queries
            # but have to return exactly one content object
            ['Article 3', {'path__endswith': 'article-3.rst'}],
        ]
    ]

This example shows how to generate a Bootstrap4 compliant menu

.. code-block::
    :include: ../../flamingo/plugins/menu/theme/templates/menu/bootstrap4.html

    <!-- theme/templates/menu/bootstrap4.html -->

.. code-block::

    <!-- base.html -->

    {% extends "DEFAULT_TEMPLATE" %}

    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav mr-auto">
        {% include "menu/bootstrap4.html" %}
      </ul>
    </div>
