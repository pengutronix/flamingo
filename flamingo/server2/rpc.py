from concurrent.futures import ThreadPoolExecutor
from asyncio import run_coroutine_threadsafe
from queue import Queue, Empty

from aiohttp_json_rpc.protocol import encode_notification
from aiohttp_json_rpc import JsonRpc as _JsonRpc


class JsonRpc(_JsonRpc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.notification_queue = Queue()
        self.executor = None
        self.worker = 0

    async def send_notification(self, client, notification):
        if client.ws._writer.transport.is_closing():
            return

            self.clients.remove(client)
            await client.ws.close()

        try:
            await client.ws.send_str(notification)

        except Exception:
            pass

    def notification_worker(self):
        self.logger.debug('notification worker started')

        while self._running:
            try:
                topic, data = self.notification_queue.get(timeout=1)

            except Empty:
                continue

            notification = None

            for client in self.filter(topic):
                if not notification:
                    notification = encode_notification(topic, data)

                if self.loop.is_running():
                    run_coroutine_threadsafe(
                        self.send_notification(client, notification),
                        loop=self.loop,
                    )

        self.logger.debug('notification worker stopped')

    def start_notification_worker(self, worker=1):
        self.worker = worker
        self.executor = ThreadPoolExecutor(max_workers=worker)
        self._running = True

        for i in range(worker):
            self.loop.run_in_executor(
                self.executor,
                self.notification_worker,
            )

    def stop_notification_worker(self):
        self._running = False

        if self.executor:
            self.executor.shutdown(wait=True)

    def notify(self, topic, data):
        self.notification_queue.put(
            (topic, data, ),
        )
