def test_second_stage_templating(tmp_build_env):
    tmp_build_env.write('/content/index.html', '({{ 1 + 1 }})')
    tmp_build_env.build()

    assert tmp_build_env.read('/output/index.html').endswith('(2)')


def test_link(tmp_build_env):
    tmp_build_env.write('/content/index.html', '')

    tmp_build_env.write('/content/page.html',
                        "{{ link('index.html', 'foo') }}")

    tmp_build_env.write('/content/page2.html',
                        "{{ link('index.html') }}")

    tmp_build_env.write('/content/page3.html', "{{ link('foo') }}")

    tmp_build_env.build()

    assert tmp_build_env.read('/output/page.html').endswith(
        '<a href="/index.html">foo</a>')

    assert tmp_build_env.read('/output/page2.html').endswith('/index.html')
    assert tmp_build_env.read('/output/page3.html').endswith('\n')


def test_I18N_link(tmp_build_env):
    tmp_build_env.settings.PLUGINS = [
        'flamingo.plugins.I18N',
    ]

    tmp_build_env.write('/content/index_de.html', """
    id: index
    lang: de

    foo
    """)

    tmp_build_env.write('/content/index_en.html', """
    id: index
    lang: en

    bar
    """)

    tmp_build_env.write('/content/page.html', """
    lang: de

    {{ link('index_en.html') }}
    """)

    tmp_build_env.write('/content/page2.html', """
    lang: de

    {{ link('index_en.html', lang='en') }}
    """)

    tmp_build_env.build()

    assert tmp_build_env.read('/output/de/page.html').endswith(
        '/index_de.html')

    assert tmp_build_env.read('/output/de/page2.html').endswith(
        '/index_en.html')
