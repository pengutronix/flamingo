def test_external_links(flamingo_env):
    from bs4 import BeautifulSoup

    flamingo_env.write(
        "/content/external-links.rst",
        """

    :link:`Flamingo <http://www.flamingo-web.org>`
    :link:`http://www.flamingo-web.org`

    """,
    )

    flamingo_env.build()

    # run tests
    html = flamingo_env.read("/output/external-links.html")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")

    assert links[0].get_text() == "Flamingo"
    assert links[0].attrs["href"] == "http://www.flamingo-web.org"

    assert links[1].get_text() == "http://www.flamingo-web.org"
    assert links[1].attrs["href"] == "http://www.flamingo-web.org"


def test_internal_links(flamingo_env):
    from bs4 import BeautifulSoup

    flamingo_env.write(
        "/content/article1.rst",
        """
    output: article1.html


    Article 1
    =========

    """,
    )

    flamingo_env.write(
        "/content/article2/article.rst",
        """
    output: article2/article.html


    Article 2
    =========

    """,
    )

    flamingo_env.write(
        "/content/article3.rst",
        """
    output: article3.html


    Article 3
    =========

    :link:`article1.rst`
    :link:`/article1.rst`
    :link:`Custom Title <article1.rst>`
    :link:`Custom Title </article1.rst>`

    :link:`article2/article.rst`
    :link:`/article2/article.rst`
    :link:`Custom Title 2 <article2/article.rst>`
    :link:`Custom Title 2 </article2/article.rst>`

    """,
    )

    flamingo_env.build()

    # run tests
    html = flamingo_env.read("/output/article3.html")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")

    # article 1
    assert links[0].get_text() == "Article 1"
    assert links[0].attrs["href"] == "/article1.html"
    assert links[1].get_text() == "Article 1"
    assert links[1].attrs["href"] == "/article1.html"

    assert links[2].get_text() == "Custom Title"
    assert links[2].attrs["href"] == "/article1.html"
    assert links[3].get_text() == "Custom Title"
    assert links[3].attrs["href"] == "/article1.html"

    # article 2
    assert links[4].get_text() == "Article 2"
    assert links[4].attrs["href"] == "/article2/article.html"
    assert links[5].get_text() == "Article 2"
    assert links[5].attrs["href"] == "/article2/article.html"

    assert links[6].get_text() == "Custom Title 2"
    assert links[6].attrs["href"] == "/article2/article.html"
    assert links[7].get_text() == "Custom Title 2"
    assert links[7].attrs["href"] == "/article2/article.html"


def test_i18n_links(flamingo_env):
    from bs4 import BeautifulSoup

    # setup i18n
    flamingo_env.settings.PLUGINS = [
        "flamingo.plugins.I18N",
    ]

    flamingo_env.settings.I18N_CONTENT_KEY = "id"
    flamingo_env.settings.I18N_LANGUAGES = ["en", "de"]
    flamingo_env.settings.I18N_DEFAULT_LANGUAGES = "en"

    # setup article
    flamingo_env.write(
        "/content/article1_en.rst",
        """
    id: article-1
    lang: en
    output: article1.html


    en Article 1
    ============

    """,
    )

    flamingo_env.write(
        "/content/article1_de.rst",
        """
    id: article-1
    lang: de
    output: article1.html


    de Article 1
    ============

    """,
    )

    flamingo_env.write(
        "/content/article3.rst",
        """
    lang: en
    output: article3.html


    Article 3
    =========

    :link:`article 1 <article1_de.rst>`
    :link:`article 1 <article1_de.rst> i18n=False`
    """,
    )

    flamingo_env.build()

    # run tests
    html = flamingo_env.read("/output/en/article3.html")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")

    assert links[0].attrs["href"] == "/en/article1.html"
    assert links[1].attrs["href"] == "/de/article1.html"


def test_downloads(flamingo_env):
    from bs4 import BeautifulSoup

    flamingo_env.write("/content/download.txt", "1")

    flamingo_env.write(
        "/content/article.rst",
        """

    Article
    =======

    :link:`download.txt`
    :link:`/download.txt`
    :link:`Download <download.txt>`

    """,
    )

    flamingo_env.build()

    # run tests
    html = flamingo_env.read("/output/article.html")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")

    assert links[0].get_text() == "download.txt"
    assert links[0].attrs["href"] == "/media/download.txt"

    assert links[1].get_text() == "download.txt"
    assert links[1].attrs["href"] == "/media/download.txt"

    assert links[2].get_text() == "Download"
    assert links[2].attrs["href"] == "/media/download.txt"

    assert flamingo_env.read("/output/media/download.txt") == "1"


def test_rendering_error(flamingo_env, caplog):
    flamingo_env.settings.PRE_RENDER_CONTENT = False

    flamingo_env.write(
        "/content/article.rst",
        """

    en Article 1
    ============

    :link:`article.rst`

    """,
    )

    flamingo_env.build()

    html = flamingo_env.read("/output/article.html")

    assert (
        "flamingo",
        40,
        "article.rst:6: LinkError: internal links depend on content pre rendering which is disabled by your settings",  # NOQA
    ) in caplog.record_tuples

    assert "{{ link(" in html
