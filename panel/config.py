"""
The config module supplies the global config object and the extension
which provides convenient support for  loading and configuring panel
components.
"""
from __future__ import annotations

import ast
import copy
import importlib
import inspect
import os
import sys
import warnings

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, ClassVar
from weakref import WeakKeyDictionary

import param

from pyviz_comms import (
    JupyterCommManager as _JupyterCommManager, extension as _pyviz_extension,
)

from .__version import __version__
from .io.logging import panel_log_handler
from .io.state import state

if TYPE_CHECKING:
    from bokeh.document import Document

_LOCAL_DEV_VERSION = (
    any(v in __version__ for v in ('post', 'dirty'))
    and not state._is_pyodide
    and 'PANEL_DOC_BUILD' not in os.environ
)

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

_PATH = os.path.abspath(os.path.dirname(__file__))
_config_uninitialized = True

def validate_config(config, parameter, value):
    """
    Validates parameter setting on a hidden config parameter.
    """
    if config._validating:
        return
    config._validating = True
    orig = getattr(config, parameter)
    try:
        setattr(config, parameter, value)
    except Exception as e:
        raise e
    finally:
        setattr(config, parameter, orig)
        config._validating = False


class _base_config(param.Parameterized):

    css_files = param.List(default=[], doc="""
        External CSS files to load.""")

    js_files = param.Dict(default={}, doc="""
        External JS files to load. Dictionary should map from exported
        name to the URL of the JS file.""")

    js_modules = param.Dict(default={}, doc="""
        External JS files to load as modules. Dictionary should map from
        exported name to the URL of the JS file.""")

    raw_css = param.List(default=[], doc="""
        List of raw CSS strings to add to load.""")


