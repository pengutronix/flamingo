def test_Tags(flamingo_env):
    flamingo_env.settings.PLUGINS = ["flamingo.plugins.Tags"]

    flamingo_env.build()
