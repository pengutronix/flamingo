import builtins
import os

from PIL import Image, UnidentifiedImageError


def get_size(context, media_content):
    path = os.path.join(context.settings.CONTENT_ROOT, media_content["path"])

    try:
        image = Image.open(path)

    except UnidentifiedImageError:
        return "800x600"

    return "{}x{}".format(*image.size)


def calc_width(context, media_content):
    path = os.path.join(context.settings.CONTENT_ROOT, media_content["path"])
    image = Image.open(path)

    original_width, original_height = image.size
    height = int(media_content["height"])
    height_percentage = (height / original_height) * 100
    width = original_width * (height_percentage / 100)

    return f"{width}px"


def add_unit(value):
    value = str(value).lower()

    units = [
        "px",
        "%",
        "em",
        "cm",
        "mm",
        "in",
        "pt",
        "pc",
        "ex",
        "ch",
        "rem",
        "vw",
        "vh",
        "vmi",
        "vma",
    ]

    for unit in units:
        if value.endswith(unit):
            return value

    return f"{value}px"


def load_builtin(name):
    return builtins.__dict__[name]
