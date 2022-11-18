from traceback import format_exception
from datetime import datetime
from textwrap import indent
import hashlib
import logging

from flamingo.core.utils.cli import color


class RPCHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loggers = []
        self.buffer_max_size = 2500
        self.internal_level = None

        self.rpc = None
        self.server = None

        self._setup(initial=True)

    def _setup(self, initial=False):
        if initial:
            self.logger = {}

        self.buffer = []

        self.stats = {
            'debug': 0,
            'info': 0,
            'warning': 0,
            'error': 0,
            'critical': 0,
        }

    def _notify(self, records=None, initial=False):
        if not self.rpc:
            return

        self.rpc.notify('log', {
            'initial': initial,
            'stats': self.stats,
            'logger': self.logger,
            'records': records or [],
        })

    def handle(self, record):
        if self.internal_level and record.levelno < self.internal_level:
            return

        # filter exceptions that flamingo server handles it self
        if record.exc_info:

            # OSErrors
            if (isinstance(record.exc_info[1], OSError) and
               record.exc_info[1].errno in (13, 98)):

                return

            # event loop exceptions
            elif (isinstance(record.exc_info[1], RuntimeError) and
                  record.exc_info[1].args[0] == 'Event loop is closed'):

                return

        # add record to ring buffer
        time_stamp = datetime.fromtimestamp(record.created)
        time_stamp_str = time_stamp.strftime('%H:%M:%S.%f')

        record_args = {
            'time': time_stamp_str,
            'name': record.name,
            'level': record.levelname.lower(),
            'message': record.getMessage(),
            'content_path': '',
            'hook': '',
        }

        # filter log if self.loggers is set
        if self.loggers and record_args['name'] not in self.loggers:
            return

        # find current hook name and content path
        if (self.server and
           self.server.build_environment and
           self.server.build_environment.context):

            context = self.server.build_environment.context

            if context.content:
                record_args['content_path'] = context.content['path']

            if context.plugins:
                plugins = self.server.build_environment.context.plugins

                record_args['hook'] = plugins.running_hook

                if plugins.running_hook == 'media_added':
                    record_args['content_path'] = plugins.content['path']

        # exc_info
        if record.exc_info:
            record_args['message'] = '{}\n{}'.format(
                record_args['message'],
                indent(
                    ''.join(format_exception(*record.exc_info))[:-1],
                    prefix='  ',
                ),
            )

        self.buffer.append(record_args)
        self.stats[record_args['level']] += 1

        # buffer rotation
        buffer_size = len(self.buffer)

        if buffer_size > self.buffer_max_size:
            # update stats
            old_records = self.buffer[:buffer_size-self.buffer_max_size]

            for old_record_args in old_records:
                self.stats[old_record_args['level']] -= 1

            # update buffer
            self.buffer = self.buffer[buffer_size-self.buffer_max_size:]

        # logger hash
        # this is necessary for the frontend stylesheet generating
        if record_args['name'] not in self.logger:
            self.logger[record_args['name']] = 'logger_{}'.format(
                hashlib.md5(record_args['name'].encode()).hexdigest())

        record_args['id'] = self.logger[record_args['name']]

        # print record to stdout
        color_args = {}

        message = '{}:{}:{}'.format(
            record_args['level'].upper(),
            record_args['name'],
            record_args['message'],
        )

        if record.levelname == 'DEBUG':
            color_args = {
                'color': 'green',
            }

        elif record.levelname == 'WARNING':
            color_args = {
                'color': 'yellow',
            }

        elif record.levelname == 'ERROR':
            color_args = {
                'color': 'red',
                'style': 'bright',
            }

        elif record.levelname == 'CRITICAL':
            color_args = {
                'color': 'white',
                'background': 'red',
                'style': 'bright',
            }

        print(color(message, **color_args))

        self._notify(records=[record_args])

    async def setup_log(self, request):
        return {
            'stats': self.stats,
            'logger': self.logger,
            'records': self.buffer,
        }

    async def clear_log(self, request):
        self._setup(initial=False)
        self._notify()

        return True

    def filter(self, paths):
        hooks = [
            'contents_parsed',
            'pre_build',
            'post_build',
            'render_content',
            'render_media_content',
        ]

        for record in self.buffer[::]:
            if (record['hook'] in hooks or
               record['content_path'] in paths):

                self.buffer.remove(record)
                self.stats[record['level']] -= 1

        self._notify(records=self.buffer, initial=True)
