def test_hooks(flamingo_env):
    import flamingo

    state = []

    @flamingo.hook("parser_setup")
    def parser_setup(context):
        state.append(("parser_setup", context))

    @flamingo.hook("templating_engine_setup")
    def templating_engine_setup(context, templating_engine):
        state.append(("templating_engine_setup", context, templating_engine))

    @flamingo.hook("content_parsed")
    def content_parsed(context, content):
        state.append(("content_parsed", context))

    @flamingo.hook("contents_parsed")
    def contents_parsed(context):
        state.append(("contents_parsed", context))

    @flamingo.hook("context_setup")
    def context_setup(context):
        state.append(("context_setup", context))

    @flamingo.hook("pre_build")
    def pre_build(context):
        state.append(("pre_build", context))

    @flamingo.hook("post_build")
    def post_build(context):
        state.append(("post_build", context))

    flamingo_env.settings.parser_setup = parser_setup
    flamingo_env.settings.templating_engine_setup = templating_engine_setup
    flamingo_env.settings.content_parsed = content_parsed
    flamingo_env.settings.contents_parsed = contents_parsed
    flamingo_env.settings.context_setup = context_setup
    flamingo_env.settings.pre_build = pre_build
    flamingo_env.settings.post_build = post_build

    # we need at least one content file to reach hook 'content_parsed'
    flamingo_env.write(
        "/content/home.rst",
        """
    author: me


    Home
    ====

    Hello world
    """,
    )

    flamingo_env.build()

    assert len(state) == 7

    assert state[0] == ("parser_setup", flamingo_env.context)

    assert state[1] == ("templating_engine_setup", flamingo_env.context, flamingo_env.context.templating_engine)

    assert state[2] == ("content_parsed", flamingo_env.context)
    assert state[3] == ("contents_parsed", flamingo_env.context)
    assert state[4] == ("context_setup", flamingo_env.context)
    assert state[5] == ("pre_build", flamingo_env.context)
    assert state[6] == ("post_build", flamingo_env.context)
