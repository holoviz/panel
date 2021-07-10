"""
Defines the Location  widget which allows changing the href of the window.
"""

import json
import urllib.parse as urlparse

import param

from ..models.location import Location as _BkLocation
from ..reactive import Syncable
from ..util import parse_query
from .state import state


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
        super().__init__(**params)
        self._synced = []
        self._syncing = False
        self.param.watch(self._update_synced, ['search'])

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = _BkLocation(**self._process_param_change(self._init_params()))
        root = root or model
        values = dict(self.param.get_param_values())
        properties = list(self._process_param_change(values))
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, properties, doc, root, comm)
        return model

    def _get_root(self, doc=None, comm=None):
        root = self._get_model(doc, comm=comm)
        ref = root.ref['id']
        state._views[ref] = (self, root, doc, comm)
        self._documents[doc] = root
        return root

    def _cleanup(self, root):
        if root.document in self._documents:
            del self._documents[root.document]
        ref = root.ref['id']
        super()._cleanup(root)
        if ref in state._views:
            del state._views[ref]

    def _update_synced(self, event=None):
        if self._syncing:
            return
        query_params = self.query_params
        for p, parameters, _, on_error in self._synced:
            mapping = {v: k for k, v in parameters.items()}
            mapped = {}
            for k, v in query_params.items():
                if k not in mapping:
                    continue
                pname = mapping[k]
                try:
                    v = p.param[pname].deserialize(v)
                except Exception:
                    pass
                try:
                    equal = v == getattr(p, pname)
                except Exception:
                    equal = False
                if not equal:
                    mapped[pname] = v
            try:
                p.param.set_param(**mapped)
            except Exception:
                if on_error:
                    on_error(mapped)

    def _update_query(self, *events, query=None):
        if self._syncing:
            return
        serialized = query or {}
        for e in events:
            matches = [ps for o, ps, _, _ in self._synced if o in (e.cls, e.obj)]
            if not matches:
                continue
            owner = e.cls if e.obj is None else e.obj
            try:
                val = owner.param[e.name].serialize(e.new)
            except Exception:
                val = e.new
            if not isinstance(val, str):
                val = json.dumps(val)
            serialized[matches[0][e.name]] = val
        self._syncing = True
        try:
            self.update_query(**{k: v for k, v in serialized.items() if v is not None})
        finally:
            self._syncing = False

    @property
    def query_params(self):
        return parse_query(self.search)

    def update_query(self, **kwargs):
        query = self.query_params
        query.update(kwargs)
        self.search = '?' + urlparse.urlencode(query)

    def sync(self, parameterized, parameters=None, on_error=None):
        """
        Syncs the parameters of a Parameterized object with the query
        parameters in the URL. If no parameters are supplied all
        parameters except the name are synced.

        Arguments
        ---------
        parameterized (param.Parameterized):
          The Parameterized object to sync query parameters with
        parameters (list or dict):
          A list or dictionary specifying parameters to sync.
          If a dictionary is supplied it should define a mapping from
          the Parameterized's parameteres to the names of the query
          parameters.
        on_error: (callable):
          Callback when syncing Parameterized with URL parameters
          fails. The callback is passed a dictionary of parameter
          values, which could not be applied.
        """
        parameters = parameters or [p for p in parameterized.param if p != 'name']
        if not isinstance(parameters, dict):
            parameters = dict(zip(parameters, parameters))
        watcher = parameterized.param.watch(self._update_query, list(parameters))
        self._synced.append((parameterized, parameters, watcher, on_error))
        self._update_synced()
        query = {}
        for p, name in parameters.items():
            v = getattr(parameterized, p)
            if v is None:
                continue
            try:
                v = parameterized.param[p].serialize(v)
            except Exception:
                pass
            if not isinstance(v, str):
                v = json.dumps(v)
            query[name] = v
        self._update_query(query=query)

    def unsync(self, parameterized, parameters=None):
        """
        Unsyncs the parameters of the Parameterized with the query
        params in the URL. If no parameters are supplied all
        parameters except the name are unsynced.

        Arguments
        ---------
        parameterized (param.Parameterized):
          The Parameterized object to unsync query parameters with
        parameters (list or dict):
          A list of parameters to unsync.
        """
        matches = [s for s in self._synced if s[0] is parameterized]
        if not matches:
            ptype = type(parameterized)
            raise ValueError(f"Cannot unsync {ptype} object since it "
                             "was never synced in the first place.")
        synced = []
        for p, params, watcher, on_error in self._synced:
            if parameterized is p:
                parameterized.param.unwatch(watcher)
                if parameters is not None:
                    new_params = {p: q for p, q in params.items()
                                  if p not in parameters}
                    new_watcher = parameterized.param.watch(watcher.fn, list(new_params))
                    synced.append((p, new_params, new_watcher, on_error))
            else:
                synced.append((p, params, watcher, on_error))
        self._synced = synced
