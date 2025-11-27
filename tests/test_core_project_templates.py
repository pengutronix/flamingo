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


@pytest.mark.parametrize("template_name", get_project_templates())
def test_project_template(template_name, run):
    from tempfile import TemporaryDirectory
    import sys
    import os

    if not os.environ.get("EXTENDED_BUILD_TESTS", ""):
        pytest.skip("EXTENDED_BUILD_TESTS is disabled")

    flamingo_path = os.path.dirname(os.path.dirname(__file__))

    with TemporaryDirectory() as tmp_dir:
        # setup environment
        executable = "python{}.{}".format(sys.version_info.major, sys.version_info.minor)

        package = os.environ["TOX_PACKAGE"]

        command = """
             {executable} -m venv bootstrap_env && \
             source bootstrap_env/bin/activate && \
             bootstrap_env/bin/pip install {package} && \
             bootstrap_env/bin/flamingo init \
                --project-template="{template_name}" \
                "wobsite" \
                python_version="{executable}" \
                flamingo_path="{flamingo_path}" \
        """.format(
            executable=executable,
            package=package,
            template_name=template_name,
            flamingo_path=flamingo_path,
        ).strip()

        returncode, output = run(command, cwd=tmp_dir, clean_env=True)
        project_root = os.path.join(tmp_dir, "wobsite")

        assert returncode == 0
        assert os.path.exists(project_root)

        # build
        returncode, output = run("make clean html", cwd=project_root, clean_env=True)

        index_html = os.path.join(project_root, "output/index.html")

        assert returncode == 0
        assert os.path.exists(index_html)
        assert len(open(index_html, "r").read()) > 0
