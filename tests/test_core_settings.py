def test_overlaying_settings(run):
    import json
    import os
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmp_dir:
        settings_path = os.path.join(tmp_dir, "settings.py")
        production_path = os.path.join(tmp_dir, "production.py")

        with open(settings_path, "w+") as f:
            f.write("a='settings'\nb='settings'\nPLUGINS=['foo']")

        with open(production_path, "w+") as f:
            f.write("b='production'")

        returncode, output = run(f"flamingo args -s {settings_path} {production_path} flamingo_test_package.settings")

        assert returncode == 0

        args = json.loads(output)

        assert args["settings"]["a"] == "settings"
        assert args["settings"]["b"] == "production"
        assert args["settings"]["PLUGINS"] == ["foo"]


def test_settings_reset():
    from flamingo.core.settings import Settings

    settings = Settings()

    settings.test_int = 10
    settings.test_list = ["a", "b", "c"]
    settings.test_dict = {"a": "a", "b": "b", "c": "c"}

    settings.overlay_enable()

    settings.test_int = 20
    settings.test_list.append("d")
    settings.test_dict["d"] = "d"

    assert settings.test_int == 20

    assert settings.test_list[0] == "a"
    assert settings.test_list[1] == "b"
    assert settings.test_list[2] == "c"
    assert settings.test_list[3] == "d"

    assert settings.test_dict["a"] == "a"
    assert settings.test_dict["b"] == "b"
    assert settings.test_dict["c"] == "c"
    assert settings.test_dict["d"] == "d"

    settings.overlay_reset()

    assert settings.test_int == 10
    assert settings.test_list == ["a", "b", "c"]
    assert settings.test_dict == {"a": "a", "b": "b", "c": "c"}
