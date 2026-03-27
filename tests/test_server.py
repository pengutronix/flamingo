async def test_server(flamingo_server_env):
    flamingo_server_env.write(
        "/content/article.rst",
        """

    Article
    =======

    """,
    )

    await flamingo_server_env.setup_live_server(overlay=False)

    response = await flamingo_server_env.client.get("/article.html")
    text = await response.text()

    assert text.startswith("Article\n")
