from flamingo.core.data_model import ContentSet, Content
from flamingo.core.utils.pprint import pformat


class History:
    def __init__(self):
        self.clear()

    def clear(self):
        self.history = []
        self.contents = ContentSet()

    def append(self, item):
        self.history.append(item)

        if isinstance(item, Content):
            self.contents.add(item)

    def __iter__(self):
        return self.history.__iter__()

    def __repr__(self):
        return pformat(self.history)
