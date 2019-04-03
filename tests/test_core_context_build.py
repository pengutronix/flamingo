def test_empty_build(tmp_build_env):
    tmp_build_env.setup()
    tmp_build_env.build()


def test_basic_build(tmp_build_env):
    tmp_build_env.write('/content/home.png', '1')
    tmp_build_env.write('/content/home-2.png', '2')
    tmp_build_env.write('/theme/static/test.css', '3')

    tmp_build_env.write('/content/home.rst', """
    author: me


    Home
    ====

    Hello world

    .. img:: home.png
    """)

    tmp_build_env.build()

    # there should be a cleaned title and something that seems like html
    assert tmp_build_env.read('/output/home.html').startswith('Home\n<')

    assert tmp_build_env.read('/output/media/home.png') == '1'
    assert tmp_build_env.read('/output/static/test.css') == '3'

    # home-2.png is referenced, so it should not be part of the output
    assert not tmp_build_env.exists('/output/media/home-2.png')


def test_chardet(tmp_build_env):
    tmp_build_env.settings.USE_CHARDET = True

    tmp_build_env.write('/content/home.html', 'index')

    tmp_build_env.build()

    assert tmp_build_env.read('/output/home.html') == '\nindex'
