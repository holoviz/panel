"""
Patches bokeh resources to make it easy to add external JS and CSS
resources via the panel.config object.
"""
from __future__ import annotations

import importlib
import json
import logging
import mimetypes
import os
import pathlib
import re
import textwrap

from base64 import b64encode
from collections import OrderedDict
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import (
    TYPE_CHECKING, Dict, List, Literal, TypedDict,
)

import param

from bokeh.embed.bundle import (
    CSS_RESOURCES as BkCSS_RESOURCES, Bundle as BkBundle, _bundle_extensions,
    _use_mathjax, bundle_models, extension_dirs,
)
from bokeh.model import Model
from bokeh.models import ImportedStyleSheet
from bokeh.resources import Resources as BkResources, _get_server_urls
from bokeh.settings import settings as _settings
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from markupsafe import Markup

from ..config import config, panel_extension as extension
from ..util import isurl, url_path
from .loading import LOADING_INDICATOR_CSS_CLASS
from .state import state

if TYPE_CHECKING:
    from bokeh.resources import Urls

    class ResourcesType(TypedDict):
        css: Dict[str, str]
        js:  Dict[str, str]
        js_modules: Dict[str, str]
        raw_css: List[str]

logger = logging.getLogger(__name__)

ResourceAttr = Literal["__css__", "__javascript__"]

with open(Path(__file__).parent.parent / 'package.json') as f:
    package_json = json.load(f)
    JS_VERSION = package_json['version'].split('+')[0]

def get_env():
    ''' Get the correct Jinja2 Environment, also for frozen scripts.
    '''
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_templates'))
    return Environment(loader=FileSystemLoader(local_path))

def conffilter(value):
    return json.dumps(OrderedDict(value)).replace('"', '\'')

_env = get_env()
_env.trim_blocks = True
_env.lstrip_blocks = True
_env.filters['json'] = lambda obj: Markup(json.dumps(obj))
_env.filters['conffilter'] = conffilter
_env.filters['sorted'] = sorted

# Handle serving of the panel extension before session is loaded
RESOURCE_MODE = 'server'
PANEL_DIR = Path(__file__).parent.parent
DIST_DIR = PANEL_DIR / 'dist'
BUNDLE_DIR = DIST_DIR / 'bundled'
ASSETS_DIR = PANEL_DIR / 'assets'
INDEX_TEMPLATE = _env.get_template('convert_index.html')
BASE_TEMPLATE = _env.get_template('base.html')
ERROR_TEMPLATE = _env.get_template('error.html')
LOGOUT_TEMPLATE = _env.get_template('logout.html')
BASIC_LOGIN_TEMPLATE = _env.get_template('basic_login.html')
DEFAULT_TITLE = "Panel Application"
JS_RESOURCES = _env.get_template('js_resources.html')
CDN_URL = f"https://cdn.holoviz.org/panel/{JS_VERSION}/"
CDN_DIST = f"{CDN_URL}dist/"
DOC_DIST = "https://panel.holoviz.org/_static/"
LOCAL_DIST = "static/extensions/panel/"
COMPONENT_PATH = "components/"

BK_PREFIX_RE = re.compile('\.bk\.')

RESOURCE_URLS = {
    'font-awesome': {
        'zip': 'https://use.fontawesome.com/releases/v5.15.4/fontawesome-free-5.15.4-web.zip',
        'src': 'fontawesome-free-5.15.4-web/',
        'exclude': ['*.svg', '*.scss', '*.less']
    },
    'bootstrap4': {
        'tar': 'https://registry.npmjs.org/bootstrap/-/bootstrap-4.6.1.tgz',
        'src': 'package/dist',
        'exclude': [],
        'dest': ''
    },
    'bootstrap5': {
        'tar': 'https://registry.npmjs.org/bootstrap/-/bootstrap-5.3.0-alpha1.tgz',
        'src': 'package/dist',
        'exclude': [],
        'dest': ''
    },
    'jQuery': {
        'tar': 'https://registry.npmjs.org/jquery/-/jquery-3.5.1.tgz',
        'src': 'package/dist',
        'exclude': [],
        'dest': ''
    }
}

CSS_URLS = {
    'font-awesome': f'{CDN_DIST}bundled/font-awesome/css/all.min.css',
    'bootstrap4': f'{CDN_DIST}bundled/bootstrap4/css/bootstrap.min.css',
    'bootstrap5': f'{CDN_DIST}bundled/bootstrap5/css/bootstrap.min.css'
}

