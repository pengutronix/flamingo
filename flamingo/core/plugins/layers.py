import os


def _cp(context, source, destination):
    for root, dirs, files in os.walk(source):
        for f in files:
            src = os.path.join(root, f)

            dst = os.path.normpath(os.path.join(
                destination, os.path.relpath(root, source), f))

            context.cp(src, dst)


class PreBuildLayers:
    def pre_build(self, context):
        OUTPUT_ROOT = context.settings.OUTPUT_ROOT

        for layer in context.settings.PRE_BUILD_LAYERS:
            _cp(context, layer, OUTPUT_ROOT)


class PostBuildLayers:
    def post_build(self, context):
        OUTPUT_ROOT = context.settings.OUTPUT_ROOT

        for layer in context.settings.POST_BUILD_LAYERS:
            _cp(context, layer, OUTPUT_ROOT)
