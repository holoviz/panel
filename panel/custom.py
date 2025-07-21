from __future__ import annotations

import asyncio
import hashlib
import importlib
import inspect
import os
import pathlib
import sys
import textwrap

from collections import defaultdict
from collections.abc import Callable, Mapping
from functools import partial
from typing import (
    TYPE_CHECKING, Any, ClassVar, Literal,
)

import param

from param.parameterized import ParameterizedMetaclass

from .config import config
from .io.datamodel import construct_data_model
from .io.document import freeze_doc, hold
from .io.model import apply_changes_without_dispatch
from .io.resources import component_resource_path
from .io.state import state
from .layout.base import Panel
from .models import (
    AnyWidgetComponent as _BkAnyWidgetComponent,
    ReactComponent as _BkReactComponent, ReactiveESM as _BkReactiveESM,
)
from .models.esm import DataEvent, ESMEvent
from .models.reactive_html import DOMEvent
from .pane.base import PaneBase  # noqa
from .reactive import (  # noqa
    Reactive, ReactiveCustomBase, ReactiveHTML, ReactiveMetaBase,
)
from .util import classproperty
from .util.checks import import_available
from .viewable import (  # noqa
    Child, Children, Layoutable, Viewable, Viewer, is_viewable_param,
)
from .widgets.base import WidgetBase  # noqa

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.events import Event
    from bokeh.model import Model
    from bokeh.models import UIElement
    from pyviz_comms import Comm

    ExportSpec = dict[str, list[str | tuple[str, ...]]]


class PyComponent(Viewable, Layoutable):
    '''
    The `PyComponent` combines the convenience of `Viewer` components
    that allow creating custom components by declaring a `__panel__`
    method with the ability of controlling layout and styling
    related parameters directly on the class. Internally the
    `PyComponent` will forward layout parameters to the underlying
    object, which is created lazily on render.

    Reference: https://panel.holoviz.org/reference/custom_components/PyComponent.html

    :Example:

    .. code-block:: python

        import panel as pn
        import param

        pn.extension()

        class CounterButton(pn.custom.PyComponent, pn.widgets.WidgetBase):

            value = param.Integer(default=0)

            def __panel__(self):
                return pn.widgets.Button(
                    name=self._button_name, on_click=self._on_click
                )

            def _on_click(self, event):
                self.value += 1

            @param.depends("value")
            def _button_name(self):
                return f"count is {self.value}"

        CounterButton().servable()
    '''

    def __init__(self, **params):
        super().__init__(**params)
        self._view__ = None
        self._changing__ = {}
        self.param.watch(self._sync__view, [p for p in Layoutable.param if p != 'name'])

    def _sync__view(self, *events):
        if not events or self._view__ is None:
            return
        target = self._view__ if events[0].obj is self else self
        params = {
            e.name: e.new for e in events if e.name not in self._changing__
            or self._changing__[e.name] is not e.new
        }
        if not params:
            return
        try:
            self._changing__.update(params)
            with param.parameterized._syncing(target, list(params)):
                target.param.update(params)
        finally:
            for p in params:
                if p in self._changing__:
                    del self._changing__[p]

    def _cleanup(self, root: Model | None = None) -> None:
        if self._view__ is None:
            return
        super()._cleanup(root)
        if root and root.ref['id'] in self._models:
            del self._models[root.ref['id']]
        self._view__._cleanup(root)

    def _create__view(self):
        from .pane import panel
        from .param import ParamMethod

        if hasattr(self.__panel__, "_dinfo"):
            view = ParamMethod(self.__panel__, lazy=True)
        else:
            view = panel(self.__panel__())
        params = view.param.values()
        overrides, sync = {}, {}
        for p in Layoutable.param:
            if p != 'name' and view.param[p].default != params[p]:
                overrides[p] = params[p]
            elif p != 'name':
                sync[p] = getattr(self, p)
        view.param.watch(self._sync__view, [p for p in Layoutable.param if p != 'name'])
        self.param.update(overrides)
        with param.parameterized._syncing(view, list(sync)):
            view.param.update(sync)
        return view

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        if self._view__ is None:
            self._view__ = self._create__view()
        model = self._view__._get_model(doc, root, parent, comm)
        root = model if root is None else root
        self._models[root.ref['id']] = (model, parent)
        return model

    def select(
        self, selector: type | Callable[[Viewable], bool] | None = None
    ) -> list[Viewable]:
        if self._view__ is None:
            self._view__ = self._create__view()
        return super().select(selector) + self._view__.select(selector)