class _config(_base_config):
    """
    Holds global configuration options for Panel.

    The options can be set directly on the global config instance, via
    keyword arguments in the extension or via environment variables.

    For example to set the embed option the following approaches can be used:

        pn.config.embed = True

        pn.extension(embed=True)

        os.environ['PANEL_EMBED'] = 'True'

    Reference: Currently none

    :Example:

    >>> pn.config.loading_spinner = 'bar'
    """

    admin_plugins = param.List(default=[], item_type=tuple, doc="""
        A list of tuples containing a title and a function that returns
        an additional panel to be rendered into the admin page.""")

    apply_signatures = param.Boolean(default=True, doc="""
        Whether to set custom Signature which allows tab-completion
        in some IDEs and environments.""")

    authorize_callback = param.Callable(default=None, doc="""
        Authorization callback that is invoked when authentication
        is enabled. The callback is given the user information returned
        by the configured Auth provider and should return True or False
        depending on whether the user is authorized to access the
        application. The callback may also contain a second parameter,
        which is the requested path the user is making. If the user
        is authenticated and has explicit access to the path, then
        the callback should return True otherwise it should return
        False.""")

    auth_template = param.Path(default=None, doc="""
        A jinja2 template rendered when the authorize_callback determines
        that a user in not authorized to access the application.""")

    autoreload = param.Boolean(default=False, doc="""
        Whether to autoreload server when script changes.""")

    basic_auth_template = param.Path(default=None, doc="""
        A jinja2 template to override the default Basic Authentication
        login page.""")

    browser_info = param.Boolean(default=True, doc="""
        Whether to request browser info from the frontend.""")

    defer_load = param.Boolean(default=False, doc="""
        Whether to defer load of rendered functions.""")

    design = param.ClassSelector(class_=None, is_instance=False, doc="""
        The design system to use to style components.""")

    disconnect_notification = param.String(doc="""
        The notification to display to the user when the connection
        to the server is dropped.""")

    exception_handler = param.Callable(default=None, doc="""
        General exception handler for events.""")

    global_css = param.List(default=[], doc="""
        List of raw CSS to be added to the header.""")

    global_loading_spinner = param.Boolean(default=False, doc="""
        Whether to add a global loading spinner for the whole application.""")

    layout_compatibility = param.Selector(default='warn', objects=['warn', 'error'], doc="""
        Provide compatibility for older layout specifications. Incompatible
        specifications will trigger warnings by default but can be set to error.
        Compatibility to be set to error by default in Panel 1.1.""")

    load_entry_points = param.Boolean(default=True, doc="""
        Load entry points from external packages.""")

    loading_indicator = param.Boolean(default=False, doc="""
        Whether a loading indicator is shown by default while panes are updating.""")

    loading_spinner = param.Selector(default='arc', objects=[
        'arc', 'arcs', 'bar', 'dots', 'petal'], doc="""
        Loading indicator to use when component loading parameter is set.""")

    loading_color = param.Color(default='#c3c3c3', doc="""
        Color of the loading indicator.""")

    loading_max_height = param.Integer(default=400, doc="""
        Maximum height of the loading indicator.""")

    notifications = param.Boolean(default=False, doc="""
        Whether to enable notifications functionality.""")

    profiler = param.Selector(default=None, allow_None=True, objects=[
        'pyinstrument', 'snakeviz', 'memray'], doc="""
        The profiler engine to enable.""")

    ready_notification = param.String(doc="""
        The notification to display when the application is ready and
        fully loaded.""")

    reuse_sessions = param.Boolean(default=False, doc="""
        Whether to reuse a session for the initial request to speed up
        the initial page render. Note that if the initial page differs
        between sessions, e.g. because it uses query parameters to modify
        the rendered content, then this option will result in the wrong
        content being rendered. Define a session_key_func to ensure that
        reused sessions are only reused when appropriate.""")

    session_key_func = param.Callable(default=None, doc="""
        Used in conjunction with the reuse_sessions option, the
        session_key_func is given a tornado.httputil.HTTPServerRequest
        and should return a key that uniquely captures a session.""")

    safe_embed = param.Boolean(default=False, doc="""
        Ensure all bokeh property changes trigger events which are
        embedded. Useful when only partial updates are made in an
        app, e.g. when working with HoloViews.""")

    session_history = param.Integer(default=0, bounds=(-1, None), doc="""
        If set to a non-negative value this determines the maximum length
        of the pn.state.session_info dictionary, which tracks
        information about user sessions. A value of -1 indicates an
        unlimited history.""")

    sizing_mode = param.Selector(default=None, objects=[
        'fixed', 'stretch_width', 'stretch_height', 'stretch_both',
        'scale_width', 'scale_height', 'scale_both', None], doc="""
        Specify the default sizing mode behavior of panels.""")

    template = param.Selector(default=None, doc="""
        The default template to render served applications into.""")

    throttled = param.Boolean(default=False, doc="""
        If sliders and inputs should be throttled until release of mouse.""")

    _admin = param.Boolean(default=False, doc="Whether the admin panel is enabled.")

    _admin_endpoint = param.String(default=None, doc="Name to use for the admin endpoint.")

    _admin_log_level = param.Selector(
        default='DEBUG', objects=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        doc="Log level of the Admin Panel logger")

    _comms = param.Selector(
        default='default', objects=['default', 'ipywidgets', 'vscode', 'colab'], doc="""
        Whether to render output in Jupyter with the default Jupyter
        extension or use the jupyter_bokeh ipywidget model.""")

    _console_output = param.Selector(default='accumulate', allow_None=True,
                                 objects=['accumulate', 'replace', 'disable',
                                          False], doc="""
        How to log errors and stdout output triggered by callbacks
        from Javascript in the notebook.""")

    _cookie_secret = param.String(default=None, doc="""
        Configure to enable getting/setting secure cookies.""")

    _embed = param.Boolean(default=False, allow_None=True, doc="""
        Whether plot data will be embedded.""")

    _embed_json = param.Boolean(default=False, doc="""
        Whether to save embedded state to json files.""")

    _embed_json_prefix = param.String(default='', doc="""
        Prefix for randomly generated json directories.""")

    _embed_load_path = param.String(default=None, doc="""
        Where to load json files for embedded state.""")

    _embed_save_path = param.String(default='./', doc="""
        Where to save json files for embedded state.""")

    _log_level = param.Selector(
        default='WARNING', objects=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        doc="Log level of Panel loggers")

    _npm_cdn = param.Selector(default='https://cdn.jsdelivr.net/npm',
        objects=['https://unpkg.com', 'https://cdn.jsdelivr.net/npm'],  doc="""
        The CDN to load NPM packages from if resources are served from
        CDN. Allows switching between [https://unpkg.com](https://unpkg.com) and
        [https://cdn.jsdelivr.net/npm](https://cdn.jsdelivr.net/npm) for most resources.""")

    _nthreads = param.Integer(default=None, doc="""
        When set to a non-None value a thread pool will be started.
        Whenever an event arrives from the frontend it will be
        dispatched to the thread pool to be processed.""")

    _basic_auth = param.ClassSelector(default=None, class_=(dict, str), allow_None=True, doc="""
        Password, dictionary with a mapping from username to password
        or filepath containing JSON to use with the basic auth
        provider.""")

    _oauth_provider = param.Selector(
        default=None, allow_None=True, objects=[], doc="""
        Select between a list of authentication providers.""")

    _oauth_expiry = param.Number(default=1, bounds=(0, None), doc="""
        Expiry of the OAuth cookie in number of days.""")

    _oauth_key = param.String(default=None, doc="""
        A client key to provide to the OAuth provider.""")

    _oauth_secret = param.String(default=None, doc="""
        A client secret to provide to the OAuth provider.""")

    _oauth_jwt_user = param.String(default=None, doc="""
        The key in the ID JWT token to consider the user.""")

    _oauth_redirect_uri = param.String(default=None, doc="""
        A redirect URI to provide to the OAuth provider.""")

    _oauth_encryption_key = param.ClassSelector(default=None, class_=bytes, doc="""
        A random string used to encode OAuth related user information.""")

    _oauth_extra_params = param.Dict(default={}, doc="""
        Additional parameters required for OAuth provider.""")

    _oauth_guest_endpoints = param.List(default=None, doc="""
        List of endpoints that can be accessed as a guest without authenticating.""")

    _oauth_optional = param.Boolean(default=False, doc="""
        Whether the user will be forced to go through login flow or if
        they can access all applications as a guest.""")

    _oauth_refresh_tokens = param.Boolean(default=False, doc="""
        Whether to automatically refresh access tokens in the background.""")

    _inline = param.Boolean(default=_LOCAL_DEV_VERSION, allow_None=True, doc="""
        Whether to inline JS and CSS resources. If disabled, resources
        are loaded from CDN if one is available.""")

    _theme = param.Selector(default=None, objects=['default', 'dark'], allow_None=True, doc="""
        The theme to apply to components.""")

    # Global parameters that are shared across all sessions
    _globals: ClassVar[set[str]] = {
        'admin_plugins', 'autoreload', 'comms', 'cookie_secret',
        'nthreads', 'oauth_provider', 'oauth_expiry', 'oauth_key',
        'oauth_secret', 'oauth_jwt_user', 'oauth_redirect_uri',
        'oauth_encryption_key', 'oauth_extra_params', 'npm_cdn',
        'layout_compatibility', 'oauth_refresh_tokens', 'oauth_guest_endpoints',
        'oauth_optional', 'admin'
    }

    _truthy = ['True', 'true', '1', True, 1]

    _session_config: ClassVar[WeakKeyDictionary[Document, dict[str, Any]]] = WeakKeyDictionary()

    def __init__(self, **params):
        super().__init__(**params)
        self._validating = False
        for p in self._parameter_set:
            if p.startswith('_') and p[1:] not in _config._globals:
                setattr(self, p+'_', None)
        if self.log_level:
            panel_log_handler.setLevel(self.log_level)

    @param.depends('_nthreads', watch=True, on_init=True)
    def _set_thread_pool(self):
        if self.nthreads is None:
            if state._thread_pool is not None:
                state._thread_pool.shutdown(wait=False)
            state._thread_pool = None
            return
        if state._thread_pool:
            raise RuntimeError("Thread pool already running")
        threads = self.nthreads if self.nthreads else None
        state._thread_pool = ThreadPoolExecutor(max_workers=threads)

    @param.depends('notifications', watch=True)
    def _setup_notifications(self):
        from .io.notifications import NotificationArea
        from .reactive import ReactiveHTMLMetaclass
        if self.notifications and 'notifications' not in ReactiveHTMLMetaclass._loaded_extensions:
            ReactiveHTMLMetaclass._loaded_extensions.add('notifications')
        if not state.curdoc:
            state._notification = NotificationArea()

    @param.depends('disconnect_notification', 'ready_notification', watch=True)
    def _enable_notifications(self):
        if self.disconnect_notification or self.ready_notification:
            self.notifications = True

    @contextmanager
    def set(self, **kwargs):
        values = [(k, v) for k, v in self.param.values().items() if k != 'name']
        overrides = [
            (k, getattr(self, k+'_')) for k in _config._parameter_set
            if k.startswith('_') and k[1:] not in _config._globals
        ]
        for k, v in kwargs.items():
            setattr(self, k, v)
        try:
            yield
        finally:
            new = self.param.values()
            restore = {k: v for k, v in values if v is not new.get(k)}
            self.param.update(**restore)
            for k, v in overrides:
                setattr(self, k+'_', v)

    def __setattr__(self, attr, value):
        from .io.state import state

        # _param__private added in Param 2
        if hasattr(self, '_param__private'):
            init = getattr(self._param__private, 'initialized', False)
        else:
            init = getattr(self, 'initialized', False)
        if not init or (attr.startswith('_') and attr.endswith('_')) or attr == '_validating':
            return super().__setattr__(attr, value)
        value = getattr(self, f'_{attr}_hook', lambda x: x)(value)
        if (
            attr in _config._globals
            or (attr.startswith("_") and attr[1:] in _config._globals)
            or self.param._TRIGGER
        ):
            super().__setattr__(attr if attr in self.param else f'_{attr}', value)
        elif state.curdoc is not None:
            if attr in _config._parameter_set:
                validate_config(self, attr, value)
            elif f'_{attr}' in _config._parameter_set:
                validate_config(self, f'_{attr}', value)
            else:
                raise AttributeError(f'{attr!r} is not a valid config parameter.')
            if state.curdoc not in self._session_config:
                self._session_config[state.curdoc] = {}
            self._session_config[state.curdoc][attr] = value
            watchers = self.param.watchers.get(attr, {}).get('value', [])
            for w in watchers:
                w.fn()
        elif f'_{attr}' in _config._parameter_set and hasattr(self, f'_{attr}_'):
            validate_config(self, f'_{attr}', value)
            super().__setattr__(f'_{attr}_', value)
        else:
            super().__setattr__(attr, value)

    @param.depends('_log_level', watch=True)
    def _update_log_level(self):
        panel_log_handler.setLevel(self._log_level)

    @param.depends('_admin_log_level', watch=True)
    def _update_admin_log_level(self):
        from .io.admin import log_handler as admin_log_handler
        admin_log_handler.setLevel(self._log_level)

    def __getattribute__(self, attr):
        """
        Ensures that configuration parameters that are defined per
        session are stored in a per-session dictionary. This is to
        ensure that even on first access mutable parameters do not
        end up being modified.
        """
        if _config_uninitialized or attr in ('_param__private', '_globals', '_parameter_set', '__class__', 'param'):
            return super().__getattribute__(attr)

        from .io.state import state

        session_config = super().__getattribute__('_session_config')
        curdoc = state.curdoc
        if curdoc and curdoc not in session_config:
            session_config[curdoc] = {}
        if (attr in ('raw_css', 'global_css', 'css_files', 'js_files', 'js_modules') and
            curdoc and attr not in session_config[curdoc]):
            new_obj = copy.copy(super().__getattribute__(attr))
            setattr(self, attr, new_obj)
        if attr in _config._globals or attr == 'theme':
            return super().__getattribute__(attr)
        elif curdoc and curdoc in session_config and attr in session_config[curdoc]:
            return session_config[curdoc][attr]
        elif f'_{attr}' in _config._parameter_set and getattr(self, f'_{attr}_') is not None:
            return super().__getattribute__(f'_{attr}_')
        return super().__getattribute__(attr)

    def _console_output_hook(self, value):
        return value if value else 'disable'

    def _template_hook(self, value):
        if isinstance(value, str):
            return self.param.template.names[value]
        return value

    @property
    def _doc_build(self):
        return os.environ.get('PANEL_DOC_BUILD')

    @property
    def admin(self):
        return self._admin

    @property
    def admin_endpoint(self):
        return os.environ.get('PANEL_ADMIN_ENDPOINT', self._admin_endpoint)

    @property
    def admin_log_level(self):
        admin_log_level = os.environ.get('PANEL_ADMIN_LOG_LEVEL', self._admin_log_level)
        return admin_log_level.upper() if admin_log_level else None

    @property
    def console_output(self):
        if self._doc_build:
            return 'disable'
        else:
            return os.environ.get('PANEL_CONSOLE_OUTPUT', _config._console_output)

    @property
    def embed(self):
        return os.environ.get('PANEL_EMBED', _config._embed) in self._truthy

    @property
    def comms(self):
        return os.environ.get('PANEL_COMMS', self._comms)

    @property
    def embed_json(self):
        return os.environ.get('PANEL_EMBED_JSON', _config._embed_json) in self._truthy

    @property
    def embed_json_prefix(self):
        return os.environ.get('PANEL_EMBED_JSON_PREFIX', _config._embed_json_prefix)

    @property
    def embed_save_path(self):
        return os.environ.get('PANEL_EMBED_SAVE_PATH', _config._embed_save_path)

    @property
    def embed_load_path(self):
        return os.environ.get('PANEL_EMBED_LOAD_PATH', _config._embed_load_path)

    @property
    def inline(self):
        return os.environ.get('PANEL_INLINE', _config._inline) in self._truthy

    @property
    def log_level(self):
        log_level = os.environ.get('PANEL_LOG_LEVEL', self._log_level)
        return log_level.upper() if log_level else None

    @property
    def npm_cdn(self):
        return os.environ.get('PANEL_NPM_CDN', _config._npm_cdn)

    @property
    def nthreads(self):
        nthreads = os.environ.get('PANEL_NUM_THREADS', self._nthreads)
        return None if nthreads is None else int(nthreads)

    @property
    def basic_auth(self):
        provider = os.environ.get('PANEL_BASIC_AUTH', self._oauth_provider)
        return provider.lower() if provider else None

    @property
    def oauth_provider(self):
        provider = os.environ.get('PANEL_OAUTH_PROVIDER', self._oauth_provider)
        return provider.lower() if provider else None

    @property
    def oauth_expiry(self):
        provider = os.environ.get('PANEL_OAUTH_EXPIRY', self._oauth_expiry)
        return float(provider)

    @property
    def oauth_key(self):
        return os.environ.get('PANEL_OAUTH_KEY', self._oauth_key)

    @property
    def cookie_secret(self):
        return os.environ.get(
            'PANEL_COOKIE_SECRET',
            os.environ.get('BOKEH_COOKIE_SECRET', self._cookie_secret)
        )

    @property
    def oauth_secret(self):
        return os.environ.get('PANEL_OAUTH_SECRET', self._oauth_secret)

    @property
    def oauth_redirect_uri(self):
        return os.environ.get('PANEL_OAUTH_REDIRECT_URI', self._oauth_redirect_uri)

    @property
    def oauth_jwt_user(self):
        return os.environ.get('PANEL_OAUTH_JWT_USER', self._oauth_jwt_user)

    @property
    def oauth_refresh_tokens(self):
        refresh = os.environ.get('PANEL_OAUTH_REFRESH_TOKENS', self._oauth_refresh_tokens)
        if isinstance(refresh, bool):
            return refresh
        return refresh.lower() in ('1', 'true')

    @property
    def oauth_encryption_key(self):
        return os.environ.get('PANEL_OAUTH_ENCRYPTION', self._oauth_encryption_key)

    @property
    def oauth_extra_params(self):
        if 'PANEL_OAUTH_EXTRA_PARAMS' in os.environ:
            return ast.literal_eval(os.environ['PANEL_OAUTH_EXTRA_PARAMS'])
        else:
            return self._oauth_extra_params

    @property
    def oauth_guest_endpoints(self):
        if 'PANEL_OAUTH_GUEST_ENDPOINTS' in os.environ:
            return ast.literal_eval(os.environ['PANEL_OAUTH_GUEST_ENDPOINTS'])
        else:
            return self._oauth_guest_endpoints

    @property
    def oauth_optional(self):
        optional = os.environ.get('PANEL_OAUTH_OPTIONAL', self._oauth_optional)
        if isinstance(optional, bool):
            return optional
        return optional.lower() in ('1', 'true')

    @property
    def theme(self):
        curdoc = state.curdoc
        if curdoc and 'theme' in self._session_config.get(curdoc, {}):
            return self._session_config[curdoc]['theme']
        elif self._theme_:
            return self._theme_
        elif isinstance(state.session_args, dict) and state.session_args:
            theme = state.session_args.get('theme', [b'default'])[0].decode('utf-8')
            if theme in self.param._theme.objects:
                return theme
        return 'default'


