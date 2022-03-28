from subprocess import check_output, CalledProcessError, STDOUT
from tempfile import TemporaryDirectory
import logging
import os
import asyncio

from aiohttp.web import Application
import pytest

from flamingo.core.data_model import ContentSet, Content
from flamingo.server.logging import RPCHandler
from flamingo.core.settings import Settings
from flamingo.server.server import Server
from flamingo.core.context import Context


class FlamingoDummyContext(Context):
    def __init__(self, settings, contents=None):
        super().__init__(settings)

        self.settings = settings
        self.contents = contents or ContentSet()
        self.content = Content(path='<string>')


class FlamingoBuildEnvironment:
    def __init__(self):
        self.tmp_dir = TemporaryDirectory()
        self.path = self.tmp_dir.name
        self.context = None

        # setup settings
        self.settings = Settings()

        self.settings.DEDENT_INPUT = True

        self.settings.CONTENT_ROOT = os.path.join(
            self.path, self.settings.CONTENT_ROOT)

        self.settings.OUTPUT_ROOT = os.path.join(
            self.path, self.settings.OUTPUT_ROOT)

        self.settings.STATIC_ROOT = os.path.join(
            self.path, self.settings.STATIC_ROOT)

        # setup machine readable theme
        self.settings.THEME_PATHS = [
            os.path.join(self.path, 'theme'),
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

    def touch(self, path):
        self.write(path, '')

        return self.gen_path(path)

    def exists(self, path):
        return os.path.exists(self.gen_path(path))


class FlamingoServerBuildEnvironment(FlamingoBuildEnvironment):
    def __init__(self, aiohttp_client):
        self._aiohttp_client = aiohttp_client

        super().__init__()

        self.rpc_logging_handler = None
        self.app = None
        self.server = None
        self.client = None
        self.loop = asyncio.get_event_loop()

    def build(self, *args, **kwargs):
        pass

    def setup(self):
        super().setup(context_class=FlamingoDummyContext)

    async def setup_live_server(self, **args):
        def _create_app(loop):
            self.rpc_logging_handler = RPCHandler(level=logging.DEBUG)
            self.app = Application()

            self.app.on_shutdown.append(self.shutdown_live_server)

            server_args = {
                'app': self.app,
                'loop': loop,
                'max_workers': 4,
                'settings_paths': [],
                'settings': self.settings,
                'overlay': False,
                'browser_caching': True,
                'watcher_interval': 0.25,
                'rpc_logging_handler': self.rpc_logging_handler,
                **args,
            }

            self.server = Server(**server_args)
            self.server.setup(initial=True)

            return self.app

        self.setup()
        self.client = await self._aiohttp_client(_create_app(self.loop))

    async def shutdown_live_server(self, app=None):
        if self.server:
            self.server.shutdown()


@pytest.fixture
def flamingo_dummy_context():
    return FlamingoDummyContext(settings=Settings())


@pytest.fixture
def flamingo_env():
    return FlamingoBuildEnvironment()


@pytest.fixture
async def flamingo_server_env(flamingo_env, aiohttp_client):
    return FlamingoServerBuildEnvironment(aiohttp_client)


@pytest.fixture
def run():
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
