"""
The config module supplies the global config object and the extension
which provides convenient support for  loading and configuring panel
components.
"""
from __future__ import absolute_import, division, unicode_literals

import glob
import inspect
import os
import sys

from contextlib import contextmanager

import param

from pyviz_comms import (JupyterCommManager as _JupyterCommManager,
                         extension as _pyviz_extension)

from .io.notebook import load_notebook
from .io.state import state


#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

_PATH = os.path.abspath(os.path.dirname(__file__))
_CSS_FILES = glob.glob(os.path.join(_PATH, '_styles', '*.css'))

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


class _config(param.Parameterized):
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

    css_files = param.List(default=_CSS_FILES, doc="""
        External CSS files to load.""")

    js_files = param.Dict(default={}, doc="""
        External JS files to load. Dictionary should map from exported
        name to the URL of the JS file.""")

    raw_css = param.List(default=[], doc="""
        List of raw CSS strings to add to load.""")

    safe_embed = param.Boolean(default=False, doc="""
        Ensure all bokeh property changes trigger events which are
        embedded. Useful when only partial updates are made in an
        app, e.g. when working with HoloViews.""")

    sizing_mode = param.ObjectSelector(default=None, objects=[
        'fixed', 'stretch_width', 'stretch_height', 'stretch_both',
        'scale_width', 'scale_height', 'scale_both', None], doc="""
        Specify the default sizing mode behavior of panels.""")

    _comms = param.ObjectSelector(
        default='default', objects=['default', 'ipywidgets'], doc="""
        Whether to render output in Jupyter with the default Jupyter
        extension or use the jupyter_bokeh ipywidget model.""")

    _console_output = param.ObjectSelector(default='accumulate', allow_None=True,
                                 objects=['accumulate', 'replace', 'disable',
                                          False], doc="""
        How to log errors and stdout output triggered by callbacks
        from Javascript in the notebook.""")

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

    _inline = param.Boolean(default=True, allow_None=True, doc="""
        Whether to inline JS and CSS resources. If disabled, resources
        are loaded from CDN if one is available.""")

    _truthy = ['True', 'true', '1', True, 1]

    def __init__(self, **params):
        super(_config, self).__init__(**params)
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

    _imports = {'katex': 'panel.models.katex',
                'mathjax': 'panel.models.mathjax',
                'plotly': 'panel.models.plotly',
                'deckgl': 'panel.models.deckgl',
                'vega': 'panel.models.vega',
                'vtk': 'panel.models.vtk',
                'ace': 'panel.models.ace'}

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

        if 'holoviews' in sys.modules:
            import holoviews as hv
            import holoviews.plotting.bokeh # noqa
            if not getattr(hv.extension, '_loaded', False):
                if hasattr(hv.Store, 'set_current_backend'):
                    hv.Store.set_current_backend('bokeh')
                else:
                    hv.Store.current_backend = 'bokeh'

        try:
            ip = params.pop('ip', None) or get_ipython() # noqa (get_ipython)
        except Exception:
            return

        if hasattr(ip, 'kernel') and not self._loaded and not config._doc_build:
            # TODO: JLab extension and pyviz_comms should be changed
            #       to allow multiple cleanup comms to be registered
            _JupyterCommManager.get_client_comm(self._process_comm_msg,
                                                "hv-extension-comm")
            state._comm_manager = _JupyterCommManager

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
