"""
Defines the Location  widget which allows changing the href of the window.
"""
from __future__ import annotations

import json
import urllib.parse as urlparse

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any, ClassVar

import param

from ..models.location import Location as _BkLocation
from ..reactive import Syncable
from ..util import edit_readonly, parse_query
from .cache import is_equal
from .document import create_doc_if_none_exists
from .state import state

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from bokeh.server.contexts import BokehSessionContext
    from pyviz_comms import Comm

def _get_location_params(protocol: str|None, host: str| None, uri: str| None)->dict:
    params = {}
    href = ''
    if protocol:
        params['protocol'] = href = f'{protocol}:'
    if host:
        if host.startswith('::ffff:'):
            host = host.replace('::ffff:', '')
        elif host == '::1':
            host = host.replace('::1', 'localhost')

        href += f'//{host}'
        if ':' in host:
            params['hostname'], params['port'] = host.split(':')
        else:
            params['hostname'] = host
    if uri:
        search = hash = None

        if uri.startswith("https,"):
            uri = uri.replace("https,", "")

        if uri.startswith("http"):
            uri = urlparse.urlparse(uri).path

        href += uri
        if '?' in uri and '#' in uri:
            params['pathname'], query = uri.split('?')
            search, hash = query.split('#')
        elif '?' in uri:
            params['pathname'], search = uri.split('?')
        elif '#' in uri:
            params['pathname'], hash = uri.split('#')
        else:
            params['pathname'] = uri
        if search:
            params['search'] = f'?{search}'
        if hash:
            params['hash'] = f'#{hash}'
    params['href'] = href
    return params

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

    pathname = param.String(regex=r"^$|[\/]|srcdoc$", doc="""
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
    _rename: ClassVar[Mapping[str, str | None]] = {"name": None}

    @classmethod
    def from_request(cls, request):
        try:
            from bokeh.server.contexts import _RequestProxy
            if not isinstance(request, _RequestProxy) or request._request is None:
                return cls()
        except ImportError:
            return cls()

        params = _get_location_params(request.protocol, request.host, request.uri)
        loc = cls()
        with edit_readonly(loc):
            loc.param.update(params)
        return loc

    def __init__(self, **params):
        super().__init__(**params)
        self._synced = []
        self._syncing = False
        self.param.watch(self._update_synced, ['search'])

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = _BkLocation(**self._process_param_change(self._init_params()))
        root = root or model
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, self._linked_properties, doc, root, comm)
        return model

    def get_root(
        self, doc: Document | None = None, comm: Comm | None = None,
        preprocess: bool = True
    ) -> Model:
        doc = create_doc_if_none_exists(doc)
        root = self._get_model(doc, comm=comm)
        ref = root.ref['id']
        state._views[ref] = (self, root, doc, comm)
        self._documents[doc] = root
        return root

    def _server_destroy(self, session_context: BokehSessionContext) -> None:
        for p, ps, _, _ in self._synced:
            try:
                self.unsync(p, ps)
            except Exception:
                pass
        super()._server_destroy(session_context)

    def _cleanup(self, root: Model | None = None) -> None:
        if root:
            if root.document in self._documents:
                del self._documents[root.document]
            ref = root.ref['id']
        else:
            ref = None
        super()._cleanup(root)
        if ref in state._views:
            del state._views[ref]

    def _update_synced(self, event: param.parameterized.Event = None) -> None:
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
                    equal = is_equal(v, getattr(p, pname))
                except Exception:
                    equal = False

                if not equal:
                    mapped[pname] = v
            try:
                p.param.update(**mapped)
            except Exception:
                if on_error:
                    on_error(mapped)

    def _update_query(
        self, *events: param.parameterized.Event, query: dict[str, Any] | None = None
    ) -> None:
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
    def query_params(self) -> dict[str, Any]:
        return parse_query(self.search)

    def update_query(self, **kwargs: Mapping[str, Any]) -> None:
        query = self.query_params
        query.update(kwargs)
        self.search = '?' + urlparse.urlencode(query)

    def sync(
        self, parameterized: param.Parameterized, parameters: list[str] | dict[str, str] | None = None,
        on_error: Callable[[dict[str, Any]], None] | None = None
    ) -> None:
        """
        Syncs the parameters of a Parameterized object with the query
        parameters in the URL. If no parameters are supplied all
        parameters except the name are synced.

        Parameters
        ----------
        parameterized (param.Parameterized):
          The Parameterized object to sync query parameters with
        parameters (list or dict):
          A list or dictionary specifying parameters to sync.
          If a dictionary is supplied it should define a mapping from
          the Parameterized's parameters to the names of the query
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

    def unsync(self, parameterized: param.Parameterized, parameters: list[str] | None = None) -> None:
        """
        Unsyncs the parameters of the Parameterized with the query
        params in the URL. If no parameters are supplied all
        parameters except the name are unsynced.

        Parameters
        ----------
        parameterized (param.Parameterized):
          The Parameterized object to unsync query parameters with
        parameters (list):
          A list of parameters to unsync.
        """
        matches = [s for s in self._synced if s[0] is parameterized]
        if not matches:
            ptype = type(parameterized)
            raise ValueError(f"Cannot unsync {ptype} object since it "
                             "was never synced in the first place.")
        synced, unsynced = [], []
        for p, params, watcher, on_error in self._synced:
            if parameterized is not p:
                synced.append((p, params, watcher, on_error))
                continue
            parameterized.param.unwatch(watcher)
            if parameters is None:
                unsynced.extend(list(params.values()))
            else:
                unsynced.extend([q for p, q in params.items() if p in parameters])
                new_params = {p: q for p, q in params.items()
                              if p not in parameters}
                new_watcher = parameterized.param.watch(watcher.fn, list(new_params))
                synced.append((p, new_params, new_watcher, on_error))
        self._synced = synced
        query = {k: v for k, v in self.query_params.items() if k not in unsynced}
        self.search = '?' + urlparse.urlencode(query) if query else ''
