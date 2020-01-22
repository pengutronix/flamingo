from functools import partial
from asyncio import Future
import logging
import types
import code
import json
import os

from aiohttp.web import FileResponse, Response

from flamingo.server.frontend_controller import FrontendController
from flamingo.legacy_server.watcher import DiscoveryWatcher, Flags
from flamingo.server.build_environment import BuildEnvironment
from flamingo.legacy_server.exporter import ContentExporter
from flamingo.core.utils.aiohttp import no_cache
from flamingo.core.data_model import QUOTE_KEYS
from flamingo.core.utils.pprint import pformat
from flamingo.server.exporter import History
from flamingo.core.settings import Settings
from flamingo.server.rpc import JsonRpc
from flamingo.core.data_model import Q

try:
    import IPython
    from traitlets.config import Config

    IPYTHON = True

except ImportError:
    IPYTHON = False

STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'static')
INDEX_HTML = os.path.join(STATIC_ROOT, 'index.html')

default_logger = logging.getLogger('flamingo.server')


class Server:
    def __init__(self, app, settings, rpc_logging_handler, loop=None,
                 rpc_max_workers=6, logger=default_logger):

        self.app = app
        self.settings_paths = settings
        self.loop = loop or app.loop
        self.logger = logger
        self.frontend_controller = FrontendController(self)

        # locks
        self._shell_running = False
        self._locked = True
        self._pending_locks = []

        # setup rpc
        self.rpc = JsonRpc(loop=self.loop, max_workers=rpc_max_workers)
        self.rpc_logging_handler = rpc_logging_handler
        self.rpc_logging_handler.set_rpc(self.rpc)

        self.app['rpc'] = self.rpc

        # setup rpc methods and topics
        self.rpc.add_topics(
            ('status',),
            ('log',),
            ('messages',),
            ('commands',),
        )

        self.rpc.add_methods(
            ('', self.get_meta_data),
            ('', self.start_shell),
            ('', self.rpc_logging_handler.setup_log),
            ('', self.rpc_logging_handler.clear_log),
        )

        # setup aiohttp
        app.router.add_route('*', '/_flamingo/rpc/', self.rpc)

        app.router.add_route(
            '*', '/_flamingo/settings.js', self.frontend_settings)

        app.router.add_route(
            '*', '/_flamingo/static/{path_info:.*}', self.static)

        app.router.add_route('*', '/{path_info:.*}', self.serve)

        # setup context
        loop.run_in_executor(
            self.rpc.worker_pool.executor,
            partial(self.setup, initial=True),
        )

    def setup(self, initial=False):
        self.lock()

        try:
            if not initial:
                self.logger.debug('shutting down watcher')
                self.watcher.shutdown()

            else:
                self.rpc.start_notification_worker(1)

            # setup settings
            self.logger.debug('setup settings')
            self.settings = Settings()

            for module in self.settings_paths:
                self.logger.debug("add '%s' to settings", module)
                self.settings.add(module)

            # setup build environment
            self.logger.debug('setup build environment')
            self.build_environment = BuildEnvironment(self)
            self.context = self.build_environment.context

            # setup content exporter
            self.logger.debug('setup content exporter')
            self.history = History()
            self.content_exporter = ContentExporter(self.context, self.history)

            # setup watcher
            if initial:
                self.logger.debug('setup watcher')
                self.watcher = DiscoveryWatcher(context=self.context)

            self.logger.debug('setup watcher task')

            self.watcher.context = self.context

            if self.loop.is_running():
                self.loop.run_in_executor(
                    self.rpc.worker_pool.executor,
                    self.watcher.watch,
                    self.handle_watcher_events,
                    self.handle_watcher_notifications,
                )

        except Exception:
            self.logger.error('setup failed', exc_info=True)

            return False

        finally:
            self.unlock()

        return True

    def shutdown(self):
        if hasattr(self, 'watcher'):
            self.watcher.shutdown()

        self.rpc.stop_notification_worker()
        self.rpc.worker_pool.shutdown()

    # locking #################################################################
    def lock(self):
        self.logger.debug('locking server')
        self._locked = True

    def unlock(self):
        self.logger.debug('unlocking server')

        self._locked = False

        while len(self._pending_locks) > 0:
            future = self._pending_locks.pop()

            if not future.cancelled():
                future.set_result(True)

        self.logger.debug('server is unlocked')

    async def await_unlock(self):
        if self._locked:
            future = Future()
            self._pending_locks.append(future)

            self.logger.debug('waiting for lock release')

            await future

        return

    # views ###################################################################
    @no_cache()
    async def frontend_settings(self, request):
        settings = {
            'log_buffer_max_size': self.rpc_logging_handler.buffer_max_size,
            'log_level': self.rpc_logging_handler.internal_level,
        }

        settings_string = "var server_settings = JSON.parse('{}');".format(
            json.dumps(settings))

        return Response(text=settings_string)

    @no_cache()
    async def static(self, request):
        await self.await_unlock()

        path = os.path.join(
            STATIC_ROOT,
            os.path.relpath(request.path, '/_flamingo/static/'),
        )

        if not os.path.exists(path):
            return Response(text='404: not found', status=404)

        return FileResponse(path)

    @no_cache()
    async def serve(self, request):
        await self.await_unlock()

        extension = os.path.splitext(request.path)[1] or '.html'

        if extension == '.html' and 'Referer' not in request.headers:
            return FileResponse(INDEX_HTML)

        return await self.content_exporter(request)

    # rpc methods #############################################################
    def get_meta_data(self, request, url):
        meta_data = {
            'meta_data': [],
            'template_context': [],
            'settings': [],
        }

        try:
            content = self.context.contents.get(url=url)

        except Exception:
            content = None

        if not content:
            url = os.path.join(url, 'index.html')

            try:
                content = self.context.contents.get(url=url)

            except Exception:
                return {
                    'meta_data': [],
                    'template_context': [],
                    'settings': [],
                }

        meta_data['meta_data'] = sorted([
            {'key': k, 'value': pformat(v), 'type': type(v).__name__}
            for k, v in content.data.items() if k not in QUOTE_KEYS
        ], key=lambda v: v['key'])

        meta_data['template_context'] = sorted([
            {'key': k, 'value': pformat(v), 'type': type(v).__name__}
            for k, v in (content['template_context'] or {}).items()
        ], key=lambda v: v['key'])

        for key, value in self.context.settings._attrs.items():
            if key.startswith('_') or key in ('add', 'modules', ):
                continue

            value_type = type(value)

            if value_type in (types.ModuleType, types.MethodType):
                continue

            meta_data['settings'].append({
                'key': key,
                'value': pformat(value),
                'type': value_type.__name__,
            })

        meta_data['settings'] = sorted(meta_data['settings'],
                                       key=lambda v: v['key'])

        return meta_data

    def start_shell(self, request=None, history=False):
        if self._shell_running:
            return

        self._shell_running = True

        try:
            if IPYTHON:
                config = Config()

                if not history:
                    # this is needed to avoid sqlite errors while running in
                    # a multithreading environment
                    config.HistoryAccessor.enabled = False

                context = self.context  # NOQA
                history = self.history  # NOQA
                frontend = self.frontend_controller  # NOQA

                IPython.embed(config=config)

            else:
                code.interact(local=globals())

        finally:
            self._shell_running = False

    # watcher events ##########################################################
    def handle_watcher_events(self, events):
        paths = []
        code_event = False
        non_content_event = False
        changed_paths = []

        # check if code changed
        for flags, path in events:
            if Flags.CODE in flags:
                code_event = True

                self.rpc.notify(
                    'messages',
                    '<span class="important">{}</span> modified'.format(path),
                )

        if code_event:
            if self.context.settings.LIVE_SERVER_RESETUP_ON_CODE_CHANGE:
                self.rpc.notify('messages', 'setup new context...')

                self.setup()

                self.rpc.notify('messages', 'setup successful')

                self.rpc.notify('status', {
                    'changed_paths': '*',
                })

                return

            else:
                self.rpc.notify('messages', 'please restart')

        # notifications
        for flags, path in events:
            if Flags.CODE in flags:
                continue

            if Flags.TEMPLATE in flags or Flags.STATIC in flags:
                non_content_event = True

            elif(os.path.splitext(path)[1].lower() in
                 ('.jpg', '.jpeg', '.png', '.svg', )):

                non_content_event = True

            elif Flags.CONTENT in flags:
                paths.append(
                    os.path.relpath(path, self.context.settings.CONTENT_ROOT)
                )

            action = 'modified'

            if Flags.CREATE in flags:
                action = 'created'

            elif Flags.DELETE in flags:
                action = 'deleted'

            self.rpc.notify(
                'messages',
                '<span class="important">{}</span> {}'.format(path, action),
            )

        # rebuild
        if paths:
            self.rpc.notify('messages', 'rebuilding...')
            self.build_environment.build(paths)
            self.rpc.notify('messages', 'rebuilding successful')

            changed_paths = [
                '/' + i for i in self.context.contents.filter(
                    Q(path__in=paths) | Q(i18n_path__in=paths)
                ).values('output')
            ]

            if changed_paths:
                for path in changed_paths[::]:
                    if path.endswith('index.html'):
                        clear_path = os.path.dirname(path)

                        changed_paths.append(clear_path)
                        changed_paths.append(clear_path + '/')

        # changed paths
        if non_content_event:
            changed_paths.append('*')

        if changed_paths:
            self.rpc.notify('status', {
                'changed_paths': changed_paths,
            })

    def handle_watcher_notifications(self, flags, message):
        self.rpc.notify('messages', message)
