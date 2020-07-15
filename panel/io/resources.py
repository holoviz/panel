"""
Patches bokeh resources to make it easy to add external JS and CSS
resources via the panel.config object.
"""
from __future__ import absolute_import, division, unicode_literals

import json
import os
from collections import OrderedDict

from bokeh.resources import Resources
from jinja2 import Environment, Markup, FileSystemLoader


def get_env():
    ''' Get the correct Jinja2 Environment, also for frozen scripts.
    '''
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_templates'))
    return Environment(loader=FileSystemLoader(local_path))

def css_raw(self):
    from ..config import config
    raw = super(Resources, self).css_raw
    for cssf in config.css_files:
        if not os.path.isfile(cssf):
            continue
        with open(cssf) as f:
            css_txt = f.read()
            if css_txt not in raw:
                raw.append(css_txt)
    return raw + config.raw_css

def js_files(self):
    from ..config import config
    files = super(Resources, self).js_files
    js_files = files + list(config.js_files.values())

    # Load requirejs last to avoid interfering with other libraries
    require_index = [i for i, jsf in enumerate(js_files) if 'require' in jsf]
    if require_index:
        requirejs = js_files.pop(require_index[0])
        if any('ace' in jsf for jsf in js_files):
            js_files.append('/panel_dist/pre_require.js')
        js_files.append(requirejs)
        if any('ace' in jsf for jsf in js_files):
            js_files.append('/panel_dist/post_require.js')
    return js_files

def css_files(self):
    from ..config import config
    files = super(Resources, self).css_files
    for cssf in config.css_files:
        if os.path.isfile(cssf) or cssf in files:
            continue
        files.append(cssf)
    return files

def conffilter(value):
    return json.dumps(OrderedDict(value)).replace('"', '\'')


class PanelResources(Resources):

    def __init__(self, extra_css_files=None, **kwargs):
        super(PanelResources, self).__init__(**kwargs)
        self._extra_css_files = extra_css_files or []

    @property
    def css_raw(self):
        raw = super(PanelResources, self).css_raw
        for cssf in self._extra_css_files:
            if not os.path.isfile(cssf):
                continue
            with open(cssf) as f:
                css_txt = f.read()
                if css_txt not in raw:
                    raw.append(css_txt)
        return raw


_env = get_env()
_env.filters['json'] = lambda obj: Markup(json.dumps(obj))
_env.filters['conffilter'] = conffilter

Resources.css_raw = property(css_raw)
Resources.js_files = property(js_files)
Resources.css_files = property(css_files)
