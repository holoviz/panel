"""
The config module supplies the global config object and the extension
which provides convenient support for  loading and configuring panel
components.
"""
from __future__ import absolute_import, division, unicode_literals

import ast
import inspect
import os
import sys

from contextlib import contextmanager

import param

from pyviz_comms import (JupyterCommManager as _JupyterCommManager,
                         extension as _pyviz_extension)

from .io.notebook import load_notebook
from .io.state import state

__version__ = str(param.version.Version(
    fpath=__file__, archive_commit="$Format:%h$", reponame="panel"))

_LOCAL_DEV_VERSION = any(v in __version__ for v in ('post', 'dirty'))

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

_PATH = os.path.abspath(os.path.dirname(__file__))


def validate_config(config, parameter, value):
    """
    Validates parameter setting on a hidden config parameter.
    """
    orig = getattr(config, parameter)
    try:
        setattr(config, parameter, value)
    except Exception as e:
        raise e
    finally:
        setattr(config, parameter, orig)


class _base_config(param.Parameterized):

    css_files = param.List(default=[], doc="""
        External CSS files to load.""")

    js_files = param.Dict(default={}, doc="""
        External JS files to load. Dictionary should map from exported
        name to the URL of the JS file.""")

    js_modules = param.Dict(default={}, doc="""
        External JS fils to load as modules. Dictionary should map from
        exported name to the URL of the JS file.""")

    raw_css = param.List(default=[], doc="""
        List of raw CSS strings to add to load.""")


