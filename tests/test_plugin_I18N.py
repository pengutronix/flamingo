def test_translations(tmp_build_env):
    tmp_build_env.settings.PLUGINS = [
        'flamingo.plugins.I18N',
    ]

    tmp_build_env.write('/content/home_en.rst', """
    lang: en
    id: home
    tag: a

    home (en)
    """)

    tmp_build_env.write('/content/home_de.rst', """
    lang: de
    id: home
    tag: b

    home (en)
    """)

    tmp_build_env.build()

    assert tmp_build_env.exists('/output/en/home_en.html')
    assert tmp_build_env.exists('/output/de/home_de.html')

    assert tmp_build_env.context.contents.get(
        path='home_en.rst')['translations'].values('path') == ['home_de.rst']

    assert tmp_build_env.context.contents.get(
        path='home_de.rst')['translations'].values('path') == ['home_en.rst']
