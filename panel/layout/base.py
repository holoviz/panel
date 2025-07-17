"""
Defines Layout classes which may be used to arrange panes and widgets
in flexible ways to build complex dashboards.
"""
from __future__ import annotations

from collections import defaultdict, namedtuple
from collections.abc import (
    Generator, Iterable, Iterator, Mapping,
)
from typing import (
    TYPE_CHECKING, Any, ClassVar, overload,
)

import param

from bokeh.models import Row as BkRow
from param.parameterized import iscoroutinefunction, resolve_ref

from ..io.document import freeze_doc, hold
from ..io.resources import CDN_DIST
from ..models.layout import Column as PnColumn, ScrollToEvent
from ..reactive import Reactive
from ..util import param_name, param_reprs
from ..viewable import Children, Viewable

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..viewable import Viewable

_SCROLL_MAPPING = {
    'both-auto': 'scrollable',
    'x-auto': 'scrollable-horizontal',
    'y-auto': 'scrollable-vertical',
    'both': 'scroll',
    'x': 'scroll-horizontal',
    'y': 'scroll-vertical',
}

_row = namedtuple("row", ["children"]) # type: ignore
_col = namedtuple("col", ["children"]) # type: ignore


class SizingModeMixin:
    """
    Mixin class to add support for computing sizing modes from the children
    based on the direction the layout flows in.
    """

    # Direction the layout flows in
    _direction: ClassVar[str | None] = None

    def _compute_sizing_mode(self, children, props):
        """
        Handles inference of correct layout sizing mode by inspecting
        the children and adapting to their layout properties. This
        aims to provide a layer of backward compatibility for the
        layout behavior before v1.0 and provide general usability
        improvements.

        The code iterates over the children and extracts their sizing_mode,
        width and height. Based on these values we infer a few overrides
        for the container sizing_mode, width and height:

        - If a child is responsive in width then the container should
          also be responsive in width (unless it has a fixed size).
        - If a container is vertical (e.g. a Column) and a child is
          responsive in height then the container should also be
          responsive.
        - If a container is horizontal (e.g. a Row) and all children
          are responsive in height then the container should also be
          responsive. This behavior is asymmetrical with height
          because there isn't always vertical space to expand into
          and it is better for the component to match the height of
          the other children.
        - Always compute the fixed sizes of the children (if available)
          and provide this as min_width and min_height settings to
          ensure sufficient space is available.
        """
        margin = props.get('margin', self.margin)
        if margin is None:
            margin = 0
        sizing_mode = props.get('sizing_mode', self.sizing_mode)
        if sizing_mode == 'fixed':
            return {}

        # Iterate over children and determine responsiveness along
        # each axis, scaling and the widths of each component.
        heights, widths = [], []
        all_expand_height, expand_width, expand_height, scale = True, self.width_policy=="max", self.height_policy=="max", False

        for child in children:
            smode = child.sizing_mode
            if smode and 'scale' in smode:
                scale = True

            width_expanded = smode in ('stretch_width', 'stretch_both', 'scale_width', 'scale_both')
            height_expanded = smode in ('stretch_height', 'stretch_both', 'scale_height', 'scale_both')
            expand_width |= width_expanded
            expand_height |= height_expanded
            if width_expanded:
                width = child.min_width
            else:
                width = child.width
                if not child.width:
                    width = child.min_width
            if width:
                if isinstance(margin, tuple):
                    if len(margin) == 2:
                        width += margin[1]*2
                    else:
                        width += margin[1] + margin[3]
                else:
                    width += margin*2
                widths.append(width)

            if height_expanded:
                height = child.min_height
            else:
                height = child.height
                if height:
                    all_expand_height = False
                else:
                    height = child.min_height
            if height:
                if isinstance(margin, tuple):
                    if len(margin) == 2:
                        height += margin[0]*2
                    else:
                        height += margin[0] + margin[2]
                else:
                    height += margin*2
                heights.append(height)

        # Infer new sizing mode based on children
        mode = 'scale' if scale else 'stretch'
        if self._direction == 'horizontal':
            allow_height_scale = all_expand_height
        else:
            allow_height_scale = True

        if expand_width and expand_height and not self.width and not self.height:
            if allow_height_scale or 'both' in (sizing_mode or ''):
                sizing_mode = f'{mode}_both'
            else:
                sizing_mode = f'{mode}_width'
        elif expand_width and not self.width:
            sizing_mode = f'{mode}_width'
        elif expand_height and not self.height and allow_height_scale:
            sizing_mode = f'{mode}_height'
        if sizing_mode is None:
            return {'sizing_mode': props.get('sizing_mode')}

        properties = {'sizing_mode': sizing_mode}
        if (sizing_mode.endswith(("_width", "_both")) and
            widths and 'min_width' not in properties):
            width_op = max if self._direction in ('vertical', None) else sum
            min_width = width_op(widths)
            op_widths = [min_width]
            if 'max_width' in properties:
                op_widths.append(properties['max_width'])
            properties['min_width'] = min(op_widths)
        if (sizing_mode.endswith(("_height", "_both")) and
            heights and 'min_height' not in properties):
            height_op = max if self._direction in ('horizontal', None) else sum
            min_height = height_op(heights)
            op_heights = [min_height]
            if 'max_height' in properties:
                op_heights.append(properties['max_height'])
            properties['min_height'] = min(op_heights)
        return properties


