import logging
import os

from flamingo.core.data_model import ContentSet, Content

logger = logging.getLogger('flamingo.core.media')


def add_media(context, content, name, **extra_meta_data):
    # path
    if name.startswith('/'):
        path = name[1:]

    else:
        path = os.path.join(os.path.dirname(content['path']), name)

    path = os.path.normpath(path)

    # output
    if name.startswith('/'):
        output = os.path.join(context.settings.MEDIA_ROOT, name[1:])

    else:
        output = os.path.join(
            context.settings.MEDIA_ROOT,
            os.path.dirname(content['path']),
            os.path.basename(name),
        )

    # url
    url = '/' + output

    # content['media']
    if not content['media']:
        content['media'] = ContentSet()

    media_content = Content(path=path, output=output, url=url,
                            **extra_meta_data)

    content['media'].add(media_content)

    # run plugin hooks on new added media
    context.plugins.run_plugin_hook('media_added', content, media_content)

    logger.debug('%s added to %s',
                 media_content['path'] or media_content,
                 content['path'] or content)

    return media_content


class Media:
    def post_build(self, context):
        if context.settings.SKIP_FILE_OPERATIONS:
            return

        for content in context.contents:
            if not content['media']:
                continue

            for media in content['media']:
                context.cp(
                    source=os.path.join(
                        context.settings.CONTENT_ROOT,
                        media['path'],
                    ),
                    destination=os.path.join(
                        context.settings.OUTPUT_ROOT,
                        media['output'],
                    ),
                )
