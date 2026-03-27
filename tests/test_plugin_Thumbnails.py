import pytest


@pytest.mark.xfail
def test_basic_thumnail_generating(flamingo_env):
    """
    This test is marked as failing for now because thumbnails get a generic
    name now and flamingo_env has currently no simple API to test
    generic file names
    """

    import os

    from PIL import Image

    flamingo_env.settings.PLUGINS = [
        "flamingo.plugins.Thumbnails",
    ]

    # setup image
    image_path = flamingo_env.touch("/content/image.png")
    pillow_image = Image.new("RGB", (1000, 8000), color="black")
    pillow_image.save(image_path)

    # setup article
    flamingo_env.write(
        "/content/article.rst",
        """

    Article
    =======

    .. image:: image.png
        :width: 200px

    .. image:: image.png
        :width: 200px
    """,
    )

    flamingo_env.build()

    # run tests
    assert flamingo_env.exists("/output/media/image.png")
    assert flamingo_env.exists("/output/media/image.thumb.png")

    thumbnail_cache_path = flamingo_env.gen_path("/content/thumbs")

    assert len(os.listdir(thumbnail_cache_path)) == 1

    original_pillow_image = Image.open(flamingo_env.gen_path("/output/media/image.png"))

    thumbnail_pillow_image = Image.open(flamingo_env.gen_path("/output/media/image.thumb.png"))

    assert original_pillow_image.size == (1000, 8000)
    assert thumbnail_pillow_image.size == (200, 1600)
