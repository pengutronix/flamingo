

How to write a parser
=====================

All parsers should inherit from ``flamingo.core.parser.ContentParser``. This
class contains all logic how to handle meta data. A parser needs to have an
attribute ``FILE_EXTENSIONS`` which has to be a list of strings with extensions
this parser is capable of.

Every parser needs a method ``parse()``. When a file gets parsed ``parse()``
gets the content of a file and a ``flamingo.Content`` object passed in.

.. code-block:: python

    from flamingo.core.parser import ContentParser


    class TxtParser(ContentParser):
        FILE_EXTENSIONS = ['txt']

        def parse(self, file_content, content):
            # ContentParser.parse_meta_data takes the file content and the
            # content object, extracts the YAML meta data of the file, sets
            # them in the content object and returns the remaining markup
            # (in this case simple text that is no YAML)
            #
            # ContentParser.parse_meta_data sets content['content_offset']
            # to the offset at which the actual content (txt) begins
            # 
            # You don't have to call this method if your file type should not
            # support meta data.
            markup_string = self.parse_meta_data(file_content, content)

            # every parser should set at least 'content_title' and
            # 'content_body' for compatibility between plugins
            content['content_title'] = 'Title'
            content['content_body'] = markup_string


    class Txt:
        def parser_setup(self, context):
            context.parser.add_parser(YamlParser(context))
