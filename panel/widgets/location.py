"""
Defines the Location  widget which allows changing the href of the window.
"""
from contextlib import contextmanager
from typing import Dict, List, Optional

# In order to enable syncing readonly values like href we define a _href helper parameter
import param

import panel as pn
from panel.models.location import Location as _BkLocation
from panel.widgets.base import Widget

from .base import Widget


# This functionality should be contributed to param
# See https://github.com/holoviz/param/issues/379
@contextmanager
def edit_readonly(parameterized):
    """
    Temporarily set parameters on Parameterized object to readonly=False
    to allow editing them.
    """
    params = parameterized.param.objects("existing").values()
    readonlys = [p.readonly for p in params]
    constants = [p.constant for p in params]
    for p in params:
        p.readonly = False
        p.constant = False
    try:
        yield
    except:
        raise
    finally:
        for (p, readonly) in zip(params, readonlys):
            p.readonly = readonly
        for (p, constant) in zip(params, constants):
            p.constant = constant


class Location(Widget):
    href = param.String(
        readonly=True,
        doc="""The full url, e.g. \
            'https://panel.holoviz.org/user_guide/Interact.html:80?color=blue#interact'""",
    )
    hostname = param.String(
        readonly=True, doc="hostname in window.location e.g. 'panel.holoviz.org'"
    )
    # Todo: Find the corect regex for pathname
    pathname = param.String(
        regex=r"^$|[\/].*$", doc="pathname in window.location e.g. '/user_guide/Interact.html'",
    )
    protocol = param.String(
        readonly=True, doc="protocol in window.location e.g. 'http:' or 'https:'"
    )
    port = param.String(readonly=True, doc="port in window.location e.g. '80'")
    search = param.String(regex=r"^$|\?", doc="search in window.location e.g. '?color=blue'")
    hash_ = param.String(regex=r"^$|#", doc="hash in window.location e.g. '#interact'")

    reload = param.Boolean(
        default=True,
        doc="""Reload the page when the location is updated. For multipage apps this should be \
        set to True, For single page apps this should be set to False""",
    )

    _href = param.String()
    _hostname = param.String()
    _protocol = param.String()
    _port = param.String()

    _widget_type = _BkLocation  # type: ignore

    # Mapping from parameter name to bokeh model property name
    _rename: Dict[str, Optional[str]] = {
        "name": None,
        "hostname": None,
        "href": None,
        "port": None,
        "protocol": None,
        "_hostname": "hostname",
        "_href": "href",
        "_port": "port",
        "_protocol": "protocol",
    }

    @param.depends("_href", watch=True)
    def _update_href(self):
        with edit_readonly(self):
            self.href = self._href

    @param.depends("_hostname", watch=True)
    def _update_hostname(self):
        with edit_readonly(self):
            self.hostname = self._hostname

    @param.depends("_protocol", watch=True)
    def _update_protocol(self):
        with edit_readonly(self):
            self.protocol = self._protocol

    @param.depends("_port", watch=True)
    def _update_port(self):
        with edit_readonly(self):
            self.port = self._port

    def update_search(
        self, param_class: param.Parameterized, parameters: Optional[List[str]] = None
    ):
        """Updates the search string from the specified parameters

        Parameters
        ----------
        param_class : param.Parameterized
            The Parameterized Class containing the Parameters
        parameters : [type], optional
            The parameters to provide in the search string. If None is provided then all, by default None
        """
        raise NotImplementedError()

    def update_param_class(self, parameters=None):
        """Updates the Parameterized Class from the parameters

        Parameters
        ----------
        param_class : param.Parameterized
            The Parameterized Class containing the Parameters
        parameters : [type], optional
            [description], by default None
        """
        raise NotImplementedError()
