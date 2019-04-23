import os

from flamingo.core.utils.string import split, slugify
from flamingo.core.utils.pagination import paginate


class Tags:
    THEME_PATHS = [os.path.join(os.path.dirname(__file__), 'theme')]

    def contents_parsed(self, context):
        CONTENT_KEY = getattr(context.settings, 'I18N_CONTENT_KEY', 'id')

        GENERATE_PAGE_ZERO = \
            getattr(context.settings, 'TAGS_GENERATE_PAGE_ZERO', True)

        # find tags
        for content in context.contents:
            if not content['tags']:
                content['tags'] = []

                continue

            content['tag_names'] = split(content['tags'])
            content['tags'] = [slugify(i) for i in content['tag_names']]

        tags = sorted(list(set(sum(context.contents.values('tags'), []))))

        # gen tag pages
        for tag in tags:
            output = os.path.join('tags/{}.html'.format(slugify(tag)))

            context.contents.add(**{
                CONTENT_KEY: '_tag/{}'.format(tag),
                'output': output,
                'url': '/' + output,
                'tag': tag,
                'template': 'tag.html',
            })

        # gen tag list
        for tags, page, total_pages in paginate(tags, context):
            context.contents.add(**{
                CONTENT_KEY: '_tags/{}'.format(page),
                'output': 'tags/{}.html'.format(page),
                'url': '/tags/{}.html'.format(page),
                'tags': tags,
                'template': 'tags.html',
                'pagination': {
                    'page': page,
                    'total_pages': total_pages,
                }
            })

            # generate a page "0" with url "/tags.html"
            # this is for users typing the url in by hand only
            if GENERATE_PAGE_ZERO and page == 1:
                context.contents.add(**{
                    CONTENT_KEY: '_tags/0',
                    'output': 'tags.html'.format(page),
                    'url': '/tags.html'.format(page),
                    'tags': tags,
                    'template': 'tags.html',
                    'pagination': {
                        'page': page,
                        'total_pages': total_pages,
                    }
                })
