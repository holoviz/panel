from __future__ import absolute_import

from .layout import Row, Column # noqa
from .panes import Pane # noqa
from .param import ParamPane # noqa
from .util import load_notebook as _load_nb

import param
from pyviz_comms import JupyterCommManager

__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                                        reponame="panel"))


class extension(param.ParameterizedFunction):
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

    @classmethod
    def _process_comm_msg(cls, msg):
        """
        Processes comm messages to handle global actions such as
        cleaning up plots.
        """
        pass
