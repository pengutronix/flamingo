def test_documentation(run):
    import os
    import sys

    import pytest

    if not os.environ.get("EXTENDED_BUILD_TESTS", ""):
        pytest.skip("EXTENDED_BUILD_TESTS is disabled")

    if (
        sys.version_info.major,
        sys.version_info.minor,
    ) != (
        3,
        6,
    ):
        pytest.skip("documentation python3.6")

    returncode, output = run("make clean html", cwd="doc", clean_env=True)

    assert returncode == 0
    assert os.path.exists("doc/output/index.html")
    with open("doc/output/index.html") as fh:
        assert len(fh.read()) > 0
