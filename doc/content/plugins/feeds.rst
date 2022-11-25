

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
            'type': 'atom',  # [rss, atom, podcast]
            'output': 'feeds/atom.xml',
            'lang': 'en',
            'description': 'Example Descriptions', # Only needed for rss and podcast
            'link': 'Link to the Feed itself',   # Only needed for rss and podcast
            'link_alternate': 'Link to the Feeds Website',   # Only needed for rss and podcast
            'podcast_image': 'URL of an Image for the Podcast Feed', # Only for podcast
            'itunes_owner': {'name': 'Contact Name', 'email': 'email@example.com'}, # Only for podcast
            'itunes_author': 'Name of the Author', # only for podcast
            'itunes_category': [ # Only for Podcast
                {'cat': 'Technology'},
            ], # A List of categories is here: https://podcasters.apple.com/support/1691-apple-podcasts-categories
            'itunes_explicit': 'no', # Only for Podcast; one of ['yes', 'no', 'clean']

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
                lambda content: content['date'].strftime('%Y-%m-%d %H:%M:%S+01:00'),

            # this callback is used to generate the 'published' flag
            # of every feed entry
            'published':
                lambda content: content['date'].strftime('%Y-%m-%d %H:%M:%S+01:00'),
        },
    ]


For the feed type `podcast` every content returned by the `contents` -filter must contain a header
field in the following format:

.. code-block:: python

    podcast:
      url: http://url.to/file.mp3
      size: 123456789   # in bytes
      type: audio/mpeg  # optional, defaults to audio/mpeg