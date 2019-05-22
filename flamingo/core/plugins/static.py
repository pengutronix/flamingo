import logging
import os

from flamingo.core.utils.files import cp

logger = logging.getLogger('flamingo.core.static')


class Static:
    def post_build(self, context):
        if context.settings.CONTENT_PATHS:
            return

        for static_dir in context.templating_engine.find_static_dirs():
            for root, dirs, files in os.walk(static_dir):
                for f in files:
                    source = os.path.join(root, f)

                    destination = os.path.join(
                        context.settings.STATIC_ROOT,
                        os.path.relpath(root, static_dir),
                        f,
                    )

                    cp(context=context, source=source, destination=destination,
                       logger=logger)
