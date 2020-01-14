from copy import copy
import logging
import os

from docutils.parsers.rst import Directive, directives
from docutils.nodes import raw

from flamingo.core.plugins.media import add_media
from flamingo.core.data_model import ContentSet

from flamingo.plugins.rst.base import parse_rst

logger = logging.getLogger('flamingo.plugins.RSTImage')


def gen_directives(context, plugin):
    # gallery settings
    default_gallery_option_spec = {
        'template': directives.unchanged,
    }

    RST_GALLERY_OPTION_SPEC = context.settings.get(
        'RST_GALLERY_OPTION_SPEC',
        default_gallery_option_spec,
    )

    RST_GALLERY_EXTRA_OPTION_SPEC = context.settings.get(
        'RST_GALLERY_EXTRA_OPTION_SPEC',
        {},
    )

    # image settings
    default_image_option_spec = {
        'template': directives.unchanged,
        'align': directives.unchanged,
        'clear': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
        'link': directives.unchanged,
        'alt': directives.unchanged,
        'title': directives.unchanged,
    }

    RST_IMAGE_CAPTION_RAW = context.settings.get(
        'RST_IMAGE_CAPTION_RAW',
        False,
    )

    RST_IMAGE_OPTION_SPEC = context.settings.get(
        'RST_IMAGE_OPTION_SPEC',
        default_image_option_spec,
    )

    RST_IMAGE_EXTRA_OPTION_SPEC = context.settings.get(
        'RST_IMAGE_EXTRA_OPTION_SPEC',
        {},
    )

    class Gallery(Directive):
        required_arguments = 0
        has_content = True

        option_spec = {
            **RST_GALLERY_OPTION_SPEC,
            **RST_GALLERY_EXTRA_OPTION_SPEC,
        }

        def run(self):
            path = context.content['path']

            try:
                # setup gallery
                plugin.galleries[path] = ContentSet()

                # find related images
                parse_rst('\n'.join(self.content), context)

                # render gallery
                contents = plugin.galleries.pop(path)

                # find template
                template = self.options.get(
                    'template', context.settings.DEFAULT_GALLERY_TEMPLATE)

                if not context.content['related_paths']:
                    context.content['related_paths'] = []

                context.content['related_paths'].append(template)

                node_content = context.templating_engine.render(
                    template,
                    {
                        'context': context,
                        'content': copy(self.options),
                        'contents': contents,
                    },
                    handle_exceptions=False,
                )

                return [
                    raw('', node_content, format='html')
                ]

            finally:
                if path and path in plugin.galleries:
                    plugin.galleries.pop(path)

    class Image(Directive):
        required_arguments = 1
        has_content = True

        option_spec = {
            **RST_IMAGE_OPTION_SPEC,
            **RST_IMAGE_EXTRA_OPTION_SPEC,
        }

        def run(self):
            meta = {
                'type': 'media/image',
            }

            if self.content:
                meta['caption'] = '\n'.join(self.content)

                if meta['caption'] and not RST_IMAGE_CAPTION_RAW:
                    meta['caption'] = parse_rst(meta['caption'], context)

            for k, v in self.options.items():
                meta[k] = v

            path = context.content['path']

            if path in plugin.galleries:
                meta['gallery'] = True

            media_content = add_media(context, context.content,
                                      self.arguments[0], **meta)

            # gallery
            if path in plugin.galleries:
                plugin.galleries[path].add(media_content)

                return []

            # image
            # find template
            if media_content['template']:
                template = media_content['template']

            else:
                template = context.settings.DEFAULT_IMAGE_TEMPLATE

            if not context.content['related_paths']:
                context.content['related_paths'] = []

            context.content['related_paths'].append(template)

            return [
                raw(
                    '',
                    context.templating_engine.render(
                        template,
                        {
                            'context': context,
                            'content': media_content,
                        },
                        handle_exceptions=False,
                    ),
                    format='html',
                ),
            ]

    return Gallery, Image


class rstImage:
    THEME_PATHS = [os.path.join(os.path.dirname(__file__), 'theme')]

    def setup(self, context):
        self.galleries = {}

    def parser_setup(self, context):
        RST_GALLERY_DIRECTIVE_NAMES = context.settings.get(
            'RST_GALLERY_DIRECTIVE_NAMES',
            ['gallery'],
        )

        RST_IMAGE_DIRECTIVE_NAMES = context.settings.get(
            'RST_IMAGE_DIRECTIVE_NAMES',
            ['img', 'image'],
        )

        _Gallery, _Image = gen_directives(context, self)

        for name in RST_GALLERY_DIRECTIVE_NAMES:
            directives.register_directive(name, _Gallery)

        for name in RST_IMAGE_DIRECTIVE_NAMES:
            directives.register_directive(name, _Image)