class Panel(Reactive, SizingModeMixin):
    """
    Abstract baseclass for a layout of Viewables.
    """

    # Used internally to optimize updates
    _batch_update: ClassVar[bool] = False

    # Bokeh model used to render this Panel
    _bokeh_model: ClassVar[type[Model]]

    # Parameters which require the preprocessors to be re-run
    _preprocess_params: ClassVar[list[str]] = []

    # Parameter -> Bokeh property renaming
    _rename: ClassVar[Mapping[str, str | None]] = {'objects': 'children'}

    __abstract = True

    def __repr__(self, depth: int = 0, max_depth: int = 10) -> str:
        if depth > max_depth:
            return '...'
        spacer = '\n' + ('    ' * (depth+1))
        cls = type(self).__name__
        params = param_reprs(self, ['objects'])
        objs = [f'[{i}] {obj.__repr__(depth+1)}' for i, obj in enumerate(self)]
        if not params and not objs:
            return super().__repr__(depth+1)

        if not params:
            template = '{cls}{spacer}{objs}'
        elif not objs:
            template = '{cls}({params})'
        else:
            template = '{cls}({params}){spacer}{objs}'
        return template.format(
            cls=cls, params=', '.join(params),
            objs=str(spacer).join(objs), spacer=spacer
        )

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    def _update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Comm | None
    ) -> None:
        msg = dict(msg)
        inverse = {v: k for k, v in self._property_mapping.items() if v is not None}
        preprocess = any(inverse.get(k, k) in self._preprocess_params for k in msg)

        # ALERT: Find a better way to handle this
        if 'styles' in msg and root is model and 'overflow-x' in msg['styles']:
            del msg['styles']['overflow-x']

        obj_key = self._property_mapping['objects']
        update_children = obj_key in msg
        if update_children:
            old = events['objects'].old
            children, old_children = self._get_objects(model, old, doc, root, comm)
            msg[obj_key] = children

            msg.update(self._compute_sizing_mode(
                children,
                dict(
                    sizing_mode=msg.get('sizing_mode', model.sizing_mode),
                    styles=msg.get('styles', model.styles),
                    width=msg.get('width', model.width),
                    min_width=msg.get('min_width', model.min_width),
                    margin=msg.get('margin', model.margin)
                )
            ))
        else:
            old_children = None

        with hold(doc):
            update = Panel._batch_update
            Panel._batch_update = True
            try:
                with freeze_doc(doc, model, msg, force=update_children):
                    super()._update_model(events, msg, root, model, doc, comm)
                    if update:
                        return
                    from ..io import state
                    ref = root.ref['id']
                    if ref in state._views and preprocess:
                        state._views[ref][0]._preprocess(root, self, old_children)
            finally:
                Panel._batch_update = update

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _get_objects(
        self, model: Model, old_objects: list[Viewable], doc: Document,
        root: Model, comm: Comm | None = None
    ):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from ..pane.base import RerenderError
        new_models, old_models = [], []

        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)

        current_objects = list(self.objects)
        ref = root.ref['id']
        for i, pane in enumerate(self.objects):
            if ref in pane._models:
                child, _ = pane._models[root.ref['id']]
                old_models.append(child)
            else:
                try:
                    child = pane._get_model(doc, root, model, comm)
                except RerenderError as e:
                    if e.layout is not None and e.layout is not self:
                        raise e
                    e.layout = None
                    return self._get_objects(model, current_objects[:i], doc, root, comm)
            new_models.append(child)
        return new_models, old_models

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        if self._bokeh_model is None:
            raise ValueError(f'{type(self).__name__} did not define a _bokeh_model.')
        model = self._bokeh_model()
        root = root or model
        self._models[root.ref['id']] = (model, parent)
        objects, _ = self._get_objects(model, [], doc, root, comm)
        props = self._get_properties(doc)
        props[self._property_mapping['objects']] = objects
        props.update(self._compute_sizing_mode(objects, props))
        model.update(**props)
        self._link_props(model, self._linked_properties, doc, root, comm)
        return model

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def get_root(
        self, doc: Document | None = None, comm: Comm | None = None,
        preprocess: bool = True
    ) -> Model:
        root = super().get_root(doc, comm, preprocess)
        # ALERT: Find a better way to handle this
        if hasattr(root, 'styles') and 'overflow-x' in root.styles:
            del root.styles['overflow-x']
        return root

    def select(self, selector=None):
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
        objects = super().select(selector)
        for obj in self:
            objects += obj.select(selector)
        return objects


