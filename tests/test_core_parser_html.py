def test_raw_html(flamingo_env):
    flamingo_env.write(
        "/content/test1.html",
        """
    raw_html: True


    <h1>Title</h1>
    <p>Content</p>
    """,
    )

    flamingo_env.write(
        "/content/test2.html",
        """
    raw_html: False


    <h1>Title</h1>
    <p>Content</p>
    """,
    )

    flamingo_env.build()

    content1 = flamingo_env.context.contents.get(path="test1.html")

    assert content1["content_title"] == ""
    assert content1["content_body"].strip().startswith("<h1>Title</h1>")

    content2 = flamingo_env.context.contents.get(path="test2.html")

    assert content2["content_title"] == "Title"
    assert not content2["content_body"].strip().startswith("<h1>Title</h1>")
