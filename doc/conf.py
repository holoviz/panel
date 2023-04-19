import json
import os
import pathlib

import param

param.parameterized.docstring_signature = False
param.parameterized.docstring_describe_params = False

from nbsite.shared_conf import *

project = 'Panel'
authors = 'Panel contributors'
copyright_years['start_year'] = '2019'
copyright = copyright_fmt.format(**copyright_years)
description = 'High-level dashboarding for python visualization libraries'

import panel

from panel.io.convert import BOKEH_VERSION, PY_VERSION
from panel.io.resources import CDN_DIST

PANEL_ROOT = pathlib.Path(panel.__file__).parent

version = release = base_version(panel.__version__)
js_version = json.loads((PANEL_ROOT / 'package.json').read_text())['version']

# For the interactivity warning box created by nbsite to point to the right
# git tag instead of the default i.e. main.
os.environ['BRANCH'] = f"v{release}"

html_static_path += ['_static']

html_css_files = [
    'nbsite.css',
    'css/custom.css',
    'css/dataframe.css',
]

html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo_horizontal.png"
html_favicon = "_static/icons/favicon.ico"

html_theme_options = {
    "github_url": "https://github.com/holoviz/panel",
    "icon_links": [
        {
            "name": "Twitter",
            "url": "https://twitter.com/Panel_Org",
            "icon": "fa-brands fa-twitter-square",
        },
        {
            "name": "Discourse",
            "url": "https://discourse.holoviz.org/c/panel/5",
            "icon": "fa-brands fa-discourse",
        },
        {
            "name": "Discord",
            "url": "https://discord.gg/muhupDZM",
            "icon": "fa-brands fa-discord",
        },
    ],
    "google_analytics_id": "UA-154795830-2",
    "pygment_light_style": "material",
    "pygment_dark_style": "material",
    "header_links_before_dropdown": 5
}

extensions += [
    'sphinx.ext.napoleon',
    'nbsite.gallery',
    'sphinx_copybutton',
    'nbsite.pyodide'
]
napoleon_numpy_docstring = True

myst_enable_extensions = ["colon_fence", "deflist"]

nbsite_gallery_conf = {
    'github_org': 'holoviz',
    'github_project': 'panel',
    'galleries': {
        'reference': {
            'title': 'Reference Gallery',
            'sections': [
                'panes',
                'layouts',
                'templates',
                'global',
                'indicators',
                'widgets',
            ],
            'titles': {
                'Vega': 'Altair & Vega',
                'DeckGL': 'PyDeck & Deck.gl',
                'ECharts': 'PyEcharts & ECharts',
                'IPyWidget': 'ipywidgets'
            },
            'as_pyodide': True,
            'normalize_titles': False
        }
    },
    'thumbnail_url': 'https://assets.holoviz.org/panel/thumbnails',
    'deployment_url': 'https://panel-gallery.pyviz.demo.anaconda.com/',
    'jupyterlite_url': 'https://panelite.holoviz.org/lab/index.html'
}

if panel.__version__ != version and (PANEL_ROOT / 'dist' / 'wheels').is_dir():
    py_version = panel.__version__.replace("-dirty", "")
    panel_req = f'./wheels/panel-{py_version}-py3-none-any.whl'
    bokeh_req = f'./wheels/bokeh-{BOKEH_VERSION}-py3-none-any.whl'
else:
    panel_req = f'{CDN_DIST}wheels/panel-{PY_VERSION}-py3-none-any.whl'
    bokeh_req = f'{CDN_DIST}wheels/bokeh-{BOKEH_VERSION}-py3-none-any.whl'

nbsite_pyodide_conf = {
    'PYODIDE_URL': 'https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js',
    'requirements': [bokeh_req, panel_req, 'pandas', 'pyodide-http', 'holoviews>=1.16.0a3'],
    'requires': {
        'gallery/penguin_crossfilter': ['scipy'],
        'gallery/windturbines': ['fastparquet']
    }
}

templates_path = [
    '_templates'
]

html_context.update({
    "last_release": f"v{release}",
    "github_user": "holoviz",
    "github_repo": "panel",
    "default_mode": "light"
})

nbbuild_patterns_to_take_along = ["simple.html", "*.json", "json_*"]

# Override the Sphinx default title that appends `documentation`
html_title = f'{project} v{version}'

suppress_warnings = ["myst.header", "ref.myst", "mystnb.unknown_mime_type"]
