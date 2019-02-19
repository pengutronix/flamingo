import re

CLEAN_RE = re.compile(r'[^a-z0-9äöüßø]')
WHITESPACE_RE = re.compile(r'\s+')

ESCAPE_TABLE = [
    ('ä', 'ae'),
    ('ö', 'oe'),
    ('ü', 'ue'),
    ('ø', 'oe'),
    ('ß', 'ss'),
]


def slugify(string):
    string = string.lower()
    string = CLEAN_RE.sub(' ', string)
    string = string.strip()
    string = WHITESPACE_RE.sub('-', string)

    for a, b in ESCAPE_TABLE:
        string = string.replace(a, b)

    return string


def split(string, delimiter=','):
    string = WHITESPACE_RE.sub(' ', string.strip())
    strings = [i.strip() for i in string.split(delimiter) if i]

    return strings


def truncate(string, max_length, truncate_string='...'):
    if len(string) <= max_length:
        return string

    return string[0:max_length-len(truncate_string)] + truncate_string
