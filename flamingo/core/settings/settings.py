from copy import deepcopy
import importlib
import runpy

from . import defaults
from flamingo.core.types import OverlayObject


class Settings(OverlayObject):
    def __init__(self):
        super().__init__()

        self.modules = []

        for name in dir(defaults):
            if name.startswith('_'):
                continue

            attr = getattr(defaults, name)

            try:
                attr_copy = deepcopy(attr)

            except Exception:
                pass

            else:
                self._attrs[name] = attr_copy

    def add(self, module):
        if not (module.endswith('.py') or '/' in module):
            module = importlib.import_module(module).__file__

        attrs = runpy.run_path(module, init_globals=self._attrs)

        self.modules.append(module)
        self._attrs = {k: v for k, v in attrs.items()
                       if not k.startswith('_')}

    def get(self, *args):
        return getattr(self, *args)

    def __iter__(self):
        ignore = ('add', )

        for key in dir(self):
            if key in ignore or key.startswith('_'):
                continue

            yield key, getattr(self, key)
