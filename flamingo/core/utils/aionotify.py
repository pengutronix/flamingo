import aionotify
import asyncio
import logging
import os


class RecursiveWatcher:
    def __init__(self, path, flags=None, loop=None, logger=None):
        self.path = path

        self.flags = flags or (aionotify.Flags.MODIFY |
                               aionotify.Flags.CREATE |
                               aionotify.Flags.DELETE)

        self.loop = loop or asyncio.get_event_loop()
        self.logger = logger or logging
        self.watcher = aionotify.Watcher()

    def watch(self, path):
        # FIXME: this should not be necessary
        if path in self.watcher.requests:
            return

        self.logger.debug('watch %s', path)
        self.watcher.watch(path, self.flags)

    def unwatch(self, path):
        self.logger.debug('unwatch %s', path)

        try:
            self.watcher.unwatch(path)

        except IOError:
            self.logger.debug('IOError', exc_info=True)

            # FIXME: this should not be necessary
            del self.watcher.aliases[self.watcher.descriptors[path]]
            del self.watcher.descriptors[path]
            del self.watcher.requests[path]

    async def setup(self):
        self.watch(self.path)

        for root, dirs, files in os.walk(self.path):
            for i in dirs:
                self.watch(os.path.join(root, i))

        return await self.watcher.setup(self.loop)

    def path_is_valid(self, path):
        if not os.path.exists(path):
            return False

        basename = os.path.basename(path)

        if basename.startswith('.'):
            return False

        if basename.endswith('~'):
            return False

        return True

    async def get_file(self):
        while True:
            event = await self.watcher.get_event()
            path = os.path.join(event.alias, event.name)
            flags = aionotify.Flags.parse(event.flags)

            if aionotify.Flags.ISDIR in flags:
                if aionotify.Flags.CREATE in flags:
                    self.watch(path)

                elif aionotify.Flags.DELETE in flags:
                    self.unwatch(path)

            elif self.path_is_valid(path):
                return path
