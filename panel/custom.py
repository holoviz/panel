from __future__ import annotations

import asyncio
import inspect
import os
import pathlib
import textwrap

from collections import defaultdict
from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Literal, Mapping, Optional,
)

import param

from param.parameterized import ParameterizedMetaclass

from .config import config
from .io.datamodel import construct_data_model
from .io.state import state
from .models import (
    AnyWidgetComponent as _BkAnyWidgetComponent,
    PreactComponent as _BkPreactComponent, ReactComponent as _BkReactComponent,
    ReactiveESM as _BkReactiveESM,
)
from .models.reactive_html import DOMEvent
from .reactive import Reactive, ReactiveCustomBase, ReactiveMetaBase
from .util.checks import import_available
from .viewable import (  # noqa
    Child, Children, Layoutable, Viewable, is_viewable_param,
)

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.events import Event
    from bokeh.model import Model
    from pyviz_comms import Comm


class ReactiveESMMetaclass(ReactiveMetaBase):

    def __init__(mcs, name: str, bases: tuple[type, ...], dict_: Mapping[str, Any]):
        mcs.__original_doc__ = mcs.__doc__
        ParameterizedMetaclass.__init__(mcs, name, bases, dict_)

        # Create model with unique name
        ReactiveMetaBase._name_counter[name] += 1
        model_name = f'{name}{ReactiveMetaBase._name_counter[name]}'
        mcs._data_model = construct_data_model(
            mcs, name=model_name, ignore=list(Reactive.param)
        )


class ReactiveESM(ReactiveCustomBase, metaclass=ReactiveESMMetaclass):
    '''
    The `ReactiveESM` classes allow you to create custom Panel
    components using HTML, CSS and/ or Javascript and without the
    complexities of Javascript build tools.

    A `ReactiveESM` subclass provides bi-directional syncing of its
    parameters with arbitrary HTML elements, attributes and
    properties. The key part of the subclass is the `_esm`
    variable. Use this to define a `render` function as shown in the
    example below.

    import panel as pn
    import param

    pn.extension()

    class CounterButton(pn.ReactiveESM):

        value = param.Integer()

        _esm = """
        export function render({ data }) {
            let btn = document.createElement("button");
            btn.innerHTML = `count is ${data.value}`;
            btn.addEventListener("click", () => {
                data.value += 1
            });
            data.watch(() => {
                btn.innerHTML = `count is ${data.value}`;
            }, 'value')
            return btn
        }
        """

    CounterButton().servable()
    '''

    _bokeh_model = _BkReactiveESM

    _esm: ClassVar[str | os.PathLike] = ""

    _import_map: ClassVar[dict[str, dict[Literal['imports', 'scopes'], str]]] = {}

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        self._watching_esm = False
        self._event_callbacks = defaultdict(list)

    def _render_esm(self):
        esm = self._esm
        if isinstance(esm, pathlib.PurePath):
            esm = esm.read_text(encoding='utf-8')
        elif esm.endswith(('.js', '.jsx', '.ts', '.tsx')):
            try:
                # Safely check if ESM is a path relative to class definition
                esm_path = pathlib.Path(inspect.getfile(type(self))).parent / esm
                if esm_path.is_file():
                    esm = esm_path.read_text(encoding='utf-8')
            except (OSError, TypeError, ValueError):
                pass
        esm = textwrap.dedent(esm)
        return esm

    def _cleanup(self, root: Model | None) -> None:
        if root:
            ref = root.ref['id']
            if ref in self._models:
                model, _ = self._models[ref]
                for child in model.children:
                    children = getattr(self, child)
                    if isinstance(children, Viewable):
                        children = [children]
                    if isinstance(children, list):
                        for child in children:
                            if isinstance(child, Viewable):
                                child._cleanup(root)
        super()._cleanup(root)
        if not self._models and self._watching_esm:
            self._watching_esm.set()
            self._watching_esm = False

    async def _watch_esm(self):
        import watchfiles
        async for _ in watchfiles.awatch(self._esm, stop_event=self._watching_esm):
            esm = self._render_esm()
            for ref, (model, _) in self._models.items():
                if esm == model.esm:
                    continue
                self._apply_update({}, {'compiled': None, 'esm': esm}, model, ref)

    @property
    def _linked_properties(self) -> list[str]:
        return [p for p in self._data_model.properties() if p not in ('js_property_callbacks',)]

    def _init_params(self) -> dict[str, Any]:
        ignored = list(Reactive.param)
        params = {
            p : getattr(self, p) for p in list(Layoutable.param)
            if getattr(self, p) is not None and p != 'name'
        }
        data_params = {}
        for k, v in self.param.values().items():
            if (
                (k in ignored and k != 'name') or
                (((p:= self.param[k]).precedence or 0) < 0) or
                is_viewable_param(p)
            ):
                continue
            data_params[k] = v
        data_props = self._process_param_change(data_params)
        params.update({
            'data': self._data_model(**data_props),
            'dev': config.autoreload,
            'esm': self._render_esm(),
            'importmap': getattr(self, '_importmap', {}),
        })
        return params

    def _get_children(self, data_model, doc, root, parent, comm):
        children = {}
        ref = root.ref['id']
        for k, v in self.param.values().items():
            p = self.param[k]
            if not is_viewable_param(p):
                continue
            if v is None:
                children[k] = None
            elif isinstance(v, list):
                children[k] = [
                    sv._models[ref][0] if ref in sv._models else sv._get_model(doc, root, parent, comm)
                    for sv in v
                ]
            elif ref in v._models:
                children[k] = v._models[ref][0]
            else:
                children[k] = v._get_model(doc, root, parent, comm)
        return children

    def _setup_autoreload(self):
        from .config import config
        if not (config.autoreload and import_available('watchfiles')):
            return
        super()._setup_autoreload()
        if isinstance(self._esm, pathlib.PurePath) and not self._watching_esm:
            self._watching_esm = asyncio.Event()
            state.execute(self._watch_esm)

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = self._bokeh_model(**self._get_properties(doc))
        root = root or model
        children = self._get_children(model.data, doc, root, model, comm)
        model.data.update(**children)
        model.children = list(children)
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model.data, self._linked_properties, doc, root, comm)
        self._register_events('dom_event', model=model, doc=doc, comm=comm)
        self._setup_autoreload()
        return model

    def _process_event(self, event: 'Event') -> None:
        if not isinstance(event, DOMEvent):
            return
        if hasattr(self, f'_handle_{event.node}'):
            getattr(self, f'_handle_{event.node}')(event)
        for cb in self._event_callbacks.get(event.node, []):
            cb(event)

    def _update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Optional[Comm]
    ) -> None:
        model_msg, data_msg  = {}, {}
        for prop, v in list(msg.items()):
            if prop in list(Reactive.param)+['compiled', 'esm', 'importmap']:
                model_msg[prop] = v
            elif prop in model.children:
                continue
            else:
                data_msg[prop] = v
        for name, event in events.items():
            if name not in model.children:
                continue
            new = event.new
            old_objects = event.old if isinstance(event.old, list) else [event.old]
            for old in old_objects:
                if old is None or old is new or (isinstance(new, list) and old in new):
                    continue
                old._cleanup(root)
        if any(e in model.children for e in events):
            children = self._get_children(model.data, doc, root, model, comm)
            data_msg.update(children)
            model_msg['children'] = list(children)
        self._set_on_model(model_msg, root, model)
        self._set_on_model(data_msg, root, model.data)

    def on_event(self, event: str, callback: Callable) -> None:
        """
        Registers a callback to be executed when the specified DOM
        event is triggered.

        Arguments
        ---------
        event: str
          Name of the DOM event to add an event listener to.
        callback: callable
          A callable which will be given the DOMEvent object.
        """
        self._event_callbacks[event].append(callback)


