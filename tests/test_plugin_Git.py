import subprocess

import pytest


def git_is_not_installed():
    try:
        subprocess.check_output(["which", "git"])

        return False

    except Exception:
        return True


pytestmark = pytest.mark.skipif(
    git_is_not_installed(),
    reason="git is not installed",
)


def test_git(flamingo_env, run):
    version = run("git describe --always")[1].strip()

    flamingo_env.settings.PLUGINS = [
        "flamingo.plugins.Git",
    ]

    flamingo_env.settings.GIT_VERSION_CMD = "git describe --always"

    flamingo_env.write(
        "/content/article.rst",
        """

    Article
    =======

    {{ GIT_VERSION }}

    """,
    )

    flamingo_env.build()

    assert version in flamingo_env.read("/output/article.html")
    assert flamingo_env.settings.EXTRA_CONTEXT["GIT_VERSION"] == version


def test_invalid_command(flamingo_env, run, caplog):
    import logging

    version = run("git describe --always")[1].strip()

    flamingo_env.settings.PLUGINS = [
        "flamingo.plugins.Git",
    ]

    flamingo_env.settings.GIT_VERSION_CMD = "echo foo"

    flamingo_env.write(
        "/content/article.rst",
        """

    Article
    =======

    {{ GIT_VERSION }}

    """,
    )

    flamingo_env.build()

    assert version not in flamingo_env.read("/output/article.html")
    assert "GIT_VERSION" not in flamingo_env.settings.EXTRA_CONTEXT

    assert (
        "flamingo.plugins.Git",
        logging.ERROR,
        'settings.GIT_VERSION_CMD has to start with "git"',
    ) in caplog.record_tuples


def test_invalid_return_code(flamingo_env, run, caplog):
    version = run("git describe --always")[1].strip()

    flamingo_env.settings.PLUGINS = [
        "flamingo.plugins.Git",
    ]

    flamingo_env.settings.GIT_VERSION_CMD = "git foo"

    flamingo_env.write(
        "/content/article.rst",
        """

    Article
    =======

    {{ GIT_VERSION }}

    """,
    )

    flamingo_env.build()

    assert version not in flamingo_env.read("/output/article.html")
    assert "GIT_VERSION" not in flamingo_env.settings.EXTRA_CONTEXT

    assert any([x[2].startswith("git foo returned 1:") for x in caplog.record_tuples])
