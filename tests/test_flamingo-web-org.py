def test_flamingo_web_org(run):
    import sys
    import os

    returncode, output = run(
        'make clean -e PYTHON={} html'.format(sys.executable),
        cwd='flamingo-web.org',
    )

    assert returncode == 0
    assert os.path.exists(os.path.join('flamingo-web.org/output/index.html'))