class ListLike(param.Parameterized):

    objects = Children(default=[], doc="""
        The list of child objects that make up the layout.""")

    _preprocess_params: ClassVar[list[str]] = ['objects']

    def __init__(self, *objects: Any, **params: Any):
        if objects:
            if 'objects' in params:
                raise ValueError(
                    f"A {type(self).__name__}'s objects should be supplied either "
                    "as positional arguments or as a keyword, not both."
                )
            params['objects'] = list(objects)
        elif 'objects' in params:
            objects = params['objects']
            if not (resolve_ref(objects) or iscoroutinefunction(objects) or isinstance(objects, Generator)):
                params['objects'] = list(objects)
        super().__init__(**params)

    def __getitem__(self, index: int | slice) -> Viewable | list[Viewable]:
        return self.objects[index]

    def __len__(self) -> int:
        return len(self.objects)

    def __iter__(self) -> Iterator[Viewable]:
        yield from self.objects

    def __iadd__(self, other: Iterable[Any]) -> ListLike:
        self.extend(other)
        return self

    def __add__(self, other: Iterable[Any]) -> ListLike:
        if isinstance(other, ListLike):
            other = other.objects
        return self.clone(*self.objects, *other)

    def __radd__(self, other: Iterable[Any]) -> ListLike:
        if isinstance(other, ListLike):
            other = other.objects
        return self.clone(*other, *self.objects)

    def __contains__(self, obj: Viewable) -> bool:
        return obj in self.objects

    @overload
    def __setitem__(self, index: int, panes: Any) -> None: ...

    @overload
    def __setitem__(self, index: slice, panes: Iterable[Any]) -> None: ...

    def __setitem__(self, index, panes) -> None:
        new_objects = list(self)
        new_objects[index] = panes
        self.objects = new_objects

    def clone(self, *objects: Any, **params: Any) -> ListLike:
        """
        Makes a copy of the layout sharing the same parameters.

        Parameters
        ----------
        objects: Objects to add to the cloned layout.
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned layout object
        """
        if not objects:
            if 'objects' in params:
                objects = params.pop('objects')
            else:
                objects = self.objects
        elif 'objects' in params:
            raise ValueError(
                f"A {type(self).__name__}'s objects should be supplied either "
                "as arguments or as a keyword, not both."
            )
        p = dict(self.param.values(), **params)
        del p['objects']
        return type(self)(*objects, **p)

    def append(self, obj: Any) -> None:
        """
        Appends an object to the layout.

        Parameters
        ----------
        obj (object): Panel component to add to the layout.
        """
        new_objects = list(self)
        new_objects.append(obj)
        self.objects = new_objects

    def clear(self) -> list[Viewable]:
        """
        Clears the objects on this layout.

        Returns
        -------
        objects (list[Viewable]): List of cleared objects.
        """
        objects = self.objects
        self.objects = []
        return objects

    def extend(self, objects: Iterable[Any]) -> None:
        """
        Extends the objects on this layout with a list.

        Parameters
        ----------
        objects (list): List of panel components to add to the layout.
        """
        new_objects = list(self)
        new_objects.extend(objects)
        self.objects = new_objects

    def index(self, obj: Viewable) -> int:
        """
        Returns the integer index of the supplied object in the list of objects.

        Parameters
        ----------
        obj (Viewable): Panel component to look up the index for.

        Returns
        -------
        index (int): Integer index of the object in the layout.
        """
        return self.objects.index(obj)

    def insert(self, index: int, obj: Any) -> None:
        """
        Inserts an object in the layout at the specified index.

        Parameters
        ----------
        index (int): Index at which to insert the object.
        object (object): Panel components to insert in the layout.
        """
        new_objects = list(self)
        new_objects.insert(index, obj)
        self.objects = new_objects

    def pop(self, index: int = -1) -> Viewable:
        """
        Pops an item from the layout by index.

        Parameters
        ----------
        index (int): The index of the item to pop from the layout.
        """
        new_objects = list(self)
        obj = new_objects.pop(index)
        self.objects = new_objects
        return obj

    def remove(self, obj: Viewable) -> None:
        """
        Removes an object from the layout.

        Parameters
        ----------
        obj (object): The object to remove from the layout.
        """
        new_objects = list(self)
        new_objects.remove(obj)
        self.objects = new_objects

    def reverse(self) -> None:
        """
        Reverses the objects in the layout.
        """
        new_objects = list(self)
        new_objects.reverse()
        self.objects = new_objects


