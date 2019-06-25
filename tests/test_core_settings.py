def test_settings_overlays(run):
    from tempfile import TemporaryDirectory
    import json
    import os

    with TemporaryDirectory() as tmp_dir:
        settings_path = os.path.join(tmp_dir, 'settings.py')
        production_path = os.path.join(tmp_dir, 'production.py')

        with open(settings_path, 'w+') as f:
            f.write("a='settings'\nb='settings'\nPLUGINS=['foo']")

        with open(production_path, 'w+') as f:
            f.write("b='production'")

        returncode, output = run(
            'flamingo args -s {} {} flamingo_test_package.settings'.format(
                settings_path,
                production_path,
            )
        )

        assert returncode == 0

        args = json.loads(output)

        assert args['settings']['a'] == 'settings'
        assert args['settings']['b'] == 'production'
        assert args['settings']['PLUGINS'] == ['foo']
