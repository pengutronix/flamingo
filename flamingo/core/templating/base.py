import os


class TemplatingEngine:
    def __init__(self, theme_paths):
        self.theme_paths = theme_paths

    def find_static_dirs(self):
        static_dirs = []

        for theme_path in self.theme_paths:
            static_path = os.path.join(theme_path, 'static')

            if os.path.exists(static_path):
                static_dirs.append(static_path)

        return static_dirs

    def render(self, template_name, template_context):
        raise NotImplementedError
