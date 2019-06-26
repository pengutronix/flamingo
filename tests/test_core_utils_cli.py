def test_project_root(run):
    from tempfile import TemporaryDirectory
    import json
    import os

    with TemporaryDirectory() as tmp_dir:
        os.mkdir(os.path.join(tmp_dir, 'content'))
        os.mkdir(os.path.join(tmp_dir, 'theme'))

        with open(os.path.join(tmp_dir, 'settings.py'), 'w+') as f:
            f.write('TEST = True')

        returncode, output = run('flamingo args -p {}'.format(tmp_dir))

        assert returncode == 0

        settings = json.loads(output)['settings']

        assert settings['CONTENT_ROOT'] == os.path.join(tmp_dir, 'content')
        assert settings['TEST'] is True


def test_debug_mode(run):
    import json

    returncode, output = run('flamingo args -d')

    assert returncode == 0

    args = json.loads(output)

    assert args['args']['debug'] is True


def test_content_root(run):
    import json

    returncode, output = run('flamingo args --content-root=foo')

    assert returncode == 0

    args = json.loads(output)

    assert args['args']['content_root'] == 'foo'
    assert args['settings']['CONTENT_ROOT'] == 'foo'


def test_content_paths(run):
    import json

    returncode, output = run('flamingo args --content-paths foo bar')

    assert returncode == 0

    args = json.loads(output)

    assert args['args']['content_paths'] == ['foo', 'bar']
    assert args['settings']['CONTENT_PATHS'] == ['foo', 'bar']
