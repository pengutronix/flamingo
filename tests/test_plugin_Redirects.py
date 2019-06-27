def test_Redirects(flamingo_env):
    flamingo_env.settings.PLUGINS = ['flamingo.plugins.Redirects']

    flamingo_env.write('/content/redirects.rr', """
    302 /foo.html /bar.html
    """)

    flamingo_env.build()

    assert flamingo_env.exists('/output/foo.html')
