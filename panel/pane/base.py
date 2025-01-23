"""
Defines base classes for Pane components which allow wrapping a Python
object transforming it into a Bokeh model that can be rendered.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
from typing import (
    TYPE_CHECKING, Any, ClassVar, TypeVar,
)

import numpy as np
import param

from bokeh.models import ImportedStyleSheet
from bokeh.models.layouts import (
    GridBox as _BkGridBox, TabPanel as _BkTabPanel, Tabs as _BkTabs,
)

from .._param import Margin
from ..io.cache import _generate_hash
from ..io.document import create_doc_if_none_exists, unlocked
from ..io.notebook import push
from ..io.state import state
from ..layout.base import (
    Column, ListPanel, NamedListPanel, Panel, Row,
)
from ..links import Link
from ..models import ReactiveHTML as _BkReactiveHTML
from ..reactive import Reactive
from ..util import param_reprs
from ..util.checks import is_dataframe, is_series
from ..util.parameters import get_params_to_inherit
from ..viewable import (
    Layoutable, ServableMixin, Viewable, Viewer,
)

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

def panel(obj: Any, **kwargs) -> Viewable | ServableMixin:
    """
    Creates a displayable Panel object given any valid Python object.

    The appropriate Pane to render a specific object is determined by
    iterating over all defined Pane types and querying it's `.applies`
    method for a priority value.

    Any keyword arguments are passed down to the applicable Pane.

    Setting `loading_indicator=True` will display a loading indicator while the function is being
    evaluated.

    To lazily render components when the application loads, you may also provide a Python
    function, with or without bound parameter dependencies and set
    `defer_load=True`.

    Reference: https://panel.holoviz.org/explanation/components/components_overview.html#panes

    >>> pn.panel(some_python_object, width=500)

    Parameters
    ----------
    obj: object
       Any object to be turned into a Panel
    **kwargs: dict
       Any keyword arguments to be passed to the applicable Pane

    Returns
    -------
    layout: Viewable
       A Viewable representation of the input object
    """
    if isinstance(obj, (Viewable, ServableMixin)):
        return obj
    elif hasattr(obj, '__panel__'):
        if isinstance(obj, Viewer):
            return obj._create_view()
        if isinstance(obj, type) and issubclass(obj, Viewer):
            return panel(obj().__panel__())
        return panel(obj.__panel__())
    if kwargs.get('name', False) is None:
        kwargs.pop('name')
    pane = PaneBase.get_pane_type(obj, **kwargs)(obj, **kwargs)
    if len(pane.layout) == 1 and pane._unpack:
        return pane.layout[0]
    return pane.layout


class RerenderError(RuntimeError):
    """
    Error raised when a pane requests re-rendering during initial render.
    """

    def __init__(self, *args, layout=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = layout


T = TypeVar('T', bound='PaneBase')


class PaneBase(Layoutable):
    """
    PaneBase represents an abstract baseclass which can be used as a
    mix-in class to define a component that mirrors the Pane API.
    This means that this component will participate in the automatic
    resolution of the appropriate pane type when Panel is asked to
    render an object of unknown type.

    The resolution of the appropriate pane type can be implemented
    using the ``applies`` method and the ``priority`` class attribute.
    The applies method should either return a boolean value indicating
    whether the pane can render the supplied object. If it can the
    priority determines which of the panes that apply will be selected.
    If the priority is None then the ``applies`` method must return
    a priority value.
    """

    default_layout = param.ClassSelector(default=Row, class_=(Panel),
                                         is_instance=False, doc="""
        Defines the layout the model(s) returned by the pane will
        be placed in.""")

    margin = Margin(default=(5, 10), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    object = param.Parameter(default=None, allow_refs=True, doc="""
        The object being wrapped, which will be converted to a
        Bokeh model.""")

    # When multiple Panes apply to an object, the one with the highest
    # numerical priority is selected. The default is an intermediate value.
    # If set to None, applies method will be called to get a priority
    # value for a specific object type.
    priority: ClassVar[float | bool | None] = 0.5

    # Whether applies requires full set of keywords
    _applies_kw: ClassVar[bool] = False

    _skip_layoutable: tuple[str, ...] = ('css_classes', 'margin', 'name')

    # Whether the Pane layout can be safely unpacked
    _unpack: ClassVar[bool] = True

    __abstract = True

    def __init__(self, object=None, **params):
        self._object_changing = False
        super().__init__(object=object, **params)
        if not hasattr(self, '_internal_callbacks'):
            self._internal_callbacks = []
        applies = self.applies(self.object, **(params if self._applies_kw else {}))
        if (isinstance(applies, bool) and not applies) and self.object is not None:
            self._type_error(self.object)

        kwargs = {
            k: v for k, v in params.items() if k in Layoutable.param and
            k not in self._skip_layoutable
        }
        self.layout = self.default_layout(self, **kwargs)
        self._internal_callbacks.append(
            self.param.watch(self._sync_layoutable, list(Layoutable.param))
        )
        self._sync_layoutable()

    def _validate_ref(self, pname, value):
        super()._validate_ref(pname, value)
        if pname == 'object' and not self._applies_kw:
            applies = self.applies(value)
            if isinstance(applies, bool) and not applies:
                raise RuntimeError('Value is not valid.')

    def _sync_layoutable(self, *events: param.parameterized.Event):
        included = set(Layoutable.param) - set(self._skip_layoutable)
        if events:
            kwargs = {
                event.name: event.new for event in events if event.name in included
            }
        else:
            kwargs = {
                k: v for k, v in self.param.values().items() if k in included
            }
        if self.margin:
            margin = self.margin
            if isinstance(margin, tuple):
                if len(margin) == 2:
                    t = b = margin[0]
                    r = l = margin[1]
                else:
                    t, r, b, l = margin
            else:
                t = r = b = l = margin
            if kwargs.get('width') is not None:
                kwargs['width'] = kwargs['width'] + l + r
            if kwargs.get('height') is not None:
                kwargs['height'] = kwargs['height'] + t + b
        old_values = self.layout.param.values()
        self.layout.param.update({k: v for k, v in kwargs.items() if v != old_values[k]})

    def _type_error(self, object):
        raise ValueError(f"{type(self).__name__} pane does not support objects of type '{type(object).__name__}'.")

    def __repr__(self, depth: int = 0) -> str:
        cls = type(self).__name__
        params = param_reprs(self, ['object'])
        obj = 'None' if self.object is None else type(self.object).__name__
        template = '{cls}({obj}, {params})' if params else '{cls}({obj})'
        return template.format(cls=cls, params=', '.join(params), obj=obj)

    def __getitem__(self, index: int | str) -> Viewable:
        """
        Allows pane objects to behave like the underlying layout
        """
        return self.layout[index]

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        """
        Returns boolean or float indicating whether the Pane
        can render the object.

        If the priority of the pane is set to
        `None`, this method may also be used to define a float priority
        depending on the object being rendered.
        """
        return None

    @classmethod
    def get_pane_type(cls, obj: Any, **kwargs) -> type[PaneBase]:
        """
        Returns the applicable Pane type given an object by resolving
        the precedence of all types whose applies method declares that
        the object is supported.

        Parameters
        ----------
        obj (object): The object type to return a Pane type for

        Returns
        -------
        The applicable Pane type with the highest precedence.
        """
        if isinstance(obj, Viewable):
            return type(obj)
        descendents = []
        for p in param.concrete_descendents(PaneBase).values():
            if p.priority is None:
                applies = True
                try:
                    priority = p.applies(obj, **(kwargs if p._applies_kw else {}))
                except Exception:
                    priority = False
            else:
                applies = None
                priority = p.priority
            if isinstance(priority, bool) and priority:
                raise ValueError('If a Pane declares no priority '
                                 'the applies method should return a '
                                 'priority value specific to the '
                                 f'object type or False, but the {p.__name__} pane '
                                 'declares no priority.')
            elif priority is None or priority is False:
                continue
            descendents.append((priority, applies, p))
        pane_types = reversed(sorted(descendents, key=lambda x: x[0]))
        for _, applies, pane_type in pane_types:
            if applies is None:
                try:
                    applies = pane_type.applies(obj, **(kwargs if pane_type._applies_kw else {}))
                except Exception:
                    applies = False
            if not applies:
                continue
            return pane_type
        raise TypeError(f'{type(obj).__name__} type could not be rendered.')


class Pane(PaneBase, Reactive):
    """
    Pane is the abstract baseclass for all atomic displayable units
    in the Panel library.

    Panes defines an extensible interface for wrapping arbitrary
    objects and transforming them into renderable components.

    Panes are reactive in the sense that when the object they are
    wrapping is replaced or modified the UI will reflect the updated
    object.
    """

    # Declares whether Pane supports updates to the Bokeh model
    _updates: ClassVar[bool] = False

    # Mapping from parameter name to bokeh model property name
    _rename: ClassVar[Mapping[str, str | None]] = {
        'default_layout': None, 'loading': None
    }

    # List of parameters that trigger a rerender of the Bokeh model
    _rerender_params: ClassVar[list[str]] = ['object']

    __abstract = True

    def __init__(self, object=None, **params):
        super().__init__(object=object, **params)
        self._internal_callbacks.append(
            self.param.watch(self._update_pane, self._rerender_params)
        )

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    @property
    def _linked_properties(self) -> tuple[str, ...]:
        return tuple(
            self._property_mapping.get(p, p) for p in self.param
            if p not in PaneBase.param and self._property_mapping.get(p, p) is not None
        )

    @property
    def _linkable_params(self) -> list[str]:
        return [p for p in self._synced_params if self._property_mapping.get(p, False) is not None]

    @property
    def _synced_params(self) -> list[str]:
        ignored_params = [
            'name', 'default_layout', 'loading', 'stylesheets'
        ] + self._rerender_params
        return [p for p in self.param if p not in ignored_params and not p.startswith('_')]

    def _param_change(self, *events: param.parameterized.Event) -> None:
        if self._object_changing:
            return
        super()._param_change(*events)

    def _update_object(
        self, ref: str, doc: Document, root: Model, parent: Model, comm: Comm | None
    ) -> None:
        old_model = self._models[ref][0]
        if self._updates:
            self._update(ref, old_model)
            return

        new_model = self._get_model(doc, root, parent, comm)

        # Ensure we also update any fake root referencing the object
        from ..io import state
        ref = root.ref['id']
        fake_view = fake_ref = fake_root = None
        if ref in state._views:
            view = state._views[ref][0]
            for fake_ref in state._fake_roots:
                if fake_ref not in state._views:
                    continue
                fake_view, fake_root = state._views[fake_ref][:2]
        if fake_ref in self._models:
            self._models[fake_ref] = (new_model, self._models[fake_ref][1])
        if hasattr(self, '_plots') and fake_ref in self._plots:
            self._plots[fake_ref] = self._plots[ref]

        try:
            if isinstance(parent, _BkGridBox):
                indexes: list[int] = []
                for i, child in enumerate(parent.children):  # type: ignore
                    if child[0] is old_model:
                        indexes.append(i)
                if indexes:
                    index = indexes[0]
                    new_model = (new_model,) + parent.children[index][1:]  # type: ignore
                    parent.children[index] = new_model  # type: ignore
                else:
                    raise ValueError
            elif isinstance(parent, _BkReactiveHTML):
                for node, children in parent.children.items():
                    if old_model in children:
                        index = children.index(old_model)
                        new_models = list(children)
                        new_models[index] = new_model
                        parent.children[node] = new_models  # type: ignore
                        break
            elif isinstance(parent, _BkTabs):
                index = [tab.child for tab in parent.tabs].index(old_model)
                old_tab = parent.tabs[index]  # type: ignore
                props = dict(old_tab.properties_with_values(), child=new_model)
                parent.tabs[index] = _BkTabPanel(**props)  # type: ignore
            else:
                index = parent.children.index(old_model)
                parent.children[index] = new_model
        except ValueError:
            self.param.warning(
                f'{type(self).__name__} pane model {old_model!r} could not be '
                f'replaced with new model {new_model!r}, ensure that the parent '
                'is not modified at the same time the panel is being updated.'
            )
            return

        layout_parent = self.layout._models.get(ref, [None])[0]
        if parent is layout_parent:
            parent.update(**self.layout._compute_sizing_mode(
                parent.children,
                dict(
                    sizing_mode=self.layout.sizing_mode,
                    styles=self.layout.styles,
                    width=self.layout.width,
                    min_width=self.layout.min_width,
                    margin=self.layout.margin
                )
            ))

        # If there is a fake root we run pre-processors on it
        if fake_view is not None and view in fake_view and fake_root:
            fake_view._preprocess(fake_root, self)
        else:
            view._preprocess(root, self)

    def _update_pane(self, *events) -> None:
        for ref, (_, parent) in self._models.copy().items():
            if ref not in state._views or ref in state._fake_roots:
                continue
            viewable, root, doc, comm = state._views[ref]
            if comm or state._unblocked(doc):
                with unlocked():
                    self._update_object(ref, doc, root, parent, comm)
                if comm and 'embedded' not in root.tags:
                    push(doc, comm)
            else:
                cb = partial(self._update_object, ref, doc, root, parent, comm)
                if doc.session_context:
                    doc.add_next_tick_callback(cb)
                else:
                    cb()

    def _update(self, ref: str, model: Model) -> None:
        """
        If _updates=True this method is used to update an existing
        Bokeh model instead of replacing the model entirely. The
        supplied model should be updated with the current state.
        """
        raise NotImplementedError

    def _get_root_model(
        self, doc: Document, comm: Comm | None = None,
        preprocess: bool = True
    ) -> tuple[Viewable, Model]:
        if self._updates:
            root = self._get_model(doc, comm=comm)
            root_view = self
        else:
            root = self.layout._get_model(doc, comm=comm)
            root_view = self.layout
        if preprocess:
            self._preprocess(root)
        return root_view, root

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def clone(self: T, object: Any | None = None, **params) -> T:
        """
        Makes a copy of the Pane sharing the same parameters.

        Parameters
        ----------
        object: Optional new object to render
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned Pane object
        """
        inherited = get_params_to_inherit(self)
        params = dict(inherited, **params)
        old_object = params.pop('object', None)
        if object is None:
            object = old_object
        return type(self)(object, **params)

    def get_root(
        self, doc: Document | None = None, comm: Comm | None = None,
        preprocess: bool = True
    ) -> Model:
        """
        Returns the root model and applies pre-processing hooks

        Parameters
        ----------
        doc: bokeh.document.Document
          Optional Bokeh document the bokeh model will be attached to.
        comm: pyviz_comms.Comm
          Optional pyviz_comms when working in notebook
        preprocess: bool (default=True)
          Whether to run preprocessing hooks

        Returns
        -------
        Returns the bokeh model corresponding to this panel object
        """
        doc = create_doc_if_none_exists(doc)
        if self._design and comm:
            wrapper = self._design._wrapper(self)
            if wrapper is self:
                root_view, root = self._get_root_model(doc, comm, preprocess)
            else:
                root_view = wrapper
                root = wrapper.get_root(doc, comm, preprocess)
        else:
            root_view, root = self._get_root_model(doc, comm, preprocess)
        ref = root.ref['id']
        state._views[ref] = (root_view, root, doc, comm)
        return root


class ModelPane(Pane):
    """
    ModelPane provides a baseclass that allows quickly wrapping a
    Bokeh model and translating parameters defined on the class
    with properties defined on the model.

    In simple cases subclasses only have to define the Bokeh model to
    render to and the `_transform_object` method which transforms the
    Python object being wrapped into properties that the
    `bokeh.model.Model` can consume.
    """

    _bokeh_model: ClassVar[type[Model] | None] = None

    __abstract = True

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        if self._bokeh_model is None:
            raise NotImplementedError(
                f'Pane {type(self).__name__} did not define a _bokeh_model'
            )
        model = self._bokeh_model(**self._get_properties(doc))
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, self._linked_properties, doc, root, comm)
        return model

    def _update(self, ref: str, model: Model) -> None:
        model.update(**self._get_properties(model.document))

    def _init_params(self):
        params = {
            p: v for p, v in self.param.values().items()
            if v is not None and p not in ('name', 'default_layout')
        }
        params['object'] = self.object
        return params

    def _transform_object(self, obj: Any) -> dict[str, Any]:
        return dict(object=obj)

    def _process_param_change(self, params):
        if 'object' in params:
            params.update(self._transform_object(params.pop('object')))
        if self._bokeh_model is not None and 'stylesheets' in params:
            css = getattr(self._bokeh_model, '__css__', [])
            params['stylesheets'] = [
                ImportedStyleSheet(url=ss) for ss in css
            ] + params['stylesheets']
        return super()._process_param_change(params)


class ReplacementPane(Pane):
    """
    ReplacementPane provides a baseclass for dynamic components that
    may have to dynamically update or switch out their contents, e.g.
    a dynamic callback that may return different objects to be rendered.

    When the pane updates it either entirely replaces the underlying
    `bokeh.model.Model`, by creating an internal layout to replace the
    children on, or updates the existing model in place.
    """

    inplace = param.Boolean(default=False, doc="""
        Whether to update the object inplace.""")

    object = param.Parameter(default=None, allow_refs=False, doc="""
        The object being wrapped, which will be converted to a
        Bokeh model.""")

    _pane = param.ClassSelector(class_=Viewable, allow_refs=False)

    _ignored_refs: ClassVar[tuple[str,...]] = ('object',)

    _linked_properties: tuple[str,...] = ()

    _rename: ClassVar[Mapping[str, str | None]] = {'_pane': None, 'inplace': None}

    _updates: ClassVar[bool] = True

    __abstract = True

    def __init__(self, object: Any=None, **params):
        self._kwargs =  {p: params.pop(p) for p in list(params)
                         if p not in self.param}
        super().__init__(object, **params)
        self._pane = panel(None)
        self._internal = True
        self._inner_layout = Column(self._pane, **{k: v for k, v in params.items() if k in Column.param})
        self._internal_callbacks.append(
            self.param.watch(self._update_inner_layout, list(Layoutable.param))
        )
        self._sync_layout()

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        if root:
            ref = root.ref['id']
            if ref in self._models:
                self._cleanup(root)
        model = self._inner_layout._get_model(doc, root, parent, comm)
        root = root or model
        self._models[root.ref['id']] = (model, parent)
        return model

    @param.depends('_pane', '_pane.sizing_mode', '_pane.width_policy', '_pane.height_policy', watch=True)
    def _sync_layout(self):
        if not hasattr(self, '_inner_layout') or (self._pane is not None and getattr(self._pane, '_object_changing', False)):
            return
        self._inner_layout.param.update({
            k: v for k, v in self._pane.param.values().items()
            if k in ('sizing_mode', 'width_policy', 'height_policy')
        })

    def _update_inner_layout(self, *events):
        self._pane.param.update({event.name: event.new for event in events})

    @classmethod
    def _recursive_update(cls, old: Reactive, new: Reactive):
        """
        Recursively descends through Panel layouts and diffs their
        contents updating only changed parameters ensuring we don't
        have to trigger a full re-render of the entire component.

        Parameters
        ----------
        old: Reactive
          The Reactive component being updated or replaced.
        new: Reactive
          The new Reactive component that the old one is being updated
          or replaced with.
        """
        ignored: tuple[str, ...] = ('name',)
        if isinstance(new, ListPanel):
            if len(old) == len(new):
                for i, (sub_old, sub_new) in enumerate(zip(old, new)):
                    if type(sub_old) is not type(sub_new):
                        old[i] = new
                        continue
                    if isinstance(new, NamedListPanel):
                        old._names[i] = new._names[i]
                    cls._recursive_update(sub_old, sub_new)
                ignored += ('objects',)
        pvals = dict(old.param.values())
        new_params = {}
        for p, p_new in new.param.values().items():
            p_old = pvals[p]
            if p in ignored or p_new is p_old:
                continue
            try:
                equal = p_new == p_old
                if is_dataframe(equal) or is_series(equal) or isinstance(equal, np.ndarray):
                    equal = equal.all()
                equal = bool(equal)
            except Exception:
                try:
                    equal = _generate_hash(p_new) == _generate_hash(p_old)
                except Exception:
                    equal = False
            if not equal:
                new_params[p] = p_new
        if isinstance(old, PaneBase):
            changing = any(p in old._rerender_params for p in new_params)
            old._object_changing = changing
            try:
                with param.edit_constant(old):
                    old.param.update(**new_params)
            finally:
                old._object_changing = False
        else:
            with param.edit_constant(old):
                old.param.update(**new_params)

    @classmethod
    def _update_from_object(cls, object: Any, old_object: Any, was_internal: bool, inplace: bool=False, **kwargs):
        pane_type = cls.get_pane_type(object)
        try:
            links = Link.registry.get(object)
        except TypeError:
            links = []
        custom_watchers = []
        if isinstance(object, Reactive):
            watchers = [
                w for pwatchers in object.param.watchers.values()
                for awatchers in pwatchers.values() for w in awatchers
            ]
            custom_watchers = [
                wfn for wfn in watchers if wfn not in object._internal_callbacks and
                not hasattr(wfn.fn, '_watcher_name')
            ]

        pane, internal = None, was_internal
        # If the object has no external referrers we can update
        # it inplace instead of replacing it
        if type(old_object) is pane_type and ((not links and not custom_watchers and was_internal) or inplace):
            if isinstance(object, Panel) and len(old_object) == len(object):
                for i, (old, new) in enumerate(zip(old_object, object)):
                    if type(old) is not type(new):
                        old_object[i] = new
                        continue
                    cls._recursive_update(old, new)
            elif isinstance(object, Reactive):
                cls._recursive_update(old_object, object)
            elif old_object.object is not object:
                # See https://github.com/holoviz/param/pull/901
                old_object.object = object
        else:
            # Replace pane entirely
            pane_params = {k: v for k, v in kwargs.items() if k in pane_type.param}
            pane = panel(object, **pane_params)
            internal = pane is not object
        return pane, internal

    def _update_inner(self, new_object: Any) -> None:
        kwargs = dict(self.param.values(), **self._kwargs)
        del kwargs['object']
        new_pane, internal = self._update_from_object(
            new_object, self._pane, self._internal, **kwargs
        )
        if new_pane is None:
            return

        self._pane = new_pane
        self._inner_layout[:] = [self._pane]
        self._internal = internal

    def _cleanup(self, root: Model | None = None) -> None:
        self._inner_layout._cleanup(root)
        super()._cleanup(root)

    #----------------------------------------------------------------
    # Developer API
    #----------------------------------------------------------------

    def _update_pane(self, *events) -> None:
        """
        Updating of the object should be handled manually.
        """

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def select(self, selector: type | Callable | None = None) -> list[Viewable]:
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Parameters
        ----------
        selector: (type | callable | None)
          The selector allows selecting a subset of Viewables by
          declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        selected = super().select(selector)
        selected += self._inner_layout.select(selector)
        return selected
