import subprocess
from shlex import split
import logging

logger = logging.getLogger('flamingo.plugins.Git')


class Git:
    def contents_parsed(self, context):
        VERSION_CMD = context.settings.get('GIT_VERSION_CMD',
                                           'git describe').strip()

        VERSION_EXTRA_CONTEXT_NAME = context.settings.get(
            'GIT_VERSION_EXTRA_CONTEXT_NAME', 'GIT_VERSION')

        if not VERSION_CMD.startswith('git'):
            logger.error('settings.GIT_VERSION_CMD has to start with "git"')

            return

        cmd = ['git', *split(VERSION_CMD)[1:]]

        try:
            version = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                shell=False,
            ).decode().strip()

        except FileNotFoundError:
            logger.error('git seems not to be installed')

            return

        except subprocess.CalledProcessError as e:
            logger.error("%s returned %s: %s",
                         VERSION_CMD, e.returncode, e.output.decode())

            return

        context.settings.EXTRA_CONTEXT[VERSION_EXTRA_CONTEXT_NAME] = version
