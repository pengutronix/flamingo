import hashlib
import os


class Static:
    def _iter_static_files(self, context):
        for static_dir in context.templating_engine.find_static_dirs():
            for dirpath, _dirnames, filenames in os.walk(static_dir):
                for filename in filenames:
                    yield (static_dir, dirpath, filename)

    def templating_engine_setup(self, context, templating_engine):
        """Add a Jinja2 filter that appends md5sum to static files as a query parameter

        Adding the checksum as a query parameter invalidates any HTTP caching when the file
        contents change.

        Usage Example:
        <link rel="stylesheet" href="{{ static_file('theme/static/css/style.css') }}" type="text/css" />

        Will be rendered as
        <link rel="stylesheet" href="/static/css/style.css?<md5sum>" type="text/css" />
        """

        self.static_files_map = {}

        for static_dir, dirpath, filename in self._iter_static_files(context):
            source = os.path.join(dirpath, filename)

            href = os.path.join(
                "/",
                os.path.relpath(
                    context.settings.STATIC_ROOT,
                    context.settings.OUTPUT_ROOT,
                ),
                os.path.relpath(dirpath, static_dir),
                filename,
            )

            with open(source, "rb") as file:
                md5 = hashlib.file_digest(file, hashlib.md5).hexdigest()

            self.static_files_map[source] = {
                "href": href,
                "md5": md5,
            }

        def static_file(source: str):
            return "?".join(
                (
                    self.static_files_map[source]["href"],
                    self.static_files_map[source]["md5"],
                )
            )

        templating_engine.env.globals["static_file"] = static_file

    def post_build(self, context):
        if context.settings.CONTENT_PATHS:
            return

        for static_dir, dirpath, filename in self._iter_static_files(context):
            source = os.path.join(dirpath, filename)
            destination = os.path.join(
                context.settings.STATIC_ROOT,
                os.path.relpath(dirpath, static_dir),
                filename,
            )
            context.cp(source=source, destination=destination)
