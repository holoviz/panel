"""
Patches bokeh resources to make it easy to add external JS and CSS
resources via the panel.config object.
"""
from __future__ import absolute_import, division, unicode_literals

import glob
import json
import os

from collections import OrderedDict
from pathlib import Path

from bokeh.resources import Resources
from bokeh.settings import settings
from jinja2 import Environment, Markup, FileSystemLoader


with open(Path(__file__).parent.parent / 'package.json') as f:
    package_json = json.load(f)
    js_version = package_json['version'].split('+')[0]

CDN_DIST = f"https://unpkg.com/@holoviz/panel@{js_version}/dist/"
LOCAL_DIST = "/static/extensions/panel/"
DIST_DIR = Path(__file__).parent.parent / 'dist'


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
        with open(cssf, encoding='utf-8') as f:
            css_txt = f.read()
            if css_txt not in raw:
                raw.append(css_txt)
    resources = settings.resources(default='server')
    for cssf in glob.glob(str(DIST_DIR / 'css' / '*.css')):
        if resources != 'inline':
            break
        with open(cssf, encoding='utf-8') as f:
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
    resources = settings.resources(default='server')
    dist_dir = LOCAL_DIST if resources == 'server' else CDN_DIST
    if require_index:
        requirejs = js_files.pop(require_index[0])
        if any('ace' in jsf for jsf in js_files):
            js_files.append(dist_dir+'pre_require.js')
        js_files.append(requirejs)
        if any('ace' in jsf for jsf in js_files):
            js_files.append(dist_dir+'post_require.js')
    return js_files

def css_files(self):
    from ..config import config

    files = super(Resources, self).css_files
    for cssf in config.css_files:
        if os.path.isfile(cssf) or cssf in files:
            continue
        files.append(cssf)
    resources = settings.resources(default='server')
    dist_dir = LOCAL_DIST if resources == 'server' else CDN_DIST
    for cssf in glob.glob(str(DIST_DIR / 'css' / '*.css')):
        if resources == 'inline':
            break
        files.append(dist_dir + f'css/{os.path.basename(cssf)}')
    return files

def conffilter(value):
    return json.dumps(OrderedDict(value)).replace('"', '\'')

_env = get_env()
_env.filters['json'] = lambda obj: Markup(json.dumps(obj))
_env.filters['conffilter'] = conffilter

Resources.css_raw = property(css_raw)
Resources.js_files = property(js_files)
Resources.css_files = property(css_files)
