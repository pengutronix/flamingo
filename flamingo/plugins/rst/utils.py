import re

from docutils.parsers.rst import roles, directives

ROLE_RE = re.compile(r'^(?P<arg0>[^<]+)((\s+)?<(?P<arg1>[^>]+)>)?((\s+)?(?P<options>.*))?$')  # NOQA
ROLE_OPTIONS_RE = re.compile(r'((?P<name>[^=]+)=(?P<value>[^\s,]+)([\s,]+)?)')


def parse_role_text(role_text):
    role_args = {
        'args': [],
        'options': {},
    }

    role_text = role_text.strip()

    if role_text.startswith('<') and role_text.endswith('>'):
        role_args['args'].append(role_text[1:-1])

        return role_args

    try:
        role_parts = ROLE_RE.search(role_text).groupdict()

    except Exception:
        role_args['args'].append(role_text)

        return role_args

    if role_parts['arg0']:
        role_args['args'].append(role_parts['arg0'].strip())

    if role_parts['arg1']:
        role_args['args'].append(role_parts['arg1'].strip())

    if role_parts['options']:
        for parts in ROLE_OPTIONS_RE.finditer(role_parts['options']):
            groups = parts.groups()

            role_args['options'][groups[1]] = groups[2]

    return role_args


def parse_bool(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        try:
            return {
                'true': True,
                '1': True,
                'false': False,
                '0': False,
            }[value.strip().lower()]

        except Exception:
            pass

    return bool(value)


def register_canonical_role(name, role):
    if name in roles._roles:
        roles._roles.pop(name)

    if name in roles._role_registry:
        roles._role_registry.pop(name)

    roles.register_canonical_role(name, role)


def register_directive(name, directive):
    if name in directives._directives:
        directives._directives.pop(name)

    if name in directives._directive_registry:
        directives._directive_registry.pop(name)

    directives.register_directive(name, directive)
