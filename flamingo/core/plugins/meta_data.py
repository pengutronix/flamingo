import os


class MetaDataDefaults:
    def contents_parsed(self, context):
        for content in context.contents:
            # set output_path
            if not content['output']:
                content['output'] = \
                    os.path.splitext(content['path'])[0] + '.html'

            # set url
            content['url'] = os.path.join('/', content['output'])

            # set template
            if not content['template']:
                content['template'] = context.settings.DEFAULT_TEMPLATE

            # set content meta data
            if not content['title']:
                content['title'] = ''

            if not content['content_title']:
                content['content_title'] = ''

            if not content['content_body']:
                content['content_body'] = ''