class NamedListLike(param.Parameterized):

    objects = Children(default=[], doc="""
        The list of child objects that make up the layout.""")

    _preprocess_params: ClassVar[list[str]] = ['objects']

    def __init__(self, *items: list[Any | tuple[str, Any]], **params: Any):
        if 'objects' in params:
            if items:
                raise ValueError(
                    f'{type(self).__name__} objects should be supplied either '
                    'as positional arguments or as a keyword, not both.'
                )
            items = params.pop('objects')
        params['objects'], names = self._to_objects_and_names(items)
        super().__init__(**params)
        self._names = names
        self._panels: defaultdict[str, dict[int, Viewable]] = defaultdict(dict)
        self.param.watch(self._update_names, 'objects')
        # ALERT: Ensure that name update happens first, should be
        #        replaced by watch precedence support in param
        self.param.watchers['objects']['value'].reverse()

    def _to_object_and_name(self, item):
        from ..pane import panel
        if isinstance(item, tuple):
            name, item = item
        else:
            name = getattr(item, 'name', None)
        pane = panel(item, name=name)
        name = param_name(pane.name) if name is None else name
        return pane, name

    def _to_objects_and_names(self, items):
        objects, names = [], []
        for item in items:
            pane, name = self._to_object_and_name(item)
            objects.append(pane)
            names.append(name)
        return objects, names

    def _update_names(self, event: param.parameterized.Event) -> None:
        if len(event.new) == len(self._names):
            return
        names = []
        for obj in event.new:
            if obj in event.old:
                index = event.old.index(obj)
                name = self._names[index]
            else:
                name = obj.name
            names.append(name)
        self._names = names

    def _update_active(self, *events: param.parameterized.Event) -> None:
        pass

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def __getitem__(self, index) -> Viewable | list[Viewable]:
        return self.objects[index]

    def __len__(self) -> int:
        return len(self.objects)

    def __iter__(self) -> Iterator[Viewable]:
        yield from self.objects

    def __iadd__(self, other: Iterable[Any]) -> NamedListLike:
        self.extend(other)
        return self

    def __add__(self, other: Iterable[Any]) -> NamedListLike:
        added: Iterable
        if isinstance(other, NamedListLike):
            added = zip(other._names, other.objects)
        elif isinstance(other, ListLike):
            added = other.objects
        else:
            added = other
        objects = zip(self._names, self.objects)
        return self.clone(*objects, *added)

    def __radd__(self, other: Iterable[Any]) -> NamedListLike:
        added: Iterable
        if isinstance(other, NamedListLike):
            added = zip(other._names, other.objects)
        elif isinstance(other, ListLike):
            added = other.objects
        else:
            added = other
        objects = zip(self._names, self.objects)
        return self.clone(*added, *objects)

    @overload
    def __setitem__(self, index: int, panes: Any) -> None: ...

    @overload
    def __setitem__(self, index: slice, panes: Iterable[Any]) -> None: ...

    def __setitem__(self, index, panes):
        new_objects = list(self)
        if isinstance(index, slice):
            new_objects[index], self._names[index] = self._to_objects_and_names(panes)
        else:
            new_objects[index], self._names[index] = self._to_object_and_name(panes)
        self.objects = new_objects

    def clone(self, *objects: Any, **params: Any) -> NamedListLike:
        """
        Makes a copy of the Tabs sharing the same parameters.

        Parameters
        ----------
        objects: Objects to add to the cloned Tabs object.
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned Tabs object
        """
        if objects:
            overrides = objects
            if 'objects' in params:
                raise ValueError(
                    'Tabs objects should be supplied either as positional '
                    'arguments or as a keyword, not both.'
                )
        elif 'objects' in params:
            overrides = params.pop('objects')
        else:
            overrides = tuple(zip(self._names, self.objects))
        p = dict(self.param.values(), **params)
        del p['objects']
        return type(self)(*overrides, **params)

    def append(self, pane: Any) -> None:
        """
        Appends an object to the tabs.

        Parameters
        ----------
        obj (object): Panel component to add as a tab.
        """
        new_object, new_name = self._to_object_and_name(pane)
        new_objects = list(self)
        new_objects.append(new_object)
        self._names.append(new_name)
        self.objects = new_objects

    def clear(self) -> None:
        """
        Clears the tabs.
        """
        self._names = []
        self.objects = []

    def extend(self, panes: Iterable[Any]) -> None:
        """
        Extends the the tabs with a list.

        Parameters
        ----------
        objects (list): List of panel components to add as tabs.
        """
        new_objects, new_names = self._to_objects_and_names(panes)
        objects = list(self)
        objects.extend(new_objects)
        self._names.extend(new_names)
        self.objects = objects

    def insert(self, index: int, pane: Any) -> None:
        """
        Inserts an object in the tabs at the specified index.

        Parameters
        ----------
        index (int): Index at which to insert the object.
        object (object): Panel components to insert as tabs.
        """
        new_object, new_name = self._to_object_and_name(pane)
        new_objects = list(self.objects)
        new_objects.insert(index, new_object)
        self._names.insert(index, new_name)
        self.objects = new_objects

    def pop(self, index: int = -1) -> Viewable:
        """
        Pops an item from the tabs by index.

        Parameters
        ----------
        index (int): The index of the item to pop from the tabs.
        """
        new_objects = list(self)
        obj = new_objects.pop(index)
        self._names.pop(index)
        self.objects = new_objects
        return obj

    def remove(self, pane: Viewable) -> None:
        """
        Removes an object from the tabs.

        Parameters
        ----------
        obj (object): The object to remove from the tabs.
        """
        new_objects = list(self)
        if pane in new_objects:
            index = new_objects.index(pane)
            new_objects.remove(pane)
            self._names.pop(index)
            self.objects = new_objects
        else:
            raise ValueError(f'{pane!r} is not in list')

    def reverse(self) -> None:
        """
        Reverses the tabs.
        """
        new_objects = list(self)
        new_objects.reverse()
        self._names.reverse()
        self.objects = new_objects


