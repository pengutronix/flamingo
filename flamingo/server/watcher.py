from enum import Enum
from copy import copy
import time
import os


class Flags(Enum):
    # file system operation flags
    CREATE = 11
    MODIFY = 12
    DELETE = 13

    # file type flags
    CODE = 21
    CONTENT = 22
    STATIC = 23
    TEMPLATE = 24

    # message type flags
    INFO = 31
    ERROR = 32


class BaseWatcher:
    def __init__(self, context, interval=0.25):
        self.context = context
        self.interval = interval
        self._running = True

        # find git dir
        self._git_dir = None
        self._git_is_locked = False

        cwd = os.path.abspath(context.settings.CONTENT_ROOT)

        while cwd != '/':
            path = os.path.join(cwd, '.git')

            if os.path.exists(path):
                self._git_dir = path
                break

            cwd = os.path.dirname(cwd)

    def check(self, notify=lambda flags, message: None):
        # check for ongoing git rebase or merge
        if not self._git_dir:
            return True

        git_dir_content = os.listdir(self._git_dir)

        if 'MERGE_HEAD' in git_dir_content:
            if not self._git_is_locked:
                self._git_is_locked = True

                notify(
                    (Flags.INFO, ), 'git merge detected. watching suspended',
                )

            return False

        if('rebase-apply' in git_dir_content or
           'rebase-merge' in git_dir_content):

            if not self._git_is_locked:
                self._git_is_locked = True

                notify(
                    (Flags.INFO, ),
                    'git rebase detected. watching suspended',
                )

            return False

        if self._git_is_locked:
            self._git_is_locked = False

            notify((Flags.INFO, ), 'resume watching')

        return True

    def is_regular_file(self, name):
        if name.startswith('.'):
            return False

        if name.startswith('~'):
            return False

        if name.endswith('.swp'):
            return False

        return True

    def ignored(self, path):
        for prefix in self.context.settings.LIVE_SERVER_IGNORE_PREFIX:
            if path.startswith(prefix):
                return True

        return False

    def get_paths(self):
        # content
        paths = [
            (Flags.CONTENT, self.context.settings.CONTENT_ROOT, True),
        ]

        # themes
        for path in self.context.templating_engine.theme_paths:
            # templates
            template_path = os.path.join(path, 'templates')

            if os.path.exists(template_path):
                paths.append(
                    (Flags.TEMPLATE, os.path.join(path, 'templates'), True, )
                )

            # static
            static_path = os.path.join(path, 'static')

            if os.path.exists(static_path):
                paths.append(
                    (Flags.STATIC, os.path.join(path, 'static'), True, )
                )

        # settings
        for path in self.context.settings.modules:
            paths.append(
                (Flags.CODE, path, False, )
            )

        # plugins
        for path in self.context.plugins.PLUGIN_PATHS:
            paths.append(
                (Flags.CODE, path, False, )
            )

        # layers
        for path in self.context.settings.PRE_BUILD_LAYERS:
            paths.append(
                (Flags.STATIC, path, False, )
            )

        for path in self.context.settings.POST_BUILD_LAYERS:
            paths.append(
                (Flags.STATIC, path, False, )
            )

        return paths

    def sleep(self):
        time.sleep(self.interval)

    def shutdown(self):
        self._running = False


class DiscoveryWatcher(BaseWatcher):
    def watch(self, handle_events=lambda events: None,
              notify=lambda flags, message: None):

        self.state = {}
        self._running = True
        first_run = True
        paths = self.get_paths()

        while self._running:
            if not self.check(notify=notify):
                self.sleep()

                continue

            events = []

            # discover files
            new_state = {}

            for flag, path, is_dir in paths:
                if is_dir:
                    for dirpath, dirnames, filenames in os.walk(path):
                        for name in filenames:
                            if not self.is_regular_file(name):
                                continue

                            abs_path = os.path.join(dirpath, name)

                            if self.ignored(abs_path):
                                continue

                            try:
                                mtime = os.path.getmtime(abs_path)
                                new_state[abs_path] = (flag, mtime, )

                            except FileNotFoundError:
                                pass

                else:
                    abs_path = os.path.join(path)

                    if self.ignored(path):
                        continue

                    try:
                        new_state[abs_path] = (flag,
                                               os.path.getmtime(abs_path), )

                    except FileNotFoundError:
                        pass

            # first run
            if first_run:
                first_run = False
                self.state = copy(new_state)
                self.sleep()

                continue

            # check for deleted files
            for path, (flag, mtime) in self.state.items():
                if path not in new_state:
                    events.append(((flag, Flags.DELETE, ), path, ))

            for path, (flag, mtime) in new_state.items():
                # check for created files
                if path not in self.state:
                    events.append(((flag, Flags.CREATE, ), path, ))

                # check for modified files
                elif self.state[path][1] < mtime:

                    events.append(((flag, Flags.MODIFY, ), path, ))

            if events:
                handle_events(events)

            self.state = copy(new_state)
            self.sleep()
