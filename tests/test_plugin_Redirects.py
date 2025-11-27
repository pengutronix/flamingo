def test_Redirects(flamingo_env):
    from bs4 import BeautifulSoup

    flamingo_env.settings.PLUGINS = ["flamingo.plugins.Redirects"]

    flamingo_env.write(
        "/content/redirects.rr",
        """
    302 /foo.html /bar.html
    """,
    )

    flamingo_env.build()

    assert flamingo_env.exists("/output/foo.html")

    file_content = flamingo_env.read("/output/foo.html")
    soup = BeautifulSoup(file_content, "html.parser")

    assert soup.head.find(
        "meta",
        attrs={
            "content": "0; url=/bar.html",
            "http-equiv": "refresh",
        },
    )
