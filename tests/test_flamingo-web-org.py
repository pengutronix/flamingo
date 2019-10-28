def test_flamingo_web_org(run):
    import pytest
    import sys
    import os

    if (sys.version_info.major, sys.version_info.minor, ) != (3, 6, ):
        pytest.skip('flamingo-web.org uses python3.6')

    returncode, output = run('make clean html', cwd='flamingo-web.org',
                             clean_env=True)

    assert returncode == 0
    assert os.path.exists('flamingo-web.org/output/index.html')
    assert len(open('flamingo-web.org/output/index.html', 'r').read()) > 0
