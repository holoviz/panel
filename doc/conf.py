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
# git tag instead of the default i.e. master.
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
            "icon": "fab fa-twitter-square",
        },
        {
            "name": "Discourse",
            "url": "https://discourse.holoviz.org/c/panel/5",
            "icon": "fab fa-discourse",
        },
    ],
    "footer_items": [
        "copyright",
        "last-updated",
    ],
    "navbar_end": ["navbar-icon-links"],
    "google_analytics_id": "UA-154795830-2",
    "pygment_light_style": "material",
    "pygment_dark_style": "material"
}

extensions += [
    'sphinx.ext.napoleon',
    'nbsite.gallery',
    'sphinx_copybutton',
    'nbsite.pyodide'
]
napoleon_numpy_docstring = True

myst_enable_extensions = ["colon_fence"]

nbsite_gallery_conf = {
    'github_org': 'holoviz',
    'github_project': 'panel',
    'galleries': {
        'gallery': {
            'title': 'Gallery',
            'sections': [
                {'path': 'demos',
                 'title': 'Demos',
                 'description': 'A set of sophisticated apps built to demonstrate the features of Panel.'},
                {'path': 'simple',
                 'title': 'Simple Apps',
                 'description': 'Simple example apps meant to provide a quick introduction to Panel.'},
                {'path': 'apis',
                 'title': 'APIs',
                 'description': ('Examples meant to demonstrate the usage of different Panel APIs '
                                 'such as interact and reactive functions.')},
                {'path': 'layout',
                 'title': 'Layouts',
                 'description': 'How to leverage Panel layout components to achieve complex layouts.'},
                {'path': 'dynamic',
                 'title': 'Dynamic UIs',
                 'description': ('Examples demonstrating how to build dynamic UIs with components that '
                                 'are added or removed interactively.')},
                {'path': 'param',
                 'title': 'Param based apps',
                 'description': 'Using the Param library to express UIs independently of Panel.'},
                {'path': 'streaming',
                 'title': 'Streaming',
                 'description': ('Streaming data to a visual component.')},
                {'path': 'components',
                 'title': 'Custom components',
                 'description': "Components created using Panel's ReactiveHTML class."},
                {'path': 'links',
                 'title': 'Linking',
                 'description': ('Using Javascript based links to define interactivity without '
                                 'without requiring a live kernel.')},
                {'path': 'styles',
                 'title': 'Styling & Theming',
                 'description': "Examples demonstrating how to style and theme different components."},
                {'path': 'external',
                 'title': 'External libraries',
                 'description': 'Wrapping external libraries with Panel.'}
            ]
        },
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
            'normalize_titles': False
        }
    },
    'thumbnail_url': 'https://assets.holoviews.org/panel/thumbnails',
    'deployment_url': 'https://panel-gallery.pyviz.demo.anaconda.com/'
}

if panel.__version__ != version and (PANEL_ROOT / 'dist' / 'wheels').is_dir():
    py_version = panel.__version__.replace("-dirty", "")
    panel_req = f'./wheels/panel-{py_version}-py3-none-any.whl'
    bokeh_req = f'./wheels/bokeh-{BOKEH_VERSION}-py3-none-any.whl'
else:
    panel_req = f'{CDN_DIST}wheels/panel-{PY_VERSION}-py3-none-any.whl'
    bokeh_req = f'{CDN_DIST}wheels/bokeh-{BOKEH_VERSION}-py3-none-any.whl'

nbsite_pyodide_conf = {
    'requirements': [bokeh_req, panel_req, 'pandas', 'pyodide-http', 'holoviews>=1.15.1']
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
