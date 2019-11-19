# The code in this module is mostly copied from pythons pprint module and
# modified slightly to add support for flamingos internal types

from pprint import PrettyPrinter, _safe_tuple, _recursion, _builtin_scalars

from flamingo.core.data_model import Content, ContentSet, QUOTE_KEYS, quote


def _safe_repr(object, context, maxlevels, level):
    typ = type(object)
    if typ in _builtin_scalars:
        return repr(object), True, False

    r = getattr(typ, "__repr__", None)
    if issubclass(typ, dict) and r is dict.__repr__:
        if not object:
            return "{}", True, False
        objid = id(object)
        if maxlevels and level >= maxlevels:
            return "{...}", False, objid in context
        if objid in context:
            return _recursion(object), False, True
        context[objid] = 1
        readable = True
        recursive = False
        components = []
        append = components.append
        level += 1
        saferepr = _safe_repr
        items = sorted(object.items(), key=_safe_tuple)
        for k, v in items:
            krepr, kreadable, krecur = saferepr(k, context, maxlevels, level)
            vrepr, vreadable, vrecur = saferepr(v, context, maxlevels, level)
            append("%s: %s" % (krepr, vrepr))
            readable = readable and kreadable and vreadable
            if krecur or vrecur:
                recursive = True
        del context[objid]
        return "{%s}" % ", ".join(components), readable, recursive

    if (issubclass(typ, list) and r is list.__repr__) or \
       (issubclass(typ, tuple) and r is tuple.__repr__):
        if issubclass(typ, list):
            if not object:
                return "[]", True, False
            format = "[%s]"
        elif len(object) == 1:
            format = "(%s,)"
        else:
            if not object:
                return "()", True, False
            format = "(%s)"
        objid = id(object)
        if maxlevels and level >= maxlevels:
            return format % "...", False, objid in context
        if objid in context:
            return _recursion(object), False, True
        context[objid] = 1
        readable = True
        recursive = False
        components = []
        append = components.append
        level += 1
        for o in object:
            orepr, oreadable, orecur = _safe_repr(o, context, maxlevels, level)
            append(orepr)
            if not oreadable:
                readable = False
            if orecur:
                recursive = True
        del context[objid]
        return format % ", ".join(components), readable, recursive

    if isinstance(object, (Content, ContentSet, )):
        rep = object.__repr__(pretty=False)

    else:
        rep = repr(object)

    return rep, (rep and not rep.startswith('<')), False


def _format_Content_items(cls, items, stream, indent, allowance, context,
                          level):

    write = stream.write
    indent += cls._indent_per_level
    delimnl = ',\n' + ' ' * indent
    last_index = len(items) - 1

    for i, (key, ent) in enumerate(items):
        last = i == last_index
        rep = cls._repr(key, context, level)
        write(key)
        write('=')

        if key in QUOTE_KEYS:
            write(quote(ent))

        else:
            cls._format(ent, stream, indent + len(rep) + 2,
                        allowance if last else 1, context, level)
        if not last:
            write(delimnl)


def _pprint_Content(cls, object, stream, indent, allowance, context, level):
    indent += 1

    write = stream.write
    write('<Content(\n{}'.format(' ' * (indent + 1)))

    if cls._indent_per_level > 1:
        write((cls._indent_per_level - 1) * ' ')
    length = len(object.data)

    if length:
        items = sorted(object.data.items(), key=_safe_tuple)
        _format_Content_items(cls, items, stream, indent, allowance + 1,
                              context, level)
    write(')>')


def _pprint_ContentSet(cls, object, stream, indent, allowance, context, level):
    indent += 1

    stream.write('<ContentSet(\n{}'.format(' ' * (indent + 1)))

    cls._format_items(object.contents, stream, indent, allowance + 1,
                      context, level)
    stream.write(')>')


class FlamingoPrettyPrinter(PrettyPrinter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._dispatch[Content.__repr__] = _pprint_Content
        self._dispatch[ContentSet.__repr__] = _pprint_ContentSet

    def format(self, object, context, maxlevels, level):
        return _safe_repr(object, context, maxlevels, level)


def pprint(object, stream=None, indent=1, width=80, depth=None, *,
           compact=False):

    FlamingoPrettyPrinter(
        stream=stream,
        indent=indent,
        width=width,
        depth=depth,
        compact=compact,
    ).pprint(object)


def pformat(object, indent=1, width=80, depth=None, *, compact=False):
    return FlamingoPrettyPrinter(
        indent=indent,
        width=width,
        depth=depth,
        compact=compact,
    ).pformat(object)
