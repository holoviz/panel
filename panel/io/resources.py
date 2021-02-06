"""
Patches bokeh resources to make it easy to add external JS and CSS
resources via the panel.config object.
"""
import glob
import json
import os

from collections import OrderedDict
from pathlib import Path
from urllib.parse import urljoin

from bokeh.embed.bundle import Bundle
from bokeh.resources import Resources
from jinja2 import Environment, Markup, FileSystemLoader

with open(Path(__file__).parent.parent / 'package.json') as f:
    package_json = json.load(f)
    js_version = package_json['version'].split('+')[0]

CDN_DIST = f"https://unpkg.com/@holoviz/panel@{js_version}/dist/"
LOCAL_DIST = "static/extensions/panel/"
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
    for cssf in glob.glob(str(DIST_DIR / 'css' / '*.css')):
        if self.mode != 'inline':
            break
        with open(cssf, encoding='utf-8') as f:
            css_txt = f.read()
        if css_txt not in raw:
            raw.append(css_txt)
    return raw + config.raw_css

def js_files(self):
    from ..config import config
    files = super(Resources, self).js_files
    js_files = files + list(config.js_files.values()) + list(config.js_modules.values())

    # Load requirejs last to avoid interfering with other libraries
    require_index = [i for i, jsf in enumerate(js_files) if 'require' in jsf]
    if self.mode == 'server':
        dist_dir = urljoin(self.root_url, LOCAL_DIST)
    else:
        dist_dir = CDN_DIST
    if require_index:
        requirejs = js_files.pop(require_index[0])
        if any('ace' in jsf for jsf in js_files):
            js_files.append(dist_dir + 'pre_require.js')
        js_files.append(requirejs)
        if any('ace' in jsf for jsf in js_files):
            js_files.append(dist_dir + 'post_require.js')
    return js_files

def css_files(self):
    from ..config import config

    files = super(Resources, self).css_files
    for cssf in config.css_files:
        if os.path.isfile(cssf) or cssf in files:
            continue
        files.append(cssf)
    if self.mode == 'server':
        dist_dir = urljoin(self.root_url, LOCAL_DIST)
    else:
        dist_dir = CDN_DIST
    for cssf in glob.glob(str(DIST_DIR / 'css' / '*.css')):
        if self.mode == 'inline':
            break
        files.append(dist_dir + f'css/{os.path.basename(cssf)}')
    return files

def render_js(self):
    return JS_RESOURCES.render(js_raw=self.js_raw, js_files=self.js_files, hashes=self.hashes)

def conffilter(value):
    return json.dumps(OrderedDict(value)).replace('"', '\'')

_env = get_env()
_env.filters['json'] = lambda obj: Markup(json.dumps(obj))
_env.filters['conffilter'] = conffilter

JS_RESOURCES = _env.get_template('js_resources.html')

Resources.css_raw = property(css_raw)
Resources.js_files = property(js_files)
Resources.css_files = property(css_files)
Resources.render_js = render_js
Bundle._render_js = render_js
