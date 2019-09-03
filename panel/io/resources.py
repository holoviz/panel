"""
Patches bokeh resources to make it easy to add external JS and CSS
resources via the panel.config object.
"""
from __future__ import absolute_import, division, unicode_literals

import os

from bokeh.resources import Resources

def css_raw(self):
    from ..config import config
    raw = super(Resources, self).css_raw
    for cssf in config.css_files:
        if not os.path.isfile(cssf):
            continue
        with open(cssf) as f:
            raw.append(f.read())
    return raw + config.raw_css

def js_files(self):
    from ..config import config
    files = super(Resources, self).js_files
    return files + list(config.js_files.values())

def css_files(self):
    from ..config import config
    files = super(Resources, self).css_files
    for cssf in config.css_files:
        if os.path.isfile(cssf):
            continue
        files.append(cssf)
    return files

Resources.css_raw = property(css_raw)
Resources.js_files = property(js_files)
Resources.css_files = property(css_files)
