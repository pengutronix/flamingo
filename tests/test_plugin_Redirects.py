import logging

import pytest


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


def test_redirects_broken_line(flamingo_env, caplog: pytest.LogCaptureFixture):
    flamingo_env.settings.PLUGINS = ["flamingo.plugins.Redirects"]

    flamingo_env.write(
        "/content/redirects.rr",
        """
    302a /foo.html /bar.html
    """,
    )

    caplog.set_level(logging.ERROR)
    flamingo_env.build()
    assert any("Invalid redirect rule line: '302a /foo.html /bar.html'" in line for line in caplog.messages)

    assert not flamingo_env.exists("/output/foo.html")
