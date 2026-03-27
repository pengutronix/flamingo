def test_Feeds(flamingo_env):
    flamingo_env.settings.PLUGINS = ["flamingo.plugins.Feeds"]
    flamingo_env.settings.FEEDS_DOMAIN = "www.example.org"

    flamingo_env.settings.FEEDS = [
        {
            "id": "www.example.org",
            "title": "Example.org",
            "type": "atom",
            "output": "en/feed.atom.xml",
            "lang": "en",
            "contents": lambda ctx: ctx.contents,
            "entry-id": lambda content: content["path"],
            "updated": lambda content: "1970-01-01 00:00:00+01:00",
        },
    ]

    flamingo_env.write(
        "/content/blog-post.html",
        """
    title: blog-post


    Blog post
    =========
    """,
    )

    flamingo_env.build()