class JSComponent(ReactiveESM):
    '''
    The `JSComponent` allows you to create custom Panel components
    using Javascript and CSS without the complexities of
    Javascript build tools.

    A `JSComponent` subclass provides bi-directional syncing of its
    parameters with arbitrary HTML elements, attributes and
    properties. The key part of the subclass is the `_esm`
    variable. Use this to define a `render` function as shown in the
    example below.

    import panel as pn
    import param

    pn.extension()

    class CounterButton(JSComponent):

        value = param.Integer()

        _esm = """
        export function render({ data }) {
            let btn = document.createElement("button");
            btn.innerHTML = `count is ${data.value}`;
            btn.addEventListener("click", () => {
                data.value += 1
            });
            data.watch(() => {
                btn.innerHTML = `count is ${data.value}`;
            }, 'value')
            return btn
        }
        """

    CounterButton().servable()
    '''


class ReactComponent(ReactiveESM):
    '''
    The `ReactComponent` allows you to create custom Panel components
    using React without the complexities of Javascript build tools.

    A `ReactComponent` subclass provides bi-directional syncing of its
    parameters with arbitrary HTML elements, attributes and
    properties. The key part of the subclass is the `_esm`
    variable. Use this to define a `render` function as shown in the
    example below.

    import panel as pn
    import param

    pn.extension()

    class CounterButton(ReactComponent):

        value = param.Integer()

        _esm = """
        export function render({ data, state }) {
          return (
            <>
              <button onClick={() => { data.value += 1 }}>{state.value}</button>
            </>
          )
        }
        """

    CounterButton().servable()
    '''


    _bokeh_model = _BkReactComponent

    _react_version = '18.2.0'

    def _init_params(self) -> dict[str, Any]:
        params = super()._init_params()
        params['react_version'] = self._react_version
        return params


class AnyWidgetComponent(ReactComponent):
    """
    The `AnyWidgetComponent` allows you to create custom Panel components
    in the style of an AnyWidget component. Specifically this component
    type creates shims that make it possible to reuse AnyWidget ESM code
    as is, without having to adapt the callbacks to use Bokeh APIs.
    """

    _bokeh_model = _BkAnyWidgetComponent


class PreactComponent(ReactiveESM):
    '''
    The `PreactComponent` allows you to create custom Panel components
    using Preact and htm without the complexities of Javascript build tools.

    A `PreactComponent` subclass provides bi-directional syncing of its
    parameters with arbitrary HTML elements, attributes and
    properties. The key part of the subclass is the `_esm`
    variable. Use this to define a `render` function as shown in the
    example below.

    import panel as pn
    import param

    pn.extension()

    class CounterButton(ReactComponent):

        value = param.Integer()

        _esm = """
        export function render({ data, html }) {
          return html`<button onClick=${() => { data.value += 1 }}>${state.value}</button>`
        }
        """

    CounterButton().servable()
    '''

    _bokeh_model = _BkPreactComponent