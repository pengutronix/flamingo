def test_basic_parsing(flamingo_env):
    flamingo_env.settings.PLUGINS = ["flamingo.plugins.Markdown"]

    flamingo_env.write(
        "/content/index.md",
        """


    # Hello World

    """,
    )

    flamingo_env.build()

    assert flamingo_env.read("/output/index.html").startswith("Hello World\n")


def test_second_stage_templating(flamingo_env):
    flamingo_env.settings.PLUGINS = ["flamingo.plugins.Markdown"]

    flamingo_env.write(
        "/content/index.md",
        """


    # index

    <p>{{ 1 + 1 }}</p>

    """,
    )

    flamingo_env.build()

    assert "<p>2</p>" in flamingo_env.read("/output/index.html")


def test_images(flamingo_env):
    from bs4 import BeautifulSoup

    flamingo_env.settings.PLUGINS = ["flamingo.plugins.Markdown"]

    flamingo_env.write("/content/home.png", "1")
    flamingo_env.write("/content/home-2.png", "2")

    flamingo_env.write(
        "/content/home.md",
        """


    # Home

    Hello world

    ![](home.png)
    """,
    )

    flamingo_env.build()

    # there should be a cleaned title and something that seems like html
    assert flamingo_env.read("/output/home.html").startswith("Home\n")

    # home.png should be present in output
    assert flamingo_env.read("/output/media/home.png") == "1"

    # home-2.png is not referenced, so it should not be part of the output
    assert not flamingo_env.exists("/output/media/home-2.png")

    # check rendered html
    html = flamingo_env.read("/output/home.html")
    soup = BeautifulSoup(html, "html.parser")
    img = soup.find_all("img")[0]

    assert img.attrs["src"] == "/media/home.png"
