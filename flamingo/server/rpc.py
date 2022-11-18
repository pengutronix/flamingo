from functools import partial
import contextlib
import asyncio
import logging
import json

from aiohttp.web import WebSocketResponse, Response
from aiohttp import WSMsgType

logger = logging.getLogger('flamingo.server.jsonrpc')


class JsonRpc:
    def __init__(self, server):
        self.server = server
        self.websockets = []

        self.loop = self.server.loop

        self.methods = {
            'subscribe': self.subscribe,
            'unsubscribe': self.unsubscribe,
        }

    async def shutdown(self):
        for websocket in self.websockets.copy():
            with contextlib.suppress(Exception):
                await websocket.close()

    # protocol ################################################################
    def decode_message(self, raw_message):
        message_id = None
        method = None
        params = None

        try:
            message = json.loads(raw_message)

            message_id = message['id']
            method = str(message['method'])
            params = message.get('params', None)

            return True, message_id, method, params

        except Exception:
            logger.error(
                "Exception raised while decoding '%s'",
                repr(raw_message),
                exc_info=True,
            )

            return False, message_id, method, params

    def encode_result(self, message_id, result):
        return json.dumps({
            'jsonrpc': '2.0',
            'id': message_id,
            'result': result
        })

    def encode_error(self, message_id, error_code, error_message):
        """
        error codes:
            -32600: RpcInvalidRequestError
            -32601: RpcMethodNotFoundError
            -32602: RpcInvalidParamsError
            -32603: RpcInternalError
            -32700: RpcParseError
        """

        return json.dumps({
            'jsonrpc': '2.0',
            'id': message_id,
            'error': {
                'code': error_code,
                'message': error_message,
            }
        })

    def encode_notification(self, topic, data):
        return json.dumps({
            'jsonrpc': '2.0',
            'method': topic,
            'params': data,
        })

    # rpc methods #############################################################
    async def subscribe(self, params):
        if not isinstance(params, list):
            params = [params]

        return params

    async def unsubscribe(self, params):
        return []

    # websocket helper ########################################################
    async def send_str(self, websocket, string):
        try:
            await websocket.send_str(string)

        except ConnectionResetError:
            # this exception gets handled by aiohttp internally and
            # can be ignored

            pass

    # notifications ###########################################################
    def notify(self, topic, message, wait=False):
        if not self.loop.is_running():
            return None

        message = self.encode_notification(topic, message)

        async def _notify():
            for websocket in self.websockets:
                await self.send_str(websocket, message)

        future = asyncio.run_coroutine_threadsafe(
            _notify(),
            loop=self.loop,
        )

        if wait:
            return future.result()

        return future

    # methods #################################################################
    def add_methods(self, *methods):
        for prefix, method in methods:
            method_name = method.__name__

            self.methods[method_name] = method

    async def handle_raw_message(self, websocket, raw_message):
        success, message_id, method, params = await self.loop.run_in_executor(
            self.server.executor,
            partial(self.decode_message, raw_message),
        )

        async def handle_error():
            error_message = await self.loop.run_in_executor(
                self.server.executor,
                partial(
                    self.encode_error,
                    message_id=message_id,
                    error_code=-32600,
                    error_message='invalid request',
                ),
            )

            return await self.send_str(websocket, error_message)

        if not success or method not in self.methods:
            return await handle_error()

        # run method
        method = self.methods[method]

        # coroutine functions
        if asyncio.iscoroutinefunction(method):
            try:
                result = await method(params)

            except Exception:
                logger.error(
                    'Exception raised while running %s(%s)',
                    repr(method),
                    repr(params),
                    exc_info=True,
                )

                return await handle_error()

        else:
            try:
                result = await self.loop.run_in_executor(
                    self.server.executor,
                    partial(method, params),
                )

            except Exception:
                logger.error(
                    'Exception raised while running %s(%s)',
                    repr(method),
                    repr(params),
                    exc_info=True,
                )

                return await handle_error()

        # send result
        message = await self.loop.run_in_executor(
            self.server.executor,
            partial(
                self.encode_result,
                message_id=message_id,
                result=result,
            ),
        )

        await self.send_str(websocket, message)

    async def __call__(self, http_request):
        if (http_request.method != 'GET' or
           http_request.headers.get('upgrade', '').lower() != 'websocket'):

            return Response(status=405)

        websocket = WebSocketResponse()
        await websocket.prepare(http_request)

        self.websockets.append(websocket)

        try:
            async for message in websocket:
                if message.type == WSMsgType.TEXT:
                    self.loop.create_task(
                        self.handle_raw_message(websocket, message.data),
                    )

                elif message.type == WSMsgType.PING:
                    await websocket.pong()

                elif message.type in (WSMsgType.CLOSED, WSMsgType.ERROR):
                    break

        except asyncio.CancelledError:
            pass

        finally:
            if websocket in self.websockets:
                self.websockets.remove(websocket)

            await websocket.close()

        return websocket
