import os

import pytest

from flamingo import PROJECT_TEMPLATES_ROOT


def get_project_templates():
    templates = []

    for template in os.listdir(PROJECT_TEMPLATES_ROOT):
        if not os.path.isdir(os.path.join(PROJECT_TEMPLATES_ROOT, template)):
            continue

        templates.append(template)

    return templates


@pytest.mark.parametrize('template_name', get_project_templates())
def test_project_template(template_name, run):
    from tempfile import TemporaryDirectory
    import sys
    import os

    with TemporaryDirectory() as tmp_dir:
        command = 'flamingo init --project-template="{}" {} python_version={}'.format(  # NOQA
            template_name, tmp_dir, sys.executable)

        returncode, output = run(command, cwd=tmp_dir)

        assert returncode == 0

        returncode, output = run('make html', cwd=tmp_dir)

        assert os.path.exists(os.path.join(tmp_dir, 'output/index.html'))
