def test_flamingo_web_org(run):
    import os

    returncode, output = run('make clean html', cwd='flamingo-web.org')

    assert returncode == 0
    assert os.path.exists(os.path.join('flamingo-web.org/output/index.html'))
