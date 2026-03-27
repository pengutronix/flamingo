def test_translations(flamingo_env):
    flamingo_env.settings.PLUGINS = [
        "flamingo.plugins.I18N",
    ]

    flamingo_env.write(
        "/content/home_en.rst",
        """
    lang: en
    id: home
    tag: a


    home (en)
    """,
    )

    flamingo_env.write(
        "/content/home_de.rst",
        """
    lang: de
    id: home
    tag: b


    home (en)
    """,
    )

    flamingo_env.build()

    assert flamingo_env.exists("/output/en/home_en.html")
    assert flamingo_env.exists("/output/de/home_de.html")

    assert flamingo_env.context.contents.get(path="home_en.rst")["translations"].values("path") == ["home_de.rst"]

    assert flamingo_env.context.contents.get(path="home_de.rst")["translations"].values("path") == ["home_en.rst"]
