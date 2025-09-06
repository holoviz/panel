"""
Declares Syncable and Reactive classes which provides baseclasses
for Panel components which sync their state with one or more bokeh
models rendered on the frontend.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import difflib
import inspect
import logging
import pathlib
import re
import sys
import textwrap

from collections import Counter, defaultdict, namedtuple
from collections.abc import Callable, Mapping, Sequence
from functools import lru_cache, partial
from pprint import pformat
from typing import (
    TYPE_CHECKING, Any, ClassVar, TypeAlias,
)

import jinja2
import numpy as np
import param

from bokeh.core.property.descriptors import UnsetValueError
from bokeh.model import DataModel
from bokeh.models import ImportedStyleSheet
from packaging.version import Version
from param.parameterized import (
    ParameterizedMetaclass, Watcher, _syncing, iscoroutinefunction,
    resolve_ref, resolve_value,
)

from .io.document import hold, unlocked
from .io.notebook import push
from .io.resources import (
    CDN_DIST, loading_css, patch_stylesheet, process_raw_css,
    resolve_stylesheet,
)
from .io.state import set_curdoc, state
from .models.reactive_html import (
    DOMEvent, ReactiveHTML as _BkReactiveHTML, ReactiveHTMLParser,
)
from .util import (
    HTML_SANITIZER, classproperty, edit_readonly, escape, updating,
)
from .util.checks import import_available
from .viewable import (
    Child, Children, Layoutable, Renderable, Viewable,
)

if TYPE_CHECKING:
    import pandas as pd

    from bokeh.document import Document
    from bokeh.events import Event
    from bokeh.model import Model, ModelEvent
    from bokeh.models.sources import DataDict, Patches
    from pandas.api.extensions import ExtensionArray
    from pyviz_comms import Comm

    from .layout.base import Panel as BasePanel
    from .links import Callback, JSLinkTarget, Link

    TData: TypeAlias = pd.DataFrame | DataDict
    TDataColumn: TypeAlias = np.ndarray | pd.Series | pd.Index | ExtensionArray | Sequence[Any]

log = logging.getLogger('panel.reactive')

_fields = tuple(Watcher._fields+('target', 'links', 'transformed', 'bidirectional_watcher'))
LinkWatcher: tuple = namedtuple("Watcher", _fields) # type: ignore


class Syncable(Renderable):
    """
    Syncable is an extension of the Renderable object which can not
    only render to a bokeh model but also sync the parameters on the
    object with the properties on the model.

    In order to bi-directionally link parameters with bokeh model
    instances the _link_params and _link_props methods define
    callbacks triggered when either the parameter or bokeh property
    values change. Since there may not be a 1-to-1 mapping between
    parameter and the model property the _process_property_change and
    _process_param_change may be overridden to apply any necessary
    transformations.
    """

    # Timeout if a notebook comm message is swallowed
    _timeout: ClassVar[int] = 20000

    # Timeout before the first event is processed
    _debounce: ClassVar[int] = 50

    # Property changes which should not be debounced
    _priority_changes: ClassVar[list[str]] = []

    # Any parameters that require manual updates handling for the models
    # e.g. parameters which affect some sub-model
    _manual_params: ClassVar[list[str]] = []

    # Mapping from parameter name to bokeh model property name
    _rename: ClassVar[Mapping[str, str | None]] = {}

    # Allows defining a mapping from model property name to a JS code
    # snippet that transforms the object before serialization
    _js_transforms: ClassVar[Mapping[str, str]] = {}

    # Transforms from input value to bokeh property value
    _source_transforms: ClassVar[Mapping[str, str | None]] = {}
    _target_transforms: ClassVar[Mapping[str, str | None]] = {}

    # A list of stylesheets specified as paths relative to the
    # panel/dist directory
    _stylesheets: ClassVar[list[str]] = []

    # Property changes that should not trigger busy indicator
    _busy__ignore: ClassVar[list[str]] = []

    __abstract = True

    def __init__(self, **params):
        self._themer = None
        super().__init__(**params)

        # Useful when updating model properties which trigger potentially
        # recursive events
        self._updating = False

        # A dictionary of current property change events
        self._events = {}

        # Any watchers associated with links between two objects
        self._links = []
        self._link_params()

        # A dictionary of bokeh property changes being processed
        self._changing = {}

        # A dictionary of parameter changes being processed
        self._in_process__events = {}

        # Whether the component is watching the stylesheets
        self._watching_stylesheets = False

        # Sets up watchers to process manual updates to models
        if self._manual_params:
            self._internal_callbacks.append(
                self.param.watch(self._update_manual, self._manual_params)
            )

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    @classproperty
    @lru_cache(maxsize=None)  # noqa: B019 (cls is not an instance)
    def _property_mapping(cls):
        rename = {}
        for scls in cls.__mro__[::-1]:
            if issubclass(scls, Syncable):
                rename.update(scls._rename)
        return rename

    @property
    def _linked_properties(self) -> tuple[str, ...]:
        return tuple(
            self._property_mapping.get(p, p) for p in self.param
            if p not in Viewable.param and self._property_mapping.get(p, p) is not None
        )

    def _get_properties(self, doc: Document | None) -> dict[str, Any]:
        return self._process_param_change(self._init_params())

    def _process_property_change(self, msg: dict[str, Any]) -> dict[str, Any]:
        """
        Transform bokeh model property changes into parameter updates.
        Should be overridden to provide appropriate mapping between
        parameter value and bokeh model change. By default uses the
        _rename class level attribute to map between parameter and
        property names.
        """
        inverted = {v: k for k, v in self._property_mapping.items()}
        return {inverted.get(k, k): v for k, v in msg.items()}

    def _process_param_change(self, msg: dict[str, Any]) -> dict[str, Any]:
        """
        Transform parameter changes into bokeh model property updates.
        Should be overridden to provide appropriate mapping between
        parameter value and bokeh model change. By default uses the
        _rename class level attribute to map between parameter and
        property names.
        """
        properties = {
            self._property_mapping.get(k) or k: v for k, v in msg.items()
            if self._property_mapping.get(k, False) is not None and
            k not in self._manual_params
        }
        if 'sizing_mode' in properties:
            sm = properties['sizing_mode']
            if sm and ('width' in sm or 'both' in sm) and self.min_width is None:
                properties['min_width'] = 0
            if sm and ('height' in sm or 'both' in sm) and self.min_height is None:
                properties['min_height'] = 0
        if 'width' in properties and self.sizing_mode is None:
            properties['min_width'] = properties['width']
        if 'height' in properties and self.sizing_mode is None:
            properties['min_height'] = properties['height']
        if 'stylesheets' in properties:
            from .config import config
            stylesheets = [loading_css(
                config.loading_spinner, config.loading_color, config.loading_max_height
            ), f'{CDN_DIST}css/loading.css']
            stylesheets += process_raw_css(config.raw_css)
            stylesheets += config.css_files
            stylesheets += [
                resolve_stylesheet(self, css_file, '_stylesheets')
                for css_file in self._stylesheets
            ]
            stylesheets += properties['stylesheets']
            wrapped = []
            if state.curdoc:
                css_cache = state._stylesheets.get(state.curdoc, {})
            else:
                css_cache = {}
            for stylesheet in stylesheets:
                if not stylesheet:
                    continue
                if isinstance(stylesheet, str) and (stylesheet.split('?')[0].endswith('.css') or stylesheet.startswith('http')):
                    if stylesheet in css_cache:
                        conv_stylesheet = css_cache[stylesheet]
                    else:
                        css_cache[stylesheet] = conv_stylesheet = ImportedStyleSheet(url=stylesheet)
                    stylesheet = conv_stylesheet
                wrapped.append(stylesheet)
            properties['stylesheets'] = wrapped
        return properties

    @property
    def _linkable_params(self) -> list[str]:
        """
        Parameters that can be linked in JavaScript via source transforms.
        """
        return [
            p for p in self._synced_params if self._rename.get(p, False) is not None
            and self._source_transforms.get(p, False) is not None and
            p not in ('design', 'stylesheets')
        ]

    @property
    def _synced_params(self) -> list[str]:
        """
        Parameters which are synced with properties using transforms
        applied in the _process_param_change method.
        """
        ignored = ['default_layout', 'loading', 'background']
        return [p for p in self.param if p not in self._manual_params+ignored]

    def _init_params(self) -> dict[str, Any]:
        return {
            k: v for k, v in self.param.values().items()
            if k in self._synced_params and v is not None
        }

    def _link_params(self) -> None:
        params = self._synced_params
        if params:
            watcher = self.param.watch(self._param_change, params)
            self._internal_callbacks.append(watcher)

    def _link_props(
        self, model: Model | DataModel, properties: Sequence[str] | Sequence[tuple[str, str]],
        doc: Document, root: Model, comm: Comm | None = None
    ) -> None:
        from .config import config
        ref = root.ref['id']
        if config.embed:
            return

        for p in properties:
            if isinstance(p, tuple):
                _, p = p
            m = model
            if '.' in p:
                *parts, p = p.split('.')
                for sp in parts:
                    m = getattr(m, sp)
                subpath = '.'.join(parts)
            else:
                subpath = None
            if comm:
                m.on_change(p, partial(self._comm_change, doc, ref, comm, subpath))
            else:
                m.on_change(p, partial(self._server_change, doc, ref, subpath))

    def _manual_update(
        self, events: tuple[param.parameterized.Event, ...], model: Model, doc: Document,
        root: Model, parent: Model | None, comm: Comm | None
    ) -> None:
        """
        Method for handling any manual update events, i.e. events triggered
        by changes in the manual params.
        """

    def _update_manual(self, *events: param.parameterized.Event) -> None:
        for ref, (model, parent) in self._models.copy().items():
            if ref not in state._views or ref in state._fake_roots:
                continue
            viewable, root, doc, comm = state._views[ref]
            if comm or state._unblocked(doc):
                with unlocked():
                    self._manual_update(events, model, doc, root, parent, comm)
                if comm and 'embedded' not in root.tags:
                    push(doc, comm)
            else:
                cb = partial(self._manual_update, events, model, doc, root, parent, comm)
                if doc.session_context:
                    with set_curdoc(doc):
                        state.execute(cb, schedule=True)
                else:
                    cb()

    def _scheduled_update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Comm | None,
        curdoc_events: dict[str, Any]
    ) -> None:
        #
        self._in_process__events[doc] = curdoc_events
        try:
            self._update_model(events, msg, root, model, doc, comm)
        finally:
            self._in_process__events.pop(doc, None)

    def _apply_update(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        model: Model, ref: str
    ) -> bool:
        if ref not in state._views or ref in state._fake_roots:
            return True
        viewable, root, doc, comm = state._views[ref]
        if comm or not doc.session_context or state._unblocked(doc):
            with unlocked():
                self._update_model(events, msg, root, model, doc, comm)
            if comm and 'embedded' not in root.tags:
                push(doc, comm)
            return True
        else:
            curdoc_events = self._in_process__events.pop(doc, {})
            cb = partial(self._scheduled_update_model, events, msg, root, model, doc, comm, curdoc_events)
            with set_curdoc(doc):
                state.execute(cb, schedule=True)
            return False

    def _update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Comm | None
    ) -> None:
        ref = root.ref['id']
        self._changing[ref] = attrs = []
        curdoc_events = self._in_process__events.get(doc, {})
        for attr, value in msg.copy().items():
            if attr in curdoc_events and value is curdoc_events[attr]:
                # Do not apply change that originated directly from
                # the frontend since this may cause boomerang if a
                # new property value is already in-flight
                del msg[attr]
                continue
            elif attr in self._events:
                # Do not override a property value that was just changed
                # on the frontend
                del self._events[attr]
                continue

            # Bokeh raises UnsetValueError if the value is Undefined.
            try:
                model_val = getattr(model, attr)
            except UnsetValueError:
                attrs.append(attr)
                continue
            if not model.lookup(attr).property.matches(model_val, value):
                attrs.append(attr)

        try:
            model.update(**msg)
        finally:
            changing = [
                attr for attr in self._changing.get(ref, [])
                if attr not in attrs
            ]
            if changing:
                self._changing[ref] = changing
            elif ref in self._changing:
                del self._changing[ref]

    def _cleanup(self, root: Model | None = None) -> None:
        super()._cleanup(root)
        if root is None:
            return
        ref = root.ref['id']
        if ref in self._models:
            model, _ = self._models.pop(ref, None)
            model._callbacks = {}
            model._event_callbacks = {}
        if not self._models and self._watching_stylesheets:
            self._watching_stylesheets.set()
            if self._watching_stylesheets in state._watch_events:
                state._watch_events.remove(self._watching_stylesheets)
            self._watching_stylesheets = False
        comm, client_comm = self._comms.pop(ref, (None, None))
        if comm:
            try:
                comm.close()
            except Exception:
                pass
        if client_comm:
            try:
                client_comm.close()
            except Exception:
                pass

    def _update_properties(
        self, *events: param.parameterized.Event, doc: Document
    ) -> dict[str, Any]:
        changes = {event.name: event.new for event in events}
        return self._process_param_change(changes)

    def _setup_autoreload(self):
        from .config import config
        paths = [sts for sts in self._stylesheets if isinstance(sts, pathlib.PurePath)]
        if (self._watching_stylesheets or not (config.autoreload and paths and import_available('watchfiles'))):
            return
        self._watching_stylesheets = event = asyncio.Event()
        state._watch_events.append(event)
        state.execute(self._watch_stylesheets)

    async def _watch_stylesheets(self):
        import watchfiles
        base_dir = pathlib.Path(inspect.getfile(type(self))).parent
        paths = []
        for sts in self._stylesheets:
            if isinstance(sts, pathlib.PurePath):
                if not sts.absolute().is_file():
                    sts = base_dir / sts
                if sts.is_file():
                    paths.append(sts)
        async for _ in watchfiles.awatch(*paths, stop_event=self._watching_stylesheets):
            self.param.trigger('stylesheets')

    def _param_change(self, *events: param.parameterized.Event) -> None:
        named_events = {event.name: event for event in events}
        for ref, (model, _) in self._models.copy().items():
            properties = self._update_properties(*events, doc=model.document)
            if not properties:
                return
            self._apply_update(named_events, properties, model, ref)

    def _process_events(self, events: dict[str, Any]) -> None:
        self._log('received events %s', events)
        if any(e for e in events if e not in self._busy__ignore):
            with edit_readonly(state):
                state._busy_counter += 1
        try:
            params = {}
            if events and state.curdoc:
                self._in_process__events[state.curdoc] = events
            params = self._process_property_change(events)
            with edit_readonly(self):
                self_params = {k: v for k, v in params.items() if '.' not in k}
                with _syncing(self, list(self_params)):
                    self.param.update(**self_params)
            for k, v in params.items():
                if '.' not in k:
                    continue
                *subpath, p = k.split('.')
                obj = self
                for sp in subpath:
                    obj = getattr(obj, sp)
                with edit_readonly(obj):
                    with _syncing(obj, [p]):
                        obj.param.update(**{p: v})
        except Exception as e:
            if len(params) > 1:
                msg_end = f"changing properties {pformat(params)} \n"
            elif len(params) == 1:
                msg_end = f"changing property {pformat(params)} \n"
            else:
                msg_end = "\n"
            log.exception(f'Callback failed for object named {self.name!r} {msg_end}')
            raise e
        finally:
            if state.curdoc and state.curdoc in self._in_process__events:
                del self._in_process__events[state.curdoc]
            self._log('finished processing events %s', events)
            if any(e for e in events if e not in self._busy__ignore):
                with edit_readonly(state):
                    state._busy_counter -= 1

    def _process_bokeh_event(self, doc: Document, event: Event) -> None:
        self._log('received bokeh event %s', event)
        with edit_readonly(state):
            state._busy_counter += 1
        try:
            with set_curdoc(doc):
                self._process_event(event)
        finally:
            self._log('finished processing bokeh event %s', event)
            with edit_readonly(state):
                state._busy_counter -= 1

    async def _change_coroutine(self, doc: Document) -> None:
        if state._thread_pool:
            future = state._thread_pool.submit(self._change_event, doc)
            future.add_done_callback(partial(state._handle_future_exception, doc=doc))
        else:
            with set_curdoc(doc):
                try:
                    self._change_event(doc)
                except Exception as e:
                    state._handle_exception(e)

    async def _event_coroutine(self, doc: Document, event) -> None:
        if state._thread_pool:
            future = state._thread_pool.submit(self._process_bokeh_event, doc, event)
            future.add_done_callback(partial(state._handle_future_exception, doc=doc))
        else:
            try:
                self._process_bokeh_event(doc, event)
            except Exception as e:
                state._handle_exception(e)

    def _change_event(self, doc: Document) -> None:
        events = self._events
        self._events = {}
        with set_curdoc(doc):
            self._process_events(events)

    def _schedule_change(self, doc: Document, comm: Comm | None) -> None:
        with hold(doc, comm=comm):
            self._change_event(doc)

    def _comm_change(
        self, doc: Document, ref: str, comm: Comm | None, subpath: str | None,
        attr: str, old: Any, new: Any
    ) -> None:
        if subpath:
            attr = f'{subpath}.{attr}'
        if attr in self._changing.get(ref, []):
            self._changing[ref].remove(attr)
            return

        self._events.update({attr: new})
        if state._thread_pool:
            future = state._thread_pool.submit(self._schedule_change, doc, comm)
            future.add_done_callback(partial(state._handle_future_exception, doc=doc))
        else:
            try:
                self._schedule_change(doc, comm)
            except Exception as e:
                state._handle_exception(e)

    def _comm_event(self, doc: Document, event: Event) -> None:
        if state._thread_pool:
            future = state._thread_pool.submit(self._process_bokeh_event, doc, event)
            future.add_done_callback(partial(state._handle_future_exception, doc=doc))
        else:
            try:
                self._process_bokeh_event(doc, event)
            except Exception as e:
                state._handle_exception(e)

    def _register_events(self, *event_names: str, model: Model, doc: Document, comm: Comm | None) -> None:
        for event_name in event_names:
            method = self._comm_event if comm else self._server_event
            model.on_event(event_name, partial(method, doc))

    def _server_event(self, doc: Document, event: Event) -> None:
        if doc.session_context and not state._unblocked(doc):
            cb = partial(self._event_coroutine, doc, event)
            with set_curdoc(doc):
                state.execute(cb, schedule=True)
        else:
            self._comm_event(doc, event)

    def _server_change(
        self, doc: Document, ref: str, subpath: str | None, attr: str,
        old: Any, new: Any
    ) -> None:
        if subpath:
            attr = f'{subpath}.{attr}'
        if attr in self._changing.get(ref, []):
            self._changing[ref].remove(attr)
            return

        processing = bool(self._events)
        self._events.update({attr: new})
        if processing:
            return

        if doc.session_context:
            cb = partial(self._change_coroutine, doc)
            if attr in self._priority_changes:
                doc.add_next_tick_callback(cb) # type: ignore
            else:
                doc.add_timeout_callback(cb, self._debounce) # type: ignore
        else:
            try:
                self._change_event(doc)
            except Exception as e:
                state._handle_exception(e)


class Reactive(Syncable, Viewable):
    """
    Reactive is a Viewable object that also supports syncing between
    the objects parameters and the underlying bokeh model either via
    the defined pyviz_comms.Comm type or using bokeh server.

    In addition it defines various methods which make it easy to link
    the parameters to other objects.
    """

    # Parameter values which should not be treated like references
    _ignored_refs: ClassVar[tuple[str,...]] = ()

    _rename: ClassVar[Mapping[str, str | None]] = {
        'design': None, 'loading': None
    }

    __abstract = True

    def __init__(self, refs=None, **params):
        for name, pobj in self.param.objects('existing').items():
            if (name not in self._param__private.explicit_no_refs and
                not isinstance(pobj, Child)):
                pobj.allow_refs = True
        if refs is not None:
            self._refs = refs
            if iscoroutinefunction(refs):
                param.parameterized.async_executor(self._async_refs)
            else:
                params.update(resolve_value(self._refs))
            refs = resolve_ref(self._refs)
            if refs:
                param.bind(self._sync_refs, *refs, watch=True)
        super().__init__(**params)

    def _sync_refs(self, *_):
        resolved = resolve_value(self._refs)
        self.param.update(resolved)

    async def _async_refs(self, *_):
        resolved = resolve_value(self._refs)
        if inspect.isasyncgenfunction(self._refs):
            async for val in resolved:
                self.param.update(val)
        else:
            self.param.update(await resolved)

    #----------------------------------------------------------------
    # Private API
    #----------------------------------------------------------------

    def _get_properties(self, doc: Document | None) -> dict[str, Any]:
        params, _ = self._design.params(self, doc) if self._design else ({}, None)
        for k, v in self._init_params().items():
            if k in ('stylesheets', 'tags') and k in params:
                params[k] = v = params[k] + v
            elif k not in params or self.param[k].default is not v:
                params[k] = v
        properties = self._process_param_change(params)
        if 'stylesheets' not in properties:
            return properties
        if doc:
            state._stylesheets[doc] = css_cache = state._stylesheets.get(doc, {})
        else:
            css_cache = {}
        if doc and 'dist_url' in doc._template_variables:
            dist_url = doc._template_variables['dist_url']
        else:
            dist_url = CDN_DIST
        stylesheets = []
        for stylesheet in properties['stylesheets']:
            if isinstance(stylesheet, ImportedStyleSheet):
                url = str(stylesheet.url)
                if url in css_cache:
                    cached = css_cache[url]
                    # Confirm if stylesheet is valid, sometimes
                    # the URL is seemingly set to None so we
                    # replace the cached stylesheet if there is
                    # a unset property error
                    try:
                        cached.url  # noqa
                    except Exception:
                        css_cache[url] = stylesheet
                    else:
                        stylesheet = cached
                else:
                    css_cache[url] = stylesheet
                patch_stylesheet(stylesheet, dist_url)
            stylesheets.append(stylesheet)
        properties['stylesheets'] = stylesheets
        return properties

    def _update_properties(self, *events: param.parameterized.Event, doc: Document) -> dict[str, Any]:
        params, _ = self._design.params(self, doc) if self._design else ({}, None)
        changes = {event.name: event.new for event in events}
        if 'stylesheets' in changes and 'stylesheets' in params:
            changes['stylesheets'] = params['stylesheets'] + changes['stylesheets']
        return self._process_param_change(changes)

    def _update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Comm | None
    ) -> None:
        if 'stylesheets' in msg:
            if doc and 'dist_url' in doc._template_variables:
                dist_url = doc._template_variables['dist_url']
            else:
                dist_url = CDN_DIST
            for stylesheet in msg['stylesheets']:
                if isinstance(stylesheet, ImportedStyleSheet):
                    patch_stylesheet(stylesheet, dist_url)
        super()._update_model(events, msg, root, model, doc, comm)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def link(
        self, target: param.Parameterized, callbacks: dict[str, str | Callable] | None=None,
        bidirectional: bool = False, **links: str
    ) -> Watcher:
        """
        Links the parameters on this `Reactive` object to attributes on the
        target `Parameterized` object.

        Supports two modes, either specify a
        mapping between the source and target object parameters as keywords or
        provide a dictionary of callbacks which maps from the source
        parameter to a callback which is triggered when the parameter
        changes.

        Parameters
        ----------
        target: param.Parameterized
          The target object of the link.
        callbacks: dict | None
          Maps from a parameter in the source object to a callback.
        bidirectional: bool
          Whether to link source and target bi-directionally
        links: dict
          Maps between parameters on this object to the parameters
          on the supplied object.
        """
        if links and callbacks:
            raise ValueError('Either supply a set of parameters to '
                             'link as keywords or a set of callbacks, '
                             'not both.')
        elif not links and not callbacks:
            raise ValueError('Declare parameters to link or a set of '
                             'callbacks, neither was defined.')
        elif callbacks and bidirectional:
            raise ValueError('Bidirectional linking not supported for '
                             'explicit callbacks. You must define '
                             'separate callbacks for each direction.')

        _updating = []
        def link_cb(*events):
            for event in events:
                if event.name in _updating: continue
                _updating.append(event.name)
                try:
                    if callbacks:
                        callbacks[event.name](target, event)
                    else:
                        setattr(target, links[event.name], event.new)
                finally:
                    _updating.pop(_updating.index(event.name))
        params = list(callbacks) if callbacks else list(links)
        cb = self.param.watch(link_cb, params)

        bidirectional_watcher = None
        if bidirectional:
            _reverse_updating = []
            reverse_links = {v: k for k, v in links.items()}
            def reverse_link(*events):
                for event in events:
                    if event.name in _reverse_updating: continue
                    _reverse_updating.append(event.name)
                    try:
                        setattr(self, reverse_links[event.name], event.new)
                    finally:
                        _reverse_updating.remove(event.name)
            bidirectional_watcher = target.param.watch(reverse_link, list(reverse_links))

        link_args = tuple(cb)
        # Compatibility with Param versions where precedence is dropped
        # from iterator for backward compatibility with older Panel versions
        if 'precedence' in Watcher._fields and len(link_args) < len(Watcher._fields):
            link_args += (cb.precedence,)
        link = LinkWatcher(*(link_args+(target, links, callbacks is not None, bidirectional_watcher)))
        self._links.append(link)
        return cb

    def controls(self, parameters: list[str] = [], jslink: bool = True, **kwargs) -> BasePanel:
        """
        Creates a set of widgets which allow manipulating the parameters
        on this instance. By default all parameters which support
        linking are exposed, but an explicit list of parameters can
        be provided.

        Parameters
        ----------
        parameters: list(str)
           An explicit list of parameters to return controls for.
        jslink: bool
           Whether to use jslinks instead of Python based links.
           This does not allow using all types of parameters.
        kwargs: dict
           Additional kwargs to pass to the Param pane(s) used to
           generate the controls widgets.

        Returns
        -------
        A layout of the controls
        """
        from .layout import Tabs, WidgetBox
        from .param import Param
        from .widgets import LiteralInput

        if parameters:
            linkable = parameters
        elif jslink:
            linkable = self._linkable_params
        else:
            linkable = list(self.param)

        params = [p for p in linkable if p not in Viewable.param]
        controls = Param(self.param, parameters=params, default_layout=WidgetBox,
                         name='Controls', **kwargs)
        layout_params = [p for p in linkable if p in Viewable.param]
        if 'name' not in layout_params and self._property_mapping.get('name', False) is not None and not parameters:
            layout_params.insert(0, 'name')
        style = Param(self.param, parameters=layout_params, default_layout=WidgetBox,
                      name='Layout', **kwargs)
        if jslink:
            for p in params:
                widget = controls._widgets[p]
                widget.jslink(self, value=p, bidirectional=True)
                if isinstance(widget, LiteralInput):
                    widget.serializer = 'json'
            for p in layout_params:
                widget = style._widgets[p]
                widget.jslink(self, value=p, bidirectional=p != 'loading')
                if isinstance(widget, LiteralInput):
                    widget.serializer = 'json'

        if params and layout_params:
            return Tabs(controls.layout[0], style.layout[0])
        elif params:
            return controls.layout[0]
        return style.layout[0]

    def jscallback(self, args: dict[str, Any]={}, **callbacks: str) -> Callback:
        """
        Allows defining a JS callback to be triggered when a property
        changes on the source object. The keyword arguments define the
        properties that trigger a callback and the JS code that gets
        executed.

        Parameters
        ----------
        args: dict
          A mapping of objects to make available to the JS callback
        callbacks: dict
          A mapping between properties on the source model and the code
          to execute when that property changes

        Returns
        -------
        callback: Callback
          The Callback which can be used to disable the callback.
        """
        from .links import Callback
        return Callback(self, code=callbacks, args=args)

    def jslink(
        self,
        target: JSLinkTarget,
        code: dict[str, str] | None = None,
        args: dict | None = None,
        bidirectional: bool = False,
        **links: str
    ) -> Link:
        """
        Links properties on the this Reactive object to those on the
        target Reactive object in JS code.

        Supports two modes, either specify a
        mapping between the source and target model properties as
        keywords or provide a dictionary of JS code snippets which
        maps from the source parameter to a JS code snippet which is
        executed when the property changes.

        Parameters
        ----------
        target: panel.viewable.Viewable | bokeh.model.Model | holoviews.core.dimension.Dimensioned
          The target to link the value to.
        code: dict
          Custom code which will be executed when the widget value
          changes.
        args: dict
          A mapping of objects to make available to the JS callback
        bidirectional: boolean
          Whether to link source and target bi-directionally
        links: dict
          A mapping between properties on the source model and the
          target model property to link it to.

        Returns
        -------
        link: GenericLink
          The GenericLink which can be used unlink the widget and
          the target model.
        """
        if links and code:
            raise ValueError('Either supply a set of properties to '
                             'link as keywords or a set of JS code '
                             'callbacks, not both.')
        elif not links and not code:
            raise ValueError('Declare parameters to link or a set of '
                             'callbacks, neither was defined.')
        if args is None:
            args = {}

        from .links import Link, assert_source_syncable, assert_target_syncable
        mapping = code or links
        assert_source_syncable(self, mapping)
        if isinstance(target, Syncable) and code is None:
            assert_target_syncable(self, target, mapping)
        return Link(self, target, properties=links, code=code, args=args,
                    bidirectional=bidirectional)

    def _send_event(self, Event: ModelEvent, **event_kwargs: Any):
        """
        Send an event to the frontend

        Parameters
        ----------
        Event: Bokeh.Event
            The event to send to the frontend
        event_kwargs: dict
            Additional keyword arguments to pass to the event
            This will create the following event:
            Event(model=model, **event_kwargs)
        """
        for ref, (model, _) in self._models.copy().items():
            if ref not in state._views or ref in state._fake_roots:
                continue
            event = Event(model=model, **event_kwargs)
            _viewable, root, doc, comm = state._views[ref]
            if comm or state._unblocked(doc) or not doc.session_context:
                with unlocked():
                    doc.callbacks.send_event(event)
                if comm and 'embedded' not in root.tags:
                    push(doc, comm)
            else:
                cb = partial(doc.callbacks.send_event, event)
                doc.add_next_tick_callback(cb)


class SyncableData(Reactive):
    """
    A baseclass for components which sync one or more data parameters
    with the frontend via a ColumnDataSource.
    """

    selection = param.List(default=[], item_type=int, doc="""
        The currently selected rows in the data.""")

    # Parameters which when changed require an update of the data
    _data_params: ClassVar[list[str]] = []

    _rename: ClassVar[Mapping[str, str | None]] = {'selection': None}

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        self._data = None
        self._processed = None
        callbacks = [self.param.watch(self._validate, self._data_params)]
        if self._data_params:
            callbacks.append(
                self.param.watch(self._update_cds, self._data_params)
            )
        callbacks.append(self.param.watch(self._update_selected, 'selection'))
        self._internal_callbacks += callbacks
        self._validate()
        self._update_cds()

    def _validate(self, *events: param.parameterized.Event) -> None:
        """
        Allows implementing validation for the data parameters.
        """

    def _get_data(self) -> tuple[TData, DataDict]:
        """
        Implemented by subclasses converting data parameter(s) into
        a ColumnDataSource compatible data dictionary.

        Returns
        -------
        processed: object
          Raw data after pre-processing (e.g. after filtering)
        data: dict
          Dictionary of columns used to instantiate and update the
          ColumnDataSource
        """
        raise NotImplementedError()

    def _update_column(self, column: str, array: TDataColumn) -> None:
        """
        Implemented by subclasses converting changes in columns to
        changes in the data parameter.

        Parameters
        ----------
        column: str
          The name of the column to update.
        array: numpy.ndarray
          The array data to update the column with.
        """
        data = getattr(self, self._data_params[0])
        data[column] = array
        if self._processed is not None:
            self._processed[column] = array

    def _update_data(self, data: TData) -> None:
        self.param.update(**{self._data_params[0]: data})

    def _manual_update(
        self, events: tuple[param.parameterized.Event, ...], model: Model,
        doc: Document, root: Model, parent: Model | None, comm: Comm
    ) -> None:
        for event in events:
            if event.type == 'triggered' and self._updating:
                continue
            elif hasattr(self, '_update_' + event.name):
                getattr(self, '_update_' + event.name)(model)

    @updating
    def _update_cds(self, *events: param.parameterized.Event) -> None:
        self._processed, self._data = self._get_data()
        msg = {'data': self._data}
        named_events = {event.name: event for event in events}
        for ref, (m, _) in self._models.copy().items():
            self._apply_update(named_events, msg, m.source, ref)

    @updating
    def _update_selected(
        self, *events: param.parameterized.Event, indices: list[int] | None = None
    ) -> None:
        indices = self.selection if indices is None else indices
        msg = {'indices': indices}
        named_events = {event.name: event for event in events}
        for ref, (m, _) in self._models.copy().items():
            self._apply_update(named_events, msg, m.source.selected, ref)

    def _apply_stream(self, ref: str, model: Model, stream: DataDict, rollover: int | None) -> None:
        self._changing[ref] = ['data']
        try:
            model.source.stream(stream, rollover)
        finally:
            del self._changing[ref]

    @updating
    def _stream(self, stream: DataDict, rollover: int | None = None) -> None:
        self._processed, _ = self._get_data()
        for ref, (m, _) in self._models.copy().items():
            if ref not in state._views or ref in state._fake_roots:
                continue
            viewable, root, doc, comm = state._views[ref]
            if comm or not doc.session_context or state._unblocked(doc):
                with unlocked():
                    m.source.stream(stream, rollover)
                if comm and 'embedded' not in root.tags:
                    push(doc, comm)
            else:
                cb = partial(self._apply_stream, ref, m, stream, rollover)
                with set_curdoc(doc):
                    state.execute(cb, schedule=True)

    def _apply_patch(self, ref: str, model: Model, patch: Patches) -> None:
        self._changing[ref] = ['data']
        try:
            model.source.patch(patch)
        finally:
            del self._changing[ref]

    @updating
    def _patch(self, patch: Patches) -> None:
        for ref, (m, _) in self._models.copy().items():
            if ref not in state._views or ref in state._fake_roots:
                continue
            viewable, root, doc, comm = state._views[ref]
            if comm or not doc.session_context or state._unblocked(doc):
                with unlocked():
                    m.source.patch(patch)
                if comm and 'embedded' not in root.tags:
                    push(doc, comm)
            else:
                cb = partial(self._apply_patch, ref, m, patch)
                with set_curdoc(doc):
                    state.execute(cb, schedule=True)

    def _update_manual(self, *events: param.parameterized.Event) -> None:
        """
        Skip events triggered internally
        """
        processed_events = []
        for e in events:
            if e.name == self._data_params[0] and e.type == 'triggered' and self._updating:
                continue
            processed_events.append(e)
        super()._update_manual(*processed_events)

    def stream(
        self, stream_value: pd.DataFrame | pd.Series | DataDict,
        rollover: int | None = None, reset_index: bool = True
    ) -> None:
        """
        Streams (appends) the `stream_value` provided to the existing
        value in an efficient manner.

        Parameters
        ----------
        stream_value: (pd.DataFrame | pd.Series | Dict)
          The new value(s) to append to the existing value.
        rollover: (int | None, default=None)
           A maximum column size, above which data from the start of
           the column begins to be discarded. If None, then columns
           will continue to grow unbounded.
        reset_index (bool, default=True):
          If True and the stream_value is a DataFrame, then its index
          is reset. Helps to keep the index unique and named `index`.

        Raises
        ------
        ValueError: Raised if the stream_value is not a supported type.

        Examples
        --------

        Stream a Series to a DataFrame
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> obj = DataComponent(value)
        >>> stream_value = pd.Series({"x": 4, "y": "d"})
        >>> obj.stream(stream_value)
        >>> obj.value.to_dict("list")
        {'x': [1, 2, 4], 'y': ['a', 'b', 'd']}

        Stream a Dataframe to a Dataframe
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> obj = DataComponent(value)
        >>> stream_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})
        >>> obj.stream(stream_value)
        >>> obj.value.to_dict("list")
        {'x': [1, 2, 3, 4], 'y': ['a', 'b', 'c', 'd']}

        Stream a Dictionary row to a DataFrame
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> tabulator = DataComponent(value)
        >>> stream_value = {"x": 4, "y": "d"}
        >>> obj.stream(stream_value)
        >>> obj.value.to_dict("list")
        {'x': [1, 2, 4], 'y': ['a', 'b', 'd']}

        Stream a Dictionary of Columns to a Dataframe
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> obj = DataComponent(value)
        >>> stream_value = {"x": [3, 4], "y": ["c", "d"]}
        >>> obj.stream(stream_value)
        >>> obj.value.to_dict("list")
        {'x': [1, 2, 3, 4], 'y': ['a', 'b', 'c', 'd']}
        """
        if 'pandas' in sys.modules:
            import pandas as pd
        else:
            pd = None # type: ignore
        if pd and isinstance(stream_value, pd.DataFrame):
            if isinstance(self._processed, dict):
                self.stream(stream_value.to_dict(), rollover)  # type: ignore
                return
            if reset_index:
                value_index_start = self._processed.index.max() + 1
                stream_value = stream_value.reset_index(drop=True)
                stream_value.index += value_index_start
            combined = pd.concat([self._processed, stream_value])
            if rollover is not None:
                combined = combined.iloc[-rollover:]
            with param.discard_events(self):
                self._update_data(combined)
            try:
                self._updating = True
                self.param.trigger(self._data_params[0])
            finally:
                self._updating = False
            self._stream(stream_value, rollover)
        elif pd and isinstance(stream_value, pd.Series):
            if isinstance(self._processed, dict):
                self.stream({k: [v] for k, v in stream_value.to_dict().items()}, rollover)
                return
            value_index_start = self._processed.index.max() + 1
            self._processed.loc[value_index_start] = stream_value
            with param.discard_events(self):
                self._update_data(self._processed)
            self._stream(self._processed.iloc[-1:], rollover)
        elif isinstance(stream_value, dict):
            if isinstance(self._processed, dict):
                if not all(col in stream_value for col in self._data):
                    raise ValueError("Stream update must append to all columns.")
                for col, array in stream_value.items():
                    concatenated = np.concatenate([self._data[col], array])
                    if rollover is not None:
                        concatenated = concatenated[-rollover:]
                    self._update_column(col, concatenated)
                self._stream(stream_value, rollover)
            else:
                try:
                    stream_value = pd.DataFrame(stream_value)
                except ValueError:
                    stream_value = pd.Series(stream_value)
                self.stream(stream_value)
        else:
            raise ValueError("The stream value provided is not a DataFrame, Series or Dict!")

    def patch(self, patch_value: pd.DataFrame | pd.Series | dict) -> None:
        """
        Efficiently patches (updates) the existing value with the `patch_value`.

        Parameters
        ----------
        patch_value: (pd.DataFrame | pd.Series | Dict)
          The value(s) to patch the existing value with.

        Raises
        ------
        ValueError: Raised if the patch_value is not a supported type.

        Examples
        --------

        Patch a DataFrame with a Dictionary row.
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> obj = DataComponent(value)
        >>> patch_value = {"x": [(0, 3)]}
        >>> obj.patch(patch_value)
        >>> obj.value.to_dict("list")
        {'x': [3, 2], 'y': ['a', 'b']}

        Patch a Dataframe with a Dictionary of Columns.
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> obj = DataComponent(value)
        >>> patch_value = {"x": [(slice(2), (3,4))], "y": [(1,'d')]}
        >>> obj.patch(patch_value)
        >>> obj.value.to_dict("list")
        {'x': [3, 4], 'y': ['a', 'd']}

        Patch a DataFrame with a Series. Please note the index is used in the update.
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> obj = DataComponent(value)
        >>> patch_value = pd.Series({"index": 1, "x": 4, "y": "d"})
        >>> obj.patch(patch_value)
        >>> obj.value.to_dict("list")
        {'x': [1, 4], 'y': ['a', 'd']}

        Patch a Dataframe with a Dataframe. Please note the index is used in the update.
        >>> value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        >>> obj = DataComponent(value)
        >>> patch_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})
        >>> obj.patch(patch_value)
        >>> obj.value.to_dict("list")
        {'x': [3, 4], 'y': ['c', 'd']}
        """
        if self._processed is None or isinstance(patch_value, dict):
            self._patch(patch_value)
            return

        if 'pandas' in sys.modules:
            import pandas as pd
        else:
            pd = None # type: ignore
        data = getattr(self, self._data_params[0])
        patch_value_dict: Patches = {}
        if pd and isinstance(patch_value, pd.DataFrame):
            for column in patch_value.columns:
                patch_value_dict[column] = []
                for index in patch_value.index:
                    patch_value_dict[column].append((index, patch_value.loc[index, column]))
            self.patch(patch_value_dict)
        elif pd and isinstance(patch_value, pd.Series):
            if "index" in patch_value:  # Series orient is row
                patch_value_dict = {
                    str(k): [(int(patch_value["index"]), v)]  # type: ignore
                    for k, v in patch_value.items()
                }
                patch_value_dict.pop("index")
            else:  # Series orient is column
                patch_value_dict = {
                    str(patch_value.name): [
                        (int(index), value)  # type: ignore
                        for index, value in patch_value.items()
                    ]
                }
            self.patch(patch_value_dict)
        elif isinstance(patch_value, dict):
            for k, v in patch_value.items():
                for index, patch  in v:
                    if pd and isinstance(self._processed, pd.DataFrame):
                        data.loc[index, k] = patch
                    else:
                        data[k][index] = patch
            self._updating = True
            try:
                self._patch(patch_value)
            finally:
                self._updating = False
        else:
            raise ValueError(
                f"Patching with a patch_value of type {type(patch_value).__name__} "
                "is not supported. Please provide a DataFrame, Series or Dict."
            )


class ReactiveData(SyncableData):
    """
    An extension of SyncableData which bi-directionally syncs a data
    parameter between frontend and backend using a ColumnDataSource.
    """

    __abstract = True

    def _update_selection(self, indices: list[int]) -> None:
        self.selection = indices

    def _convert_column(
        self, values: np.ndarray, old_values: TDataColumn
    ) -> TDataColumn:
        dtype = getattr(old_values, 'dtype', np.dtype('O'))
        converted: TDataColumn | None = None
        if dtype.kind == 'M':
            if values.dtype.kind in 'if':
                tz = getattr(dtype, 'tz', None)
                if tz:
                    import pandas as pd

                    # Using pandas to convert from milliseconds
                    # timezone-aware, to UTC nanoseconds, to datetime64.
                    converted = (
                        pd.Series(pd.to_datetime(values, unit="ms"))
                        .dt.tz_localize(tz)
                    )
                else:
                    # Timestamps converted from milliseconds to nanoseconds,
                    # to datetime.
                    converted = (values * 1e6).astype(dtype)  # type: ignore
        elif dtype.kind == 'O':
            if (all(isinstance(ov, dt.date) for ov in old_values) and
                not all(isinstance(iv, dt.date) for iv in values)):
                new_values = []
                for iv in values:
                    if isinstance(iv, dt.datetime):
                        iv = iv.date()
                    elif not isinstance(iv, dt.date):
                        iv = dt.date.fromtimestamp(iv/1000)
                    new_values.append(iv)
                converted = new_values
        elif 'pandas' in sys.modules:
            import pandas as pd
            tmp_values: np.ndarray | list[Any] | pd.api.extensions.ExtensionArray = values
            if Version(pd.__version__) >= Version('1.1.0'):
                from pandas.core.arrays.masked import BaseMaskedDtype
                if isinstance(dtype, BaseMaskedDtype):
                    tmp_values = [
                        dtype.na_value if v == '<NA>' else v for v in values
                    ]
            converted = pd.Series(tmp_values).astype(dtype).values
        else:
            converted = values.astype(dtype)  # type: ignore
        return values if converted is None else converted

    def _process_data(self, data: Mapping[str, list | dict[int, Any] | np.ndarray]) -> None:
        if self._updating:
            return
        # Get old data to compare to
        old_raw, old_data = self._get_data()
        old_raw = old_raw.copy()
        if hasattr(old_raw, 'columns'):
            columns = list(old_raw.columns) # type: ignore
        else:
            columns = list(old_raw)

        updated = False
        for col, values in data.items():
            col = self._renamed_cols.get(col, col)
            if col in self.indexes or col not in columns:
                continue
            if isinstance(values, dict):
                sorted_values = sorted(values.items(), key=lambda it: int(it[0]))
                values = [v for _, v in sorted_values]
            converted = self._convert_column(np.asarray(values), old_raw[col])

            isequal = None
            if hasattr(old_raw, 'columns') and isinstance(converted, np.ndarray):
                try:
                    isequal = np.array_equal(old_raw[col], converted, equal_nan=True)
                except Exception:
                    pass
            if isequal is None:
                try:
                    isequal = (old_raw[col] == converted).all() # type: ignore
                except Exception:
                    isequal = False
            if not isequal:
                self._update_column(col, converted)
                updated = True

        # If no columns were updated we don't have to sync data
        if not updated:
            return

        # Ensure we trigger events
        self._updating = True
        old_data = getattr(self, self._data_params[0])
        try:
            if old_data is self.value: # type: ignore
                with _syncing(self, ['value']):
                    with param.discard_events(self):
                        self.value = old_raw
                    self.value = old_data
            else:
                self.param.trigger('value')
        finally:
            self._updating = False
        # Ensure that if the data was changed in a user
        # callback, we still send the updated data
        if old_data is not self.value:
            self._update_cds()

    def _process_events(self, events: dict[str, Any]) -> None:
        if 'data' in events:
            self._process_data(events.pop('data'))
        if 'indices' in events:
            self._updating = True
            try:
                self._update_selection(events.pop('indices'))
            finally:
                self._updating = False
        super()._process_events(events)  # noqa


class ReactiveMetaBase(ParameterizedMetaclass):

    _loaded_extensions: ClassVar[set[str]] = set()

    _name_counter: ClassVar[Counter] = Counter()


class ReactiveHTMLMetaclass(ReactiveMetaBase):
    """
    Parses the ReactiveHTML._template of the class and initializes
    variables, callbacks and the data model to sync the parameters and
    HTML attributes.
    """

    _script_regex: ClassVar[str] = r"script\([\"|'](.*)[\"|']\)"

    def __init__(mcs, name: str, bases: tuple[type, ...], dict_: Mapping[str, Any]):
        from .io.datamodel import PARAM_MAPPING, construct_data_model

        mcs.__original_doc__ = mcs.__doc__
        ParameterizedMetaclass.__init__(mcs, name, bases, dict_)
        cls_name = mcs.__name__

        # Validate _child_config
        for name, child_type in mcs._child_config.items():
            if name not in mcs.param:
                raise ValueError(
                    f"{cls_name}._child_config for {name!r} does not "
                    "match any parameters. Ensure the name of each "
                    "child config matches one of the parameters."
                )
            elif child_type not in ('model', 'template', 'literal'):
                raise ValueError(
                    f"{cls_name}._child_config for {name!r} child "
                    "parameter declares unknown type {child_type!r}. "
                    f"The '_child_config' mode must be one of 'model', "
                    "'template' or 'literal'."
                )

        mcs._parser = ReactiveHTMLParser(mcs)
        mcs._parser.feed(mcs._template)

        # Ensure syntactically valid jinja2 for loops
        if mcs._parser._open_for:
            raise ValueError(
                f"{cls_name}._template contains for loop without closing {{% endfor %}} statement."
            )

        # Ensure there are no open tags
        if mcs._parser._node_stack:
            raise ValueError(
                f"{cls_name}._template contains tags which were never "
                "closed. Ensure all tags in your template have a "
                "matching closing tag, e.g. if there is a tag <div>, "
                "ensure there is a matching </div> tag."
            )

        mcs._node_callbacks: dict[str, list[tuple[str, str]]]  = {}
        mcs._inline_callbacks = []
        for node, attrs in mcs._parser.attrs.items():
            for (attr, parameters, _template) in attrs:
                for p in parameters:
                    if p in mcs.param or '.' in p:
                        continue
                    if re.match(mcs._script_regex, p):
                        name = re.findall(mcs._script_regex, p)[0]
                        if name not in mcs._scripts:
                            raise ValueError(
                                f"{cls_name}._template inline callback "
                                f"references unknown script {name!r}, "
                                "ensure the referenced script is declared"
                                "in the _scripts dictionary."
                            )
                        if node not in mcs._node_callbacks:
                            mcs._node_callbacks[node] = []
                        mcs._node_callbacks[node].append((attr, p))
                    elif hasattr(mcs, p):
                        if node not in mcs._node_callbacks:
                            mcs._node_callbacks[node] = []
                        mcs._node_callbacks[node].append((attr, p))
                        mcs._inline_callbacks.append((node, attr, p))
                    else:
                        matches = difflib.get_close_matches(p, dir(mcs))
                        raise ValueError(
                            f"{cls_name}._template references unknown "
                            f"parameter or method '{p}', similar parameters "
                            f"and methods include {matches}."
                        )

        ignored = list(Reactive.param)
        types = {}
        for child in mcs._parser.children.values():
            cparam = mcs.param[child]
            if mcs._child_config.get(child) == 'literal':
                types[child] = param.String
            elif (type(cparam) not in PARAM_MAPPING or
                  isinstance(cparam, (param.List, param.Dict, param.Tuple)) or
                  (isinstance(cparam, param.ClassSelector) and
                   isinstance(cparam.class_, type) and
                   (not issubclass(cparam.class_, param.Parameterized) or
                    issubclass(cparam.class_, Reactive)))):
                # Any parameter which can be consistently serialized
                # (except) Panel Reactive objects can be reflected
                # on the data model
                ignored.append(child)
        ignored.remove('name')

        # Create model with unique name
        ReactiveHTMLMetaclass._name_counter[name] += 1
        model_name = f'{name}{ReactiveHTMLMetaclass._name_counter[name]}'

        mcs._data_model = construct_data_model(
            mcs, name=model_name, ignore=ignored, types=types
        )


class ReactiveCustomBase(Reactive):

    _extension_name: ClassVar[str | None] = None

    __css__: ClassVar[list[str] | None] = None
    __javascript__: ClassVar[list[str] | None] = None
    __javascript_modules__: ClassVar[list[str] | None] = None

    @classmethod
    def _loaded(cls) -> bool:
        """
        Whether the component has been loaded.
        """
        return (
            cls._extension_name is None or
            (cls._extension_name in ReactiveMetaBase._loaded_extensions and
             (state._extensions is None or (cls._extension_name in state._extensions)))
        )

    def _process_param_change(self, params):
        props = super()._process_param_change(params)
        if 'stylesheets' in params:
            css = getattr(self, '__css__', []) or []
            if state.rel_path:
                css = [
                    ss if ss.startswith('http') else f'{state.rel_path}/{ss}'
                    for ss in css
                ]
            props['stylesheets'] = [
                ImportedStyleSheet(url=ss) for ss in css if ss
            ] + props['stylesheets']
        return props

    @classmethod
    def _patch_datamodel_ref(cls, props, ref):
        """
        Ensure all DataModels have reference to the root model to ensure
        that they can be cleaned up correctly.
        """
        ref_str = f"__ref:{ref}"
        for m in props.select({'type': DataModel}):
            if ref_str not in m.tags:
                m.tags.append(ref_str)

    def _set_on_model(self, msg: Mapping[str, Any], root: Model, model: Model) -> list[str]:
        if not msg:
            return []
        prev_changing = self._changing.get(root.ref['id'], [])
        changing = []
        transformed = {}
        for attr, value in msg.items():
            prop = model.lookup(attr).property
            old = getattr(model, attr)
            try:
                matches = bool(prop.matches(old, value))
            except Exception:
                for tp, converter in prop.alternatives:
                    if tp.is_valid(value):
                        value = converter(value)
                        break
                try:
                    matches = bool(prop.matches(old, value))
                except Exception:
                    matches = False
            if not matches:
                transformed[attr] = value
                changing.append(attr)
        self._changing[root.ref['id']] = changing
        try:
            model.update(**transformed)
        finally:
            if prev_changing:
                self._changing[root.ref['id']] = prev_changing
            else:
                del self._changing[root.ref['id']]
        if isinstance(model, DataModel):
            self._patch_datamodel_ref(model, root.ref['id'])
        return changing


class ReactiveHTML(ReactiveCustomBase, metaclass=ReactiveHTMLMetaclass):
    """
    The ReactiveHTML class enables you to create custom Panel components using HTML, CSS and/ or
    Javascript and without the complexities of Javascript build tools.

    A `ReactiveHTML` subclass provides bi-directional syncing of its parameters with arbitrary HTML
    elements, attributes and properties. The key part of the subclass is the `_template`
    variable. This is the HTML template that gets rendered and declares how to link parameters on the
    subclass to HTML.

    >>>    import panel as pn
    >>>    import param
    >>>    class CustomComponent(pn.reactive.ReactiveHTML):
    ...
    ...        index = param.Integer(default=0)
    ...
    ...        _template = '<img id="slideshow" src="https://picsum.photos/800/300?image=${index}" onclick="${_img_click}"></img>'
    ...
    ...        def _img_click(self, event):
    ...            self.index += 1
    >>>    CustomComponent(width=500, height=200).servable()

    HTML templates
    ~~~~~~~~~~~~~~

    A ReactiveHTML component is declared by providing an HTML template
    on the `_template` attribute on the class. Parameters are synced by
    inserting them as template variables of the form `${parameter_name}`,
    e.g.:

        <div class="${parameter_1}">${parameter_2}</div>

    will interpolate the parameter1 parameter on the class.
    In addition to providing attributes we can also provide children to an HTML
    tag. By default any parameter referenced as a child will be
    treated as a Panel components to be rendered into the containing
    HTML. This makes it possible to use ReactiveHTML to lay out other
    components.

    Children
    ~~~~~~~~

    As mentioned above parameters may be referenced as children of a
    DOM node and will, by default, be treated as Panel components to
    insert on the DOM node. However by declaring a `_child_config` we
    can control how the DOM nodes are treated. The `_child_config` is
    indexed by parameter name and may declare one of three rendering
    modes:

      - model (default): Create child and render child as a Panel
        component into it.
      - literal: Create child and set child as its innerHTML.
      - template: Set child as innerHTML of the container.

    If the type is 'template' the parameter will be inserted as is and
    the DOM node's innerHTML will be synced with the child parameter.

    DOM Events
    ~~~~~~~~~~

    In certain cases it is necessary to explicitly declare event
    listeners on the DOM node to ensure that changes in their
    properties are synced when an event is fired. To make this possible
    the HTML element in question must be given a unique id, e.g.:

        <input id="input_el"></input>

    Now we can use this name to declare set of `_dom_events` to
    subscribe to. The following will subscribe to change DOM events
    on the input element:

       {'input_el': ['change']}

    Once subscribed the class may also define a method following the
    `_{node}_{event}` naming convention which will fire when the DOM
    event triggers, e.g. we could define a `_input_el_change` method.
    Any such callback will be given a DOMEvent object as the first and
    only argument. The DOMEvent contains information about the event
    on the .data attribute and declares the type of event on the .type
    attribute.

    Inline callbacks
    ~~~~~~~~~~~~~~~~

    Instead of declaring explicit DOM events Python callbacks can also
    be declared inline, e.g.:

        <input id="input_el" onchange="${_input_change}"></input>

    will look for an `_input_change` method on the ReactiveHTML
    component and call it when the event is fired.

    Additionally we can invoke pure JS scripts defined on the class, e.g.:

        <input id="input_el" onchange="${script('some_script')}"></input>

    This will invoke the following script if it is defined on the class:

        _scripts = {
            'some_script': 'console.log(model, data, input_el, view)'
       }

    Scripts
    ~~~~~~~

    In addition to declaring callbacks in Python it is also possible
    to declare Javascript callbacks to execute when any synced
    attribute changes. Let us say we have declared an input element
    with a synced value parameter:

        <input id="input_el" value="${value}"></input>

    We can now declare a set of `_scripts`, which will fire whenever
    the value updates:

        _scripts = {
            'value': 'console.log(model, data, input_el)'
       }

    The Javascript is provided multiple objects in its namespace
    including:

      * data :  The data model holds the current values of the synced
                parameters, e.g. data.value will reflect the current
                value of the `input_el` node.
      * model:  The ReactiveHTML model which holds layout information
                and information about the children and events.
      * state:  An empty state dictionary which scripts can use to
                store state for the lifetime of the view.
      * view:   The Bokeh View class responsible for rendering the
                component. This provides access to method like
                `invalidate_layout` and `run_script` which allows
                invoking other scripts.
      * <node>: All named DOM nodes in the HTML template, e.g. the
                `input_el` node in the example above.
    """

    _child_config: ClassVar[Mapping[str, str]] = {}

    _dom_events: ClassVar[Mapping[str, list[str]]] = {}

    _template: ClassVar[str] = ""

    _scripts: ClassVar[Mapping[str, str | list[str]]] = {}

    _script_assignment: ClassVar[str] = (
        r'data\.([^[^\d\W]\w*)[ ]*[\+,\-,\*,\\,%,\*\*,<<,>>,>>>,&,\^,|,\&\&,\|\|,\?\?]*='
    )

    __abstract = True

    def __init__(self, **params):
        from .pane import panel
        cls = type(self)
        for children_param in self._parser.children.values():
            mode = self._child_config.get(children_param, 'model')
            if children_param not in params or mode != 'model':
                continue
            child_value = params[children_param]
            if isinstance(child_value, list):
                children = []
                for pane in child_value:
                    if isinstance(pane, tuple):
                        name, pane = pane
                        children.append((name, panel(pane)))
                    else:
                        children.append(panel(pane))
                params[children_param] = children
            elif isinstance(child_value, dict):
                children = {}
                for key, pane in child_value.items():
                    children[key] = panel(pane)
                params[children_param] = children
            else:
                params[children_param] = children = panel(child_value)
            child_param = cls.param[children_param]
            try:
                if children_param not in self._param__private.explicit_no_refs:
                    children = resolve_value(children)
                if not ((isinstance(child_param, Children) and isinstance(children, list)) or
                        (isinstance(child_param, Child))):
                    child_param._validate(children)
            except Exception as e:
                raise RuntimeError(
                    f"{cls.__name__}._template declares {children_param!r} "
                    "parameter as a child, however the parameter is of type "
                    f"{type(child_param).__name__}. Either ensure that the parameter "
                    "can accept a Panel component, use literal template using the "
                    "Jinja2 templating syntax (i.e. {{ <param> }}) or declare the "
                    "child as a literal in the _child_config."
                ) from e
        super().__init__(**params)
        self._attrs = {}
        self._panes = {}
        self._event_callbacks = defaultdict(lambda: defaultdict(list))

    def _cleanup(self, root: Model | None = None) -> None:
        for _child, panes in self._panes.items():
            for pane in panes:
                pane._cleanup(root)
        super()._cleanup(root)

    @property
    def _linkable_params(self) -> list[str]:
        return [
            p for p in super()._linkable_params if p not in self._parser.children.values() and
            p not in ('loading')]

    @property
    def _child_names(self):
        return {}

    def _process_children(
        self, doc: Document, root: Model, model: Model, comm: Comm | None,
        children: dict[str, list[Model]]
    ) -> dict[str, list[Model]]:
        return children

    def _process_param_change(self, params):
        props = super()._process_param_change(params)
        if 'stylesheets' in params:
            css = getattr(self, '__css__', []) or []
            if state.rel_path:
                css = [
                    ss if ss.startswith('http') else f'{state.rel_path}/{ss}'
                    for ss in css
                ]
            props['stylesheets'] = [
                ImportedStyleSheet(url=ss) for ss in css if ss
            ] + props['stylesheets']
        return props

    def _init_params(self) -> dict[str, Any]:
        ignored = list(Reactive.param)
        for child in self._parser.children.values():
            if self._child_config.get(child) != 'literal':
                ignored.append(child)
        params = {
            p : getattr(self, p) for p in list(Layoutable.param)
            if getattr(self, p) is not None and p != 'name'
        }
        data_params, event_params = {}, []
        for k, v in self.param.values().items():
            pobj = self.param[k]
            if (
                (k in ignored and k != 'name') or
                ((pobj.precedence or 0) < 0) or
                (isinstance(v, Viewable) and not isinstance(pobj, param.ClassSelector))
            ):
                continue
            if isinstance(v, str):
                v = HTML_SANITIZER.clean(v)
            data_params[k] = v
            if isinstance(pobj, param.Event):
                event_params.append(k)
        html, nodes, self._attrs = self._get_template()
        params.update({
            'attrs': self._attrs,
            'callbacks': self._node_callbacks,
            'data': self._data_model(**self._process_param_change(data_params)),
            'events': self._get_events(),
            'event_params': event_params,
            'html': escape(textwrap.dedent(html)),
            'nodes': nodes,
            'looped': [node for node, _ in self._parser.looped],
            'scripts': {}
        })
        for trigger, scripts in self._scripts.items():
            if not isinstance(scripts, list):
                scripts = [scripts]
            params['scripts'][trigger] = [
                escape(textwrap.dedent(script).strip()) for script in scripts
            ]
        return params

    def _get_events(self) -> dict[str, dict[str, bool]]:
        events = {}
        for node, dom_events in self._dom_events.items():
            if isinstance(dom_events, list):
                events[node] = {e: True for e in dom_events}
            else:
                events[node] = dom_events
        for node, evs in self._event_callbacks.items():
            events[node] = node_events = events.get(node, {})
            for e in evs:
                if e not in node_events:
                    node_events[e] = False
        return events

    def _get_children(
        self, doc: Document, root: Model, model: Model, comm: Comm | None
    ) -> dict[str, list[Model]]:
        from .pane import panel
        old_models = model.children
        new_models: dict[str, list[Model]] = {parent: [] for parent in self._parser.children}
        new_panes: dict[str, list[Viewable] | dict[str, Viewable] | None] = {}
        internal_panes: dict[str, list[Viewable] | None] = {}

        for parent, children_param in self._parser.children.items():
            mode = self._child_config.get(children_param, 'model')
            if mode == 'literal':
                new_panes[parent] = None
                continue
            panes = getattr(self, children_param)
            if isinstance(panes, dict):
                for key, value in panes.items():
                    panes[key] = panel(value)
            elif isinstance(panes, list):
                for i, pane in enumerate(panes):
                    panes[i] = panel(pane)
            else:
                panes = [panel(panes)]
            new_panes[parent] = panes
            if isinstance(panes, dict):
                panes = list(panes.values())
            internal_panes[children_param] = panes

        for children_param, old_panes in self._panes.items():
            for old_pane in old_panes:
                if old_pane not in (internal_panes.get(children_param) or []):
                    old_pane._cleanup(root)

        for parent, child_panes in new_panes.items():
            children_param = self._parser.children[parent]
            if isinstance(child_panes, dict):
                child_panes = list(child_panes.values())
            mode = self._child_config.get(children_param, 'model')
            if mode == 'literal' or child_panes is None:
                new_models[parent] = children_param
            elif children_param in self._panes:
                # Find existing models
                old_panes = self._panes[children_param]
                for pane in child_panes:
                    if pane in old_panes and root.ref['id'] in pane._models:
                        child, _ = pane._models[root.ref['id']]
                    else:
                        child = pane._get_model(doc, root, model, comm)
                    new_models[parent].append(child)
            elif parent in old_models:
                # Children parameter unchanged
                new_models[parent] = old_models[parent]
            else:
                new_models[parent] = [
                    pane._get_model(doc, root, model, comm)
                    for pane in child_panes
                ]
        self._panes = internal_panes
        return self._process_children(doc, root, model, comm, new_models)

    def _get_template(self) -> tuple[str, list[str], Mapping[str, list[tuple[str, list[str], str]]]]:
        # Replace loop variables with indexed child parameter e.g.:
        #   {% for obj in objects %}
        #     ${obj}
        #   {% endfor %}
        # becomes:
        #   {% for obj in objects %}
        #     ${objects[{{ loop.index0 }}]}
        #  {% endfor %}
        template_string = self._template
        for parent_var, obj in self._parser.loop_map.items():
            for var in self._parser.loop_var_map[parent_var]:
                template_string = template_string.replace(
                    '${%s}' % var, '${%s[{{ loop.index0 }}]}' % obj)  # noqa: UP031

        # Add index to templated loop node ids
        for dom_node, _ in self._parser.looped:
            replacement = 'id="%s-{{ loop.index0 }}"' % dom_node  # noqa: UP031
            if f'id="{dom_node}"' in template_string:
                template_string = template_string.replace(
                    f'id="{dom_node}"', replacement)
            else:
                template_string = template_string.replace(
                    f"id='{dom_node}'", replacement)

        # Render Jinja template
        template = jinja2.Template(template_string)
        context = {'param': self.param, '__doc__': self.__original_doc__, 'id': id}
        for parameter, value in self.param.values().items():
            context[parameter] = value
            if parameter in self._child_names:
                context[f'{parameter}_names'] = self._child_names[parameter]
        try:
            html = template.render(context)
        except Exception as e:
            raise RuntimeError(
                f"{type(self).__name__} could not render "
                f"template, errored with:\n\n{type(e).__name__}: {e}.\n"
                f"Full template:\n\n{template_string}"
            ) from e

        # Parse templated HTML
        parser = ReactiveHTMLParser(self.__class__, template=False)
        parser.feed(html)

        # Add node ids to all parsed nodes
        for name in list(parser.nodes):
            html = (
                html
                .replace(f"id='{name}'", f"id='{name}-${{id}}'")
                .replace(f'id="{name}"', f'id="{name}-${{id}}"')
            )

        # Parse attrs
        p_attrs: dict[str, list[tuple[str, list[str], str]]] = {}
        for node, attrs in parser.attrs.items():
            for (attr, parameters, tmpl) in attrs:
                param_attrs = []
                for p in parameters:
                    if p in self.param or '.' in p:
                        param_attrs.append(p)
                if node not in p_attrs:
                    p_attrs[node] = []
                p_attrs[node].append((attr, param_attrs, tmpl))

        # Remove child node template syntax
        for parent, child_name in self._parser.children.items():
            if (parent, child_name) in self._parser.looped:
                for i, _ in enumerate(getattr(self, child_name)):
                    html = html.replace(f'${{{child_name}[{i}]}}', '')
            else:
                html = html.replace(f'${{{child_name}}}', '')
        return html, parser.nodes, p_attrs

    @property
    def _linked_properties(self) -> tuple[str, ...]:
        linked_properties = [p for pss in self._attrs.values() for _, ps, _ in pss for p in ps]
        for scripts in self._scripts.values():
            if not isinstance(scripts, list):
                scripts = [scripts]
            for script in scripts:
                for p in re.findall(self._script_assignment, script):
                    if p not in linked_properties:
                        linked_properties.append(p)
        for children_param in self._parser.children.values():
            if children_param in self._data_model.properties():
                linked_properties.append(children_param)
        return tuple(linked_properties)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = _BkReactiveHTML(**self._get_properties(doc))
        if comm and not self._loaded():
            self.param.warning(
                f'{type(self).__name__} was not imported on instantiation and may not '
                'render in a notebook. Restart the notebook kernel and '
                'ensure you load it as part of the extension using:'
                f'\n\npn.extension(\'{self._extension_name}\')\n'
            )
        elif root is not None and not self._loaded() and root.ref['id'] in state._views:
            self.param.warning(
                f'{type(self).__name__} was not imported on instantiation may not '
                'render in the served application. Ensure you add the '
                'following to the top of your application:'
                f'\n\npn.extension(\'{self._extension_name}\')\n'
            )
        if self._extension_name:
            ReactiveMetaBase._loaded_extensions.add(self._extension_name)

        if not root:
            root = model

        ref = root.ref['id']
        data_model: DataModel = model.data # type: ignore
        self._patch_datamodel_ref(data_model, ref)
        model.update(children=self._get_children(doc, root, model, comm))
        self._register_events('dom_event', model=model, doc=doc, comm=comm)
        self._link_props(data_model, self._linked_properties, doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _process_event(self, event: Event) -> None:
        if not isinstance(event, DOMEvent):
            return
        cb = getattr(self, f"_{event.node}_{event.data['type']}", None)
        if cb is not None:
            cb(event)
        event_type = event.data['type']
        star_cbs = self._event_callbacks.get('*', {})
        node_cbs = self._event_callbacks.get(event.node, {})

        def match(node, pattern):
            return re.findall(re.sub(r'\{\{.*loop.index.*\}\}', r'\\d+', pattern), node)

        inline_cbs = {attr: [getattr(self, p)] for node, attr, p in self._inline_callbacks
                      if node == event.node or match(event.node, node)}
        event_cbs = (
            node_cbs.get(event_type, []) + node_cbs.get('*', []) +
            star_cbs.get(event_type, []) + star_cbs.get('*', []) +
            inline_cbs.get(event_type, [])
        )
        for cb in event_cbs:
            cb(event)

    def _update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Comm | None
    ) -> None:
        child_params = self._parser.children.values()
        new_children, model_msg, data_msg  = {}, {}, {}
        for prop, v in list(msg.items()):
            if prop in child_params:
                new_children[prop] = prop
                if self._child_config.get(prop) == 'literal':
                    data_msg[prop] = HTML_SANITIZER.clean(v)
                elif prop in model.data.properties():
                    data_msg[prop] = v
            elif prop in list(Reactive.param)+['events']:
                model_msg[prop] = v
            elif (
                (prop in self.param) and (
                    ((self.param[prop].precedence or 0) < 0) or
                    (isinstance(v, Viewable) and not isinstance(self.param[prop], param.ClassSelector))
                )
            ):
                continue
            elif isinstance(v, list) and all(isinstance(vs, param.Parameterized) for vs in v):
                from .io.datamodel import create_linked_datamodel
                old = getattr(model.data, prop)
                if isinstance(old, list):
                    mapping = {getattr(o, "name", o): o for o in old}
                    vals = []
                    for vs in v:
                        if (vname:=f"{root.ref['id']}-{id(vs)}") in mapping:
                            vals.append(mapping[vname])
                        else:
                            vals.append(create_linked_datamodel(vs, root))
                    v = vals
                data_msg[prop] = v
            elif isinstance(v, param.Parameterized):
                from .io.datamodel import create_linked_datamodel
                old = getattr(model.data, prop)
                if old.name == f"{root.ref['id']}-{id(v)}":
                    v = old
                else:
                    v = create_linked_datamodel(v, root)
                data_msg[prop] = v
            elif isinstance(v, str):
                data_msg[prop] = HTML_SANITIZER.clean(v)
            else:
                data_msg[prop] = v
        if new_children:
            if self._parser.looped:
                html, nodes, self._attrs = self._get_template()
                model_msg['attrs'] = self._attrs
                model_msg['nodes'] = nodes
                model_msg['html'] = escape(textwrap.dedent(html))
            children = self._get_children(doc, root, model, comm)
        else:
            children = None
        if children is not None:
            model_msg['children'] = children
        self._set_on_model(model_msg, root, model)
        self._set_on_model(data_msg, root, model.data)
        reset = {p: False for p in data_msg if p in model.event_params}
        if reset:
            self._set_on_model(reset, root, model.data)

    def on_event(self, node: str, event: str, callback: Callable) -> None:
        """
        Registers a callback to be executed when the specified DOM
        event is triggered on the named node. Note that the named node
        must be declared in the HTML. To create a named node you must
        give it an id of the form `id="name"`, where `name` will
        be the node identifier.

        Parameters
        ----------
        node: str
          Named node in the HTML identifiable via id of the form `id="name"`.
        event: str
          Name of the DOM event to add an event listener to.
        callback: callable
          A callable which will be given the DOMEvent object.
        """
        if node not in self._parser.nodes and node != '*':
            raise ValueError(f"Named node '{node}' not found. Available "
                             f"nodes include: {self._parser.nodes}.")
        self._event_callbacks[node][event].append(callback)
        events = self._get_events()
        for ref, (model, _) in self._models.copy().items():
            self._apply_update({}, {'events': events}, model, ref)

__all__ = (
    "Reactive",
    "ReactiveHTML",
    "ReactiveData"
)
