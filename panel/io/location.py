"""
Defines the Location  widget which allows changing the href of the window.
"""

import urllib.parse as urlparse

import param

from ..models.location import Location as _BkLocation
from ..viewable import Syncable


class Location(Syncable):

    href = param.String(readonly=True, doc="""
        The full url, e.g. 'https://localhost:80?color=blue#interact'""")

    hostname = param.String(readonly=True, doc="""
        hostname in window.location e.g. 'panel.holoviz.org'""")

    pathname = param.String(regex=r"^$|[\/].*$", doc="""
        pathname in window.location e.g. '/user_guide/Interact.html'""")

    protocol = param.String(readonly=True, doc="""
        protocol in window.location e.g. 'http:' or 'https:'""")

    port = param.String(readonly=True, doc="""
        port in window.location e.g. '80'""")

    search = param.String(regex=r"^$|\?", doc="""
        search in window.location e.g. '?color=blue'""")

    hash_ = param.String(regex=r"^$|#", doc="""
        hash in window.location e.g. '#interact'""")

    reload = param.Boolean(default=True, doc="""
        Reload the page when the location is updated. For multipage
        apps this should be set to True, For single page apps this
        should be set to False""")

    # Mapping from parameter name to bokeh model property name
    _rename = {"name": None}

    def _get_model(self, doc, root, parent=None, comm=None):
        model = _BkLocation(**self._process_param_change(self._init_properties()))
        values = dict(self.param.get_param_values())
        properties = list(self._process_param_change(values))
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, properties, doc, root, comm)
        return model

    @property
    def query_params(self):
        return dict(urlparse.parse_qsl(self.search[1:]))

    def update_query(self, **kwargs):
        query = self.query_params
        query.update(kwargs)
        self.search = '?' + urlparse.urlencode(query)
