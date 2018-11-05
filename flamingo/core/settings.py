import runpy


class Settings:
    def __init__(self):
        self._values = {}
        self._modules = []

        self.add('flamingo.default_settings')

    def add(self, module):
        self._modules.append(module)

        if module.endswith('.py') or '/' in module:
            values = runpy.run_path(module, init_globals=self._values)

        else:
            values = runpy.run_module(module, init_globals=self._values)

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
        return super().__dir__() + list(self._values.keys())
