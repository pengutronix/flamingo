import logging
import shutil
import os

FLAMINGO_BUILD = 1

logger = logging.getLogger('flamingo.plugins.Layers')


class Layers:
    def _copy(self, source, destination):
        def makedirs(path):
            dirname = os.path.dirname(path)

            if not os.path.exists(dirname):
                logger.debug('mkdir -p %s', dirname)
                os.makedirs(dirname)

        for root, dirs, files in os.walk(source):
            for f in files:
                src = os.path.join(root, f)

                dst = os.path.normpath(os.path.join(
                    destination, os.path.relpath(root, source), f))

                makedirs(dst)

                logger.debug('cp %s %s', src, dst)
                shutil.copy(src, dst)

    def pre_build(self, context):
        layers = getattr(context.settings, 'LAYERS', [])
        output_root = getattr(context.settings, 'OUTPUT_ROOT')

        if FLAMINGO_BUILD not in layers:
            return

        layers = layers[:layers.index(FLAMINGO_BUILD)]

        for layer in layers:
            self._copy(layer, output_root)

    def post_build(self, context):
        layers = getattr(context.settings, 'LAYERS', [])
        output_root = getattr(context.settings, 'OUTPUT_ROOT')

        if FLAMINGO_BUILD in layers:
            layers = layers[layers.index(FLAMINGO_BUILD) + 1:]

        for layer in layers:
            self._copy(layer, output_root)
