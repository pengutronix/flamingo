

Feeds
=====

This plugin is used to generate RSS and ATOM feeds.


Installation
------------

``Feeds`` is based on `feedgen <https://feedgen.kiesow.be/>`_, so you have
to install flamingo with feedgen support

.. code-block:: txt

    # REQUIREMENTS.txt

    flamingo[feedgen]

.. code-block:: python

    # settings.py

    PLUGINS = [
        'flamingo.plugins.Feeds',
    ]


Settings
--------

.. raw-setting::

    FEEDS_DOMAIN = '/'

    All urls mentioned in feed items will be relative to this domain

.. raw-setting::

    FEEDS = []


Usage
-----

.. code-block:: python

    # settings.py
    FEEDS = [
        {
            'id': 'www.example.org',
            'title': 'Example.org feed',
            'type': 'atom',  # [rss, atom]
            'output': 'feeds/atom.xml',
            'lang': 'en',
            'description': 'Example Descriptions', # Only needed for RSS
            'link': 'Link to the Feeds Website',   # Only needed for RSS

            # this callback is used to specify which contents should
            # be used to generate this feed
            'contents':
                lambda ctx: ctx.contents.filter(
                    lang='en',
                ).order_by(
                    'date',
                ),

            # this callback is used to generate an unique id for each
            # feed entry
            'entry-id':
                lambda content: 'tag:www.example.org,{}:/{}'.format(
                    content['date'].strftime('%Y-%m-%d'),
                    os.path.basename(content['output']),
                ),

            # this callback is used to generate the 'updated' flag
            # of every feed entry
            'updated':
                lambda content: content['date'].strftime('%Y-%m-%d %H:%M:%S+01:00')
        },
    ]
