from __future__ import absolute_import

import sys

from . import holoviews # noqa
from . import layout # noqa
from . import pipeline # noqa
from . import plotly # noqa
from . import vega # noqa
from . import widgets # noqa
from . import links # noqa

from .interact import interact # noqa
from .layout import Row, Column, Tabs, Spacer # noqa
from .pane import panel, Pane # noqa
from .param import Param # noqa
from .util import load_notebook as _load_nb
from .viewable import Viewable

import param
from pyviz_comms import JupyterCommManager, extension as _pyviz_extension

__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                                        reponame="panel"))


class extension(_pyviz_extension):
    """
    Initializes the pyviz notebook extension to allow plotting with
    bokeh and enable comms.
    """

    inline = param.Boolean(default=True, doc="""
        Whether to inline JS and CSS resources.
        If disabled, resources are loaded from CDN if one is available.""")

    _loaded = False

    def __call__(self, *args, **params):
        # Abort if IPython not found
        try:
            ip = params.pop('ip', None) or get_ipython() # noqa (get_ipython)
        except:
            return

        p = param.ParamOverrides(self, params)
        if hasattr(ip, 'kernel') and not self._loaded:
            # TODO: JLab extension and pyviz_comms should be changed
            #       to allow multiple cleanup comms to be registered
            JupyterCommManager.get_client_comm(self._process_comm_msg,
                                               "hv-extension-comm")
        _load_nb(p.inline)
        self._loaded = True

        Viewable._comm_manager = JupyterCommManager

        if 'holoviews' in sys.modules:
            import holoviews as hv
            if hv.extension._loaded:
                return
            import holoviews.plotting.bokeh # noqa
            if hasattr(hv.Store, 'set_current_backend'):
                hv.Store.set_current_backend('bokeh')
            else:
                hv.Store.current_backend = 'bokeh'


def _cleanup_panel(msg_id):
    """
    A cleanup action which is called when a plot is deleted in the notebook
    """
    if msg_id not in Viewable._views:
        return
    viewable, model = Viewable._views.pop(msg_id)
    viewable._cleanup(model)

extension.add_delete_action(_cleanup_panel)
