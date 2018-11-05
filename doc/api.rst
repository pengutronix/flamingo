# vim: ts=4 sw=4 expandtab ft=rst

Plugin
======


.. codeblock:: python

class FlamingoPlugin:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def parser_setup(self, context):
        pass

    def content_parsed(self, context, content):
        pass

    def contents_parsed(self, context):
        pass
