import contextlib

from .authors.authors import Authors  # NOQA
from .bootstrap.plugins import Bootstrap3, Bootstrap4  # NOQA
from .git import Git  # NOQA
from .html import HTML  # NOQA
from .i18n import I18N  # NOQA
from .jquery.plugins import jQuery1, jQuery2, jQuery3  # NOQA
from .menu.menu import Menu  # NOQA
from .photoswipe.plugin import PhotoSwipe  # NOQA
from .redirects import Redirects  # NOQA
from .rst.bootstrap3 import rstBootstrap3  # NOQA
from .rst.image import rstImage  # NOQA
from .rst.include import rstInclude  # NOQA
from .rst.link import rstLink  # NOQA
from .rst.plugin import reStructuredText  # NOQA
from .rst.table import rstTable  # NOQA
from .rtd.plugin import ReadTheDocs  # NOQA
from .tags.tags import Tags  # NOQA
from .time import Time  # NOQA
from .yaml import Yaml  # NOQA

with contextlib.suppress(ImportError):
    from .rst.pygments import rstPygments  # NOQA


with contextlib.suppress(ImportError):
    from .feeds import Feeds  # NOQA


with contextlib.suppress(ImportError):
    from .md import Markdown  # NOQA


with contextlib.suppress(ImportError):
    from .thumbnails import Thumbnails  # NOQA


with contextlib.suppress(ImportError):
    from .sphinx_themes.plugin import SphinxThemes  # NOQA