class ListPanel(ListLike, Panel):
    """
    An abstract baseclass for Panel objects with list-like children.
    """

    scroll = param.Selector(
        default=False,
        objects=[False, True, "both-auto", "y-auto", "x-auto", "both", "x", "y"],
        doc="""Whether to add scrollbars if the content overflows the size
        of the container. If "both-auto", will only add scrollbars if
        the content overflows in either directions. If "x-auto" or "y-auto",
        will only add scrollbars if the content overflows in the
        respective direction. If "both", will always add scrollbars.
        If "x" or "y", will always add scrollbars in the respective
        direction. If False, overflowing content will be clipped.
        If True, will only add scrollbars in the direction of the container,
        (e.g. Column: vertical, Row: horizontal).""")

    _rename: ClassVar[Mapping[str, str | None]] = {'scroll': None}

    _source_transforms: ClassVar[Mapping[str, str | None]] = {'scroll': None}

    __abstract = True

    @property
    def _linked_properties(self) -> tuple[str, ...]:
        return tuple(
            self._property_mapping.get(p, p) for p in self.param
            if p not in ListPanel.param and self._property_mapping.get(p, p) is not None
        )

    def _process_param_change(self, params: dict[str, Any]) -> dict[str, Any]:
        if (scroll := params.get('scroll')):
            css_classes = params.get('css_classes', self.css_classes)
            if scroll in _SCROLL_MAPPING:
                scroll_class = _SCROLL_MAPPING[scroll]
            elif self._direction:
                scroll_class = f'scrollable-{self._direction}'
            else:
                scroll_class = 'scrollable'
            params['css_classes'] = css_classes + [scroll_class]
        return super()._process_param_change(params)

    def _cleanup(self, root: Model | None = None) -> None:
        super()._cleanup(root)
        for p in self.objects:
            p._cleanup(root)


