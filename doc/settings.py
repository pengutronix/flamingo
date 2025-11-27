PROJECT_NAME = "flamingo"
CONTENT_ROOT = "content"
OUTPUT_ROOT = "output"

THEME_PATHS = [
    "theme",
]

PLUGINS = [
    "flamingo.plugins.rstPygments",
    "flamingo.plugins.Menu",
    "flamingo.plugins.Git",
    "flamingo.plugins.Thumbnails",
    "flamingo.plugins.SphinxThemes",
    "plugins/rst_setting.py::rstSetting",
]

POST_BUILD_LAYERS = [
    "overlay",
]

# sphinx theme
SPHINX_THEMES_HTML_THEME = "sphinx_rtd_theme"
SPHINX_THEMES_LOGO_URL = "/static/flamingo.svg"
SPHINX_THEMES_DOCSTITLE = "Flamingo"
SPHINX_THEMES_SHORTTITLE = "Flamingo"
SPHINX_THEMES_PROJECT = "Flamingo"

SPHINX_THEMES_EXTRA_STYLESHEETS = [
    "/static/custom.css",
]
