def test_error_management(flamingo_env, caplog):
    import logging

    flamingo_env.settings.PRE_BUILD_LAYERS = [
        "foo",
    ]

    flamingo_env.settings.POST_BUILD_LAYERS = [
        "bar",
    ]

    flamingo_env.build()

    assert (
        "flamingo.core.layers",
        logging.ERROR,
        "PreBuildLayer 'foo' not found.",
    ) in caplog.record_tuples

    assert (
        "flamingo.core.layers",
        logging.ERROR,
        "PostBuildLayer 'bar' not found.",
    ) in caplog.record_tuples


def test_pre_build_layers(flamingo_env):
    import os

    flamingo_env.settings.PRE_BUILD_LAYERS = [
        os.path.join(flamingo_env.path, "layers/pre-build-1"),
        os.path.join(flamingo_env.path, "layers/pre-build-2"),
    ]

    flamingo_env.write("/layers/pre-build-1/article-1.html", "1")
    flamingo_env.write("/layers/pre-build-2/article-2.html", "2")

    flamingo_env.write(
        "/content/article-1.rst",
        """

    Article 1
    =========

    """,
    )

    flamingo_env.build()

    assert flamingo_env.exists("/output/article-1.html")
    assert flamingo_env.exists("/output/article-2.html")

    assert flamingo_env.read("/output/article-1.html") != "1"
    assert flamingo_env.read("/output/article-2.html") == "2"


def test_post_build_layers(flamingo_env):
    import os

    flamingo_env.settings.POST_BUILD_LAYERS = [
        os.path.join(flamingo_env.path, "layers/post-build-1"),
        os.path.join(flamingo_env.path, "layers/post-build-2"),
    ]

    flamingo_env.write("/layers/post-build-1/article-1.html", "1")
    flamingo_env.write("/layers/post-build-2/article-2.html", "2")

    flamingo_env.write(
        "/content/article-1.rst",
        """

    Article 1
    =========

    """,
    )

    flamingo_env.build()

    assert flamingo_env.exists("/output/article-1.html")
    assert flamingo_env.exists("/output/article-2.html")

    assert flamingo_env.read("/output/article-1.html") == "1"
    assert flamingo_env.read("/output/article-2.html") == "2"


def test_layers(flamingo_env):
    import os

    flamingo_env.settings.PRE_BUILD_LAYERS = [
        os.path.join(flamingo_env.path, "layers/pre-build"),
    ]

    flamingo_env.settings.POST_BUILD_LAYERS = [
        os.path.join(flamingo_env.path, "layers/post-build"),
    ]

    # setup pre build layer
    flamingo_env.write("/layers/pre-build/article-1.html", "pre-1")
    flamingo_env.write("/layers/pre-build/article-2.html", "pre-2")
    flamingo_env.write("/layers/pre-build/article-3.html", "pre-3")

    # setup contents
    flamingo_env.write(
        "/content/article-2.rst",
        """

    Article 2
    =========

    """,
    )

    flamingo_env.write(
        "/content/article-3.rst",
        """

    Article 3
    =========

    """,
    )

    # setup post build layer
    flamingo_env.write("/layers/post-build/article-3.html", "post-3")

    flamingo_env.build()

    assert flamingo_env.read("/output/article-1.html") == "pre-1"
    assert flamingo_env.read("/output/article-2.html").startswith("Article 2")
    assert flamingo_env.read("/output/article-3.html") == "post-3"
