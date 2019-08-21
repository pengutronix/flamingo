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
        if name not in HOOK_NAMES:
            logger.warn("hook '%s' is unknown", name)

        function.flamingo_hook_name = name

        return function

    return decorator


class PluginManager:
    def __init__(self, context):
        self._context = context
        self._plugins = []
        self._plugin_paths = []
        self._hooks = {key: [] for key in HOOK_NAMES}

        self.THEME_PATHS = []
        self.PLUGIN_PATHS = []

        # setup plugins
        plugins = (self._context.settings.CORE_PLUGINS_PRE +
                   self._context.settings.DEFAULT_PLUGINS +
                   self._context.settings.PLUGINS +
                   self._context.settings.CORE_PLUGINS_POST)

        discovered_local_hooks = []

        for plugin in plugins:
            logger.debug("setting up plugin '%s' ", plugin)

            try:
                # local hooks
                if isinstance(plugin, str) and plugin.startswith('.'):
                    logger.debug("'%s' gets handled as local hook", plugin)

                    plugin = plugin[1:]

                    if not hasattr(self._context.settings, plugin):
                        logger.error('settings.%s does not exist', plugin)

                        continue

                    hook = getattr(self._context.settings, plugin)

                    if not hasattr(hook, 'flamingo_hook_name'):
                        logger.error('settings.%s is no flamingo hook', plugin)

                        continue

                    if hook.flamingo_hook_name not in self._hooks:
                        self._hooks[hook.flamingo_hook_name] = []

                    self._hooks[hook.flamingo_hook_name].append(
                        ('settings', hook, ),
                    )

                    discovered_local_hooks.append(plugin)

                # plugin classes
                else:
                    plugin_class, plugin_path = acquire(plugin)
                    plugin_object = plugin_class()

                    self.PLUGIN_PATHS.append(plugin_path)

                    # find theme_paths
                    if hasattr(plugin_object, 'THEME_PATHS'):
                        self.THEME_PATHS.extend(plugin_object.THEME_PATHS)

                    # discover hooks
                    for hook_name in HOOK_NAMES:
                        if hasattr(plugin_object, hook_name):
                            logger.debug('%s.%s discoverd', plugin, hook_name)

                            self._hooks[hook_name].append(
                                (plugin_object.__class__.__name__,
                                 getattr(plugin_object, hook_name), )
                            )

                    self._plugins.append(
                        (plugin_object.__class__.__name__, plugin_object, )
                    )

                    self._plugin_paths.append(plugin_path)

            except Exception:
                logger.error("setup of '%s' failed", plugin, exc_info=True)

        # discover local hooks
        logger.debug('discover local hooks')

        for attr_name in dir(self._context.settings):
            attr = getattr(self._context.settings, attr_name)

            if attr_name in discovered_local_hooks:
                logger.debug('settings.%s skipped. already discovered',
                             attr_name)

                continue

            if hasattr(attr, 'flamingo_hook_name'):
                logger.debug("settings.%s discoverd as",
                             attr.flamingo_hook_name)

                if attr.flamingo_hook_name not in self._hooks:
                    self._hooks[attr.flamingo_hook_name] = []

                self._hooks[attr.flamingo_hook_name].append(
                    ('settings', attr, ),
                )

    def run_plugin_hook(self, name, *args, **kwargs):
        if name in self._context.settings.SKIP_HOOKS:
            logger.debug("'%s' skipped because of settings.SKIP_HOOKS", name)

            return

        if name not in self._hooks:
            logger.error("unknown hook name '%s'", name)

            return

        if not self._hooks[name]:
            return

        logger.debug("running plugin hook '%s'", name)
        args = (self._context, *args)

        for plugin_name, hook in self._hooks[name]:
            logger.debug('running %s.%s', plugin_name, name)

            try:
                hook(*args, **kwargs)

            except Exception:
                logger.error('%s.%s failed', plugin_name, name, exc_info=True)

    def get_plugin(self, name):
        for plugin_name, plugin_object in self._plugins:
            if plugin_name == name:
                return plugin_object

        raise ValueError("unknown plugin '{}'".format(name))
