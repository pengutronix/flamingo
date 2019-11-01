import builtins
import os

from PIL import Image


def get_size(context, media_content):
    path = os.path.join(context.settings.CONTENT_ROOT, media_content['path'])
    image = Image.open(path)

    return '{}x{}'.format(*image.size)


def calc_width(context, media_content):
    path = os.path.join(context.settings.CONTENT_ROOT, media_content['path'])
    image = Image.open(path)

    original_width, original_height = image.size
    height = int(media_content['height'])
    height_percentage = (height / original_height) * 100
    width = original_width * (height_percentage / 100)

    return '{}px'.format(width)


def add_unit(value):
    value = str(value).lower()

    units = [
        'px',
        '%',
        'em',
        'cm',
        'mm',
        'in',
        'pt',
        'pc',
        'ex',
        'ch',
        'rem',
        'vw',
        'vh',
        'vmi',
        'vma',
    ]

    for unit in units:
        if value.endswith(unit):
            return value

    return '{}px'.format(value)


def load_builtin(name):
    return builtins.__dict__[name]