class NamedListPanel(NamedListLike, Panel):

    active = param.Integer(default=0, bounds=(0, None), doc="""
        Index of the currently displayed objects.""")

    scroll = param.Selector(
        default=False,
        objects=[False, True, "both-auto", "y-auto", "x-auto", "both", "x", "y"],
        doc="""Whether to add scrollbars if the content overflows the size
        of the container. If "both-auto", will only add scrollbars if
        the content overflows in either directions. If "x-auto" or "y-auto",
        will only add scrollbars if the content overflows in the
        respective direction. If "both", will always add scrollbars.
        If "x" or "y", will always add scrollbars in the respective
        direction. If False, overflowing content will be clipped.
        If True, will only add scrollbars in the direction of the container,
        (e.g. Column: vertical, Row: horizontal).""")

    _rename: ClassVar[Mapping[str, str | None]] = {'scroll': None}

    _source_transforms: ClassVar[Mapping[str, str | None]] = {'scroll': None}

    __abstract = True

    def _process_param_change(self, params: dict[str, Any]) -> dict[str, Any]:
        if (scroll := params.get('scroll')):
            css_classes = params.get('css_classes', self.css_classes)
            if scroll in _SCROLL_MAPPING:
                scroll_class = _SCROLL_MAPPING[scroll]
            elif self._direction:
                scroll_class = f'scrollable-{self._direction}'
            else:
                scroll_class = 'scrollable'
            params['css_classes'] = css_classes + [scroll_class]
        return super()._process_param_change(params)

    def _cleanup(self, root: Model | None = None) -> None:
        super()._cleanup(root)
        for p in self.objects:
            p._cleanup(root)


class Row(ListPanel):
    """
    The `Row` layout allows arranging multiple panel objects in a horizontal
    container.

    It has a list-like API with methods to `append`, `extend`, `clear`,
    `insert`, `pop`, `remove` and `__setitem__`, which makes it possible to
    interactively update and modify the layout.

    Reference: https://panel.holoviz.org/reference/layouts/Row.html

    :Example:

    >>> pn.Row(some_widget, some_pane, some_python_object)
    """

    _bokeh_model: ClassVar[type[Model]] = BkRow

    _direction = 'horizontal'

    _stylesheets: ClassVar[list[str]] = [f'{CDN_DIST}css/listpanel.css']