if hasattr(_config.param, 'objects'):
    _params = _config.param.objects()
else:
    _params = _config.param.params()
_config._parameter_set = set(_params)
config = _config(**{k: None if p.allow_None else getattr(_config, k)
                    for k, p in _params.items() if k != 'name'})
_config_uninitialized = False

class panel_extension(_pyviz_extension):
    """
    Initializes and configures Panel. You should always run `pn.extension`.
    This will

    - Initialize the `pyviz` notebook extension to enable bi-directional
    communication and for example plotting with Bokeh.
    - Load `.js` libraries (positional arguments).
    - Update the global configuration `pn.config`
    (keyword arguments).

    Parameters
    ----------
    *args : list[str]
        Positional arguments listing the extension to load. For example "plotly",
        "tabulator".
    **params : dict[str,Any]
        Keyword arguments to be set on the `pn.config` element. See
        https://panel.holoviz.org/api/config.html

    :Example:

    >>> import panel as pn
    >>> pn.extension("plotly", sizing_mode="stretch_width", template="fast")

    This will

    - Initialize the `pyviz` notebook extension.
    - Enable you to use the `Plotly` pane by loading `plotly.js`.
    - Set the default `sizing_mode` to `stretch_width` instead of `fixed`.
    - Set the global configuration `pn.config.template` to `fast`, i.e. you
    will be using the `FastListTemplate`.
    """

    _loaded: bool = False

    _imports: ClassVar[dict[str, str]] = {
        'ace': 'panel.models.ace',
        'codeeditor': 'panel.models.ace',
        'deckgl': 'panel.models.deckgl',
        'echarts': 'panel.models.echarts',
        'filedropper': 'panel.models.file_dropper',
        'ipywidgets': 'panel.io.ipywidget',
        'jsoneditor': 'panel.models.jsoneditor',
        'katex': 'panel.models.katex',
        'mathjax': 'panel.models.mathjax',
        'modal': 'panel.models.modal',
        'perspective': 'panel.models.perspective',
        'plotly': 'panel.models.plotly',
        'tabulator': 'panel.models.tabulator',
        'terminal': 'panel.models.terminal',
        'texteditor': 'panel.models.quill',
        'vizzu': 'panel.models.vizzu',
        'vega': 'panel.models.vega',
        'vtk': 'panel.models.vtk'
    }

    # Check whether these are loaded before rendering (if any item
    # in the list is available the extension will be confidered as
    # loaded)
    _globals: ClassVar[dict[str, list[str]]] = {
        'deckgl': ['deck'],
        'echarts': ['echarts'],
        'filedropper': ['FilePond'],
        'floatpanel': ['jsPanel'],
        'gridstack': ['GridStack'],
        'katex': ['katex'],
        'mathjax': ['MathJax'],
        'modal': ['A11yDialog'],
        'perspective': ["customElements.get('perspective-viewer')"],
        'plotly': ['Plotly'],
        'tabulator': ['Tabulator'],
        'terminal': ['Terminal', 'xtermjs'],
        'vega': ['vega'],
        'vizzu': ['Vizzu'],
        'vtk': ['vtk']
    }

    _loaded_extensions: list[str] = []

    _comms_detected_before: bool = False

    def __call__(self, *args, **params):
        from bokeh.core.has_props import _default_resolver
        from bokeh.model import Model
        from bokeh.settings import settings as bk_settings

        from .reactive import ReactiveHTML, ReactiveHTMLMetaclass
        reactive_exts = {
            v._extension_name: v for k, v in param.concrete_descendents(ReactiveHTML).items()
        }
        newly_loaded = [arg for arg in args if arg not in panel_extension._loaded_extensions]
        if state.curdoc and state.curdoc not in state._extensions_:
            state._extensions_[state.curdoc] = []
        if params.get('ready_notification') or params.get('disconnect_notification'):
            params['notifications'] = True
        if params.get('notifications', config.notifications) and 'notifications' not in args:
            args += ('notifications',)
        for arg in args:
            if arg == 'notifications' and 'notifications' not in params:
                params['notifications'] = True
            if arg == 'ipywidgets':
                from .io.resources import CSS_URLS
                params['css_files'] = params.get('css_files', []) + [CSS_URLS['font-awesome']]
            if arg in self._imports:
                try:
                    if (arg == 'ipywidgets' and get_ipython() and # noqa (get_ipython)
                        "PANEL_IPYWIDGET" not in os.environ):
                        continue
                except Exception:
                    pass

                # Ensure all models are registered
                module = self._imports[arg]
                if module in sys.modules:
                    for model in sys.modules[module].__dict__.values():
                        if isinstance(model, type) and issubclass(model, Model):
                            qual = getattr(model, '__qualified_model__', None)
                            if qual and qual not in _default_resolver.known_models:
                                _default_resolver.add(model)
                else:
                    __import__(module)
                self._loaded_extensions.append(arg)

                if state.curdoc:
                    state._extensions_[state.curdoc].append(arg)

            elif arg in reactive_exts:
                if state.curdoc:
                    state._extensions.append(arg)
                ReactiveHTMLMetaclass._loaded_extensions.add(arg)
            else:
                self.param.warning(f'{arg} extension not recognized and '
                                   'will be skipped.')

        for k, v in params.items():
            if k == 'design' and isinstance(v, str):
                from .theme import Design
                try:
                    importlib.import_module(f'panel.theme.{self._design}')
                except Exception:
                    pass
                designs = {
                    p.lower(): t for p, t in param.concrete_descendents(Design).items()
                }
                if v not in designs:
                    raise ValueError(
                        f'Design {v!r} was not recognized, available design '
                        f'systems include: {list(designs)}.'
                    )
                setattr(config, k, designs[v])
            elif k in ('css_files', 'raw_css', 'global_css'):
                if not isinstance(v, list):
                    raise ValueError(f'{k} should be supplied as a list, '
                                     f'not as a {type(v).__name__} type.')
                existing = getattr(config, k)
                existing.extend([new for new in v if new not in existing])
            elif k == 'js_files':
                getattr(config, k).update(v)
            else:
                setattr(config, k, v)

        if config.apply_signatures:
            self._apply_signatures()

        loaded = self._loaded
        panel_extension._loaded = True

        # Short circuit pyvista extension load if VTK is already initialized
        if loaded and args == ('vtk',) and 'vtk' in self._loaded_extensions:
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            if len(calframe) >= 3 and 'pyvista' in calframe[2].filename:
                return

        if 'holoviews' in sys.modules:
            import holoviews as hv
            import holoviews.plotting.bokeh  # noqa
            loaded = loaded or getattr(hv.extension, '_loaded', False)

            if hv.Store.current_backend in hv.Store.renderers:
                backend = hv.Store.current_backend
            else:
                backend = 'bokeh'
            if not loaded or (loaded and backend != hv.Store.current_backend) and hasattr(hv.Store, 'set_current_backend'):
                hv.Store.set_current_backend(backend)
            else:
                hv.Store.current_backend = backend

        if not loaded and config.load_entry_points:
            self._load_entry_points()

        # Abort if IPython not found
        try:
            ip = params.pop('ip', None) or get_ipython() # noqa (get_ipython)
        except Exception:
            return

        from .io.notebook import load_notebook

        self._detect_comms(params)

        panel_extension._loaded_extensions += newly_loaded

        if hasattr(ip, 'kernel') and not loaded and not config._doc_build:
            # TODO: JLab extension and pyviz_comms should be changed
            #       to allow multiple cleanup comms to be registered
            _JupyterCommManager.get_client_comm(self._process_comm_msg,
                                                "hv-extension-comm")
            state._comm_manager = _JupyterCommManager

        if 'ipywidgets' in sys.modules and config.embed:
            # In embedded mode the ipywidgets_bokeh model must be loaded
            __import__(self._imports['ipywidgets'])

        nb_loaded = published = getattr(self, '_repeat_execution_in_cell', False)
        if 'holoviews' in sys.modules:
            if getattr(hv.extension, '_loaded', False):
                nb_loaded = True
            else:
                with param.logging_level('ERROR'):
                    hv.plotting.Renderer.load_nb(config.inline)
                    nb_loaded = True

        # Disable simple ids, old state and multiple tabs in notebooks can cause IDs to clash
        bk_settings.simple_ids.set_value(False)

        if hasattr(ip, 'kernel'):
            load_notebook(
                config.inline, reloading=nb_loaded
            )

        if not published:
            self._display_globals()

    @staticmethod
    def _display_globals():
        if config.browser_info and state.browser_info:
            from bokeh.document import Document
            doc = Document()
            comm = state._comm_manager.get_server_comm()
            model = state.browser_info._render_model(doc, comm)
            bundle, meta = state.browser_info._render_mimebundle(model, doc, comm)
            display(bundle, metadata=meta, raw=True)  # noqa
        if config.notifications:
            display(state.notifications)  # noqa

    def _detect_comms(self, params):
        called_before = self._comms_detected_before
        self._comms_detected_before = True

        if 'comms' in params:
            config.comms = params.pop("comms")
            return

        if called_before:
            return

        # Try to detect environment so that we can enable comms
        if "google.colab" in sys.modules:
            try:
                import jupyter_bokeh  # noqa
                config.comms = "colab"
            except Exception:
                warnings.warn(
                    'Using Panel interactively in Colab notebooks requires '
                    'the jupyter_bokeh package to be installed. '
                    'Install it with:\n\n    !pip install jupyter_bokeh'
                    '\n\nand try again.', stacklevel=5
                )
            return

        if "VSCODE_CWD" in os.environ or "VSCODE_PID" in os.environ:
            try:
                import jupyter_bokeh  # noqa
                config.comms = "vscode"
            except Exception:
                warnings.warn(
                    'Using Panel interactively in VSCode notebooks requires '
                    'the jupyter_bokeh package to be installed. '
                    'You can install it with:\n\n   pip install jupyter_bokeh'
                    '\n\nor:\n    conda install jupyter_bokeh\n\nand try again.',
                    stacklevel=5
                )
            self._ignore_bokeh_warnings()
            return

    def _apply_signatures(self):
        from inspect import Parameter, Signature

        from .viewable import Viewable

        descendants = param.concrete_descendents(Viewable)
        for cls in reversed(list(descendants.values())):
            if cls.__doc__ is None:
                pass
            elif cls.__doc__.startswith('params'):
                prefix = cls.__doc__.split('\n')[0]
                cls.__doc__ = cls.__doc__.replace(prefix, '')
            sig = inspect.signature(cls.__init__)
            sig_params = list(sig.parameters.values())
            if not sig_params or sig_params[-1] != Parameter('params', Parameter.VAR_KEYWORD):
                continue
            parameters = sig_params[:-1]

            processed_kws, keyword_groups = set(), []
            for scls in reversed(cls.mro()):
                keyword_group = []
                for (k, v) in sorted(scls.__dict__.items()):
                    if (isinstance(v, param.Parameter) and k not in processed_kws
                        and not v.readonly):
                        keyword_group.append(k)
                        processed_kws.add(k)
                keyword_groups.append(keyword_group)

            parameters += [
                Parameter(name, Parameter.KEYWORD_ONLY)
                for kws in reversed(keyword_groups) for name in kws
                if name not in sig.parameters
            ]
            kwarg_name = '_kwargs' if 'kwargs' in processed_kws else 'kwargs'
            parameters.append(Parameter(kwarg_name, Parameter.VAR_KEYWORD))
            cls.__init__.__signature__ = Signature(
                parameters, return_annotation=sig.return_annotation
            )

    def _load_entry_points(self):
        """
        Load entry points from external packages.
        Import is performed here, so any importlib
        can be easily bypassed by switching off the configuration flag.
        Also, there is no reason to waste time importing this module
        if it won't be used.
        """
        from .entry_points import load_entry_points
        load_entry_points('panel.extension')

    def _ignore_bokeh_warnings(self):
        from bokeh.util.warnings import BokehUserWarning
        warnings.filterwarnings("ignore", category=BokehUserWarning, message="reference already known")


#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

def _cleanup_panel(msg_id):
    """
    A cleanup action which is called when a plot is deleted in the notebook
    """
    if msg_id not in state._views:
        return
    viewable, model, _, _ = state._views.pop(msg_id)
    viewable._cleanup(model)


def _cleanup_server(server_id):
    """
    A cleanup action which is called when a server is deleted in the notebook
    """
    if server_id not in state._servers:
        return
    server, viewable, docs = state._servers.pop(server_id)
    server.stop()
    for doc in docs:
        for root in doc.roots:
            if root.ref['id'] in viewable._models:
                viewable._cleanup(root)


panel_extension.add_delete_action(_cleanup_panel)
if hasattr(panel_extension, 'add_server_delete_action'):
    panel_extension.add_server_delete_action(_cleanup_server)

__all__ = ['config', 'panel_extension']
