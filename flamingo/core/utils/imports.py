import importlib
import inspect
import runpy
import re

SCRIPT_RE = re.compile(r'^[^:]+::[a-zA-Z0-9_]+$')
MODULE_RE = re.compile(r'^[a-zA-Z0-9_.]+$')


def acquire(item, types=None):
    path = item

    if types and not isinstance(types, tuple):
        types = (types, )

    if isinstance(item, str):
        if MODULE_RE.match(item):
            try:
                item = importlib.import_module(item)
                path = inspect.getfile(item)

            except Exception:
                if '.' in item:
                    module_name, attr_name = item.rsplit('.', 1)

                else:
                    module_name = item
                    attr_name = None

                module = importlib.import_module(module_name)
                path = inspect.getfile(module)

                if attr_name:
                    item = getattr(module, attr_name)

                else:
                    item = module

        elif SCRIPT_RE.match(item):
            script, attr_name = item.split('::')
            values = runpy.run_path(script)

            if attr_name not in values:
                raise ImportError("script '{}' has no attribute '{}'".format(
                    script, attr_name))

            item = values[attr_name]
            path = script

        else:
            raise ValueError("invalid import string '{}'".format(item))

    if types and not isinstance(item, types):
        raise ValueError("'{}' has wrong type. Allowed types: {}".format(
            attr_name, ', '.join([i.__name__ for i in types])))

    return item, path
