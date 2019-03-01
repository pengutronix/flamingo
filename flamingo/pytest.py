import pytest


@pytest.fixture
def dummy_context():
    from flamingo.core.data_model import ContentSet
    from flamingo.core.settings import Settings
    from flamingo.core.context import Context

    class DummyContext(Context):
        def __init__(self, settings, contents=None):
            self.settings = settings
            self.contents = contents or ContentSet()

    return DummyContext(settings=Settings())
