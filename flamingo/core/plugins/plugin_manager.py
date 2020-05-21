import logging

from flamingo.core.utils.imports import acquire

logger = logging.getLogger('flamingo.core.PluginManager')

HOOK_NAMES = [
    'setup',
    'settings_setup',
    'parser_setup',
    'templating_engine_setup',
    'content_parsed',
    'contents_parsed',
    'context_setup',
    'pre_build',
    'post_build',

    # media
    'media_added',

    # live-server hooks
    'render_content',
    'render_media_content',
]


def hook(name):
    def decorator(function):
        function.flamingo_hook_name = name

        return function

    return decorator


class SettingsHook:
    pass


class PluginManager:
    def __init__(self, context):
        self._context = context
        self._plugins = []
        self._plugin_paths = []
        self._hooks = {}
        self._running_hook = ''

        self.PLUGIN_PATHS = []

        self.content = None

        # setup plugins
        plugins = (self._context.settings.CORE_PLUGINS_PRE +
                   self._context.settings.DEFAULT_PLUGINS +
                   self._context.settings.PLUGINS +
                   self._context.settings.CORE_PLUGINS_POST)

        for plugin in plugins:
            logger.debug("setting up plugin '%s' ", plugin)

            try:
                # settings hooks
                if isinstance(plugin, str) and plugin.startswith('.'):
                    logger.debug("'%s' gets handled as settings hook", plugin)

                    plugin = plugin[1:]

                    if not hasattr(self._context.settings, plugin):
                        logger.error('settings.%s does not exist', plugin)

                        continue

                    hook = getattr(self._context.settings, plugin)

                    if not hasattr(hook, 'flamingo_hook_name'):
                        logger.error('settings.%s is no flamingo hook', plugin)

                        continue

                    settings_hook = SettingsHook()

                    hook_name = getattr(hook, 'flamingo_hook_name')
                    setattr(settings_hook, hook_name, hook)

                    self._plugins.append(
                        (hook.__name__, settings_hook, )
                    )

                # plugin classes
                else:
                    plugin_class, plugin_path = acquire(plugin)
                    plugin_object = plugin_class()

                    self.PLUGIN_PATHS.append(plugin_path)

                    self._plugins.append(
                        (plugin_object.__class__.__name__, plugin_object, )
                    )

                    self._plugin_paths.append(plugin_path)

            except Exception:
                logger.error("setup of '%s' failed", plugin, exc_info=True)

        self._discover(HOOK_NAMES)

    def __dir__(self):
        return [
            *super().__dir__(),
            *[i[0] for i in self._plugins],
        ]

    def __getattr__(self, name):
        for plugin_name, plugin_object in self._plugins:
            if name == plugin_name:
                return plugin_object

        return super().__getattr__(name)

    def _discover(self, names):
        hook_names_to_discover = []

        for hook_name in names:
            if hook_name not in self._hooks:
                hook_names_to_discover.append(hook_name)
                self._hooks[hook_name] = []

        for hook_name in hook_names_to_discover:
            logger.debug("searching for '%s' hooks", hook_name)

            for plugin_path, plugin_object in self._plugins:
                if hasattr(plugin_object, hook_name):
                    logger.debug('%s.%s discoverd', plugin_object, hook_name)

                    self._hooks[hook_name].append(
                        (plugin_object.__class__.__name__,
                         getattr(plugin_object, hook_name), )
                    )

        # settings hooks
        logger.debug('searching for settings hooks')

        for attr_name in dir(self._context.settings):
            attr = getattr(self._context.settings, attr_name)

            if(not hasattr(attr, 'flamingo_hook_name') or
               attr.flamingo_hook_name not in hook_names_to_discover or
               attr in self._hooks[attr.flamingo_hook_name]):

                continue

            logger.debug("settings.%s discoverd as", attr.flamingo_hook_name)

            self._hooks[attr.flamingo_hook_name].append(
                ('settings', attr, ),
            )

    @property
    def running_hook(self):
        return self._running_hook

    @property
    def THEME_PATHS(self):
        paths = []

        for plugin_path, plugin_object in self._plugins:
            if hasattr(plugin_object, 'THEME_PATHS'):
                paths.extend(plugin_object.THEME_PATHS)

        return paths

    def run_plugin_hook(self, name, *args, **kwargs):
        if name in self._context.settings.SKIP_HOOKS:
            logger.debug("'%s' skipped because of settings.SKIP_HOOKS", name)

            return

        if name not in self._hooks:
            self._discover([name])

        if not self._hooks[name]:
            return

        try:
            logger.debug("running plugin hook '%s'", name)
            self._running_hook = name

            # make current content object available for logging
            if name == 'media_added':
                self.content = args[0]

            args = (self._context, *args)

            for plugin_name, hook in self._hooks[name]:
                logger.debug('running %s.%s', plugin_name, name)

                try:
                    hook(*args, **kwargs)

                except Exception:
                    logger.error('%s.%s failed', plugin_name, name,
                                 exc_info=True)

        finally:
            self._running_hook = ''
            self.content = None

    def get_plugin(self, name):
        for plugin_name, plugin_object in self._plugins:
            if plugin_name == name:
                return plugin_object

        raise ValueError("unknown plugin '{}'".format(name))

    def run_hook(self, *args, **kwargs):
        return self.run_plugin_hook(*args, **kwargs)