class ReactiveESMMetaclass(ReactiveMetaBase):

    def __init__(mcs, name: str, bases: tuple[type, ...], dict_: Mapping[str, Any]):
        mcs.__original_doc__ = mcs.__doc__
        ParameterizedMetaclass.__init__(mcs, name, bases, dict_)

        # Create model with unique name
        ReactiveMetaBase._name_counter[name] += 1
        model_name = f'{name}{ReactiveMetaBase._name_counter[name]}'
        ignored = [
            p for p in Reactive.param
            if not issubclass(type(mcs.param[p].owner), ReactiveESMMetaclass)
        ]
        mcs._data_model = construct_data_model(
            mcs, name=model_name, ignore=ignored, extras={'esm_constants': param.Dict}
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

    :Example:

    .. code-block:: python

        import panel as pn
        import param

        pn.extension()

        class CounterButton(pn.custom.ReactiveESM):

            value = param.Integer()

            _esm = """
            export function render({ model }) {
                let btn = document.createElement("button");
                btn.innerHTML = `count is ${model.value}`;
                btn.addEventListener("click", () => {
                    model.value += 1
                });
                model.on('value', () => {
                    btn.innerHTML = `count is ${model.value}`;
                })
                return btn
            }
            """

        CounterButton().servable()
    '''

    _bokeh_model = _BkReactiveESM

    _bundle: ClassVar[str | os.PathLike | None] = None

    _constants: ClassVar[dict[str, Any]] = {}

    _esm: ClassVar[str | os.PathLike] = ""

    _esm_shared: ClassVar[dict[str, str | os.PathLike]] = {}

    # Specifies exports to make available to JS in a bundled file
    # 1. Default export: "<export>"
    # 2. Import all (`* as`): "*<export>"
    # 3. Named export (`{ <export>, ... }`): ("<export>", ...)
    _exports__: ClassVar[ExportSpec] = {}

    _importmap: ClassVar[dict[Literal['imports', 'scopes'], dict[str,str]]] = {}

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        self._watching_esm = False
        self._event__callbacks = defaultdict(list)
        self._msg__callbacks = []

    @classproperty
    def _module_path(cls):
        if hasattr(cls, '__path__'):
            return pathlib.Path(cls.__path__)
        try:
            return pathlib.Path(inspect.getfile(cls)).parent
        except (OSError, TypeError, ValueError):
            if not isinstance(cls._bundle, pathlib.PurePath):
                return

    @classproperty
    def _bundle_path(cls) -> os.PathLike | None:
        if config.autoreload and cls._esm:
            return None
        mod_path = cls._module_path
        if mod_path is None:
            return None
        if cls._bundle:
            for scls in cls.__mro__:
                if issubclass(scls, ReactiveESM) and cls._bundle == scls._bundle:
                    cls = scls
            mod_path = cls._module_path
            bundle = cls._bundle
            if isinstance(bundle, os.PathLike):
                return bundle
            elif bundle and bundle.endswith('.js'):
                bundle_path = mod_path / bundle
                if bundle_path.is_file():
                    return bundle_path
            raise ValueError(
                f'Could not resolve {cls.__name__}._bundle: {cls._bundle}. Ensure '
                'you provide either a string with a relative or absolute '
                'path or a Path object to a .js file extension.'
            )

        # Attempt resolving bundle for this component specifically
        path = mod_path / f'{cls.__name__}.bundle.js'
        if path.is_file():
            return path

        # Attempt to resolve bundle in current module and parent modules
        module = cls.__module__
        modules = module.split('.')
        for i in reversed(range(len(modules))):
            submodule = '.'.join(modules[:i+1])
            try:
                mod = importlib.import_module(submodule)
            except (ModuleNotFoundError, ImportError):
                continue
            mod_file = getattr(mod, '__file__', None)
            if not mod_file:
                continue
            submodule_path = pathlib.Path(mod_file).parent
            path = submodule_path / f'{submodule}.bundle.js'
            if path.is_file():
                return path

        if module in sys.modules:
            # Get module name from the module
            module_obj = sys.modules[module]
            path = mod_path / f'{module_obj.__name__}.bundle.js'
            return path if path.is_file() else None
        return None

    @classproperty
    def _bundle_css(cls):
        try:
            esm_path = cls._esm_path(compiled=True)
        except ValueError:
            return []
        css_path = esm_path.with_suffix('.css')
        if css_path.is_file():
            return [css_path]
        return []

    @classmethod
    def _esm_path(cls, compiled: bool | Literal['compiling'] = True) -> os.PathLike | None:
        if compiled or not cls._esm:
            bundle_path = cls._bundle_path
            if bundle_path:
                return bundle_path
        esm = cls._esm
        if isinstance(esm, os.PathLike):
            return esm
        elif not esm or not esm.endswith(('.js', '.jsx', '.ts', '.tsx')):
            return None
        try:
            if hasattr(cls, '__path__'):
                mod_path = cls.__path__
            else:
                mod_path = pathlib.Path(inspect.getfile(cls)).parent
            esm_path = mod_path / esm
            if esm_path.is_file():
                return esm_path
        except (OSError, TypeError, ValueError):
            pass
        return None

    @classmethod
    def _component_resource_path(cls, esm_path, compiled):
        base_cls = cls
        for scls in cls.__mro__[1:]:
            if not issubclass(scls, ReactiveESM):
                continue
            if esm_path == scls._esm_path(compiled=compiled is True):
                base_cls = scls
        return component_resource_path(base_cls, '_bundle_path', esm_path)

    @classmethod
    def _render_esm(cls, compiled: bool | Literal['compiling'] = True, server: bool = False):
        esm_path = cls._esm_path(compiled=compiled is True)
        if esm_path:
            if esm_path == cls._bundle_path and cls.__module__ in sys.modules and server:
                # Generate relative path to handle apps served on subpaths
                esm = (state.rel_path or './') + cls._component_resource_path(esm_path, compiled)
                if config.autoreload:
                    modified = hashlib.sha256(str(esm_path.stat().st_mtime).encode('utf-8')).hexdigest()
                    esm += f'?{modified}'
            else:
                esm = esm_path.read_text(encoding='utf-8')
        else:
            esm = cls._esm
        if esm is None:
            raise ValueError(
                f'{cls.__name__}._esm was found empty. Ensure you define an ESM module.'
            )
        esm = textwrap.dedent(esm)
        return esm

    def _cleanup(self, root: Model | None = None) -> None:
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
            if self._watching_esm in state._watch_events:
                state._watch_events.remove(self._watching_esm)
            self._watching_esm = False

    async def _watch_esm(self):
        import watchfiles
        path = self._esm_path(compiled=False)
        async for changes in watchfiles.awatch(path, stop_event=self._watching_esm):
            update = False
            for (change, path) in changes:
                if change != watchfiles.Change.modified:
                    continue
                # Ensure that the file exists (in case filesystem write is not atomic)
                retries = 0
                while not os.path.exists(path):
                    await asyncio.sleep(0.1)
                    retries += 1
                    if retries == 5:
                        break
                # Ignore change if file is not written within 0.5 seconds
                if retries != 5:
                    update = True
            if update:
                self._update_esm()

    def _update_esm(self):
        for ref, (model, _) in self._models.copy().items():
            if ref not in state._views:
                continue
            doc = state._views[ref][2]
            is_session = doc.session_context and doc.session_context.server_context
            esm = self._render_esm(not config.autoreload, server=is_session)
            if esm == model.esm:
                continue
            self._apply_update({}, {'esm': esm}, model, ref)

    @property
    def _linked_properties(self) -> tuple[str, ...]:
        return tuple(p for p in self._data_model.properties() if p != 'js_property_callbacks')

    def _get_properties(self, doc: Document | None) -> dict[str, Any]:
        props = super()._get_properties(doc)
        cls = type(self)
        data_params = {}
        # Split data model properties from ESM model properties
        # Note that inherited parameters are generally treated
        # as ESM model properties unless their type has changed
        ignored = [
            p for p in Reactive.param
            if not issubclass(cls.param[p].owner, ReactiveESM) or
            (p in Viewable.param and p not in ('name', 'use_shadow_dom')
             and type(Reactive.param[p]) is type(cls.param[p]))
        ]
        events = []
        for k, v in self.param.values().items():
            p = self.param[k]
            if is_viewable_param(p) or type(self)._property_mapping.get(k, "") is None:
                props.pop(k, None)
                continue
            elif (k in ignored and k != 'name') or ((p.precedence or 0) < 0):
                continue
            if k in props:
                props.pop(k)
            if isinstance(p, param.Event):
                events.append(k)
            data_params[k] = v
        bundle_path = self._bundle_path
        importmap = self._process_importmap()
        is_session = False
        css_bundle = None
        if bundle_path:
            is_session = bool(doc and doc.session_context and doc.session_context.server_context)
            if bundle_path == self._esm_path(not config.autoreload) and cls.__module__ in sys.modules and is_session:
                bundle_hash = 'url'
                if self._bundle_css:
                    esm_bundle = self._component_resource_path(bundle_path, compiled=True)
                    css_bundle = esm_bundle.replace('_bundle_path', '_bundle_css').replace('.js', '.css')
            else:
                bundle_hash = hashlib.sha256(str(bundle_path).encode('utf-8')).hexdigest()
        else:
            bundle_hash = None
        data_props = self._process_param_change(data_params)
        data_props['esm_constants'] = self._constants
        props.update({
            'bundle': bundle_hash,
            'css_bundle': css_bundle,
            'class_name': cls.__name__,
            'data': self._data_model(**{p: v for p, v in data_props.items() if p not in ignored}),
            'dev': config.autoreload or getattr(self, '_debug', False),
            'esm': self._render_esm(not config.autoreload, server=is_session),
            'events': events,
            'importmap': importmap,
            'name': cls.__name__
        })
        return props

    @classmethod
    def _process_importmap(cls):
        return cls._importmap

    def _get_child_model(
        self, child: Viewable, doc: Document, root: Model, parent: Model, comm: Comm | None
    ) -> tuple[list[UIElement] | UIElement | None, list[UIElement]]:
        if child is None:
            return None, []
        ref = root.ref['id']
        old = []
        if isinstance(child, list):
            models = []
            for sv in child:
                if ref in sv._models:
                    model = sv._models[ref][0]
                    old.append(model)
                else:
                    model = sv._get_model(doc, root, parent, comm)
                models.append(model)
            return models, old
        elif ref in child._models:
            model = child._models[ref][0]
            old.append(model)
        else:
            model = child._get_model(doc, root, parent, comm)
        return model, old

    def _get_children(self, data_model, doc, root, parent, comm) -> tuple[dict[str, list[UIElement] | UIElement | None], list[UIElement]]:
        children = {}
        old_models = []
        for k, v in self.param.values().items():
            p = self.param[k]
            if not is_viewable_param(p) or type(self)._property_mapping.get(k, "") is None:
                continue
            children[k], old = self._get_child_model(v, doc, root, parent, comm)
            old_models += old
        return children, old_models

    def _setup_autoreload(self):
        from .config import config
        if not ((config.autoreload or getattr(self, '_debug', False)) and import_available('watchfiles')):
            return
        super()._setup_autoreload()
        if (self._esm_path(compiled=False) and not self._watching_esm):
            self._watching_esm = event = asyncio.Event()
            state._watch_events.append(event)
            state.execute(self._watch_esm)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        props = self._get_properties(doc)
        model = self._bokeh_model(**props)
        root = root or model
        children, _ = self._get_children(model.data, doc, root, model, comm)
        model.data.update(**children)
        model.children = list(children)  # type: ignore
        ref = root.ref['id']
        self._models[ref] = (model, parent)
        self._patch_datamodel_ref(model.data, ref)
        self._link_props(props['data'], self._linked_properties, doc, root, comm)
        self._register_events('dom_event', 'data_event', model=model, doc=doc, comm=comm)
        self._setup_autoreload()
        return model

    def _process_event(self, event: Event) -> None:
        if isinstance(event, DataEvent):
            for cb in self._msg__callbacks:
                state.execute(partial(cb, event), schedule=False)
            state.execute(partial(self._handle_msg, event.data), schedule=False)
            return
        elif not isinstance(event, DOMEvent):
            return
        if hasattr(self, f'_handle_{event.node}'):
            getattr(self, f'_handle_{event.node}')(event)
        for cb in self._event__callbacks.get(event.node, []):
            state.execute(partial(cb, event), schedule=False)

    def _update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Comm | None
    ) -> None:
        model_msg, data_msg, data_resets  = {}, {}, {}
        for prop, v in list(msg.items()):
            if prop in list(Reactive.param)+['esm', 'importmap']:
                model_msg[prop] = v
            elif prop in model.children:
                continue
            else:
                data_msg[prop] = v
                if prop in self.param and isinstance(self.param[prop], param.Event) and v:
                    data_resets[prop] = False
        for name, event in events.items():
            if name not in model.children:
                continue
            new = event.new
            old_objects = event.old if isinstance(event.old, list) else [event.old]
            for old in old_objects:
                if old is None or old is new or (isinstance(new, list) and old in new):
                    continue
                old._cleanup(root)

        update_children = any(e in model.children for e in events)
        if update_children:
            children, old_children = self._get_children(model.data, doc, root, model, comm)
            data_msg.update(children)
            model_msg['children'] = list(children)

        ref = root.ref['id']
        prev_changing = self._changing.get(ref, [])
        try:
            update = Panel._batch_update
            Panel._batch_update = True
            with hold(doc):
                changing = []
                with freeze_doc(doc, model, msg, force=update_children):
                    if model_msg:
                        changing += self._set_on_model(model_msg, root, model)
                    if data_msg:
                        changing += self._set_on_model(data_msg, root, model.data)
                    if update and update_children and ref in state._views:
                        state._views[ref][0]._preprocess(root, self, old_children)
                self._changing[ref] = changing
        finally:
            Panel._batch_update = update
            if prev_changing:
                self._changing[ref] = prev_changing
            elif ref in self._changing:
                del self._changing[ref]
        if data_resets:
            apply_changes_without_dispatch(doc, model.data, data_resets)

    def _handle_msg(self, data: Any) -> None:
        """
        Message handler for messages sent from the frontend using the
        `model.send_msg` API.

        Parameters
        ----------
        data: any
            Data received from the frontend.
        """

    def _send_msg(self, data: Any) -> None:
        """
        Sends data to the frontend which can be observed on the frontend
        with the `model.on("msg:custom", callback)` API.

        Parameters
        ----------
        data: any
            Data to send to the frontend.
        """
        self._send_event(ESMEvent, data=data)

    def on_msg(self, callback: Callable) -> None:
        """
        Registers a callback to be executed when a message event
        containing arbitrary data is received.

        Parameters
        ----------
        event: str
          Name of the DOM event to add an event listener to.
        callback: callable
          A callable which will be given the msg data.
        """
        self._msg__callbacks.append(callback)

    def on_event(self, event: str, callback: Callable) -> None:
        """
        Registers a callback to be executed when the specified DOM
        event is triggered.

        Parameters
        ----------
        event: str
          Name of the DOM event to add an event listener to.
        callback: callable
          A callable which will be given the DOMEvent object.
        """
        self._event__callbacks[event].append(callback)

    def select(
        self, selector: type | Callable[[Viewable], bool] | None = None
    ) -> list[Viewable]:
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Parameters
        ----------
        selector: type or callable or None
          The selector allows selecting a subset of Viewables by
          declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        selected = super().select(selector)
        if (selector is None or
            (isinstance(selector, type) and isinstance(self, selector)) or
            (callable(selector) and not isinstance(selector, type) and selector(self))):
            selected = [self]
        else:
            selected = []
        for p, pobj in self.param.objects(instance='existing').items():
            if isinstance(pobj, Children):
                p_children = getattr(self, p, []) or []
                for child in p_children:
                    selected += child.select(selector)
            elif isinstance(pobj, Child):
                p_child = getattr(self, p, None)
                if p_child is not None:
                    selected += p_child.select(selector)
        return selected



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

    Reference: https://panel.holoviz.org/reference/custom_components/JSComponent.html

    :Example:

    .. code-block:: python

        import panel as pn
        import param

        pn.extension()

        class CounterButton(pn.custom.JSComponent):

            value = param.Integer()

            _esm = """
            export function render({ model }) {
                let btn = document.createElement("button");
                btn.innerHTML = `count is ${model.value}`;
                btn.addEventListener("click", () => {
                    model.value += 1
                });
                model.on('value', () => {
                    btn.innerHTML = `count is ${model.value}`;
                })
                return btn
            }
            """

        CounterButton().servable()
    '''

    __abstract = True


class ReactComponent(ReactiveESM):
    '''
    The `ReactComponent` allows you to create custom Panel components
    using React without the complexities of Javascript build tools.

    A `ReactComponent` subclass provides bi-directional syncing of its
    parameters with arbitrary HTML elements, attributes and
    properties. The key part of the subclass is the `_esm`
    variable. Use this to define a `render` function as shown in the
    example below.

    Reference: https://panel.holoviz.org/reference/custom_components/ReactComponent.html

    :Example:

    .. code-block:: python

        import panel as pn
        import param

        class CounterButton(pn.custom.ReactComponent):

            value = param.Integer()

            _esm = """
            export function render({model}) {
            const [value, setValue] = model.useState("value");
            return (
                <button onClick={e => setValue(value+1)}>
                count is {value}
                </button>
            )
            }
            """

        CounterButton().servable()
    '''

    use_shadow_dom = param.Boolean(default=True, constant=True, doc="""
        Whether to render component into a shadow root.
        This may optionally be disabled but will only take
        effect if the parent is also a React component.
        If disabled the component will be rendered into
        the parent's React DOM tree.""")

    __abstract = True

    _bokeh_model = _BkReactComponent

    _react_version = '18.3.1'

    @classproperty  # type: ignore
    def _exports__(cls) -> ExportSpec:  # type: ignore
        imports = cls._importmap.get('imports', {})
        exports: dict[str, list[str | tuple[str, ...]]] = {
            "react": ["*React"],
            "react-dom/client": [("createRoot",)]
        }
        if any('@mui' in v for v in imports.values()):
            exports.update({
                "@emotion/cache": ["createCache"],
                "@emotion/react": [("CacheProvider",)],
            })
        return exports

    @classmethod
    def _render_esm(cls, compiled: bool | Literal['compiling'] = True, server: bool = False):
        esm = super()._render_esm(compiled=compiled, server=server)
        if compiled == 'compiling':
            esm = 'import * as React from "react"\n' + esm
        return esm

    @classmethod
    def _process_importmap(cls):
        imports = cls._importmap.get('imports', {})
        v_react = cls._react_version
        if config.autoreload:
            pkg_suffix, path_suffix = '?dev', '&dev'
        else:
            pkg_suffix = path_suffix = ''
        imports_with_deps = {
            "react": f"https://esm.sh/react@{v_react}{pkg_suffix}",
            "react/": f"https://esm.sh/react@{v_react}{path_suffix}/",
            "react-dom": f"https://esm.sh/react-dom@{v_react}?deps=react@{v_react}&external=react",
            "react-dom/": f"https://esm.sh/react-dom@{v_react}&deps=react@{v_react}{path_suffix}&external=react/"
        }
        suffix = f'deps=react@{v_react},react-dom@{v_react}&external=react,react-dom'
        if any('@mui' in v for v in imports.values()):
            suffix += ',react-is,@emotion/react'
            imports_with_deps.update({
                "react-is": f"https://esm.sh/react-is@{v_react}&external=react",
                "@emotion/cache": f"https://esm.sh/@emotion/cache?deps=react@{v_react},react-dom@{v_react}",
                "@emotion/react": f"https://esm.sh/@emotion/react?deps=react@{v_react},react-dom@{v_react}&external=react,react-is",
                "@emotion/styled": f"https://esm.sh/@emotion/styled?deps=react@{v_react},react-dom@{v_react}&external=react,react-is",
            })
        for k, v in imports.items():
            if '?' not in v and 'esm.sh' in v:
                if v.endswith('/'):
                    v = f'{v[:-1]}?{suffix}&path=/'
                else:
                    v = f'{v}?{suffix}'
            imports_with_deps[k] = v
        return {
            'imports': imports_with_deps,
            'scopes': cls._importmap.get('scopes', {})
        }

    def _get_properties(self, doc: Document | None) -> dict[str, Any]:
        props = super()._get_properties(doc)
        props['use_shadow_dom'] = self.use_shadow_dom
        return props


class AnyWidgetComponent(ReactComponent):
    '''
    The `AnyWidgetComponent` allows you to create custom Panel components
    in the style of an AnyWidget component. Specifically this component
    type creates shims that make it possible to reuse AnyWidget ESM code
    as is, without having to adapt the callbacks to use Bokeh APIs.

    Reference: https://panel.holoviz.org/reference/custom_components/AnyWidgetComponent.html

    :Example:

    .. code-block:: python

        import param
        import panel as pn

        pn.extension()

        class CounterWidget(pn.custom.AnyWidgetComponent):
            _esm = """
            function render({ model, el }) {
            let count = () => model.get("value");
            let btn = document.createElement("button");
            btn.innerHTML = `count is ${count()}`;
            btn.addEventListener("click", () => {
                model.set("value", count() + 1);
                model.save_changes();
            });
            model.on("change:value", () => {
                btn.innerHTML = `count is ${count()}`;
            });
            el.appendChild(btn);
            }
            export default { render };
            """
            value = param.Integer()

        CounterWidget().servable()
    '''

    __abstract = True

    _bokeh_model = _BkAnyWidgetComponent

    _react_version = "19"

    def send(self, msg: dict):
        """
        Sends a custom event containing the provided message to the frontend.

        Parameters
        ----------
        msg: dict
        """
        self._send_msg(msg)

    def _get_properties(self, doc: Document | None) -> dict[str, Any]:
        props = super()._get_properties(doc)
        del props['use_shadow_dom']
        return props