JS_URLS = {
    'jQuery': f'{CDN_DIST}bundled/jquery/jquery.slim.min.js',
    'bootstrap4': f'{CDN_DIST}bundled/bootstrap4/js/bootstrap.bundle.min.js',
    'bootstrap5': f'{CDN_DIST}bundled/bootstrap5/js/bootstrap.bundle.min.js'
}

extension_dirs['panel'] = str(DIST_DIR)

mimetypes.add_type("application/javascript", ".js")

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

def use_cdn() -> bool:
    return _settings.resources(default="server") != 'server'

def get_dist_path(cdn: bool | Literal['auto'] = 'auto') -> str:
    cdn = use_cdn() if cdn == 'auto' else cdn
    if cdn:
        dist_path = CDN_DIST
    elif state.rel_path:
        dist_path = f'{state.rel_path}/{LOCAL_DIST}'
    else:
        dist_path = f'{LOCAL_DIST}'
    return dist_path

def is_cdn_url(url) -> bool:
    return isurl(url) and url.startswith(CDN_DIST)

def process_raw_css(raw_css):
    """
    Converts old-style Bokeh<3 compatible CSS to Bokeh 3 compatible CSS.
    """
    return [BK_PREFIX_RE.sub('.', css) for css in raw_css]

@lru_cache(maxsize=None)
def loading_css(loading_spinner, color, max_height):
    with open(ASSETS_DIR / f'{loading_spinner}_spinner.svg', encoding='utf-8') as f:
        svg = f.read().replace('\n', '').format(color=color)
    b64 = b64encode(svg.encode('utf-8')).decode('utf-8')
    return textwrap.dedent(f"""
    :host(.{LOADING_INDICATOR_CSS_CLASS}.pn-{loading_spinner}):before, .pn-loading.pn-{loading_spinner}:before {{
      background-image: url("data:image/svg+xml;base64,{b64}");
      background-size: auto calc(min(50%, {max_height}px));
    }}""")

def resolve_custom_path(
    obj, path: str | os.PathLike, relative: bool = False
) -> pathlib.Path | None:
    """
    Attempts to resolve a path relative to some component.

    Arguments
    ---------
    obj: type | object
       The component to resolve the path relative to.
    path: str | os.PathLike
        Absolute or relative path to a resource.
    relative: bool
        Whether to return a relative path.

    Returns
    -------
    path: pathlib.Path | None
    """
    if not path:
        return
    if not isinstance(obj, type):
        obj = type(obj)
    try:
        mod = importlib.import_module(obj.__module__)
        module_path = Path(mod.__file__).parent
        assert module_path.exists()
    except Exception:
        return None
    path = pathlib.Path(path)
    if path.is_absolute():
        abs_path = path
    else:
        abs_path = module_path / path
    if not abs_path.is_file():
        return None
    abs_path = abs_path.resolve()
    if not relative:
        return abs_path
    return os.path.relpath(abs_path, module_path)

def component_resource_path(component, attr, path):
    """
    Generates a canonical URL for a component resource.

    To be used in conjunction with the `panel.io.server.ComponentResourceHandler`
    which allows dynamically resolving resources defined on components.
    """
    if not isinstance(component, type):
        component = type(component)
    component_path = COMPONENT_PATH
    if state.rel_path:
        component_path = f"{state.rel_path}/{component_path}"
    rel_path = str(resolve_custom_path(component, path, relative=True)).replace(os.path.sep, '/')
    return f'{component_path}{component.__module__}/{component.__name__}/{attr}/{rel_path}'

def patch_stylesheet(stylesheet, dist_url):
    url = stylesheet.url
    if url.startswith(CDN_DIST+dist_url) and dist_url != CDN_DIST:
        patched_url = url.replace(CDN_DIST+dist_url, dist_url) + f'?v={JS_VERSION}'
    elif url.startswith(CDN_DIST) and dist_url != CDN_DIST:
        patched_url = url.replace(CDN_DIST, dist_url) + f'?v={JS_VERSION}'
    else:
        return
    try:
        stylesheet.url = patched_url
    except Exception:
        pass

