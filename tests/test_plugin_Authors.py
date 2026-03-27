def test_Authors(flamingo_env):
    flamingo_env.settings.PLUGINS = ["flamingo.plugins.Authors"]

    flamingo_env.build()
