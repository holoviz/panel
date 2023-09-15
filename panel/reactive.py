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
import re
import sys
import textwrap
import types

from collections import Counter, defaultdict, namedtuple
from functools import lru_cache, partial
from pprint import pformat
from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Dict, Generator, List, Mapping,
    Optional, Set, Tuple, Type, Union,
)

import numpy as np
import param

from bokeh.core.property.descriptors import UnsetValueError
from bokeh.model import DataModel
from bokeh.models import ImportedStyleSheet
from packaging.version import Version
from param.parameterized import ParameterizedMetaclass, Watcher

from .io.document import unlocked
from .io.model import hold
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
    BOKEH_JS_NAT, HTML_SANITIZER, classproperty, edit_readonly, escape,
    eval_function, extract_dependencies, updating,
)
from .viewable import Layoutable, Renderable, Viewable

if TYPE_CHECKING:
    import pandas as pd

    from bokeh.document import Document
    from bokeh.events import Event
    from bokeh.model import Model
    from bokeh.models.sources import DataDict, Patches
    from pyviz_comms import Comm

    from .layout.base import Panel
    from .links import Callback, JSLinkTarget, Link

log = logging.getLogger('panel.reactive')

_fields = tuple(Watcher._fields+('target', 'links', 'transformed', 'bidirectional_watcher'))
LinkWatcher: Tuple = namedtuple("Watcher", _fields) # type: ignore


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
    _priority_changes: ClassVar[List[str]] = []

    # Any parameters that require manual updates handling for the models
    # e.g. parameters which affect some sub-model
    _manual_params: ClassVar[List[str]] = []

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
    _stylesheets: ClassVar[List[str]] = []

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

        # Sets up watchers to process manual updates to models
        if self._manual_params:
            self._internal_callbacks.append(
                self.param.watch(self._update_manual, self._manual_params)
            )

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    @classproperty
    @lru_cache(maxsize=None)
    def _property_mapping(cls):
        rename = {}
        for scls in cls.__mro__[::-1]:
            if issubclass(scls, Syncable):
                rename.update(scls._rename)
        return rename

    @property
    def _linked_properties(self) -> Tuple[str]:
        return tuple(
            self._property_mapping.get(p, p) for p in self.param
            if p not in Viewable.param and self._property_mapping.get(p, p) is not None
        )

    def _get_properties(self, doc: Document) -> Dict[str, Any]:
        return self._process_param_change(self._init_params())

    def _process_property_change(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform bokeh model property changes into parameter updates.
        Should be overridden to provide appropriate mapping between
        parameter value and bokeh model change. By default uses the
        _rename class level attribute to map between parameter and
        property names.
        """
        inverted = {v: k for k, v in self._property_mapping.items()}
        return {inverted.get(k, k): v for k, v in msg.items()}

    def _process_param_change(self, msg: Dict[str, Any]) -> Dict[str, Any]:
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
            for stylesheet in stylesheets:
                if isinstance(stylesheet, str) and stylesheet.endswith('.css'):
                    stylesheet = ImportedStyleSheet(url=stylesheet)
                wrapped.append(stylesheet)
            properties['stylesheets'] = wrapped
        return properties

    @property
    def _linkable_params(self) -> List[str]:
        """
        Parameters that can be linked in JavaScript via source transforms.
        """
        return [
            p for p in self._synced_params if self._rename.get(p, False) is not None
            and self._source_transforms.get(p, False) is not None and
            p not in ('design', 'stylesheets')
        ]

    @property
    def _synced_params(self) -> List[str]:
        """
        Parameters which are synced with properties using transforms
        applied in the _process_param_change method.
        """
        ignored = ['default_layout', 'loading', 'background']
        return [p for p in self.param if p not in self._manual_params+ignored]

    def _init_params(self) -> Dict[str, Any]:
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
        self, model: Model, properties: List[str] | List[Tuple[str, str]],
        doc: Document, root: Model, comm: Optional[Comm] = None
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
                *subpath, p = p.split('.')
                for sp in subpath:
                    m = getattr(m, sp)
            else:
                subpath = None
            if comm:
                m.on_change(p, partial(self._comm_change, doc, ref, comm, subpath))
            else:
                m.on_change(p, partial(self._server_change, doc, ref, subpath))

    def _manual_update(
        self, events: Tuple[param.parameterized.Event, ...], model: Model, doc: Document,
        root: Model, parent: Optional[Model], comm: Optional[Comm]
    ) -> None:
        """
        Method for handling any manual update events, i.e. events triggered
        by changes in the manual params.
        """

    def _update_manual(self, *events: param.parameterized.Event) -> None:
        for ref, (model, parent) in self._models.items():
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
                    doc.add_next_tick_callback(cb)
                else:
                    cb()

    def _apply_update(
        self, events: Dict[str, param.parameterized.Event], msg: Dict[str, Any],
        model: Model, ref: str
    ) -> None:
        if ref not in state._views or ref in state._fake_roots:
            return
        viewable, root, doc, comm = state._views[ref]
        if comm or not doc.session_context or state._unblocked(doc):
            with unlocked():
                self._update_model(events, msg, root, model, doc, comm)
            if comm and 'embedded' not in root.tags:
                push(doc, comm)
        else:
            cb = partial(self._update_model, events, msg, root, model, doc, comm)
            doc.add_next_tick_callback(cb)

    def _update_model(
        self, events: Dict[str, param.parameterized.Event], msg: Dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Optional[Comm]
    ) -> None:
        ref = root.ref['id']
        self._changing[ref] = attrs = []
        for attr, value in msg.items():
            # Bokeh raises UnsetValueError if the value is Undefined.
            try:
                model_val = getattr(model, attr)
            except UnsetValueError:
                attrs.append(attr)
                continue
            if not model.lookup(attr).property.matches(model_val, value):
                attrs.append(attr)

            # Do not apply model change that is in flight
            if attr in self._events:
                del self._events[attr]

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

    def _cleanup(self, root: Model | None) -> None:
        super()._cleanup(root)
        if root is None:
            return
        ref = root.ref['id']
        if ref in self._models:
            model, _ = self._models.pop(ref, None)
            model._callbacks = {}
            model._event_callbacks = {}
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
    ) -> Dict[str, Any]:
        changes = {event.name: event.new for event in events}
        return self._process_param_change(changes)

    def _param_change(self, *events: param.parameterized.Event) -> None:
        named_events = {event.name: event for event in events}
        for ref, (model, _) in self._models.copy().items():
            properties = self._update_properties(*events, doc=model.document)
            if not properties:
                return
            self._apply_update(named_events, properties, model, ref)

    def _process_events(self, events: Dict[str, Any]) -> None:
        self._log('received events %s', events)
        with edit_readonly(state):
            state._busy_counter += 1
        events = self._process_property_change(events)
        try:
            with edit_readonly(self):
                self_events = {k: v for k, v in events.items() if '.' not in k}
                self.param.update(**self_events)
            for k, v in self_events.items():
                if '.' not in k:
                    continue
                *subpath, p = k.split('.')
                obj = self
                for sp in subpath:
                    obj = getattr(obj, sp)
                with edit_readonly(obj):
                    obj.param.update(**{p: v})
        except Exception:
            if len(events)>1:
                msg_end = f" changing properties {pformat(events)} \n"
            elif len(events)==1:
                msg_end = f" changing property {pformat(events)} \n"
            else:
                msg_end = "\n"
            log.exception(f'Callback failed for object named "{self.name}"{msg_end}')
            raise
        finally:
            self._log('finished processing events %s', events)
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
        self, doc: Document, ref: str, comm: Comm | None, subpath: str,
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
            doc.add_next_tick_callback(
                partial(self._event_coroutine, doc, event) # type: ignore
            )
        else:
            self._comm_event(doc, event)

    def _server_change(
        self, doc: Document, ref: str, subpath: str, attr: str,
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
    _ignored_refs: ClassVar[List[str]] = []

    _rename: ClassVar[Mapping[str, str | None]] = {
        'design': None, 'loading': None
    }

    __abstract = True

    def __init__(self, refs=None, **params):
        self._async_refs = {}
        params, refs = self._extract_refs(params, refs)
        super().__init__(**params)
        self._refs = refs
        self._setup_refs(refs)

    def _resolve_ref(self, pname, value):
        from .depends import param_value_if_widget
        ref = None
        value = param_value_if_widget(value)
        if isinstance(value, param.Parameter):
            ref = value
            value = getattr(value.owner, value.name)
        elif hasattr(value, '_dinfo'):
            ref = value
            value = eval_function(value)
            if isinstance(value, Generator):
                if pname == 'refs':
                    v = {}
                    for iv in value:
                        v.update(iv)
                else:
                    for v in value:
                        pass
                value = v
        if inspect.isawaitable(value) or isinstance(value, types.AsyncGeneratorType):
            param.parameterized.async_executor(partial(self._async_ref, pname, value))
            value = None
        return ref, value

    def _validate_ref(self, pname, value):
        if pname == 'refs':
            raise ValueError(
                'refs should never be captured.'
            )
        pobj = self.param[pname]
        pobj._validate(value)
        if isinstance(pobj, param.Dynamic) and callable(value) and hasattr(value, '_dinfo'):
            raise ValueError(
                'Dynamic parameters should not capture functions with dependencies.'
            )

    def _extract_refs(self, params, refs):
        processed, out_refs = {}, {}
        params['refs'] = refs
        for pname, value in params.items():
            if pname != 'refs' and (pname not in self.param or pname in self._ignored_refs):
                processed[pname] = value
                continue

            # Only consider extracting reference if the provided value is not
            # a valid value for the parameter (or no validation was defined)
            try:
                self._validate_ref(pname, value)
            except Exception:
                pass
            else:
                pobj = self.param[pname]
                if type(pobj) is not param.Parameter:
                    processed[pname] = value
                    continue

            # Resolve references, allowing for Widget, Parameter and
            # objects with dependencies
            ref, value = self._resolve_ref(pname, value)
            if ref is not None:
                out_refs[pname] = ref
            if pname == 'refs':
                if value is not None:
                    processed.update(value)
            else:
                processed[pname] = value
        return processed, out_refs

    async def _async_ref(self, pname, awaitable):
        if pname in self._async_refs:
            self._async_refs[pname].cancel()
        self._async_refs[pname] = task = asyncio.current_task()
        curdoc = state.curdoc
        has_context = bool(curdoc.session_context) if curdoc else False
        if has_context:
            curdoc.on_session_destroyed(lambda context: task.cancel())
        try:
            if isinstance(awaitable, types.AsyncGeneratorType):
                async for new_obj in awaitable:
                    if pname == 'refs':
                        self.param.update(new_obj)
                    else:
                        self.param.update({pname: new_obj})
            elif pname == 'refs':
                self.param.update(await awaitable)
            else:
                self.param.update({pname: await awaitable})
        except Exception as e:
            if not curdoc or (has_context and curdoc.session_context):
                raise e
        finally:
            del self._async_refs[pname]

    def _sync_refs(self, *events):
        from .config import config
        if config.loading_indicator:
            self.loading = True
        updates = {}
        generators = {}
        for pname, p in self._refs.items():
            if isinstance(p, param.Parameter):
                deps = (p,)
            else:
                deps = extract_dependencies(p)

            # Skip updating value if dependency has not changed
            if not any((dep.owner is e.obj and dep.name == e.name) for dep in deps for e in events):
                continue
            if isinstance(p, param.Parameter):
                new_val = getattr(p.owner, p.name)
            else:
                new_val = eval_function(p)

            if inspect.isawaitable(new_val) or isinstance(new_val, types.AsyncGeneratorType):
                param.parameterized.async_executor(partial(self._async_ref, pname, new_val))
                continue

            if isinstance(new_val, Generator):
                generators[pname] = new_val
                new_val = next(new_val)

            if pname == 'refs':
                updates.update(new_val)
            else:
                updates[pname] = new_val

        if config.loading_indicator:
            updates['loading'] = False
        with param.edit_constant(self):
            self.param.update(updates)
        for pname, gen in generators.items():
            for v in gen:
                if pname == 'refs':
                    updates.update(v)
                else:
                    updates[pname] = v
                with param.edit_constant(self):
                    self.param.update(updates)

    def _setup_refs(self, refs):
        groups = defaultdict(list)
        for pname, p in refs.items():
            if isinstance(p, param.Parameter):
                groups[p.owner].append(p.name)
            else:
                for sp in extract_dependencies(p):
                    groups[sp.owner].append(sp.name)
        for owner, pnames in groups.items():
            self._internal_callbacks.append(
                owner.param.watch(self._sync_refs, list(set(pnames)))
            )

    #----------------------------------------------------------------
    # Private API
    #----------------------------------------------------------------

    def _get_properties(self, doc: Document) -> Dict[str, Any]:
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
            state._stylesheets[doc] = cache = state._stylesheets.get(doc, {})
        else:
            cache = {}
        if doc and 'dist_url' in doc._template_variables:
            dist_url = doc._template_variables['dist_url']
        else:
            dist_url = CDN_DIST
        stylesheets = []
        for stylesheet in properties['stylesheets']:
            if isinstance(stylesheet, ImportedStyleSheet):
                if stylesheet.url in cache:
                    stylesheet = cache[stylesheet.url]
                else:
                    cache[stylesheet.url] = stylesheet
                patch_stylesheet(stylesheet, dist_url)
            stylesheets.append(stylesheet)
        properties['stylesheets'] = stylesheets
        return properties

    def _update_properties(self, *events: param.parameterized.Event, doc: Document) -> Dict[str, Any]:
        params, _ = self._design.params(self, doc) if self._design else ({}, None)
        changes = {event.name: event.new for event in events}
        if 'stylesheets' in changes and 'stylesheets' in params:
            changes['stylesheets'] = params['stylesheets'] + changes['stylesheets']
        return self._process_param_change(changes)

    def _update_model(
        self, events: Dict[str, param.parameterized.Event], msg: Dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Optional[Comm]
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
        self, target: param.Parameterized, callbacks: Optional[Dict[str, str | Callable]]=None,
        bidirectional: bool=False, **links: str
    ) -> Watcher:
        """
        Links the parameters on this `Reactive` object to attributes on the
        target `Parameterized` object.

        Supports two modes, either specify a
        mapping between the source and target object parameters as keywords or
        provide a dictionary of callbacks which maps from the source
        parameter to a callback which is triggered when the parameter
        changes.

        Arguments
        ---------
        target: param.Parameterized
          The target object of the link.
        callbacks: dict | None
          Maps from a parameter in the source object to a callback.
        bidirectional: bool
          Whether to link source and target bi-directionally
        **links: dict
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

    def controls(self, parameters: List[str] = [], jslink: bool = True, **kwargs) -> 'Panel':
        """
        Creates a set of widgets which allow manipulating the parameters
        on this instance. By default all parameters which support
        linking are exposed, but an explicit list of parameters can
        be provided.

        Arguments
        ---------
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

    def jscallback(self, args: Dict[str, Any]={}, **callbacks: str) -> Callback:
        """
        Allows defining a JS callback to be triggered when a property
        changes on the source object. The keyword arguments define the
        properties that trigger a callback and the JS code that gets
        executed.

        Arguments
        ----------
        args: dict
          A mapping of objects to make available to the JS callback
        **callbacks: dict
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
        self, target: JSLinkTarget , code: Dict[str, str] = None, args: Optional[Dict] = None,
        bidirectional: bool = False, **links: str
    ) -> Link:
        """
        Links properties on the this Reactive object to those on the
        target Reactive object in JS code.

        Supports two modes, either specify a
        mapping between the source and target model properties as
        keywords or provide a dictionary of JS code snippets which
        maps from the source parameter to a JS code snippet which is
        executed when the property changes.

        Arguments
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
        **links: dict
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


TData = Union['pd.DataFrame', 'DataDict']


class SyncableData(Reactive):
    """
    A baseclass for components which sync one or more data parameters
    with the frontend via a ColumnDataSource.
    """

    selection = param.List(default=[], item_type=int, doc="""
        The currently selected rows in the data.""")

    # Parameters which when changed require an update of the data
    _data_params: ClassVar[List[str]] = []

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

    def _get_data(self) -> Tuple[TData, 'DataDict']:
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

    def _update_column(self, column: str, array: np.ndarray | List) -> None:
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
        self, events: Tuple[param.parameterized.Event, ...], model: Model,
        doc: Document, root: Model, parent: Optional[Model], comm: Comm
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
        for ref, (m, _) in self._models.items():
            self._apply_update(named_events, msg, m.source, ref)

    @updating
    def _update_selected(
        self, *events: param.parameterized.Event, indices: Optional[List[int]] = None
    ) -> None:
        indices = self.selection if indices is None else indices
        msg = {'indices': indices}
        named_events = {event.name: event for event in events}
        for ref, (m, _) in self._models.items():
            self._apply_update(named_events, msg, m.source.selected, ref)

    def _apply_stream(self, ref: str, model: Model, stream: 'DataDict', rollover: Optional[int]) -> None:
        self._changing[ref] = ['data']
        try:
            model.source.stream(stream, rollover)
        finally:
            del self._changing[ref]

    @updating
    def _stream(self, stream: 'DataDict', rollover: Optional[int] = None) -> None:
        self._processed, _ = self._get_data()
        for ref, (m, _) in self._models.items():
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
                doc.add_next_tick_callback(cb)

    def _apply_patch(self, ref: str, model: Model, patch: 'Patches') -> None:
        self._changing[ref] = ['data']
        try:
            model.source.patch(patch)
        finally:
            del self._changing[ref]

    @updating
    def _patch(self, patch: 'Patches') -> None:
        for ref, (m, _) in self._models.items():
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
                doc.add_next_tick_callback(cb)

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
        self, stream_value: 'pd.DataFrame' | 'pd.Series' | Dict,
        rollover: Optional[int] = None, reset_index: bool = True
    ) -> None:
        """
        Streams (appends) the `stream_value` provided to the existing
        value in an efficient manner.

        Arguments
        ---------
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
                self.stream(stream_value.to_dict(), rollover)
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
                    combined = np.concatenate([self._data[col], array])
                    if rollover is not None:
                        combined = combined[-rollover:]
                    self._update_column(col, combined)
                self._stream(stream_value, rollover)
            else:
                try:
                    stream_value = pd.DataFrame(stream_value)
                except ValueError:
                    stream_value = pd.Series(stream_value)
                self.stream(stream_value)
        else:
            raise ValueError("The stream value provided is not a DataFrame, Series or Dict!")

    def patch(self, patch_value: 'pd.DataFrame' | 'pd.Series' | Dict) -> None:
        """
        Efficiently patches (updates) the existing value with the `patch_value`.

        Arguments
        ---------
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
                    k: [(patch_value["index"], v)] for k, v in patch_value.items()
                }
                patch_value_dict.pop("index")
            else:  # Series orient is column
                patch_value_dict = {
                    patch_value.name: [(index, value) for index, value in patch_value.items()]
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

    def __init__(self, **params):
        super().__init__(**params)

    def _update_selection(self, indices: List[int]) -> None:
        self.selection = indices

    def _convert_column(
        self, values: np.ndarray, old_values: np.ndarray | 'pd.Series'
    ) -> np.ndarray | List:
        dtype = old_values.dtype
        converted: List | np.ndarray | None = None
        if dtype.kind == 'M':
            if values.dtype.kind in 'if':
                NATs = values == BOKEH_JS_NAT
                converted = np.where(NATs, np.nan, values * 10e5).astype(dtype)
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
            if Version(pd.__version__) >= Version('1.1.0'):
                from pandas.core.arrays.masked import BaseMaskedDtype
                if isinstance(dtype, BaseMaskedDtype):
                    values = [dtype.na_value if v == '<NA>' else v for v in values]
            converted = pd.Series(values).astype(dtype).values
        else:
            converted = values.astype(dtype)
        return values if converted is None else converted

    def _process_data(self, data: Mapping[str, List | Dict[int, Any] | np.ndarray]) -> None:
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
            values = self._convert_column(
                np.asarray(values), old_raw[col]
            )

            isequal = None
            if hasattr(old_raw, 'columns') and isinstance(values, np.ndarray):
                try:
                    isequal = np.array_equal(old_raw[col], values, equal_nan=True)
                except Exception:
                    pass
            if isequal is None:
                try:
                    isequal = (old_raw[col] == values).all() # type: ignore
                except Exception:
                    isequal = False
            if not isequal:
                self._update_column(col, values)
                updated = True

        # If no columns were updated we don't have to sync data
        if not updated:
            return

        # Ensure we trigger events
        self._updating = True
        old_data = getattr(self, self._data_params[0])
        try:
            if old_data is self.value: # type: ignore
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

    def _process_events(self, events: Dict[str, Any]) -> None:
        if 'data' in events:
            self._process_data(events.pop('data'))
        if 'indices' in events:
            self._updating = True
            try:
                self._update_selection(events.pop('indices'))
            finally:
                self._updating = False
        super(ReactiveData, self)._process_events(events)



class ReactiveHTMLMetaclass(ParameterizedMetaclass):
    """
    Parses the ReactiveHTML._template of the class and initializes
    variables, callbacks and the data model to sync the parameters and
    HTML attributes.
    """

    _loaded_extensions: ClassVar[Set[str]] = set()

    _name_counter: ClassVar[Counter] = Counter()

    _script_regex: ClassVar[str] = r"script\([\"|'](.*)[\"|']\)"

    def __init__(mcs, name: str, bases: Tuple[Type, ...], dict_: Mapping[str, Any]):
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

        mcs._node_callbacks: Dict[str, List[Tuple[str, str]]]  = {}
        mcs._inline_callbacks = []
        for node, attrs in mcs._parser.attrs.items():
            for (attr, parameters, template) in attrs:
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



class ReactiveHTML(Reactive, metaclass=ReactiveHTMLMetaclass):
    """
    ReactiveHTML provides bi-directional syncing of arbitrary HTML
    attributes and DOM properties with parameters on the subclass.

    HTML templates
    ~~~~~~~~~~~~~~

    A ReactiveHTML component is declared by providing an HTML template
    on the `_template` attribute on the class. Parameters are synced by
    inserting them as template variables of the form `${parameter}`,
    e.g.:

        <div class="${div_class}">${children}</div>

    will interpolate the div_class parameter on the class. In addition
    to providing attributes we can also provide children to an HTML
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

        <input id="input"></input>

    Now we can use this name to declare set of `_dom_events` to
    subscribe to. The following will subscribe to change DOM events
    on the input element:

       {'input': ['change']}

    Once subscribed the class may also define a method following the
    `_{node}_{event}` naming convention which will fire when the DOM
    event triggers, e.g. we could define a `_input_change` method.
    Any such callback will be given a DOMEvent object as the first and
    only argument. The DOMEvent contains information about the event
    on the .data attribute and declares the type of event on the .type
    attribute.

    Inline callbacks
    ~~~~~~~~~~~~~~~~

    Instead of declaring explicit DOM events Python callbacks can also
    be declared inline, e.g.:

        <input id="input" onchange="${_input_change}"></input>

    will look for an `_input_change` method on the ReactiveHTML
    component and call it when the event is fired.

    Additionally we can invoke pure JS scripts defined on the class, e.g.:

        <input id="input" onchange="${script('some_script')}"></input>

    This will invoke the following script if it is defined on the class:

        _scripts = {
            'some_script': 'console.log(model, data, input, view)'
       }

    Scripts
    ~~~~~~~

    In addition to declaring callbacks in Python it is also possible
    to declare Javascript callbacks to execute when any synced
    attribute changes. Let us say we have declared an input element
    with a synced value parameter:

        <input id="input" value="${value}"></input>

    We can now declare a set of `_scripts`, which will fire whenever
    the value updates:

        _scripts = {
            'value': 'console.log(model, data, input)'
       }

    The Javascript is provided multiple objects in its namespace
    including:

      * data :  The data model holds the current values of the synced
                parameters, e.g. data.value will reflect the current
                value of the input node.
      * model:  The ReactiveHTML model which holds layout information
                and information about the children and events.
      * state:  An empty state dictionary which scripts can use to
                store state for the lifetime of the view.
      * view:   The Bokeh View class responsible for rendering the
                component. This provides access to method like
                `invalidate_layout` and `run_script` which allows
                invoking other scripts.
      * <node>: All named DOM nodes in the HTML template, e.g. the
                `input` node in the example above.
    """

    _child_config: ClassVar[Mapping[str, str]] = {}

    _dom_events: ClassVar[Mapping[str, List[str]]] = {}

    _extension_name: ClassVar[Optional[str]] = None

    _template: ClassVar[str] = ""

    _scripts: ClassVar[Mapping[str, str | List[str]]] = {}

    _script_assignment: ClassVar[str] = (
        r'data\.([^[^\d\W]\w*)[ ]*[\+,\-,\*,\\,%,\*\*,<<,>>,>>>,&,\^,|,\&\&,\|\|,\?\?]*='
    )

    __css__: ClassVar[Optional[List[str]]] = None
    __javascript__: ClassVar[Optional[List[str]]] = None
    __javascript_modules__: ClassVar[Optional[List[str]]] = None

    __abstract = True

    def __init__(self, **params):
        from .pane import panel
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
                params[children_param] = panel(child_value)
        super().__init__(**params)
        self._attrs = {}
        self._panes = {}
        self._event_callbacks = defaultdict(lambda: defaultdict(list))

    @classmethod
    def _loaded(cls) -> bool:
        """
        Whether the component has been loaded.
        """
        return (
            cls._extension_name is None or
            (cls._extension_name in ReactiveHTMLMetaclass._loaded_extensions and
             (state._extensions is None or (cls._extension_name in state._extensions)))
        )

    def _cleanup(self, root: Model | None = None) -> None:
        for child, panes in self._panes.items():
            for pane in panes:
                pane._cleanup(root)
        super()._cleanup(root)

    @property
    def _linkable_params(self) -> List[str]:
        return [
            p for p in super()._linkable_params if p not in self._parser.children.values() and
            p not in ('loading')]

    @property
    def _child_names(self):
        return {}

    def _process_children(
        self, doc: Document, root: Model, model: Model, comm: Optional[Comm],
        children: Dict[str, List[Model]]
    ) -> Dict[str, List[Model]]:
        return children

    def _process_param_change(self, params):
        props = super()._process_param_change(params)
        if 'stylesheets' in params:
            css = getattr(self, '__css__', []) or []
            props['stylesheets'] = [
                ImportedStyleSheet(url=ss) for ss in css
            ] + props['stylesheets']
        return props

    def _init_params(self) -> Dict[str, Any]:
        ignored = list(Reactive.param)
        for child in self._parser.children.values():
            if self._child_config.get(child) != 'literal':
                ignored.append(child)
        params = {
            p : getattr(self, p) for p in list(Layoutable.param)
            if getattr(self, p) is not None and p != 'name'
        }
        data_params = {}
        for k, v in self.param.values().items():
            if (
                (k in ignored and k != 'name') or
                ((self.param[k].precedence or 0) < 0) or
                (isinstance(v, Viewable) and not isinstance(self.param[k], param.ClassSelector))
            ):
                continue
            if isinstance(v, str):
                v = HTML_SANITIZER.clean(v)
            data_params[k] = v
        html, nodes, self._attrs = self._get_template()
        params.update({
            'attrs': self._attrs,
            'callbacks': self._node_callbacks,
            'data': self._data_model(**self._process_param_change(data_params)),
            'events': self._get_events(),
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

    def _get_events(self) -> Dict[str, Dict[str, bool]]:
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
        self, doc: Document, root: Model, model: Model, comm: Optional[Comm]
    ) -> Dict[str, List[Model]]:
        from .pane import panel
        old_models = model.children
        new_models: Dict[str, List[Model]] = {parent: [] for parent in self._parser.children}
        new_panes: Dict[str, List[Viewable] | Dict[str, Viewable] | None] = {}
        internal_panes: Dict[str, List[Viewable] | None] = {}

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
                for i, pane in enumerate(child_panes):
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

    def _get_template(self) -> Tuple[str, List[str], Mapping[str, List[Tuple[str, List[str], str]]]]:
        import jinja2

        # Replace loop variables with indexed child parameter e.g.:
        #   {% for obj in objects %}
        #     ${obj}
        #   {% endfor %}
        # becomes:
        #   {% for obj in objects %}
        #     ${objects[{{ loop.index0 }}]}
        #  {% endfor %}
        template_string = self._template
        for var, obj in self._parser.loop_map.items():
            for var in self._parser.loop_var_map[var]:
                template_string = template_string.replace(
                    '${%s}' % var, '${%s[{{ loop.index0 }}]}' % obj)

        # Add index to templated loop node ids
        for dom_node, _ in self._parser.looped:
            replacement = 'id="%s-{{ loop.index0 }}"' % dom_node
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
            )

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
        p_attrs: Dict[str, List[Tuple[str, List[str], str]]] = {}
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
                    html = html.replace('${%s[%d]}' % (child_name, i), '')
            else:
                html = html.replace('${%s}' % child_name, '')
        return html, parser.nodes, p_attrs

    @property
    def _linked_properties(self) -> List[str]:
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
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
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
            ReactiveHTMLMetaclass._loaded_extensions.add(self._extension_name)

        if not root:
            root = model

        data_model: DataModel = model.data # type: ignore
        for p, v in data_model.properties_with_values().items():
            if isinstance(v, DataModel):
                v.tags.append(f"__ref:{root.ref['id']}")
        model.update(children=self._get_children(doc, root, model, comm))
        self._register_events('dom_event', model=model, doc=doc, comm=comm)
        self._link_props(data_model, self._linked_properties, doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _process_event(self, event: 'Event') -> None:
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

    def _set_on_model(self, msg: Mapping[str, Any], root: Model, model: Model) -> None:
        if not msg:
            return
        old = self._changing.get(root.ref['id'], [])
        self._changing[root.ref['id']] = [
            attr for attr, value in msg.items()
            if not model.lookup(attr).property.matches(getattr(model, attr), value)
        ]
        try:
            model.update(**msg)
        finally:
            if old:
                self._changing[root.ref['id']] = old
            else:
                del self._changing[root.ref['id']]

    def _update_model(
        self, events: Dict[str, param.parameterized.Event], msg: Dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Optional[Comm]
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

    def on_event(self, node: str, event: str, callback: Callable) -> None:
        """
        Registers a callback to be executed when the specified DOM
        event is triggered on the named node. Note that the named node
        must be declared in the HTML. To create a named node you must
        give it an id of the form `id="name"`, where `name` will
        be the node identifier.

        Arguments
        ---------
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
        for ref, (model, _) in self._models.items():
            self._apply_update({}, {'events': events}, model, ref)

__all__ = (
    "Reactive",
    "ReactiveHTML",
    "ReactiveData"
)
