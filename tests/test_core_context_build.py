def test_empty_build(flamingo_env):
    flamingo_env.setup()
    flamingo_env.build()


def test_basic_build(flamingo_env):
    flamingo_env.write("/content/home.png", "1")
    flamingo_env.write("/content/home-2.png", "2")
    flamingo_env.write("/theme/static/test.css", "3")

    flamingo_env.write(
        "/content/home.rst",
        """
    author: me


    Home
    ====

    Hello world

    .. img:: home.png
    """,
    )

    flamingo_env.build()

    # there should be a cleaned title and something that seems like html
    assert flamingo_env.read("/output/home.html").startswith("Home\n<")

    assert flamingo_env.read("/output/media/home.png") == "1"
    assert flamingo_env.read("/output/static/test.css") == "3"

    # home-2.png is referenced, so it should not be part of the output
    assert not flamingo_env.exists("/output/media/home-2.png")


def test_chardet(flamingo_env):
    flamingo_env.settings.USE_CHARDET = True

    flamingo_env.write(
        "/content/home.html",
        """


    index
    """,
    )

    flamingo_env.build()

    assert flamingo_env.read("/output/home.html").strip() == "index"
