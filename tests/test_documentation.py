def test_documentation(run):
    import pytest
    import sys
    import os

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
    assert len(open("doc/output/index.html", "r").read()) > 0