class _config(_base_config):
    """
    Holds global configuration options for Panel. The options can be
    set directly on the global config instance, via keyword arguments
    in the extension or via environment variables. For example to set
    the embed option the following approaches can be used:

        pn.config.embed = True

        pn.extension(embed=True)

        os.environ['PANEL_EMBED'] = 'True'
    """

    apply_signatures = param.Boolean(default=True, doc="""
        Whether to set custom Signature which allows tab-completion
        in some IDEs and environments.""")

    autoreload = param.Boolean(default=False, doc="""
        Whether to autoreload server when script changes.""")

    safe_embed = param.Boolean(default=False, doc="""
        Ensure all bokeh property changes trigger events which are
        embedded. Useful when only partial updates are made in an
        app, e.g. when working with HoloViews.""")

    session_history = param.Integer(default=0, bounds=(-1, None), doc="""
        If set to a non-negative value this determines the maximum length
        of the pn.state.session_info dictionary, which tracks
        information about user sessions. A value of -1 indicates an
        unlimited history.""")

    sizing_mode = param.ObjectSelector(default=None, objects=[
        'fixed', 'stretch_width', 'stretch_height', 'stretch_both',
        'scale_width', 'scale_height', 'scale_both', None], doc="""
        Specify the default sizing mode behavior of panels.""")

    _comms = param.ObjectSelector(
        default='default', objects=['default', 'ipywidgets', 'vscode', 'colab'], doc="""
        Whether to render output in Jupyter with the default Jupyter
        extension or use the jupyter_bokeh ipywidget model.""")

    _console_output = param.ObjectSelector(default='accumulate', allow_None=True,
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
        default=None, objects=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        doc="Log level of Panel loggers")

    _oauth_provider = param.ObjectSelector(
        default=None, allow_None=True, objects=[], doc="""
        Select between a list of authentification providers.""")

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

    _inline = param.Boolean(default=_LOCAL_DEV_VERSION, allow_None=True, doc="""
        Whether to inline JS and CSS resources. If disabled, resources
        are loaded from CDN if one is available.""")

    _truthy = ['True', 'true', '1', True, 1]

    def __init__(self, **params):
        super().__init__(**params)
        for p in self.param:
            if p.startswith('_'):
                setattr(self, p+'_', None)

    @contextmanager
    def set(self, **kwargs):
        values = [(k, v) for k, v in self.param.get_param_values() if k != 'name']
        overrides = [(k, getattr(self, k+'_')) for k in self.param if k.startswith('_')]
        for k, v in kwargs.items():
            setattr(self, k, v)
        try:
            yield
        finally:
            self.param.set_param(**dict(values))
            for k, v in overrides:
                setattr(self, k+'_', v)

    @property
    def _doc_build(self):
        return os.environ.get('PANEL_DOC_BUILD')

    @property
    def console_output(self):
        if self._console_output_ is not None:
            return 'disable' if not self._console_output_ else self._console_output_
        elif self._doc_build:
            return 'disable'
        else:
            return os.environ.get('PANEL_CONSOLE_OUTPUT', _config._console_output)

    @console_output.setter
    def console_output(self, value):
        validate_config(self, '_console_output', value)
        self._console_output_ = value

    @property
    def embed(self):
        if self._embed_ is not None:
            return self._embed_
        else:
            return os.environ.get('PANEL_EMBED', _config._embed) in self._truthy

    @embed.setter
    def embed(self, value):
        validate_config(self, '_embed', value)
        self._embed_ = value

    @property
    def comms(self):
        if self._comms_ is not None:
            return self._comms_
        else:
            return os.environ.get('PANEL_COMMS', _config._comms)

    @comms.setter
    def comms(self, value):
        validate_config(self, '_comms', value)
        self._comms_ = value

    @property
    def embed_json(self):
        if self._embed_json_ is not None:
            return self._embed_json_
        else:
            return os.environ.get('PANEL_EMBED_JSON', _config._embed_json) in self._truthy

    @embed_json.setter
    def embed_json(self, value):
        validate_config(self, '_embed_json', value)
        self._embed_json_ = value

    @property
    def embed_json_prefix(self):
        if self._embed_json_prefix_ is not None:
            return self._embed_json_prefix_
        else:
            return os.environ.get('PANEL_EMBED_JSON_PREFIX', _config._embed_json_prefix)

    @embed_json_prefix.setter
    def embed_json_prefix(self, value):
        validate_config(self, '_embed_json_prefix', value)
        self._embed_json_prefix_ = value

    @property
    def embed_save_path(self):
        if self._embed_save_path_ is not None:
            return self._embed_save_path_
        else:
            return os.environ.get('PANEL_EMBED_SAVE_PATH', _config._embed_save_path)

    @embed_save_path.setter
    def embed_save_path(self, value):
        validate_config(self, '_embed_save_path', value)
        self._embed_save_path_ = value

    @property
    def embed_load_path(self):
        if self._embed_load_path_ is not None:
            return self._embed_load_path_
        else:
            return os.environ.get('PANEL_EMBED_LOAD_PATH', _config._embed_load_path)

    @embed_load_path.setter
    def embed_load_path(self, value):
        validate_config(self, '_embed_load_path', value)
        self._embed_load_path_ = value

    @property
    def inline(self):
        if self._inline_ is not None:
            return self._inline_
        else:
            return os.environ.get('PANEL_INLINE', _config._inline) in self._truthy

    @inline.setter
    def inline(self, value):
        validate_config(self, '_inline', value)
        self._inline_ = value

    @property
    def log_level(self):
        if self._log_level_ is not None:
            return self._log_level_
        elif 'PANEL_LOG_LEVEL' in os.environ:
            return os.environ['PANEL_LOG_LEVEL'].upper()
        else:
            return self._log_level

    @log_level.setter
    def log_level(self, value):
        validate_config(self, '_log_level', value)
        self._log_level_ = value

    @property
    def oauth_provider(self):
        if self._oauth_provider_ is not None:
            return self._oauth_provider_
        else:
            provider = os.environ.get('PANEL_OAUTH_PROVIDER', _config._oauth_provider)
            return provider.lower() if provider else None

    @oauth_provider.setter
    def oauth_provider(self, value):
        validate_config(self, '_oauth_provider', value.lower())
        self._oauth_provider_ = value.lower()

    @property
    def oauth_key(self):
        if self._oauth_key_ is not None:
            return self._oauth_key_
        else:
            return os.environ.get('PANEL_OAUTH_KEY', _config._oauth_key)

    @oauth_key.setter
    def oauth_key(self, value):
        validate_config(self, '_oauth_key', value)
        self._oauth_key_ = value

    @property
    def cookie_secret(self):
        if self._cookie_secret_ is not None:
            return self._cookie_secret_
        else:
            return os.environ.get(
                'PANEL_COOKIE_SECRET',
                os.environ.get('BOKEH_COOKIE_SECRET', _config._cookie_secret)
            )

    @cookie_secret.setter
    def cookie_secret(self, value):
        validate_config(self, '_cookie_secret', value)
        self._cookie_secret_ = value

    @property
    def oauth_secret(self):
        if self._oauth_secret_ is not None:
            return self._oauth_secret_
        else:
            return os.environ.get('PANEL_OAUTH_SECRET', _config._oauth_secret)

    @oauth_secret.setter
    def oauth_secret(self, value):
        validate_config(self, '_oauth_secret', value)
        self._oauth_secret_ = value

    @property
    def oauth_redirect_uri(self):
        if self._oauth_redirect_uri_ is not None:
            return self._oauth_redirect_uri_
        else:
            return os.environ.get('PANEL_OAUTH_REDIRECT_URI', _config._oauth_redirect_uri)

    @oauth_redirect_uri.setter
    def oauth_redirect_uri(self, value):
        validate_config(self, '_oauth_redirect_uri', value)
        self._oauth_redirect_uri_ = value

    @property
    def oauth_jwt_user(self):
        if self._oauth_jwt_user_ is not None:
            return self._oauth_jwt_user_
        else:
            return os.environ.get('PANEL_OAUTH_JWT_USER', _config._oauth_jwt_user)

    @oauth_jwt_user.setter
    def oauth_jwt_user(self, value):
        validate_config(self, '_oauth_jwt_user', value)
        self._oauth_jwt_user_ = value

    @property
    def oauth_encryption_key(self):
        if self._oauth_encryption_key_ is not None:
            return self._oauth_encryption_key_
        else:
            return os.environ.get('PANEL_OAUTH_ENCRYPTION', _config._oauth_encryption_key)

    @oauth_encryption_key.setter
    def oauth_encryption_key(self, value):
        validate_config(self, '_oauth_encryption_key', value)
        self._oauth_encryption_key_ = value

    @property
    def oauth_extra_params(self):
        if self._oauth_extra_params_ is not None:
            return self._oauth_extra_params_
        else:
            if 'PANEL_OAUTH_EXTRA_PARAMS' in os.environ:
                return ast.literal_eval(os.environ['PANEL_OAUTH_EXTRA_PARAMS'])
            else:
                return _config._oauth_extra_params

    @oauth_extra_params.setter
    def oauth_extra_params(self, value):
        validate_config(self, '_oauth_extra_params', value)
        self._oauth_extra_params_ = value

        

