from functools import partial
from asyncio import Future
import logging
import types
import code
import os

from aiohttp.web import FileResponse, Response
from aiohttp_json_rpc import JsonRpc

from flamingo.server.build_environment import BuildEnvironment
from flamingo.server.exporter import ContentExporter, History
from flamingo.server.watcher import DiscoveryWatcher, Flags
from flamingo.core.utils.aiohttp import no_cache
from flamingo.core.data_model import QUOTE_KEYS
from flamingo.core.utils.pprint import pformat
from flamingo.core.settings import Settings
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
                 rpc_max_workers=4, logger=default_logger):

        self.app = app
        self.settings_paths = settings
        self.loop = loop or app.loop
        self.logger = logger

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

            # setup settings
            self.logger.debug('setup settings')
            self.settings = Settings()

            for module in self.settings_paths:
                self.logger.debug("add '%s' to settings", module)
                self.settings.add(module)

            # setup build environment
            self.logger.debug('setup build environment')
            self.build_environment = BuildEnvironment(self.settings)
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
        self.watcher.shutdown()
        self.rpc.worker_pool.shutdown()

    def notify_sync(self, topic, message, wait=False):
        self.rpc.worker_pool.run_sync(
            partial(self.rpc.notify, topic, message), wait=True,
        )

    # locking #################################################################
    def lock(self):
        self.logger.debug('locking server')
        self._locked = True

    def unlock(self):
        self.logger.debug('unlocking server')

        self._locked = False

        while len(self._pending_locks) > 0:
            future = self._pending_locks.pop()
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

                self.notify_sync(
                    'messages',
                    '<span class="important">{}</span> changed'.format(path),
                )

        if code_event:
            self.notify_sync('messages', 'setup new context...')

            self.setup()

            self.notify_sync('messages', 'setup successful')

            self.notify_sync('status', {
                'changed_paths': '*',
            })

            return

        # notifications
        for flags, path in events:
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

            self.notify_sync(
                'messages',
                '<span class="important">{}</span> {}'.format(path, action),
            )

        # rebuild
        if paths:
            self.notify_sync('messages', 'rebuilding...')
            self.build_environment.build(paths)
            self.notify_sync('messages', 'rebuilding successful')

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
            self.notify_sync('status', {
                'changed_paths': changed_paths,
            })

    def handle_watcher_notifications(self, flags, message):
        self.notify_sync('messages', message)
