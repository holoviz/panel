# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u'Panel'
authors = u'Panel contributors'
copyright = u'2018 ' + authors
description = 'High-level dashboarding for python visualization libraries'

import panel
version = release = str(panel.__version__)

html_static_path += ['_static']
html_theme = 'sphinx_ioam_theme'
html_theme_options = {
    'logo': 'logo_horizontal.png',
    'favicon': 'favicon.ico',
    'css': 'site.css'    
}

extensions += ['nbsite.gallery']

nbsite_gallery_conf = {
    'github_org': 'pyviz',
    'github_project': 'panel',
    'galleries': {
        'gallery': {
            'title': 'Gallery',
            'sections': [
                'links',
                'external'
            ]
        },
        'reference': {
            'title': 'Reference Gallery',
            'sections': [
                'panes',
                'widgets'
            ]
        }
    },
    'thumbnail_url': 'https://assets.holoviews.org/panel/thumbnails'
}

_NAV =  (
    ('User Guide', 'user_guide/index'),
    ('Gallery', 'gallery/index'),
    ('Reference Gallery', 'reference/index'),
    ('Developer Guide', 'developer_guide/index'),
    ('FAQ', 'FAQ'),
    ('About', 'about')
)

templates_path = ['_templates']

html_context.update({
    'PROJECT': project,
    'DESCRIPTION': description,
    'AUTHOR': authors,
    'VERSION': version,
    'WEBSITE_URL': 'https://panel.pyviz.org',
    'WEBSITE_SERVER': 'https://panel.pyviz.org',
    'VERSION': version,
    'NAV': _NAV,
    'LINKS': _NAV,
    'SOCIAL': (
        ('Gitter', '//gitter.im/pyviz/pyviz'),
        ('Github', '//github.com/pyviz/panel'),
    )
})

nbbuild_patterns_to_take_along = ["simple.html"]
