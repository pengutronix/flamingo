from collections import OrderedDict
import hashlib
import logging
import re
import os

try:
    from docutils.parsers.rst import directives

    RST = True

except ImportError:
    RST = False

from PIL import Image as PillowImage

from flamingo.core.data_model import Content

logger = logging.getLogger('flamingo.plugins.Thumbnails')

DEFAULT_THUMBNAIL_CACHE = 'thumbs'
DIMENSION_RE = re.compile('^([0-9]{1,})(px)?$')


def parse_bool(value):
    value = value.lower()

    values = {
        'false': False,
        'true': True,
        '0': False,
        '1': True,
    }

    if value not in values:
        return False

    return values[value]


def parse_dimensions(dimension):
    if isinstance(dimension, int):
        return dimension

    try:
        return int(DIMENSION_RE.search(dimension).groups()[0])

    except Exception:
        return 0


def hash_image(path, options):
    options = OrderedDict(options)
    stream = b''

    for k, v in options.items():
        stream += '{}={},'.format(k, v).encode()

    stream += open(path, 'rb').read()

    return hashlib.md5(stream).hexdigest()


def scale_image(original_size, width=None, height=None):
    if width and height:
        return int(width), int(height)

    original_width, original_height = original_size

    if width:
        width_percentage = (width / original_width) * 100
        height = original_height * (width_percentage / 100)

        return width, int(height)

    if height:
        height_percentage = (height / original_height) * 100
        width = original_width * (height_percentage / 100)

        return int(width), height

    return original_size


class Thumbnails:
    THEME_PATHS = [os.path.join(os.path.dirname(__file__), 'theme')]

    def settings_setup(self, context):
        THUMBNAIL_CACHE = getattr(context.settings, 'THUMBNAIL_CACHE',
                                  DEFAULT_THUMBNAIL_CACHE)

        context.settings.LIVE_SERVER_IGNORE_PREFIX.append(
            os.path.join(context.settings.CONTENT_ROOT, THUMBNAIL_CACHE))

        if RST:
            logger.debug("setting up 'thumbnail' option for rst images")

            if not hasattr(context.settings, 'RST_IMAGE_EXTRA_OPTION_SPEC'):
                context.settings.RST_IMAGE_EXTRA_OPTION_SPEC = {}

            context.settings.RST_IMAGE_EXTRA_OPTION_SPEC['thumbnail'] = \
                directives.unchanged

        else:
            logger.debug('docutils seems to be not installed. setup skipped')

    def media_added(self, context, content, media_content):
        logger.debug('processing %s:%s',
                     content['path'] or content,
                     media_content['path'] or media_content)

        if media_content['is_thumbnail'] or media_content['original']:
            logger.debug(
                "setup of thumbnail for %s:%s skipped: image is already a thumbnail",  # NOQA
                content['path'], media_content['path'])

            return

        if media_content['type'] != 'media/image':
            logger.debug(
                "setup of thumbnail for %s:%s skipped: type is not 'media/image'",  # NOQA
                content['path'], media_content['path'])

            return

        if('thumbnail' in media_content and
           not parse_bool(media_content['thumbnail'])):

            logger.debug(
                'setup of thumbnail for %s:%s skipped: disabled by option',
                content['path'], media_content['path'])

            return

        if not media_content['width'] and not media_content['height']:
            logger.debug(
                'setup of thumbnail for %s:%s skipped: no dimensions set',
                content['path'], media_content['path'])

            return

        # parse dimensions
        width = parse_dimensions(media_content['width'])
        height = parse_dimensions(media_content['height'])

        # scale image
        image = PillowImage.open(
            os.path.join(context.settings.CONTENT_ROOT, media_content['path']))

        width, height = scale_image(image.size, width=width, height=height)

        media_content['width'] = width
        media_content['height'] = height

        # setup thumbnail media content
        image_hash = hash_image(
            os.path.join(context.settings.CONTENT_ROOT,
                         media_content['path']),
            {
                'width': media_content['width'],
                'height': media_content['height'],
            }
        )

        logger.debug('setup thumbnail for %s:%s (%s)',
                     content['path'], media_content['path'], image_hash)

        # gen thumbnail paths
        image_name, image_extension = os.path.splitext(media_content['output'])

        thumbnail_path = os.path.join(
            getattr(context.settings, 'THUMBNAIL_CACHE',
                    DEFAULT_THUMBNAIL_CACHE),
            '{}{}'.format(image_hash, image_extension))

        thumbnail_output = '{}.thumb{}'.format(image_name, image_extension)
        thumbnail_url = '/' + thumbnail_output

        # inject thumbnail paths into original media content
        original_content = Content(
            url=media_content['url'],
            path=media_content['path'],
            output=media_content['output'],
            thumbnail=False,
        )

        content['media'].add(original_content)

        media_content['path'] = thumbnail_path
        media_content['output'] = thumbnail_output
        media_content['url'] = thumbnail_url
        media_content['is_thumbnail'] = True

        # link original and thumbnail together
        media_content['original'] = original_content
        original_content['thumbnail'] = media_content

        # generate thumbnail file
        if context.settings.LIVE_SERVER_RUNNING:
            return

        self.gen_thumbnail(context, media_content, image=image)

    def gen_thumbnail(self, context, media_content, image=None):
        image = image or PillowImage.open(
            os.path.join(context.settings.CONTENT_ROOT,
                         media_content['original']['path']))

        # check if thumbnail already exists
        output = os.path.join(context.settings.CONTENT_ROOT,
                              media_content['path'])

        if os.path.exists(output):
            return

        # generate thumbnail
        if not media_content['width']:
            logger.error("%s: invalid width '%s'",
                         media_content['original']['path'],
                         media_content['width'])

        if not media_content['height']:
            logger.error("%s: invalid height '%s'",
                         media_content['original']['path'],
                         media_content['height'])

            if not media_content['width']:
                return

        context.mkdir_p(output, force=True)

        image.thumbnail((media_content['width'], media_content['height'],))
        image.save(output)

    def render_media_content(self, context, media_content):
        if not media_content['is_thumbnail']:
            return

        self.gen_thumbnail(context, media_content)

    def post_build(self, context):
        THUMBNAIL_CACHE = os.path.join(
            context.settings.CONTENT_ROOT,
            context.settings.get(
                'THUMBNAIL_CACHE',
                DEFAULT_THUMBNAIL_CACHE,
            ),
        )

        THUMBNAIL_REMOVE_ORPHANED = context.settings.get(
            'THUMBNAIL_REMOVE_ORPHANED', True)

        if not THUMBNAIL_REMOVE_ORPHANED:
            return

        if not os.path.exists(THUMBNAIL_CACHE):
            return

        # find generated thumbnails
        thumbnails = []

        for content in context.contents:
            if not content['media']:
                continue

            for media_content in content['media']:
                if media_content['is_thumbnail']:
                    path = os.path.join(
                        context.settings.CONTENT_ROOT,
                        media_content['path'],
                    )

                    thumbnails.append(path)

        # remove obsolete thumbnails
        for path in os.listdir(THUMBNAIL_CACHE):
            path = os.path.join(THUMBNAIL_CACHE, path)

            if path not in thumbnails:
                logger.info('removing orphaned %s', path)
                context.rm_rf(path, force=True)
