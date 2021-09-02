# -*- coding: utf-8 -*-

import param

param.parameterized.docstring_signature = False
param.parameterized.docstring_describe_params = False

from nbsite.shared_conf import *

project = u'Panel'
authors = u'Panel contributors'
copyright = u'2019-2021 ' + authors
description = 'High-level dashboarding for python visualization libraries'

import panel
version = release = str(panel.__version__)

html_static_path += ['_static']

html_css_files = [
    'nbsite.css',
    'css/custom.css'
]

html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo_horizontal.png"
html_favicon = "_static/favicon.ico"

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
            "url": "https://discourse.holoviz.org/",
            "icon": "fab fa-discourse",
        },
    ]
}

extensions += ['sphinx.ext.napoleon', 'nbsite.gallery']
napoleon_numpy_docstring = True

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
                 'description': ('Examples demonstrating how to build dynamic UIs with components that'
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
                'indicators',
                'widgets',
            ]
        }
    },
    'thumbnail_url': 'https://assets.holoviews.org/panel/thumbnails',
    'deployment_url': 'https://panel-gallery.pyviz.demo.anaconda.com/'
}

templates_path = ['_templates']

html_context.update({
    "last_release": f"v{'.'.join(panel.__version__.split('.')[:3])}",
    "github_user": "holoviz",
    "github_repo": "panel",
    "google_analytics_id": "UA-154795830-2",
})

nbbuild_patterns_to_take_along = ["simple.html", "*.json", "json_*"]
