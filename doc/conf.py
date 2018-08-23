# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u'PyVizPanels'
authors = u'PyVizPanels contributors'
copyright = u'2018 ' + authors
description = 'High-level dashboarding for python visualization libraries'

import pyviz_panels
version = release = str(pyviz_panels.__version__)

html_static_path += ['_static']
html_theme = 'sphinx_ioam_theme'
html_theme_options = {
    'logo':'param-logo.png',
    'favicon':'favicon.ico',
#    'css':'parambokeh.css'
}

_NAV =  (
)

html_context.update({
    'PROJECT': project,
    'DESCRIPTION': description,
    'AUTHOR': authors,
    'WEBSITE_URL': 'https://panels.pyviz.org',
    'VERSION': version,
    'NAV': _NAV,
    'LINKS': _NAV,
    'SOCIAL': (
        ('Gitter', '//gitter.im/ioam/holoviews'),
        ('Github', '//github.com/pyviz/pyviz_panels'),
    )
})

nbbuild_patterns_to_take_along = ["simple.html"]