if hasattr(_config.param, 'objects'):
    _params = _config.param.objects()
else:
    _params = _config.param.params()

config = _config(**{k: None if p.allow_None else getattr(_config, k)
                    for k, p in _params.items() if k != 'name'})


class panel_extension(_pyviz_extension):
    """
    Initializes the pyviz notebook extension to allow plotting with
    bokeh and enable comms.
    """

    _loaded = False

    _imports = {
        'katex': 'panel.models.katex',
        'mathjax': 'panel.models.mathjax',
        'plotly': 'panel.models.plotly',
        'deckgl': 'panel.models.deckgl',
        'vega': 'panel.models.vega',
        'vtk': 'panel.models.vtk',
        'ace': 'panel.models.ace',
        'echarts': 'panel.models.echarts',
        'ipywidgets': 'ipywidgets_bokeh.widget'
    }

    # Check whether these are loaded before rendering
    _globals = {
        'deckgl': 'deck',
        'echarts': 'echarts',
        'katex': 'katex',
        'mathjax': 'MathJax',
        'plotly': 'Plotly',
        'vega': 'vega',
        'vtk': 'vtk'
    }

    _loaded_extensions = []

    def __call__(self, *args, **params):
        # Abort if IPython not found
        for arg in args:
            if arg not in self._imports:
                self.param.warning('%s extension not recognized and '
                                   'will be skipped.' % arg)
            else:
                __import__(self._imports[arg])

        for k, v in params.items():
            if k in ['raw_css', 'css_files']:
                if not isinstance(v, list):
                    raise ValueError('%s should be supplied as a list, '
                                     'not as a %s type.' %
                                     (k, type(v).__name__))
                getattr(config, k).extend(v)
            elif k == 'js_files':
                getattr(config, k).update(v)
            else:
                setattr(config, k, v)

        if config.apply_signatures and sys.version_info.major >= 3:
            self._apply_signatures()

        loaded = self._loaded

        # Short circuit pyvista extension load if VTK is already initialized
        if loaded and args == ('vtk',) and 'vtk' in self._loaded_extensions:
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            if len(calframe) >= 3 and 'pyvista' in calframe[2].filename:
                return

        if 'holoviews' in sys.modules:
            import holoviews as hv
            import holoviews.plotting.bokeh # noqa
            loaded = loaded or getattr(hv.extension, '_loaded', False)

            if hv.Store.current_backend in hv.Store.renderers:
                backend = hv.Store.current_backend
            else:
                backend = 'bokeh'
            if hasattr(hv.Store, 'set_current_backend'):
                hv.Store.set_current_backend(backend)
            else:
                hv.Store.current_backend = backend

        try:
            ip = params.pop('ip', None) or get_ipython() # noqa (get_ipython)
        except Exception:
            return

        newly_loaded = [arg for arg in args if arg not in panel_extension._loaded_extensions]
        if loaded and newly_loaded:
            self.param.warning(
                "A HoloViz extension was loaded previously. This means "
                "the extension is already initialized and the following "
                "Panel extensions could not be properly loaded: %s. "
                "If you are loading custom extensions with pn.extension(...) "
                "ensure that this is called before any other HoloViz "
                "extension such as hvPlot or HoloViews." % newly_loaded)
        else:
            panel_extension._loaded_extensions += newly_loaded

        if hasattr(ip, 'kernel') and not self._loaded and not config._doc_build:
            # TODO: JLab extension and pyviz_comms should be changed
            #       to allow multiple cleanup comms to be registered
            _JupyterCommManager.get_client_comm(self._process_comm_msg,
                                                "hv-extension-comm")
            state._comm_manager = _JupyterCommManager

        if 'ipywidgets' in sys.modules and config.embed:
            # In embedded mode the ipywidgets_bokeh model must be loaded
            __import__(self._imports['ipywidgets'])

        nb_load = False
        if 'holoviews' in sys.modules:
            if getattr(hv.extension, '_loaded', False):
                return
            with param.logging_level('ERROR'):
                hv.plotting.Renderer.load_nb(config.inline)
                if hasattr(hv.plotting.Renderer, '_render_with_panel'):
                    nb_load = True

        if not nb_load and hasattr(ip, 'kernel'):
            load_notebook(config.inline)
        panel_extension._loaded = True


    def _apply_signatures(self):
        from inspect import Parameter, Signature
        from .viewable import Viewable

        descendants = param.concrete_descendents(Viewable)
        for cls in reversed(list(descendants.values())):
            if cls.__doc__.startswith('params'):
                prefix = cls.__doc__.split('\n')[0]
                cls.__doc__ = cls.__doc__.replace(prefix, '')
            sig = inspect.signature(cls.__init__)
            sig_params = list(sig.parameters.values())
            if not sig_params or sig_params[-1] != Parameter('params', Parameter.VAR_KEYWORD):
                continue
            parameters = sig_params[:-1]

            processed_kws, keyword_groups = set(), []
            for cls in reversed(cls.mro()):
                keyword_group = []
                for (k, v) in sorted(cls.__dict__.items()):
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
            parameters.append(Parameter('kwargs', Parameter.VAR_KEYWORD))
            cls.__init__.__signature__ = Signature(
                parameters, return_annotation=sig.return_annotation
            )


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
