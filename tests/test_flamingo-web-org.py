def test_flamingo_web_org(run):
    import os

    returncode, output = run('make clean html', cwd='flamingo-web.org',
                             clean_env=True)

    assert returncode == 0
    assert os.path.exists('flamingo-web.org/output/index.html')
    assert len(open('flamingo-web.org/output/index.html', 'r').read()) > 0
