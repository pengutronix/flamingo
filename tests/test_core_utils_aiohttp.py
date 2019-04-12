async def test_DirectoryExporter(aiohttp_client, tmp_build_env):
    def create_app(loop):
        from aiohttp.web import Application

        from flamingo.core.utils.aiohttp import DirectoryExporter

        exporter = DirectoryExporter(tmp_build_env.path)

        prefixed_exporter = DirectoryExporter(tmp_build_env.path,
                                              prefix='/output/')

        app = Application(loop=loop)
        app.router.add_route('*', '/output/{path_info:.*}', prefixed_exporter)
        app.router.add_route('*', '/{path_info:.*}', exporter)

        return app

    # setup client
    client = await aiohttp_client(create_app)

    # setup files
    tmp_build_env.write('/index.html', '1')
    tmp_build_env.write('/en/about/index.html', '2')

    # test without prefix
    assert await (await client.get('/index.html')).text() == '1'
    assert await (await client.get('/en/about/index.html')).text() == '2'

    # test with prefix
    assert await (await client.get('/output/index.html')).text() == '1'

    assert await (
        await client.get('/output/en/about/index.html')).text() == '2'