def resolve_stylesheet(cls, stylesheet: str, attribute: str | None = None):
    """
    Resolves a stylesheet definition, e.g. originating on a component
    Reactive._stylesheets or a Design.modifiers attribute. Stylesheets
    may be defined as one of the following:

    - Absolute URL defined with http(s) protocol
    - A path relative to the component

    Arguments
    ---------
    cls: type | object
        Object or class defining the stylesheet
    stylesheet: str
        The stylesheet definition
    """
    stylesheet = str(stylesheet)
    if not stylesheet.startswith('http') and attribute and (custom_path:= resolve_custom_path(cls, stylesheet)):
        if not state._is_pyodide and state.curdoc and state.curdoc.session_context:
            stylesheet = component_resource_path(cls, attribute, stylesheet)
        else:
            stylesheet = custom_path.read_text(encoding='utf-8')
    return stylesheet

def patch_model_css(root, dist_url):
    """
    Temporary patch for Model.css property used by Panel to provide
    stylesheets for components.

    ALERT: Should find better solution before official Bokeh 3.x compatible release
    """
    # Patch model CSS properties
    doc = root.document
    if doc:
        held = doc.callbacks.hold_value
        events = list(doc.callbacks._held_events)
        doc.hold()
    for stylesheet in root.select({'type': ImportedStyleSheet}):
        patch_stylesheet(stylesheet, dist_url)
    if doc:
        doc.callbacks._held_events = events
        if held:
            doc.callbacks._hold = held
        else:
            doc.unhold()

def global_css(name):
    if RESOURCE_MODE == 'server':
        return f'static/extensions/panel/css/{name}.css'
    else:
        return f'{CDN_DIST}css/{name}.css'

def bundled_files(model, file_type='javascript'):
    name = model.__name__.lower()
    bdir = BUNDLE_DIR / name
    shared = list((JS_URLS if file_type == 'javascript' else CSS_URLS).values())
    files = []
    for url in getattr(model, f"__{file_type}_raw__", []):
        if url.startswith(CDN_DIST):
            filepath = url.replace(f'{CDN_DIST}bundled/', '')
        elif url.startswith(config.npm_cdn):
            filepath = url.replace(config.npm_cdn, '')[1:]
        else:
            filepath = url_path(url)
        test_filepath = filepath.split('?')[0]
        if url in shared:
            prefixed = filepath
            test_path = BUNDLE_DIR / test_filepath
        elif not test_filepath.replace('/', '').startswith(f'{name}/'):
            prefixed = f'{name}/{test_filepath}'
            test_path = bdir / test_filepath
        else:
            prefixed = test_filepath
            test_path = BUNDLE_DIR / test_filepath
        if test_path.is_file():
            if RESOURCE_MODE == 'server':
                files.append(f'static/extensions/panel/bundled/{prefixed}')
            elif filepath == test_filepath:
                files.append(f'{CDN_DIST}bundled/{prefixed}')
            else:
                files.append(url)
        else:
            files.append(url)
    return files

def bundle_resources(roots, resources, notebook=False, reloading=False, enable_mathjax='auto'):
    from ..config import panel_extension as ext
    global RESOURCE_MODE
    if not isinstance(resources, Resources):
        resources = Resources.from_bokeh(resources, notebook=notebook)
    js_resources = css_resources = resources
    RESOURCE_MODE = mode = js_resources.mode if resources is not None else "inline"

    js_files = []
    js_raw = []
    css_files = []
    css_raw = []

    if isinstance(enable_mathjax, bool):
        use_mathjax = enable_mathjax
    elif roots:
        use_mathjax = _use_mathjax(roots) or 'mathjax' in ext._loaded_extensions
    else:
        use_mathjax = False

    if js_resources:
        js_resources = js_resources.clone()
        if not use_mathjax and "bokeh-mathjax" in js_resources.components:
            js_resources.components.remove("bokeh-mathjax")
        if reloading:
            js_resources.components.clear()

        js_files.extend(js_resources.js_files)
        js_raw.extend(js_resources.js_raw)

    css_files.extend(css_resources.css_files)
    css_raw.extend(css_resources.css_raw)

    extensions = _bundle_extensions(None, js_resources)
    if reloading:
        extensions = [
            ext for ext in extensions if not ext.cdn_url.startswith('https://unpkg.com/@holoviz/panel@')
        ]
    extra_js = []
    if mode == "inline":
        js_raw.extend([ Resources._inline(bundle.artifact_path) for bundle in extensions ])
    elif mode == "server":
        for bundle in extensions:
            server_url = bundle.server_url
            if resources.root_url and not resources.absolute:
                server_url = server_url.replace(resources.root_url, '', 1)
            js_files.append(server_url)
    elif mode == "cdn":
        for bundle in extensions:
            if bundle.cdn_url is not None:
                extra_js.append(bundle.cdn_url)
            else:
                js_raw.append(Resources._inline(bundle.artifact_path))
    else:
        extra_js.extend([ bundle.artifact_path for bundle in extensions ])
    js_files += resources.adjust_paths(extra_js)

    ext = bundle_models(None)
    if ext is not None:
        js_raw.append(ext)

    hashes = js_resources.hashes if js_resources else {}
    return Bundle(
        css_files=css_files,
        css_raw=css_raw,
        hashes=hashes,
        js_files=js_files,
        js_raw=js_raw,
        js_module_exports=resources.js_module_exports,
        js_modules=resources.js_modules,
        notebook=notebook,
    )


