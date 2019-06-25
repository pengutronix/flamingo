import pytest


@pytest.mark.asyncio
async def test_RecursiveWatcher(event_loop):
    from tempfile import TemporaryDirectory
    import asyncio
    import shutil
    import os

    from aionotify import Flags

    from flamingo.core.utils.aionotify import RecursiveWatcher

    watcher_is_set_up = asyncio.Future()
    events = []

    expected_events = [
        ([Flags.CREATE], 'dir-2/file-3', ),
        ([Flags.MODIFY], 'file-1', ),
        ([Flags.CREATE], 'file-2', ),
    ]

    async def catch_events(watcher):
        await watcher.setup()

        watcher_is_set_up.set_result(True)

        while True:
            flags, path = await watcher.get_file()

            if path:
                events.append(
                    (flags, os.path.relpath(path, watcher.path), )
                )

            if len(events) == len(expected_events):
                return

    async def create_events(tmp_dir):
        await watcher_is_set_up

        # directories
        os.mkdir(os.path.join(tmp_dir, 'dir-2'))
        await asyncio.sleep(0.1)

        open(os.path.join(tmp_dir, 'dir-2/file-3'), 'w+')
        await asyncio.sleep(0.1)

        shutil.rmtree(os.path.join(tmp_dir, 'dir-2'))
        await asyncio.sleep(0.1)

        # create invalid paths
        open(os.path.join(tmp_dir, 'file-4'), 'w+')
        os.unlink(os.path.join(tmp_dir, 'file-4'))
        await asyncio.sleep(0.1)

        open(os.path.join(tmp_dir, '.file-5'), 'w+')
        await asyncio.sleep(0.1)

        open(os.path.join(tmp_dir, 'file-6~'), 'w+')
        await asyncio.sleep(0.1)

        # modify
        open(os.path.join(tmp_dir, 'file-1'), 'w').write('foo')
        await asyncio.sleep(0.1)

        # create valid path
        open(os.path.join(tmp_dir, 'file-2'), 'w+')
        await asyncio.sleep(0.1)

    with TemporaryDirectory() as tmp_dir:
        # setup directory structure
        os.mkdir(os.path.join(tmp_dir, 'dir-1'))
        open(os.path.join(tmp_dir, 'file-1'), 'w+')

        # start test
        watcher = RecursiveWatcher(path=tmp_dir, loop=event_loop)

        try:
            await asyncio.gather(
                asyncio.wait_for(catch_events(watcher), 5, loop=event_loop),
                asyncio.wait_for(create_events(tmp_dir), 5, loop=event_loop),
            )

        except asyncio.TimeoutError:
            pass

    assert events == expected_events
