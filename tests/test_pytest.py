def test_run(run):
    assert run("true || echo error") == (0, "")
    assert run("false || echo error; false") == (1, "error\n")


def test_already_existing_directories(flamingo_env):
    import os

    os.mkdir(flamingo_env.settings.CONTENT_ROOT)
    os.mkdir(flamingo_env.settings.OUTPUT_ROOT)
    os.mkdir(flamingo_env.settings.STATIC_ROOT)

    flamingo_env.build()
