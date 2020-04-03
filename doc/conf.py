# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u'Panel'
authors = u'Panel contributors'
copyright = u'2019 ' + authors
description = 'High-level dashboarding for python visualization libraries'

import param

param.parameterized.docstring_signature = False
param.parameterized.docstring_describe_params = False

import panel
version = release = str(panel.__version__)

html_static_path += ['_static']
html_theme = 'sphinx_holoviz_theme'
html_theme_options = {
    'favicon': 'favicon.ico',
    'logo': 'logo_horizontal.png',
    'include_logo_text': False,
    'primary_color': '#00aa41',
    'primary_color_dark': '#00aa41',
    'secondary_color': '#5f9df0',
    'custom_css': 'site.css',
    'second_nav': True,
    'footer': False,
}

extensions += ['sphinx.ext.napoleon', 'nbsite.gallery']
napoleon_numpy_docstring = True

extensions += []

nbsite_gallery_conf = {
    'github_org': 'pyviz',
    'github_project': 'panel',
    'galleries': {
        'reference': {
            'title': 'Reference Gallery',
            'sections': [
                'panes',
                'layouts',
                'widgets'
            ]
        }
    },
    'thumbnail_url': 'https://assets.holoviews.org/panel/thumbnails',
    'deployment_url': 'https://panel-gallery.pyviz.demo.anaconda.com/'
}

_NAV = (
    ('Getting started', 'getting_started/index'),
    ('User Guide', 'user_guide/index'),
    ('Gallery', 'gallery/index'),
    ('Reference Gallery', 'reference/index'),
    ('Developer Guide', 'developer_guide/index'),
    ('Releases', 'releases'),
    ('API', 'api/index'),
    ('FAQ', 'FAQ'),
    ('About', 'about')
)

templates_path = ['_templates']

html_context.update({
    'js_includes': ['nbsite.js'],
    'PROJECT': project,
    'DESCRIPTION': description,
    'AUTHOR': authors,
    'VERSION': version,
    'GOOGLE_SEARCH_ID': '017396756996884923145:moq4gmnf37j',
    'GOOGLE_ANALYTICS_UA': 'UA-154795830-2',
    'WEBSITE_URL': 'https://panel.holoviz.org',
    'WEBSITE_SERVER': 'https://panel.holoviz.org',
    'NAV': _NAV,
    'LINKS': _NAV,
    'SOCIAL': (
        ('Discourse', '//discourse.holoviz.org'),
        ('Twitter', '//twitter.com/Panel_org'),
        ('Github', '//github.com/pyviz/panel'),
    )
})

nbbuild_patterns_to_take_along = ["simple.html", "*.json", "json_*"]


html_context['js_includes'].remove('nbsite.js')
html_context = {
    'js_includes': ['nbsite.js', 'require.js'],
    'css_includes': ['nbsite.css'] 
}
