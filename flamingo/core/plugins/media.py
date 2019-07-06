import os

from flamingo.core.data_model import ContentSet, Content


def add_media(context, content, name):
    # gen source
    if name.startswith('/'):
        source = os.path.join(context.settings.CONTENT_ROOT, name[1:])

    else:
        source = os.path.join(
            os.path.dirname(
                os.path.join(context.settings.CONTENT_ROOT, content['path'])
            ),
            name,
        )

    source = os.path.normpath(source)

    # gen destination
    if name.startswith('/'):
        destination = os.path.join(
            context.settings.MEDIA_ROOT,
            name[1:],
        )

    else:
        destination = os.path.join(
            context.settings.MEDIA_ROOT,
            os.path.dirname(content['path']),
            os.path.basename(name),
        )

    # gen link
    link = os.path.join(
        '/media',
        os.path.relpath(destination, context.settings.MEDIA_ROOT),
    )

    # content['media']
    if not content['media']:
        content['media'] = ContentSet()

    media_content = Content(source=source, destination=destination, link=link)

    content['media'].add(media_content)

    return media_content


class Media:
    def post_build(self, context):
        if context.settings.CONTENT_PATHS:
            return

        for content in context.contents:
            if not content['media']:
                continue

            for media in content['media']:
                context.cp(source=media['source'],
                           destination=media['destination'])
