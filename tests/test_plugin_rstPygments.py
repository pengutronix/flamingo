def test_rstPygments(flamingo_env):
    flamingo_env.settings.PLUGINS = ["flamingo.plugins.rstPygments"]

    flamingo_env.write(
        "/content/test.rst",
        """


    .. code-block::

        foo

    .. code-block:: python

        import flamingo
    """,
    )

    flamingo_env.build()
