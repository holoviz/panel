"""
Patches bokeh resources to make it easy to add external JS and CSS
resources via the panel.config object.
"""
import glob
import json
import os

from base64 import b64encode
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path

import param

from bokeh.embed.bundle import (
    Bundle as BkBundle, _bundle_extensions, extension_dirs,
    bundle_models
)

from bokeh.resources import Resources as BkResources
from bokeh.settings import settings as _settings
from jinja2 import Environment, Markup, FileSystemLoader

from ..util import url_path
from .state import state


with open(Path(__file__).parent.parent / 'package.json') as f:
    package_json = json.load(f)
    js_version = package_json['version'].split('+')[0]

def get_env():
    ''' Get the correct Jinja2 Environment, also for frozen scripts.
    '''
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_templates'))
    return Environment(loader=FileSystemLoader(local_path))

def conffilter(value):
    return json.dumps(OrderedDict(value)).replace('"', '\'')

_env = get_env()
_env.filters['json'] = lambda obj: Markup(json.dumps(obj))
_env.filters['conffilter'] = conffilter

# Handle serving of the panel extension before session is loaded
RESOURCE_MODE = 'server'
PANEL_DIR = Path(__file__).parent.parent
DIST_DIR = PANEL_DIR / 'dist'
BUNDLE_DIR = DIST_DIR / 'bundled'
ASSETS_DIR = PANEL_DIR / 'assets'
BASE_TEMPLATE = _env.get_template('base.html')
DEFAULT_TITLE = "Panel Application"
JS_RESOURCES = _env.get_template('js_resources.html')
CDN_DIST = f"https://unpkg.com/@holoviz/panel@{js_version}/dist/"
LOCAL_DIST = "static/extensions/panel/"

extension_dirs['panel'] = str(DIST_DIR)

@contextmanager
def set_resource_mode(mode):
    global RESOURCE_MODE
    old_resources = _settings.resources._user_value
    old_mode = RESOURCE_MODE
    _settings.resources = RESOURCE_MODE = mode
    try:
        yield
    finally:
        RESOURCE_MODE = old_mode
        _settings.resources.set_value(old_resources)


def loading_css():
    from ..config import config
    with open(ASSETS_DIR / f'{config.loading_spinner}_spinner.svg', encoding='utf-8') as f:
        svg = f.read().replace('\n', '').format(color=config.loading_color)
    b64 = b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"""
    .bk.pn-loading.{config.loading_spinner}:before {{
      background-image: url("data:image/svg+xml;base64,{b64}")
    }}
    """


def bundled_files(model, file_type='javascript'):
    bdir = os.path.join(PANEL_DIR, 'dist', 'bundled', model.__name__.lower())
    name = model.__name__.lower()

    files = []
    for url in getattr(model, f"__{file_type}_raw__", []):
        filepath = url_path(url)
        test_filepath = filepath.split('?')[0]
        if RESOURCE_MODE == 'server' and os.path.isfile(os.path.join(bdir, test_filepath)):
            files.append(f'static/extensions/panel/bundled/{name}/{filepath}')
        else:
            files.append(url)
    return files


def bundle_resources(resources):
    global RESOURCE_MODE
    js_resources = css_resources = resources
    RESOURCE_MODE = mode = js_resources.mode if resources is not None else "inline"

    js_files = []
    js_raw = []
    css_files = []
    css_raw = []

    js_files.extend(js_resources.js_files)
    js_raw.extend(js_resources.js_raw)

    css_files.extend(css_resources.css_files)
    css_raw.extend(css_resources.css_raw)

    extensions = _bundle_extensions(None, js_resources)
    if mode == "inline":
        js_raw.extend([ Resources._inline(bundle.artifact_path) for bundle in extensions ])
    elif mode == "server":
        js_files.extend([ bundle.server_url for bundle in extensions ])
    elif mode == "cdn":
        for bundle in extensions:
            if bundle.cdn_url is not None:
                js_files.append(bundle.cdn_url)
            else:
                js_raw.append(Resources._inline(bundle.artifact_path))
    else:
        js_files.extend([ bundle.artifact_path for bundle in extensions ])

    ext = bundle_models(None)
    if ext is not None:
        js_raw.append(ext)

    hashes = js_resources.hashes if js_resources else {}

    return Bundle(
        js_files=js_files, js_raw=js_raw, css_files=css_files,
        css_raw=css_raw, hashes=hashes
    )


