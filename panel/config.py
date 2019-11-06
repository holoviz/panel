"""
The config module supplies the global config object and the extension
which provides convenient support for  loading and configuring panel
components.
"""
from __future__ import absolute_import, division, unicode_literals

import glob
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

    css_files = param.List(default=_CSS_FILES, doc="""
        External CSS files to load as part of the template.""")

    js_files = param.Dict(default={}, doc="""
        External JS files to load as part of the template. Dictionary
        should map from exported name to the URL of the JS file.""")

    raw_css = param.List(default=[], doc="""
        List of raw CSS strings to add to the template.""")

    _embed = param.Boolean(default=False, allow_None=True, doc="""
        Whether plot data will be embedded.""")

    _embed_json = param.Boolean(default=False, doc="""
        Whether to save embedded state to json files.""")

    _embed_json_prefix = param.String(default='', doc="""
        Prefix for randomly generated json directories.""")

    _embed_save_path = param.String(default='./', doc="""
        Where to save json files for embedded state.""")

    _embed_load_path = param.String(default=None, doc="""
        Where to load json files for embedded state.""")

    _comms = param.ObjectSelector(
        default='default', objects=['default', 'ipywidgets'], doc="""
        Whether to render output in Jupyter with the default Jupyter
        extension or use the jupyter_bokeh ipywidget model.""") 

    _inline = param.Boolean(default=True, allow_None=True, doc="""
        Whether to inline JS and CSS resources.
        If disabled, resources are loaded from CDN if one is available.""")

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
            self.set_param(**dict(values))
            for k, v in overrides:
                setattr(self, k+'_', v)

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
    _params = _config.params()

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

        try:
            ip = params.pop('ip', None) or get_ipython() # noqa (get_ipython)
        except:
            return

        if hasattr(ip, 'kernel') and not self._loaded:
            # TODO: JLab extension and pyviz_comms should be changed
            #       to allow multiple cleanup comms to be registered
            _JupyterCommManager.get_client_comm(self._process_comm_msg,
                                                "hv-extension-comm")
            state._comm_manager = _JupyterCommManager

        load_notebook(config.inline)
        panel_extension._loaded = True

        if 'holoviews' in sys.modules:
            import holoviews as hv
            if hv.extension._loaded:
                return
            import holoviews.plotting.bokeh # noqa

            if hasattr(ip, 'kernel'):
                with param.logging_level('ERROR'):
                    hv.plotting.Renderer.load_nb()

            if hasattr(hv.Store, 'set_current_backend'):
                hv.Store.set_current_backend('bokeh')
            else:
                hv.Store.current_backend = 'bokeh'


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
