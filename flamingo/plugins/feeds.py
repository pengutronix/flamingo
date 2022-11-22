import logging

from feedgen.feed import FeedGenerator

logger = logging.getLogger('flamingo.plugins.Feeds')


class Feeds:
    def pre_build(self, context):
        FEEDS_DOMAIN = getattr(context.settings, 'FEEDS_DOMAIN', '/')
        FEEDS = getattr(context.settings, 'FEEDS', [])

        for feed_config in FEEDS:
            try:
                content = {
                    'type': 'feed',
                    'feed_type': feed_config['type'],
                    'output': feed_config['output'],
                    'url': '/' + feed_config['output'],
                }

                if 'lang' in feed_config:
                    content['lang'] = feed_config['lang']

                fg = FeedGenerator()

                if 'lang' in feed_config:
                    fg.language(feed_config['lang'])

                fg.id(feed_config['id'])
                fg.title(feed_config['title'])

                # set parameters needed for rss-feeds
                if feed_config['type'] in ['rss', 'podcast']:
                    fg.description(feed_config['description'])
                    fg.link(href=feed_config['link'], rel='self')
                    fg.link(href=feed_config['link_alternate'], rel='alternate')

                # setup podcast environment
                if feed_config['type'] == 'podcast':
                    fg.load_extension('podcast')
                    fg.podcast.itunes_image(feed_config['podcast_image'])
                    if 'itunes_owner' in feed_config:
                        fg.podcast.itunes_owner(**feed_config['itunes_owner'])
                    if 'itunes_category' in feed_config:
                        fg.podcast.itunes_category(feed_config['itunes_category'])
                    if 'itunes_explicit' in feed_config:
                        fg.podcast.itunes_explicit(feed_config['itunes_explicit'])

                for i in feed_config['contents'](context):
                    fe = fg.add_entry()

                    # setup required entry attributes
                    fe_title = i['title'] or i['content_title']

                    fe_link = {
                        'href': '{}{}'.format(FEEDS_DOMAIN, i['url']),
                        'rel': 'alternate'
                    }

                    if 'entry-id' in feed_config:
                        fe_id = feed_config['entry-id'](i)

                    else:
                        fe_id = i['output']

                    if 'updated' in feed_config:
                        fe_updated = feed_config['updated'](i)
                    else:
                        fe_updated = ''

                    if 'published' in feed_config:
                        fe_published = feed_config['published'](i)
                    else:
                        fe_published = ''

                    if 'podcast' in i:
                        fe_podcast_url = i['podcast'].get('url', '')
                        fe_podcast_size = i['podcast'].get('size', 0)
                        fe_podcast_type = i['podcast'].get('type', 'audio/mpeg')
                    else:
                        fe_podcast_url = ''
                        fe_podcast_size = ''
                        fe_podcast_type = 'audio/mpeg'  # default value; will never be reported as missing

                    # check entry attributes
                    missing_attributes = []

                    if not fe_id:
                        missing_attributes.append('id')

                    if not fe_title:
                        missing_attributes.append('title')

                    if not fe_updated:
                        missing_attributes.append('updated')

                    if not fe_published:
                        missing_attributes.append('published')

                    if feed_config['type'] == 'podcast':
                        if not fe_podcast_url:
                            missing_attributes.append('podcast->url')
                        if not fe_podcast_size:
                            missing_attributes.append('podcast->size')

                    if missing_attributes:
                        logger.error('%s is missing attributes: %s',
                                     i['path'] or i['i18n_path'] or i,
                                     ', '.join(missing_attributes))

                        return

                    # optional attributes
                    fe.id(fe_id)
                    fe.title(fe_title)
                    fe.updated(fe_updated)
                    fe.published(fe_published)
                    fe.link(fe_link)

                    if i['content_body']:
                        exitcode, output = context.pre_render(i)
                        fe.content(output, type='html')

                    if i['authors']:
                        for author in i['authors']:
                            fe.author({
                                'name': author,
                            })

                    if i['summary']:
                        fe.summary(str(i['summary']))

                    if feed_config['type'] == 'podcast':
                        fe.enclosure(fe_podcast_url, str(fe_podcast_size), fe_podcast_type)

                # generate output
                if feed_config['type'] == 'atom':
                    content['content_body'] = fg.atom_str().decode()

                elif feed_config['type'] in ['rss', 'podcast']:
                    content['content_body'] = fg.rss_str().decode()
                else:
                    raise ValueError(f'Unkown Feed type {feed_config["type"]}')

                context.contents.add(**content)

            except Exception:
                logger.error("feed '%s' setup failed", feed_config['id'],
                             exc_info=True)
