import os


class TemplatingEngine:
    def __init__(self, context):
        self.context = context

        self.theme_paths = (
            context.settings.THEME_PATHS +
            self.context.plugins.THEME_PATHS +
            context.settings.CORE_THEME_PATHS
        )

    def find_static_dirs(self):
        static_dirs = []

        for theme_path in self.theme_paths:
            static_path = os.path.join(theme_path, 'static')

            if os.path.exists(static_path):
                static_dirs.append(static_path)

        return static_dirs

    def render(self, template_name, template_context):
        raise NotImplementedError

    def render_string(self, string, template_context):
        raise NotImplementedError