class ResourceComponent:
    """
    Mix-in class for components that define a set of resources
    that have to be resolved.
    """

    _resources = {
        'css': {},
        'font': {},
        'js': {},
        'js_modules': {},
        'raw_css': [],
    }

    @classmethod
    def _resolve_resource(cls, resource_type: str, resource: str, cdn: bool = False):
        dist_path = get_dist_path(cdn=cdn)
        if resource.startswith(CDN_DIST):
            resource_path = resource.replace(f'{CDN_DIST}bundled/', '')
        elif resource.startswith(config.npm_cdn):
            resource_path = resource.replace(config.npm_cdn, '')[1:]
        elif resource.startswith('http:'):
            resource_path = url_path(resource)
        else:
            resource_path = resource

        if resource_type == 'js_modules' and not (state.rel_path or cdn):
            prefixed_dist = f'./{dist_path}'
        else:
            prefixed_dist = dist_path

        bundlepath = BUNDLE_DIR / resource_path.replace('/', os.path.sep)
        # Windows may trigger OSError: [WinError 123]
        try:
            is_file = bundlepath.is_file()
        except Exception:
            is_file = False
        if is_file:
            return f'{prefixed_dist}bundled/{resource_path}'
        elif isurl(resource):
            return resource
        elif resolve_custom_path(cls, resource):
            return component_resource_path(
                cls, f'_resources/{resource_type}', resource
            )

    def resolve_resources(self, cdn: bool | Literal['auto'] = 'auto') -> ResourcesType:
        """
        Resolves the resources required for this component.

        Arguments
        ---------
        cdn: bool | Literal['auto']
            Whether to load resources from CDN or local server. If set
            to 'auto' value will be automatically determine based on
            global settings.

        Returns
        -------
        Dictionary containing JS and CSS resources.
        """
        cls = type(self)
        resources = {}
        for rt, res in self._resources.items():
            if not isinstance(res, dict):
                continue
            if rt == 'font':
                rt = 'css'
            res = {
                name: url if isurl(url) else f'{cls.__name__.lower()}/{url}'
                for name, url in res.items()
            }
            if rt in resources:
                resources[rt] = dict(resources[rt], **res)
            else:
                resources[rt] = res

        cdn = use_cdn() if cdn == 'auto' else cdn
        resource_types: ResourcesType = {
            'js': {},
            'js_modules': {},
            'css': {},
            'raw_css': []
        }

        for resource_type in resource_types:
            if resource_type not in resources or resource_type == 'raw_css':
                continue
            resource_files = resource_types[resource_type]
            for rname, resource in resources[resource_type].items():
                resolved_resource = self._resolve_resource(
                    resource_type, resource, cdn=cdn
                )
                if resolved_resource:
                    resource_files[rname] = resolved_resource
        return resource_types


