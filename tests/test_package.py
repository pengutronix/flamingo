def find_source_files(path):
    import os

    source_files = []

    for root, dirs, files in os.walk(path):
        if "__pycache__" in root:
            continue

        for name in files:
            if name.startswith(".") or "~" in name or "#" in name:
                continue

            extension = os.path.splitext(name)[1]

            if extension in (
                ".swp",
                ".pyc",
            ):
                continue

            source_files.append(
                os.path.join(
                    "flamingo",
                    os.path.relpath(os.path.join(root, name), path),
                )
            )

    return set(source_files)


def test_imports():
    """
    This test checks if flamingo is importable.
    """

    import flamingo  # NOQA


def test_package_data():
    """
    This test checks if all source code files in flamingo/ were rolled out to
    the test environment.
    """

    import os

    import flamingo

    source_files = find_source_files(os.path.join(os.getcwd(), "flamingo"))
    package_files = find_source_files(os.path.dirname(flamingo.__file__))

    assert source_files == package_files


def test_vcs():
    """
    This test checks if all source code files in flamingo/ are part of the vcs.
    """

    from subprocess import check_output
    import os

    import pytest

    try:
        check_output(["git", "status"])

    except Exception:
        pytest.skip("git is not available")

    source_files = find_source_files(os.path.join(os.getcwd(), "flamingo"))

    vcs_source_files = set(
        [i for i in check_output(["git", "ls-files"]).decode().splitlines() if i.startswith("flamingo/")]
    )

    assert source_files == vcs_source_files
