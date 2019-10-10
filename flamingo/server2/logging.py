from traceback import format_exception
from datetime import datetime
from textwrap import indent
import hashlib
import logging


class RPCHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.buffer = []
        self.buffer_max_size = 2500
        self.logger = {}

        self.rpc = None
        self.internal_level = None

    def set_rpc(self, rpc):
        self.rpc = rpc

    def set_internal_level(self, level):
        self.internal_level = level

    def handle(self, record):
        # add record to ring buffer
        time_stamp = datetime.fromtimestamp(record.created)
        time_stamp_str = time_stamp.strftime('%H:%M:%S.%f')

        record_args = {
            'time': time_stamp_str,
            'name': record.name,
            'level': record.levelname.lower(),
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
            self.logger[record_args['name']] = 'logger_{}'.format(
                hashlib.md5(record_args['name'].encode()).hexdigest())

        record_args['id'] = self.logger[record_args['name']]

        # print record to stdout
        if self.internal_level and record.levelno >= self.internal_level:
            print('{}:{}:{}'.format(
                record_args['level'],
                record_args['name'],
                record_args['message'],
            ))

        # send rpc notification
        if self.rpc:
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
