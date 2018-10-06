# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u' '
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

_NAV =  (
    ('User Guide', 'user_guide/index'),
    ('About', 'about')
)


templates_path = ['_templates']

html_context.update({
    'PROJECT': project,
    'DESCRIPTION': description,
    'AUTHOR': authors,
    'WEBSITE_URL': 'https://panel.pyviz.org',
    'WEBSITE_SERVER': 'https://panel.pyviz.org',
    'VERSION': version,
    'NAV': _NAV,
    'LINKS': _NAV,
    'SOCIAL': (
        ('Gitter', '//gitter.im/ioam/holoviews'),
        ('Github', '//github.com/pyviz/panel'),
    )
})

nbbuild_patterns_to_take_along = ["simple.html"]
