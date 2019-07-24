from copy import deepcopy
import importlib
import runpy

from . import defaults


class Settings:
    def __init__(self):
        self._values = {}
        self.modules = []

        for i in dir(defaults):
            attr = getattr(defaults, i)

            try:
                attr_copy = deepcopy(attr)

            except Exception:
                pass

            else:
                self._values[i] = attr_copy

    def add(self, module):
        if not (module.endswith('.py') or '/' in module):
            module = importlib.import_module(module).__file__

        values = runpy.run_path(module, init_globals=self._values)

        self.modules.append(module)
        self._values = {k: v for k, v in values.items()
                        if not k.startswith('_')}

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)

        except AttributeError:
            if name in self._values:
                return self._values[name]

            raise

    def __dir__(self):
        return list(set(super().__dir__() + list(self._values.keys())))

    def __iter__(self):
        ignore = ('add', )

        for key in dir(self):
            if key in ignore or key.startswith('_'):
                continue

            yield key, getattr(self, key)
