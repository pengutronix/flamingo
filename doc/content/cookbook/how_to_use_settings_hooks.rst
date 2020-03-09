

How to use settings hooks
=========================

Sometimes a plugin is a little bit much for a simple approach. Lets say you
want to delete all Contents from output that have a specific path prefix.

.. code-block:: python

    # settings.py

    import flamingo

    @flamingo.hook('contents_parsed')
    def remove_contents(context):
        context.contents = context.contents.exclude(path__starstwith='foo/')

If your settings hook need to run at a very specific time you can install it
like plugin. If a plugin path starts with ``.``, the plugin loader will search
in the settings for a hook instead trying to import a plugin class.

.. code-block:: python

    # settings.py

    import flamingo

    PLUGINS = [
        # [...]
        '.remove_contents',
        # [...]
    ]

    @flamingo.hook('contents_parsed')
    def remove_contents(context):
        context.contents = context.contents.exclude(path__starstwith='foo/')
