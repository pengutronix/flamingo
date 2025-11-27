def test_rstBootstrap3(flamingo_env):
    flamingo_env.settings.PLUGINS = ["flamingo.plugins.rstBootstrap3"]

    flamingo_env.write(
        "/content/test.rst",
        """


    .. div::

        .. alert:: info

            info

        .. youtube:: foo

    .. row::

        .. col:: md-6

            foo

        .. col:: md-6

            bar
    """,
    )

    flamingo_env.build()
