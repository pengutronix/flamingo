from traceback import format_exception
from datetime import datetime
from textwrap import indent
import logging


class RPCHandler(logging.Handler):
    def __init__(self, rpc, log_level_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rpc = rpc
        self.buffer = []
        self.buffer_max_size = 2500

        self.log_level = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARN,
            'ERROR': logging.ERROR,
            'FATAL': logging.FATAL,
        }[log_level_name]

        self.logger = []

    def handle(self, record):
        # add record to ring buffer
        record_args = {
            'time': str(datetime.fromtimestamp(record.created)),
            'name': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
        }

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

        buffer_size = len(self.buffer)

        if buffer_size > self.buffer_max_size:
            self.buffer = self.buffer[buffer_size-self.buffer_max_size:]

        if record_args['name'] not in self.logger:
            self.logger.append(record_args['name'])

        # print record to stdout
        if record.levelno >= self.log_level:
            print('{}:{}:{}'.format(
                record_args['level'],
                record_args['name'],
                record_args['message'],
            ))

        # send rpc notification
        self.rpc.worker_pool.run_sync(
            self.rpc.notify,
            'log',
            {
                'logger': self.logger,
                'records': [record_args],
            },
            wait=False,
        )

    async def setup_log(self, request):
        request.subscriptions.add('log')

        return {
            'logger': self.logger,
            'records': self.buffer,
        }

    async def clear_log(self, request):
        self.buffer = []

        return True
