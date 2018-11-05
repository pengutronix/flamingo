import re
import os

from flamingo.core.utils.pagination import paginate


class Tags:
    TAGS_RE = re.compile(r'[^\s,]+')

    def contents_parsed(self, context):
        content_key = getattr(context.settings, 'I18N_CONTENT_KEY', 'id')

        # find tags
        for content in context.contents:
            if content['tags']:
                content['tags'] = self.TAGS_RE.findall(content['tags'])

            else:
                content['tags'] = []

        tags = sorted(list(set(sum(context.contents.values('tags'), []))))

        # gen tag pages
        for tag in tags:
            output = os.path.join('tags/{}.html'.format(tag))

            context.contents.add(**{
                content_key: '_tags/{}'.format(tag),
                'output': output,
                'url': '/' + output,
                'tag': tag,
                'template': 'tag.html',
            })

        # gen tag list
        for tags, page, total_pages in paginate(tags, context):
            context.contents.add(**{
                content_key: '_tags/{}'.format(page),
                'output': 'tags/{}.html'.format(page),
                'url': '/tags/{}.html'.format(page),
                'tags': tags,
                'template': 'tags.html',
                'pagination': {
                    'page': page,
                    'total_pages': total_pages,
                }
            })
