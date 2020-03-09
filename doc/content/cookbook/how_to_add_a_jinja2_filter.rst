

How to write a Jinja2 filter
============================

If a jinja2 filter gets setup using ``templating_engine_setup()`` it is in
every flamingo template context available.

.. code-block:: python

    class ExamplePlugin:
        def templating_engine_setup(self, context, templating_engine):
            def example_filter():
                return 'example'

            templating_engine.env.globals['example'] = example_filter
