async def test_DirectoryExporter(aiohttp_client, flamingo_env):
    def create_app(loop):
        from aiohttp.web import Application

        from flamingo.core.utils.aiohttp import DirectoryExporter

        exporter = DirectoryExporter(flamingo_env.path)

        prefixed_exporter = DirectoryExporter(flamingo_env.path,
                                              prefix='/output/')

        exporter.show_index = False
        prefixed_exporter.show_index = False

        app = Application(loop=loop)
        app.router.add_route('*', '/output/{path_info:.*}', prefixed_exporter)
        app.router.add_route('*', '/{path_info:.*}', exporter)

        return app

    # setup client
    client = await aiohttp_client(create_app)

    # setup files
    flamingo_env.write('/index.html', '1')
    flamingo_env.write('/en/about/index.html', '2')

    # test without prefix
    assert await (await client.get('/index.html')).text() == '1'
    assert await (await client.get('/en/about/index.html')).text() == '2'

    # test with prefix
    assert await (await client.get('/output/index.html')).text() == '1'

    assert await (
        await client.get('/output/en/about/index.html')).text() == '2'


async def test_DirectoryExporter_show_index(aiohttp_client):
    from tempfile import TemporaryDirectory
    import os

    from aiohttp.web import Application

    from flamingo.core.utils.aiohttp import DirectoryExporter

    def create_app(loop, path):
        exporter = DirectoryExporter(path)
        exporter.show_index = True

        app = Application(loop=loop)
        app.router.add_route('*', '/{path_info:.*}', exporter)

        return app

    with TemporaryDirectory() as tmp_dir:
        client = await aiohttp_client(create_app, tmp_dir)

        # test directory listing
        os.mkdir(os.path.join(tmp_dir, 'directory1'))
        open(os.path.join(tmp_dir, 'directory1/file-1'), 'w+').write('1')
        open(os.path.join(tmp_dir, 'directory1/file-2'), 'w+')

        response_text = await (await client.get('/directory1')).text()

        assert '<h1>Index of /directory1</h1>' in response_text
        assert '<a href="/directory1/file-1">' in response_text
        assert '<a href="/directory1/file-2">' in response_text

        assert await (await client.get('/directory1/file-1')).text() == '1'

        # test index.html serving
        os.mkdir(os.path.join(tmp_dir, 'directory2'))
        open(os.path.join(tmp_dir, 'directory2/index.html'), 'w+').write('2')

        assert await (await client.get('/directory2')).text() == '2'
