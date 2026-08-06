import os

from flamingo.core.plugins.plugin_manager import PluginDependencyError

try:
    import PIL
except ImportError:
    PIL = None


class PhotoSwipe:
    def __init__(self):
        if not PIL:
            raise PluginDependencyError(
                "PhotoSwipe plugin is missing optional installation dependency flamingo[photoswipe]."
            )

    THEME_PATHS = [
        os.path.join(os.path.dirname(__file__), "theme"),
    ]
