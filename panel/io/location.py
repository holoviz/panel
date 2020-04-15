"""
Defines the Location  widget which allows changing the href of the window.
"""

import urllib.parse as urlparse

import param

from ..models.location import Location as _BkLocation
from ..reactive import Syncable
from ..util import parse_query


class Location(Syncable):
    """
    The Location component can be made available in a server context
    to provide read and write access to the URL components in the
    browser.
    """

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

    hash = param.String(regex=r"^$|#", doc="""
        hash in window.location e.g. '#interact'""")

    reload = param.Boolean(default=False, doc="""
        Reload the page when the location is updated. For multipage
        apps this should be set to True, For single page apps this
        should be set to False""")

    # Mapping from parameter name to bokeh model property name
    _rename = {"name": None}

    def __init__(self, **params):
        super(Location, self).__init__(**params)
        self._synced = []
        self._syncing = False
        self.param.watch(self._update_synced, ['search'])

    def _get_model(self, doc, root, parent=None, comm=None):
        model = _BkLocation(**self._process_param_change(self._init_properties()))
        values = dict(self.param.get_param_values())
        properties = list(self._process_param_change(values))
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, properties, doc, root, comm)
        return model

    def _update_synced(self, event):
        if self._syncing:
            return
        query_params = self.query_params
        for p in self._synced:
            p.param.set_param(**{k: v for k, v in query_params.items()
                                 if k in p.param})

    def _update_query(self, *events):
        self._syncing = True
        try:
            self.update_query(**{e.name: e.new for e in events})
        finally:
            self._syncing = False

    @property
    def query_params(self):
        return parse_query(self.search)

    def update_query(self, **kwargs):
        query = self.query_params
        query.update(kwargs)
        self.search = '?' + urlparse.urlencode(query)

    def sync(self, parameterized, parameters=None):
        self._synced.append(parameterized)
        parameters = parameters or [p for p in parameterized.param if p != 'name']
        parameterized.param.watch(self._update_query, parameters)
