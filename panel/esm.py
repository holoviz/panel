from __future__ import annotations

import asyncio
import inspect
import os
import pathlib
import textwrap

from collections import defaultdict
from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Literal, Mapping,
    Optional, Tuple, Type,
)

import param

from param.parameterized import ParameterizedMetaclass

from .io.datamodel import construct_data_model
from .io.state import state
from .models import ReactiveESM as _BkReactiveESM
from .models.reactive_html import DOMEvent
from .reactive import Reactive, ReactiveCustomBase, ReactiveMetaBase
from .util.checks import import_available
from .viewable import Layoutable, Viewable

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.events import Event
    from bokeh.model import Model
    from pyviz_comms import Comm


class ReactiveESMMetaclass(ReactiveMetaBase):

    def __init__(mcs, name: str, bases: Tuple[Type, ...], dict_: Mapping[str, Any]):
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
    The `ReactiveESM` class enables you to create custom Panel components using HTML, CSS and/ or
    Javascript and without the complexities of Javascript build tools.

    A `ReactiveESM` subclass provides bi-directional syncing of its parameters with arbitrary HTML
    elements, attributes and properties. The key part of the subclass is the `_esm`
    variable. Use this to define a `render` function as shown in the example below.

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

    _esm: ClassVar[str | os.PathLike] = ""

    _import_map: ClassVar[Dict[str, Dict[Literal['imports', 'scopes'], str]]] = {}

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
        super()._cleanup(root)
        if not self._models and self._watching_esm:
            self._watching_esm.set()
            self._watching_esm = False

    async def _watch_esm(self):
        import watchfiles
        async for _ in watchfiles.awatch(self._esm, stop_event=self._watching_esm):
            for ref, (model, _) in self._models.items():
                self._apply_update({}, {'esm': self._render_esm()}, model, ref)

    @property
    def _linked_properties(self) -> List[str]:
        return [p for p in self._data_model.properties() if p not in ('js_property_callbacks',)]

    def _init_params(self) -> Dict[str, Any]:
        ignored = list(Reactive.param)
        params = {
            p : getattr(self, p) for p in list(Layoutable.param)
            if getattr(self, p) is not None and p != 'name'
        }
        data_params = {}
        for k, v in self.param.values().items():
            if (
                (k in ignored and k != 'name') or
                ((self.param[k].precedence or 0) < 0) or
                (isinstance(v, Viewable) and isinstance(self.param[k], param.ClassSelector))
            ):
                continue
            data_params[k] = v
        params.update({
            'data': self._data_model(**self._process_param_change(data_params)),
            'esm': self._render_esm(),
            'importmap': getattr(self, '_importmap', {}),
        })
        return params

    def _get_children(self, data_model, doc, root, parent, comm):
        children = {}
        ref = root.ref['id']
        for k, v in self.param.values().items():
            p = self.param[k]
            if not (isinstance(p, param.ClassSelector) and issubclass(p.class_, Viewable)):
                continue
            if v is None:
                children[k] = None
            elif ref in v._models:
                children[k] = v._models[ref]
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
        model = _BkReactiveESM(**self._get_properties(doc))
        root = root or model
        children = self._get_children(model.data, doc, root, model, comm)
        model.data.update(**children)
        model.children = list(children)
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model.data, self._linked_properties, doc, root, comm)
        self._setup_autoreload()
        self._register_events('dom_event', model=model, doc=doc, comm=comm)
        return model

    def _process_event(self, event: 'Event') -> None:
        if not isinstance(event, DOMEvent):
            return
        if hasattr(self, f'_handle_{event.node}'):
            getattr(self, f'_handle_{event.node}')(event)
        for cb in self._event_callbacks.get(event.node, []):
            cb(event)

    def _update_model(
        self, events: Dict[str, param.parameterized.Event], msg: Dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Optional[Comm]
    ) -> None:
        model_msg, data_msg  = {}, {}
        for prop, v in list(msg.items()):
            if prop in list(Reactive.param)+['esm', 'importmap']:
                model_msg[prop] = v
            elif ((prop in self.param) and (
                    ((self.param[prop].precedence or 0) < 0) or
                    (isinstance(v, Viewable) and not isinstance(self.param[prop], param.ClassSelector))
            )):
                continue
            else:
                data_msg[prop] = v
        for name, event in events.items():
            if name not in model.children or event.old in (None, event.new):
                continue
            event.old._cleanup(root)
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
