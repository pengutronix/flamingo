def test_second_stage_templating(flamingo_env):
    flamingo_env.write(
        "/content/index.html",
        """


    ({{ 1 + 1 }})
    """,
    )

    flamingo_env.build()

    assert flamingo_env.read("/output/index.html").strip().endswith("(2)")


def test_link(flamingo_env):
    flamingo_env.write(
        "/content/index.html",
        """


    index
    """,
    )

    flamingo_env.write(
        "/content/page.html",
        """


    {{ link('index.html', 'foo') }}
    """,
    )

    flamingo_env.write(
        "/content/page2.html",
        """


    {{ link('index.html') }}
    """,
    )

    flamingo_env.write(
        "/content/page3.html",
        """


    {{ link('foo') }}
    """,
    )

    flamingo_env.build()

    assert flamingo_env.read("/output/page.html").strip().endswith('<a href="/index.html">foo</a>')

    assert flamingo_env.read("/output/page2.html").strip().endswith("/index.html")

    assert not flamingo_env.read("/output/page3.html").strip()


def test_I18N_link(flamingo_env):
    flamingo_env.settings.PLUGINS = [
        "flamingo.plugins.I18N",
    ]

    flamingo_env.write(
        "/content/index_de.html",
        """
    id: index
    lang: de


    foo
    """,
    )

    flamingo_env.write(
        "/content/index_en.html",
        """
    id: index
    lang: en


    bar
    """,
    )

    flamingo_env.write(
        "/content/page.html",
        """
    lang: de


    {{ link('index_en.html') }}
    """,
    )

    flamingo_env.write(
        "/content/page2.html",
        """
    lang: de


    {{ link('index_en.html', lang='en') }}
    """,
    )

    flamingo_env.build()

    assert flamingo_env.read("/output/de/page.html").endswith("/index_de.html")

    assert flamingo_env.read("/output/de/page2.html").endswith("/index_en.html")
