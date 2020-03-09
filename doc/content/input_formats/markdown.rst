

Markdown
========

Installation
------------

.. code-block:: python

    # settings.py

    PLUGINS = [
        'flamingo.plugins.Markdown',
    ]


Plugins
-----------------------

Python-markdown has its own plugins! You can enable them like this,
for example:

.. code-block:: python

    # better GFM and KaTeX support:
    MARKDOWN_EXTENSIONS = [
        "fenced_code",
        "mdx_linkify",
        "markdown_katex",
    ]

Note that some of them require extra python modules to be installed.
To make the above example work you will further need to add these
lines to REQUIREMENTS.txt:

.. code-block:: text

    mdx_linkify
    markdown-katex

You can also configure enabled extensions. Here's an example modifying
mdx_linkify's behaviour with a callback:

.. code-block:: python

    def linkify_callback(attrs, new=False):
        attrs[(None, 'target')] = '_blank'
        if new:
            attrs[(None, 'class')] = 'linkify'
            if not attrs['_text'].startswith(('http:', 'https:')):
                return None
        return attrs

    MARKDOWN_EXTENSION_CONFIGS = {
        'mdx_linkify': {
            "linkify_callbacks": [linkify_callback]
        }
    }

See python-markdown's documentation for more information about its
plugins: https://python-markdown.github.io/
