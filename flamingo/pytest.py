import pytest


@pytest.fixture
def flamingo_dummy_context():
    from flamingo.core.data_model import ContentSet, Content
    from flamingo.core.settings import Settings
    from flamingo.core.context import Context

    class DummyContext(Context):
        def __init__(self, settings, contents=None):
            super().__init__(settings)

            self.settings = settings
            self.contents = contents or ContentSet()
            self.content = Content(path='<string>')

    return DummyContext(settings=Settings())


@pytest.fixture
def flamingo_env():
    from tempfile import TemporaryDirectory
    import os

    from flamingo.core.settings import Settings
    from flamingo.core.context import Context

    class TempBuildEnv:
        def __init__(self, path):
            self.path = path
            self.context = None

            # setup settings
            self.settings = Settings()

            self.settings.DEDENT_INPUT = True

            self.settings.CONTENT_ROOT = os.path.join(
                path, self.settings.CONTENT_ROOT)

            self.settings.OUTPUT_ROOT = os.path.join(
                path, self.settings.OUTPUT_ROOT)

            self.settings.STATIC_ROOT = os.path.join(
                path, self.settings.STATIC_ROOT)

            # setup machine readable theme
            self.settings.THEME_PATHS = [
                os.path.join(path, 'theme'),
            ]

            self.write(
                '/theme/templates/page.html',
                '{{ content.content_title }}\n{{ content.content_body }}'
            )

        def setup(self, context_class=Context):
            if not os.path.exists(self.settings.CONTENT_ROOT):
                os.makedirs(self.settings.CONTENT_ROOT)

            if not os.path.exists(self.settings.OUTPUT_ROOT):
                os.makedirs(self.settings.OUTPUT_ROOT)

            if not os.path.exists(self.settings.MEDIA_ROOT):
                os.makedirs(self.settings.MEDIA_ROOT)

            if not os.path.exists(self.settings.STATIC_ROOT):
                os.makedirs(self.settings.STATIC_ROOT)

            self.context = context_class(self.settings)

        def build(self, *args, **kwargs):
            if not self.context:
                self.setup()

            self.context.build()

        def gen_path(self, path):
            assert path.startswith('/'), 'path should be absolute'

            return os.path.join(self.path, path[1:])

        def read(self, path, *args, mode='r', **kwargs):
            return open(self.gen_path(path), *args, mode=mode, **kwargs).read()

        def write(self, path, text, *args, mode='w+', **kwargs):
            path = self.gen_path(path)
            dirname = os.path.dirname(path)

            if not os.path.exists(dirname):
                os.makedirs(dirname)

            return open(path, *args, mode=mode, **kwargs).write(text)

        def exists(self, path):
            return os.path.exists(self.gen_path(path))

    with TemporaryDirectory() as tmp_dir:
        yield TempBuildEnv(tmp_dir)


@pytest.fixture
def run():
    from subprocess import check_output, CalledProcessError, STDOUT
    import logging
    import os

    def _run(command, cwd=None, clean_env=False, logger=logging):
        cwd = cwd or os.getcwd()
        env = None

        if clean_env:
            env = {
                'PATH': os.environ['PATH'].split(':', 1)[1],
            }

        logger.debug("running '%s' in '%s'", command, cwd)

        returncode = 0

        try:
            output = check_output(
                command,
                shell=True,
                stderr=STDOUT,
                cwd=cwd,
                env=env,
                executable='/bin/bash',
            ).decode()

        except CalledProcessError as e:
            returncode = e.returncode
            output = e.output.decode()

            logger.error('returncode: %s output: \n%s', returncode, output)

        return returncode, output

    return _run
