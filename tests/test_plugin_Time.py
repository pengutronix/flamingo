def test_Time(flamingo_env):
    import datetime

    flamingo_env.settings.PLUGINS = ["flamingo.plugins.Time"]

    flamingo_env.write(
        "/content/test.rst",
        """
    time: 1970-01-01 00:00:00


    Time
    ====

    """,
    )

    flamingo_env.setup()

    content = flamingo_env.context.contents.get(path="test.rst")

    assert content["time"] == datetime.datetime(1970, 1, 1, 0, 0, 0)
    assert str(content["time"]).startswith("<time")