class Resources(BkResources):

    @classmethod
    def from_bokeh(cls, bkr):
        kwargs = {}
        if bkr.mode.startswith("server"):
            kwargs['root_url'] = bkr.root_url
        return cls(
            mode=bkr.mode, version=bkr.version, minified=bkr.minified,
            legacy=bkr.legacy, log_level=bkr.log_level,
            path_versioner=bkr.path_versioner,
            components=bkr._components, base_dir=bkr.base_dir,
            root_dir=bkr.root_dir, **kwargs
        )

    @property
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

        if config.loading_spinner:
            raw.append(loading_css())
        return raw + config.raw_css

    @property
    def js_files(self):
        from ..config import config
        from ..reactive import ReactiveHTML

        files = super(Resources, self).js_files

        for model in param.concrete_descendents(ReactiveHTML).values():
            if hasattr(model, '__javascript__'):
                for jsfile in model.__javascript__:
                    if jsfile not in files:
                        files.append(jsfile)

        js_files = []
        for js_file in files:
            if (js_file.startswith(state.base_url) or js_file.startswith('static/')):
                if js_file.startswith(state.base_url):
                    js_file = js_file[len(state.base_url):]
                if state.rel_path:
                    js_file = f'{state.rel_path}/{js_file}'
            js_files.append(js_file)
        js_files += list(config.js_files.values())

        # Load requirejs last to avoid interfering with other libraries
        require_index = [i for i, jsf in enumerate(js_files) if 'require' in jsf]
        if self.mode == 'server':
            if state.rel_path:
                dist_dir = f'{state.rel_path}/{LOCAL_DIST}'
            else:
                dist_dir = LOCAL_DIST
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

    @property
    def js_modules(self):
        from ..config import config
        from ..reactive import ReactiveHTML
        modules = list(config.js_modules.values())
        for model in param.concrete_descendents(ReactiveHTML).values():
            if hasattr(model, '__javascript_modules__'):
                for jsmodule in model.__javascript_modules__:
                    if jsmodule not in modules:
                        modules.append(jsmodule)
        return modules

    @property
    def css_files(self):
        from ..config import config
        from ..reactive import ReactiveHTML

        files = super(Resources, self).css_files

        for model in param.concrete_descendents(ReactiveHTML).values():
            if hasattr(model, '__css__'):
                for css_file in model.__css__:
                    if css_file not in files:
                        files.append(css_file)

        for cssf in config.css_files:
            if os.path.isfile(cssf) or cssf in files:
                continue
            files.append(cssf)
        if self.mode == 'server':
            if state.rel_path:
                dist_dir = f'{state.rel_path}/{LOCAL_DIST}'
            else:
                dist_dir = LOCAL_DIST
        else:
            dist_dir = CDN_DIST
        for cssf in glob.glob(str(DIST_DIR / 'css' / '*.css')):
            if self.mode == 'inline':
                break
            files.append(dist_dir + f'css/{os.path.basename(cssf)}')
        return files

    @property
    def render_js(self):
        return JS_RESOURCES.render(
            js_raw=self.js_raw, js_files=self.js_files,
            js_modules=self.js_modules, hashes=self.hashes
        )


class Bundle(BkBundle):

    def __init__(self, **kwargs):
        from ..config import config
        from ..reactive import ReactiveHTML
        js_modules = list(config.js_modules.values())
        for model in param.concrete_descendents(ReactiveHTML).values():
            if hasattr(model, '__javascript_modules__'):
                for js_module in model.__javascript_modules__:
                    if js_module not in js_modules:
                        js_modules.append(js_module)
        self.js_modules = kwargs.pop("js_modules", js_modules)
        super().__init__(**kwargs)

    @classmethod
    def from_bokeh(cls, bk_bundle):
        return cls(
            js_files=bk_bundle.js_files,
            js_raw=bk_bundle.js_raw,
            css_files=bk_bundle.css_files,
            css_raw=bk_bundle.css_raw,
            hashes=bk_bundle.hashes
        )

    def _render_js(self):
        js_files = []
        for js_file in self.js_files:
            if (js_file.startswith(state.base_url) or js_file.startswith('static/')):
                if js_file.startswith(state.base_url):
                    js_file = js_file[len(state.base_url):]
                
                if state.rel_path:
                    js_file = f'{state.rel_path}/{js_file}'
            js_files.append(js_file)
        return JS_RESOURCES.render(
            js_raw=self.js_raw, js_files=js_files,
            js_modules=self.js_modules, hashes=self.hashes
        )