class Column(ListPanel):
    """
    The `Column` layout allows arranging multiple panel objects in a vertical
    container.

    It has a list-like API with methods to `append`, `extend`, `clear`,
    `insert`, `pop`, `remove` and `__setitem__`, which makes it possible to
    interactively update and modify the layout.

    Reference: https://panel.holoviz.org/reference/layouts/Column.html

    :Example:

    >>> pn.Column(some_widget, some_pane, some_python_object)
    """

    auto_scroll_limit = param.Integer(bounds=(0, None), doc="""
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.""")

    scroll_button_threshold = param.Integer(bounds=(0, None), doc="""
        Min pixel distance from the latest object in the Column to
        display the scroll button. Setting to 0
        disables the scroll button.""")

    scroll_position = param.Integer(default=0, doc="""
        Current scroll position of the Column. Setting this value
        will update the scroll position of the Column. Setting to
        0 will scroll to the top.""")

    view_latest = param.Boolean(default=False, doc="""
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.""")

    _bokeh_model: ClassVar[type[Model]] = PnColumn

    _busy__ignore = ['scroll_position']

    _direction = 'vertical'

    _stylesheets: ClassVar[list[str]] = [f'{CDN_DIST}css/listpanel.css']

    @param.depends(
        "auto_scroll_limit",
        "scroll_button_threshold",
        "view_latest",
        watch=True,
        on_init=True
    )
    def _set_scrollable(self):
        self.scroll = (
            self.scroll or
            bool(self.scroll_position) or
            bool(self.auto_scroll_limit) or
            bool(self.scroll_button_threshold) or
            self.view_latest
        )

    def scroll_to(self, index: int):
        """
        Scrolls to the child at the provided index.

        Parameters
        ----------
        index: int
            Index of the child object to scroll to.
        """
        self._send_event(ScrollToEvent, index=index)


class WidgetBox(ListPanel):
    """
    The `WidgetBox` layout allows arranging multiple panel objects in a
    vertical (or horizontal) container.

    It is largely identical to the `Column` layout, but has some default
    styling that makes widgets be clearly grouped together visually.

    It has a list-like API with methods to `append`, `extend`, `clear`,
    `insert`, `pop`, `remove` and `__setitem__`, which make it possible to
    interactively update and modify the layout.

    Reference: https://panel.holoviz.org/reference/layouts/WidgetBox.html

    :Example:

    >>> pn.WidgetBox(some_widget, another_widget)
    """

    css_classes = param.List(default=['panel-widget-box'], doc="""
        CSS classes to apply to the layout.""")

    disabled = param.Boolean(default=False, doc="""
        Whether the widget is disabled.""")

    horizontal = param.Boolean(default=False, doc="""
        Whether to lay out the widgets in a Row layout as opposed
        to a Column layout.""")

    _source_transforms: ClassVar[Mapping[str, str | None]] = {
        'disabled': None, 'horizontal': None
    }

    _rename: ClassVar[Mapping[str, str | None]] = {
        'disabled': None, 'objects': 'children', 'horizontal': None
    }

    _stylesheets: ClassVar[list[str]] = [
        f'{CDN_DIST}css/widgetbox.css', f'{CDN_DIST}css/listpanel.css'
    ]

    @property
    def _bokeh_model(self) -> type[Model]: # type: ignore
        return BkRow if self.horizontal else PnColumn

    @property
    def _direction(self):
        return 'vertical' if self.horizontal else 'vertical'

    @param.depends('disabled', 'objects', watch=True)
    def _disable_widgets(self) -> None:
        from ..widgets import Widget
        for obj in self.select(Widget):
            obj.disabled = self.disabled

    def __init__(self, *objects: Any, **params: Any):
        super().__init__(*objects, **params)
        if self.disabled:
            self._disable_widgets()