class Resources(BkResources):

    def __init__(self, *args, absolute=False, notebook=False, **kwargs):
        self.absolute = absolute
        self.notebook = notebook
        super().__init__(*args, **kwargs)

    @classmethod
    def from_bokeh(cls, bkr, absolute=False, notebook=False):
        kwargs = {}
        if bkr.mode.startswith("server"):
            kwargs['root_url'] = bkr.root_url

        components = bkr.components if hasattr(bkr, 'components_for') else bkr._components
        return cls(
            mode=bkr.mode, version=bkr.version, minified=bkr.minified,
            log_level=bkr.log_level, notebook=notebook,
            path_versioner=bkr.path_versioner,
            components=components, base_dir=bkr.base_dir,
            root_dir=bkr.root_dir, absolute=absolute, **kwargs
        )

    def _collect_external_resources(self, resource_attr: ResourceAttr) -> list[str]:
        """ Collect external resources set on resource_attr attribute of all models."""
        external_resources: list[str] = []

        if state._extensions is not None:
            external_modules = {
                module: ext for ext, module in extension._imports.items()
            }
        else:
            external_modules = None

        for _, cls in sorted(Model.model_class_reverse_map.items(), key=lambda arg: arg[0]):
            if external_modules is not None and cls.__module__ in external_modules:
                if external_modules[cls.__module__] not in state._extensions:
                    continue
            external: list[str] | str | None = getattr(cls, resource_attr, None)

            if isinstance(external, str):
                if external not in external_resources:
                    external_resources.append(external)
            elif isinstance(external, list):
                for e in external:
                    if e not in external_resources:
                        external_resources.append(e)

        return external_resources

    def _server_urls(self) -> Urls:
        return _get_server_urls(
            self.root_url if self.absolute else '',
            False if self.dev else self.minified,
            self.path_versioner
        )

    def extra_resources(self, resources, resource_type):
        """
        Adds resources for ReactiveHTML components.
        """
        from ..reactive import ReactiveHTML
        for model in param.concrete_descendents(ReactiveHTML).values():
            if not (getattr(model, resource_type, None) and model._loaded()):
                continue
            for resource in getattr(model, resource_type, []):
                if not isurl(resource) and not resource.startswith('static/extensions'):
                    resource = component_resource_path(model, resource_type, resource)
                if resource not in resources:
                    resources.append(resource)

    def adjust_paths(self, resources):
        """
        Computes relative and absolute paths for resources.
        """
        new_resources = []
        cdn_base = f'{config.npm_cdn}/@holoviz/panel@{JS_VERSION}/dist/'
        for resource in resources:
            resource = resource.replace('https://unpkg.com', config.npm_cdn)
            if resource.startswith(cdn_base):
                resource = resource.replace(cdn_base, CDN_DIST)
            if self.mode == 'server':
                resource = resource.replace(CDN_DIST, LOCAL_DIST)
            if (resource.startswith(state.base_url) or resource.startswith('static/')):
                if resource.startswith(state.base_url):
                    resource = resource[len(state.base_url):]
                if state.rel_path:
                    resource = f'{state.rel_path}/{resource}'
                elif self.absolute and self.mode == 'server':
                    resource = f'{self.root_url}{resource}'
            new_resources.append(resource)
        return new_resources

    def clone(self, *, components=None) -> Resources:
        """
        Make a clone of a resources instance allowing to override its components.
        """
        return Resources(
            mode=self.mode,
            version=self.version,
            root_dir=self.root_dir,
            dev=self.dev,
            minified=self.minified,
            log_level=self.log_level,
            root_url=self._root_url,
            path_versioner=self.path_versioner,
            components=components if components is not None else list(self.components),
            base_dir=self.base_dir,
            notebook=self.notebook,
            absolute=self.absolute
        )

    @property
    def dist_dir(self):
        if self.notebook and self.mode == 'server':
            dist_dir = '/panel-preview/static/extensions/panel/'
        elif self.mode == 'server':
            if state.rel_path:
                dist_dir = f'{state.rel_path}/{LOCAL_DIST}'
            else:
                dist_dir = LOCAL_DIST
            if self.absolute:
                dist_dir = f'{self.root_url}{dist_dir}'
        else:
            dist_dir = CDN_DIST
        return dist_dir

    @property
    def css_files(self):
        from ..config import config

        files = super(Resources, self).css_files
        self.extra_resources(files, '__css__')
        css_files = self.adjust_paths([
            css for css in files if self.mode != 'inline' or not is_cdn_url(css)
        ])
        if config.design:
            css_files += list(config.design._resources.get('font', {}).values())
        for cssf in config.css_files:
            if os.path.isfile(cssf) or cssf in files:
                continue
            css_files.append(cssf)
        return css_files

    @property
    def css_raw(self):
        from ..config import config
        raw = super(Resources, self).css_raw

        # Inline local dist resources
        css_files = self._collect_external_resources("__css__")
        self.extra_resources(css_files, '__css__')
        raw += [
            (DIST_DIR / css.replace(CDN_DIST, '')).read_text(encoding='utf-8')
            for css in css_files if is_cdn_url(css)
        ]

        # Add local CSS files
        for cssf in config.css_files:
            if not os.path.isfile(cssf):
                continue
            css_txt = process_raw_css([Path(cssf).read_text(encoding='utf-8')])[0]
            if css_txt not in raw:
                raw.append(css_txt)

        # Add loading spinner
        if config.global_loading_spinner:
            loading_base = (DIST_DIR / "css" / "loading.css").read_text(encoding='utf-8')
            raw.extend([loading_base, loading_css(
                config.loading_spinner, config.loading_color, config.loading_max_height
            )])
        return raw + process_raw_css(config.raw_css) + process_raw_css(config.global_css)

    @property
    def js_files(self):
        from ..config import config

        # Gather JS files
        files = super(Resources, self).js_files
        self.extra_resources(files, '__javascript__')
        files += [js for js in config.js_files.values()]
        if config.design:
            design_js = config.design().resolve_resources(
                cdn=self.notebook or 'auto', include_theme=False
            )['js'].values()
            files += [res for res in design_js if res not in files]

        # Filter and adjust JS file urls
        js_files = self.adjust_paths([
            js for js in files if self.mode != 'inline' or not is_cdn_url(js)
        ])

        # Load requirejs last to avoid interfering with other libraries
        dist_dir = self.dist_dir
        require_index = [i for i, jsf in enumerate(js_files) if 'require' in jsf]
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
        self.extra_resources(modules, '__javascript_modules__')
        if config.design:
            design_resources = config.design().resolve_resources(
                cdn=self.notebook or 'auto', include_theme=False
            )
            modules += [
                res for res in design_resources['js_modules'].values()
                if res not in modules
            ]

        for model in param.concrete_descendents(ReactiveHTML).values():
            if not (getattr(model, '__javascript_modules__', None) and model._loaded()):
                continue
            for js_module in model.__javascript_modules__:
                if not isurl(js_module) and not js_module.startswith('static/extensions'):
                    js_module = component_resource_path(model, '__javascript_modules__', js_module)
                if js_module not in modules:
                    modules.append(js_module)

        return self.adjust_paths(modules)

    @property
    def js_module_exports(self):
        modules = {}
        for model in Model.model_class_reverse_map.values():
            if hasattr(model, '__javascript_module_exports__'):
                modules.update(dict(zip(model.__javascript_module_exports__, model.__javascript_modules__)))
        return modules

    @property
    def js_raw(self):
        raw_js = super(Resources, self).js_raw
        if not self.mode == 'inline':
            return raw_js

        # Inline local dist resources
        js_files = self._collect_external_resources("__javascript__")
        self.extra_resources(js_files, '__javascript__')
        raw_js += [
            (DIST_DIR / js.replace(CDN_DIST, '')).read_text(encoding='utf-8')
            for js in js_files if is_cdn_url(js)
        ]

        # Inline config.js_files
        from ..config import config
        raw_js += [
            Path(js).read_text(encoding='utf-8') for js in config.js_files.values()
            if os.path.isfile(js)
        ]

        # Inline config.design JS resources
        if config.design:
            design_js = config.design().resolve_resources(
                cdn=True, include_theme=False
            )['js'].values()
            raw_js += [
                (DIST_DIR / js.replace(CDN_DIST, '')).read_text(encoding='utf-8')
                for js in design_js if is_cdn_url(js)
            ]
        return raw_js

    @property
    def render_js(self):
        return JS_RESOURCES.render(
            js_raw=self.js_raw, js_files=self.js_files,
            js_modules=self.js_modules, hashes=self.hashes,
            js_module_exports=self.js_module_exports
        )


class Bundle(BkBundle):

    def __init__(self, notebook=False, **kwargs):
        self.js_modules = kwargs.pop("js_modules", [])
        self.js_module_exports = kwargs.pop("js_module_exports", {})
        self.notebook = notebook
        super().__init__(**kwargs)

    @classmethod
    def from_bokeh(cls, bk_bundle, notebook=False):
        return cls(
            notebook=notebook,
            js_files=bk_bundle.js_files,
            js_raw=bk_bundle.js_raw,
            css_files=bk_bundle.css_files,
            css_raw=bk_bundle.css_raw,
            hashes=bk_bundle.hashes,
        )

    def _render_css(self) -> str:
        return BkCSS_RESOURCES.render(
            css_files=self.css_files,
            css_raw=self.css_raw
        )

    def _render_js(self):
        return JS_RESOURCES.render(
            js_raw=self.js_raw,
            js_files=self.js_files,
            js_modules=self.js_modules,
            js_module_exports=self.js_module_exports,
            hashes=self.hashes
        )
