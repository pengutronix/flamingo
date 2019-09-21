import json
import os


class ReadTheDocs:
    THEME_PATHS = [
        os.path.join(os.path.dirname(__file__), 'theme'),
    ]

    def templating_engine_setup(self, context, templating_engine):
        context.settings.EXTRA_CONTEXT['json'] = json

    def contents_parsed(self, context):
        context.contents.add(
            template='rtd/search.html',
            output='search.html',
        )
