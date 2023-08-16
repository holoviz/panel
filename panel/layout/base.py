"""
Defines Layout classes which may be used to arrange panes and widgets
in flexible ways to build complex dashboards.
"""
from __future__ import annotations

from collections import defaultdict, namedtuple
from typing import (
    TYPE_CHECKING, Any, ClassVar, Dict, Iterable, Iterator, List, Mapping,
    Optional, Tuple, Type,
)

import param

from bokeh.models import Row as BkRow

from ..io.model import hold
from ..io.resources import CDN_DIST
from ..io.state import state
from ..models import Column as PnColumn
from ..reactive import Reactive
from ..util import param_name, param_reprs, param_watchers

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..viewable import Viewable

_row = namedtuple("row", ["children"]) # type: ignore
_col = namedtuple("col", ["children"]) # type: ignore


class Panel(Reactive):
    """
    Abstract baseclass for a layout of Viewables.
    """

    # Used internally to optimize updates
    _batch_update: ClassVar[bool] = False

    # Bokeh model used to render this Panel
    _bokeh_model: ClassVar[Type[Model]]

    # Direction the layout flows in
    _direction: ClassVar[str | None] = None

    # Parameters which require the preprocessors to be re-run
    _preprocess_params: ClassVar[List[str]] = []

    # Parameter -> Bokeh property renaming
    _rename: ClassVar[Mapping[str, str | None]] = {'objects': 'children'}

    __abstract = True

    def __repr__(self, depth: int = 0, max_depth: int = 10) -> str:
        if depth > max_depth:
            return '...'
        spacer = '\n' + ('    ' * (depth+1))
        cls = type(self).__name__
        params = param_reprs(self, ['objects'])
        objs = ['[%d] %s' % (i, obj.__repr__(depth+1)) for i, obj in enumerate(self)]
        if not params and not objs:
            return super().__repr__(depth+1)
        elif not params:
            template = '{cls}{spacer}{objs}'
        elif not objs:
            template = '{cls}({params})'
        else:
            template = '{cls}({params}){spacer}{objs}'
        return template.format(
            cls=cls, params=', '.join(params),
            objs=('%s' % spacer).join(objs), spacer=spacer)

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    def _update_model(
        self, events: Dict[str, param.parameterized.Event], msg: Dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Optional[Comm]
    ) -> None:
        msg = dict(msg)
        inverse = {v: k for k, v in self._property_mapping.items() if v is not None}
        preprocess = any(inverse.get(k, k) in self._preprocess_params for k in msg)

        # ALERT: Find a better way to handle this
        if 'styles' in msg and root is model and 'overflow-x' in msg['styles']:
            del msg['styles']['overflow-x']

        obj_key = self._property_mapping['objects']
        if obj_key in msg:
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
                with doc.models.freeze():
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
        self, model: Model, old_objects: List[Viewable], doc: Document,
        root: Model, comm: Optional[Comm] = None
    ):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from ..pane.base import RerenderError, panel
        new_models, old_models = [], []
        for i, pane in enumerate(self.objects):
            pane = panel(pane)
            self.objects[i] = pane

        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)

        current_objects = list(self.objects)
        ref = root.ref['id']
        for i, pane in enumerate(self.objects):
            if pane in old_objects and ref in pane._models:
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
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
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
        sizing_mode = props.get('sizing_mode', self.sizing_mode)
        if sizing_mode == 'fixed':
            return {}

        # Iterate over children and determine responsiveness along
        # each axis, scaling and the widths of each component.
        heights, widths = [], []
        all_expand_height, expand_width, expand_height, scale = True, False, False, False
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
        if ((sizing_mode.endswith('_width') or sizing_mode.endswith('_both')) and
            widths and 'min_width' not in properties):
            width_op = max if self._direction == 'vertical' else sum
            min_width = width_op(widths)
            op_widths = [min_width]
            if 'max_width' in properties:
                op_widths.append(properties['max_width'])
            properties['min_width'] = min(op_widths)
        if ((sizing_mode.endswith('_height') or sizing_mode.endswith('_both')) and
            heights and 'min_height' not in properties):
            height_op = max if self._direction == 'horizontal' else sum
            min_height = height_op(heights)
            op_heights = [min_height]
            if 'max_height' in properties:
                op_heights.append(properties['max_height'])
            properties['min_height'] = min(op_heights)
        return properties

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def get_root(
        self, doc: Optional[Document] = None, comm: Optional[Comm] = None,
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

        Arguments
        ---------
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

    objects = param.List(default=[], doc="""
        The list of child objects that make up the layout.""")

    _preprocess_params: ClassVar[List[str]] = ['objects']

    def __getitem__(self, index: int | slice) -> Viewable | List[Viewable]:
        return self.objects[index]

    def __len__(self) -> int:
        return len(self.objects)

    def __iter__(self) -> Iterator[Viewable]:
        for obj in self.objects:
            yield obj

    def __iadd__(self, other: Iterable[Any]) -> 'ListLike':
        self.extend(other)
        return self

    def __add__(self, other: Iterable[Any]) -> 'ListLike':
        if isinstance(other, ListLike):
            other = other.objects
        else:
            other = list(other)
        return self.clone(*(self.objects+other))

    def __radd__(self, other: Iterable[Any]) -> 'ListLike':
        if isinstance(other, ListLike):
            other = other.objects
        else:
            other = list(other)
        return self.clone(*(other+self.objects))

    def __contains__(self, obj: Viewable) -> bool:
        return obj in self.objects

    def __setitem__(self, index: int | slice, panes: Iterable[Any]) -> None:
        from ..pane import panel
        new_objects = list(self)
        if not isinstance(index, slice):
            start, end = index, index+1
            if start > len(self.objects):
                raise IndexError('Index %d out of bounds on %s '
                                 'containing %d objects.' %
                                 (end, type(self).__name__, len(self.objects)))
            panes = [panes]
        else:
            start = index.start or 0
            end = len(self) if index.stop is None else index.stop
            if index.start is None and index.stop is None:
                if not isinstance(panes, list):
                    raise IndexError('Expected a list of objects to '
                                     'replace the objects in the %s, '
                                     'got a %s type.' %
                                     (type(self).__name__, type(panes).__name__))
                expected = len(panes)
                new_objects = [None]*expected # type: ignore
                end = expected
            elif end > len(self.objects):
                raise IndexError('Index %d out of bounds on %s '
                                 'containing %d objects.' %
                                 (end, type(self).__name__, len(self.objects)))
            else:
                expected = end-start
            if not isinstance(panes, list) or len(panes) != expected:
                raise IndexError('Expected a list of %d objects to set '
                                 'on the %s to match the supplied slice.' %
                                 (expected, type(self).__name__))
        for i, pane in zip(range(start, end), panes):
            new_objects[i] = panel(pane)

        self.objects = new_objects

    def clone(self, *objects: Any, **params: Any) -> 'ListLike':
        """
        Makes a copy of the layout sharing the same parameters.

        Arguments
        ---------
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
            raise ValueError("A %s's objects should be supplied either "
                             "as arguments or as a keyword, not both."
                             % type(self).__name__)
        p = dict(self.param.values(), **params)
        del p['objects']
        return type(self)(*objects, **p)

    def append(self, obj: Any) -> None:
        """
        Appends an object to the layout.

        Arguments
        ---------
        obj (object): Panel component to add to the layout.
        """
        from ..pane import panel
        new_objects = list(self)
        new_objects.append(panel(obj))
        self.objects = new_objects

    def clear(self) -> None:
        """
        Clears the objects on this layout.
        """
        self.objects = []

    def extend(self, objects: Iterable[Any]) -> None:
        """
        Extends the objects on this layout with a list.

        Arguments
        ---------
        objects (list): List of panel components to add to the layout.
        """
        from ..pane import panel
        new_objects = list(self)
        new_objects.extend(list(map(panel, objects)))
        self.objects = new_objects

    def insert(self, index: int, obj: Any) -> None:
        """
        Inserts an object in the layout at the specified index.

        Arguments
        ---------
        index (int): Index at which to insert the object.
        object (object): Panel components to insert in the layout.
        """
        from ..pane import panel
        new_objects = list(self)
        new_objects.insert(index, panel(obj))
        self.objects = new_objects

    def pop(self, index: int) -> Viewable:
        """
        Pops an item from the layout by index.

        Arguments
        ---------
        index (int): The index of the item to pop from the layout.
        """
        new_objects = list(self)
        obj = new_objects.pop(index)
        self.objects = new_objects
        return obj

    def remove(self, obj: Viewable) -> None:
        """
        Removes an object from the layout.

        Arguments
        ---------
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

    objects = param.List(default=[], doc="""
        The list of child objects that make up the layout.""")

    _preprocess_params: ClassVar[List[str]] = ['objects']

    def __init__(self, *items: List[Any | Tuple[str, Any]], **params: Any):
        if 'objects' in params:
            if items:
                raise ValueError('%s objects should be supplied either '
                                 'as positional arguments or as a keyword, '
                                 'not both.' % type(self).__name__)
            items = params.pop('objects')
        params['objects'], self._names = self._to_objects_and_names(items)
        super().__init__(**params)
        self._panels = defaultdict(dict)
        self.param.watch(self._update_names, 'objects')
        # ALERT: Ensure that name update happens first, should be
        #        replaced by watch precedence support in param
        param_watchers(self)['objects']['value'].reverse()

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

    def __getitem__(self, index) -> Viewable | List[Viewable]:
        return self.objects[index]

    def __len__(self) -> int:
        return len(self.objects)

    def __iter__(self) -> Iterator[Viewable]:
        for obj in self.objects:
            yield obj

    def __iadd__(self, other: Iterable[Any]) -> 'NamedListLike':
        self.extend(other)
        return self

    def __add__(self, other: Iterable[Any]) -> 'NamedListLike':
        if isinstance(other, NamedListLike):
            added = list(zip(other._names, other.objects))
        elif isinstance(other, ListLike):
            added = other.objects
        else:
            added = list(other)
        objects = list(zip(self._names, self.objects))
        return self.clone(*(objects+added))

    def __radd__(self, other: Iterable[Any]) -> 'NamedListLike':
        if isinstance(other, NamedListLike):
            added = list(zip(other._names, other.objects))
        elif isinstance(other, ListLike):
            added = other.objects
        else:
            added = list(other)
        objects = list(zip(self._names, self.objects))
        return self.clone(*(added+objects))

    def __setitem__(self, index: int | slice, panes: Iterable[Any]) -> None:
        new_objects = list(self)
        if not isinstance(index, slice):
            if index > len(self.objects):
                raise IndexError('Index %d out of bounds on %s '
                                 'containing %d objects.' %
                                 (index, type(self).__name__, len(self.objects)))
            start, end = index, index+1
            panes = [panes]
        else:
            start = index.start or 0
            end = len(self.objects) if index.stop is None else index.stop
            if index.start is None and index.stop is None:
                if not isinstance(panes, list):
                    raise IndexError('Expected a list of objects to '
                                     'replace the objects in the %s, '
                                     'got a %s type.' %
                                     (type(self).__name__, type(panes).__name__))
                expected = len(panes)
                new_objects = [None]*expected # type: ignore
                self._names = [None]*len(panes)
                end = expected
            else:
                expected = end-start
                if end > len(self.objects):
                    raise IndexError('Index %d out of bounds on %s '
                                     'containing %d objects.' %
                                     (end, type(self).__name__, len(self.objects)))
            if not isinstance(panes, list) or len(panes) != expected:
                raise IndexError('Expected a list of %d objects to set '
                                 'on the %s to match the supplied slice.' %
                                 (expected, type(self).__name__))
        for i, pane in zip(range(start, end), panes):
            new_objects[i], self._names[i] = self._to_object_and_name(pane)
        self.objects = new_objects

    def clone(self, *objects: Any, **params: Any) -> 'NamedListLike':
        """
        Makes a copy of the Tabs sharing the same parameters.

        Arguments
        ---------
        objects: Objects to add to the cloned Tabs object.
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned Tabs object
        """
        if objects:
            overrides = objects
        elif 'objects' in params:
            raise ValueError('Tabs objects should be supplied either '
                             'as positional arguments or as a keyword, '
                             'not both.')
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

        Arguments
        ---------
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

        Arguments
        ---------
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

        Arguments
        ---------
        index (int): Index at which to insert the object.
        object (object): Panel components to insert as tabs.
        """
        new_object, new_name = self._to_object_and_name(pane)
        new_objects = list(self.objects)
        new_objects.insert(index, new_object)
        self._names.insert(index, new_name)
        self.objects = new_objects

    def pop(self, index: int) -> Viewable:
        """
        Pops an item from the tabs by index.

        Arguments
        ---------
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

        Arguments
        ---------
        obj (object): The object to remove from the tabs.
        """
        new_objects = list(self)
        if pane in new_objects:
            index = new_objects.index(pane)
        new_objects.remove(pane)
        self._names.pop(index)
        self.objects = new_objects

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

    scroll = param.Boolean(default=False, doc="""
        Whether to add scrollbars if the content overflows the size
        of the container.""")

    _rename: ClassVar[Mapping[str, str | None]] = {'scroll': None}

    _source_transforms: ClassVar[Mapping[str, str | None]] = {'scroll': None}

    __abstract = True

    def __init__(self, *objects: Any, **params: Any):
        from ..pane import panel
        if objects:
            if 'objects' in params:
                raise ValueError("A %s's objects should be supplied either "
                                 "as positional arguments or as a keyword, "
                                 "not both." % type(self).__name__)
            params['objects'] = [panel(pane) for pane in objects]
        elif 'objects' in params:
            if not hasattr(params['objects'], '_dinfo'):
                params['objects'] = [panel(pane) for pane in params['objects']]
        super(Panel, self).__init__(**params)

    @property
    def _linked_properties(self):
        return tuple(
            self._property_mapping.get(p, p) for p in self.param
            if p not in ListPanel.param and self._property_mapping.get(p, p) is not None
        )

    def _process_param_change(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if 'scroll' in params:
            scroll = params['scroll']
            css_classes = params.get('css_classes', self.css_classes)
            if scroll:
                if self._direction is not None:
                    css_classes += [f'scrollable-{self._direction}']
                else:
                    css_classes += ['scrollable']
            params['css_classes'] = css_classes
        return super()._process_param_change(params)

    def _cleanup(self, root: Model | None = None) -> None:
        if root is not None and root.ref['id'] in state._fake_roots:
            state._fake_roots.remove(root.ref['id'])
        super()._cleanup(root)
        for p in self.objects:
            p._cleanup(root)


class NamedListPanel(NamedListLike, Panel):

    active = param.Integer(default=0, bounds=(0, None), doc="""
        Index of the currently displayed objects.""")

    scroll = param.Boolean(default=False, doc="""
        Whether to add scrollbars if the content overflows the size
        of the container.""")

    _rename: ClassVar[Mapping[str, str | None]] = {'scroll': None}

    _source_transforms: ClassVar[Mapping[str, str | None]] = {'scroll': None}

    __abstract = True

    def _process_param_change(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if 'scroll' in params:
            scroll = params['scroll']
            css_classes = params.get('css_classes', self.css_classes)
            if scroll:
                if self._direction is not None:
                    css_classes += [f'scrollable-{self._direction}']
                else:
                    css_classes += ['scrollable']
            params['css_classes'] = css_classes
        return super()._process_param_change(params)

    def _cleanup(self, root: Model | None = None) -> None:
        if root is not None and root.ref['id'] in state._fake_roots:
            state._fake_roots.remove(root.ref['id'])
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

    _bokeh_model: ClassVar[Type[Model]] = BkRow

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

    scroll_position = param.Integer(default=None, doc="""
        Current scroll position of the Column. Setting this value
        will update the scroll position of the Column. Setting to
        0 will scroll to the top.""")

    auto_scroll_limit = param.Integer(bounds=(0, None), doc="""
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.""")

    scroll_button_threshold = param.Integer(bounds=(0, None), doc="""
        Min pixel distance from the latest object in the Column to
        display the scroll button. Setting to 0
        disables the scroll button.""")

    view_latest = param.Boolean(default=False, doc="""
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.""")

    _bokeh_model: ClassVar[Type[Model]] = PnColumn

    _direction = 'vertical'

    _stylesheets: ClassVar[list[str]] = [f'{CDN_DIST}css/listpanel.css']

    @param.depends(
        "scroll_position",
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
    def _bokeh_model(self) -> Type[Model]: # type: ignore
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
