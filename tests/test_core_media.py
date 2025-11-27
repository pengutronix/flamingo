def test_add_media(flamingo_dummy_context, flamingo_env):
    from flamingo.core.plugins.media import add_media
    from flamingo.core.data_model import Content

    # relative path
    content = Content(path="foo/bar/index.rst")
    media_content = add_media(flamingo_dummy_context, content, "image.jpg")

    assert media_content["path"] == "foo/bar/image.jpg"
    assert media_content["output"] == "media/foo/bar/image.jpg"
    assert media_content["url"] == "/media/foo/bar/image.jpg"

    # absolute path
    content = Content(path="foo/bar/index.rst")
    media_content = add_media(flamingo_dummy_context, content, "/image.jpg")

    assert media_content["path"] == "image.jpg"
    assert media_content["output"] == "media/image.jpg"
    assert media_content["url"] == "/media/image.jpg"

    # real build tests
    flamingo_env.settings.PLUGINS.append("flamingo.core.plugins.Media")

    flamingo_env.write("/content/foo.jpg", "1")

    flamingo_env.write(
        "/content/index.rst",
        """


    Hello World
    ===========

    .. img:: foo.jpg

    """,
    )

    flamingo_env.build()

    assert flamingo_env.read("/output/media/foo.jpg") == "1"
