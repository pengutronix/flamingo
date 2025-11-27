def test_debug_mode(run):
    import json

    returncode, output = run("flamingo args -d")

    assert returncode == 0

    args = json.loads(output)

    assert args["args"]["debug"] is True


def test_content_root(run):
    import json

    returncode, output = run("flamingo args --content-root=foo")

    assert returncode == 0

    args = json.loads(output)

    assert args["args"]["content_root"] == "foo"
    assert args["settings"]["CONTENT_ROOT"] == "foo"


def test_content_paths(run):
    import json

    returncode, output = run("flamingo args --content-paths foo bar")

    assert returncode == 0

    args = json.loads(output)

    assert args["args"]["content_paths"] == ["foo", "bar"]
    assert args["settings"]["CONTENT_PATHS"] == ["foo", "bar"]
