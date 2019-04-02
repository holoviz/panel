"""
Defines Layout classes which may be used to arrange panes and widgets
in flexible ways to build complex dashboards.
"""
from __future__ import absolute_import, division, unicode_literals

from collections import OrderedDict

import param
import numpy as np

from bokeh.models import (Column as BkColumn, Row as BkRow,
                          Spacer as BkSpacer, GridBox as BkGridBox,
                          Box as BkBox, Markup as BkMarkup)
from bokeh.models.widgets import Tabs as BkTabs, Panel as BkPanel

from .util import param_name, param_reprs
from .viewable import Reactive


class Panel(Reactive):
    """
    Abstract baseclass for a layout of Viewables.
    """

    objects = param.Parameter(default=[], doc="""
        The list of child objects that make up the layout.""")

    _bokeh_model = None

    __abstract = True

    _rename = {'objects': 'children'}

    _linked_props = []

    def __repr__(self, depth=0, max_depth=10):
        if depth > max_depth:
            return '...'
        spacer = '\n' + ('    ' * (depth+1))
        cls = type(self).__name__
        params = param_reprs(self, ['objects'])
        objs = ['[%d] %s' % (i, obj.__repr__(depth+1)) for i, obj in enumerate(self)]
        if not params and not objs:
            return super(Panel, self).__repr__(depth+1)
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

    def _update_model(self, events, msg, root, model, doc, comm=None):
        if self._rename['objects'] in msg:
            old = events['objects'].old
            msg[self._rename['objects']] = self._get_objects(model, old, doc, root, comm)
        model.update(**msg)

        from .io import state
        ref = root.ref['id']
        if ref in state._views:
            state._views[ref][0]._preprocess(root)

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _init_properties(self):
        properties = {k: v for k, v in self.param.get_param_values()
                      if v is not None}
        del properties['objects']
        return self._process_param_change(properties)

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from .pane import panel
        new_models = []
        for i, pane in enumerate(self.objects):
            pane = panel(pane)
            self.objects[i] = pane
            if pane in old_objects:
                child, _ = pane._models[root.ref['id']]
            else:
                child = pane._get_model(doc, root, model, comm)
            new_models.append(child)
        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)
        return new_models

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._bokeh_model()
        if root is None:
            root = model
        objects = self._get_objects(model, [], doc, root, comm)
        props = dict(self._init_properties(), objects=objects)
        model.update(**self._process_param_change(props))
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, self._linked_props, doc, root, comm)
        return model

    def _cleanup(self, root):
        super(Panel, self)._cleanup(root)
        for p in self.objects:
            p._cleanup(root)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

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
        objects = super(Panel, self).select(selector)
        for obj in self:
            objects += obj.select(selector)
        return objects



class ListPanel(Panel):
    """
    An abstract baseclass for Panel objects with list-like children.
    """

    objects = param.List(default=[], doc="""
        The list of child objects that make up the layout.""")

    __abstract = True

    def __init__(self, *objects, **params):
        from .pane import panel
        if objects:
            if 'objects' in params:
                raise ValueError("A %s's objects should be supplied either "
                                 "as positional arguments or as a keyword, "
                                 "not both." % type(self).__name__)
            params['objects'] = [panel(pane) for pane in objects]
        super(Panel, self).__init__(**params)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def __getitem__(self, index):
        return self.objects[index]

    def __len__(self):
        return len(self.objects)

    def __iter__(self):
        for obj in self.objects:
            yield obj

    def __contains__(self, obj):
        return obj in self.objects

    def __setitem__(self, index, panes):
        from .pane import panel
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
                new_objects = [None]*expected
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

    def clone(self, *objects, **params):
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
        p = dict(self.param.get_param_values(), **params)
        del p['objects']
        return type(self)(*objects, **params)

    def append(self, obj):
        """
        Appends an object to the layout.

        Arguments
        ---------
        obj (object): Panel component to add to the layout.
        """
        from .pane import panel
        new_objects = list(self)
        new_objects.append(panel(obj))
        self.objects = new_objects

    def clear(self):
        """
        Clears the objects on this layout.
        """
        self.objects = []

    def extend(self, objects):
        """
        Extends the objects on this layout with a list.

        Arguments
        ---------
        objects (list): List of panel components to add to the layout.
        """
        from .pane import panel
        new_objects = list(self)
        new_objects.extend(list(map(panel, objects)))
        self.objects = new_objects

    def insert(self, index, obj):
        """
        Inserts an object in the layout at the specified index.

        Arguments
        ---------
        index (int): Index at which to insert the object.
        object (object): Panel components to insert in the layout.
        """
        from .pane import panel
        new_objects = list(self)
        new_objects.insert(index, panel(obj))
        self.objects = new_objects

    def pop(self, index):
        """
        Pops an item from the layout by index.

        Arguments
        ---------
        index (int): The index of the item to pop from the layout.
        """
        new_objects = list(self)
        if index in new_objects:
            index = new_objects.index(index)
        obj = new_objects.pop(index)
        self.objects = new_objects
        return obj

    def remove(self, obj):
        """
        Removes an object from the layout.

        Arguments
        ---------
        obj (object): The object to remove from the layout.
        """
        new_objects = list(self)
        new_objects.remove(obj)
        self.objects = new_objects

    def reverse(self):
        """
        Reverses the objects in the layout.
        """
        new_objects = list(self)
        new_objects.reverse()
        self.objects = new_objects


class Row(ListPanel):
    """
    Horizontal layout of Viewables.
    """

    _bokeh_model = BkRow


class Column(ListPanel):
    """
    Vertical layout of Viewables.
    """

    _bokeh_model = BkColumn


class Tabs(ListPanel):
    """
    Panel of Viewables to be displayed in separate tabs.
    """

    active = param.Integer(default=0, doc="""
        Number of the currently active tab.""")

    closable = param.Boolean(default=False, doc="""
        Whether it should be possible to close tabs.""")

    objects = param.List(default=[], doc="""
        The list of child objects that make up the tabs.""")

    tabs_location = param.ObjectSelector(
        default='above', objects=['above', 'below', 'left', 'right'], doc="""
        The location of the tabs relative to the tab contents.""")

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    _bokeh_model = BkTabs

    _rename = {'objects': 'tabs'}

    _linked_props = ['active']

    def __init__(self, *items, **params):
        if 'objects' in params:
            if items:
                raise ValueError('Tabs objects should be supplied either '
                                 'as positional arguments or as a keyword, '
                                 'not both.')
            items = params['objects']
        objects, self._names = self._to_objects_and_names(items)
        super(Tabs, self).__init__(*objects, **params)
        self.param.watch(self._update_names, 'objects')
        # ALERT: Ensure that name update happens first, should be
        #        replaced by watch precedence support in param
        self._param_watchers['objects']['value'].reverse()

    def _to_object_and_name(self, item):
        from .pane import panel
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

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None and k != 'closable'}

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    def _update_names(self, event):
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

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _update_model(self, events, msg, root, model, doc, comm=None):
        if 'closable' in msg:
            closable = msg.pop('closable')
            for child in model.tabs:
                child.closable = closable
        super(Tabs, self)._update_model(events, msg, root, model, doc, comm)

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        """
        Returns new child models for the layout while reusing unchanged
        models and cleaning up any dropped objects.
        """
        from .pane import panel
        new_models = []
        if len(self._names) != len(self):
            raise ValueError('Tab names do not match objects, ensure '
                             'that the Tabs.objects are not modified '
                             'directly. Found %d names, expected %d.' %
                             (len(self._names), len(self)))
        for i, (name, pane) in enumerate(zip(self._names, self)):
            pane = panel(pane, name=name)
            self.objects[i] = pane
            if pane in old_objects:
                child, _ = pane._models[root.ref['id']]
            else:
                child = pane._get_model(doc, root, model, comm)
            child = BkPanel(title=name, name=pane.name, child=child,
                            closable=self.closable)
            new_models.append(child)
        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)
        return new_models

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def __setitem__(self, index, panes):
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
                new_objects = [None]*expected
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

    def clone(self, *objects, **params):
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
        if not objects:
            if 'objects' in params:
                objects = params.pop('objects')
            else:
                objects = zip(self._names, self.objects)
        elif 'objects' in params:
            raise ValueError('Tabs objects should be supplied either '
                             'as positional arguments or as a keyword, '
                             'not both.')
        p = dict(self.param.get_param_values(), **params)
        del p['objects']
        return type(self)(*objects, **params)

    def append(self, pane):
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

    def clear(self):
        """
        Clears the tabs.
        """
        self._names = []
        self.objects = []

    def extend(self, panes):
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

    def insert(self, index, pane):
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

    def pop(self, index):
        """
        Pops an item from the tabs by index.

        Arguments
        ---------
        index (int): The index of the item to pop from the tabs.
        """
        new_objects = list(self)
        if index in new_objects:
            index = new_objects.index(index)
        new_objects.pop(index)
        self._names.pop(index)
        self.objects = new_objects

    def remove(self, pane):
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

    def reverse(self):
        """
        Reverses the tabs.
        """
        new_objects = list(self)
        new_objects.reverse()
        self._names.reverse()
        self.objects = new_objects


class GridSpec(Panel):

    objects = param.Dict(default={}, doc="""
        The dictionary of child objects that make up the grid.""")

    mode = param.ObjectSelector(
        default='warn', objects=['warn', 'error', 'override'], doc="""
        Whether to warn, error or simply override on overlapping
        assignment.""")

    width = param.Integer(default=600)

    height = param.Integer(default=600)

    _bokeh_model = BkGridBox

    _rename = {'objects': 'children', 'mode': None}

    def __init__(self, **params):
        if 'objects' not in params:
            params['objects'] = OrderedDict()
        super(GridSpec, self).__init__(**params)

    def _init_properties(self):
        properties = super(GridSpec, self)._init_properties()
        if self.sizing_mode not in ['fixed', None]:
            if 'min_width' not in properties and 'width' in properties:
                properties['min_width'] = properties['width']
            if 'min_height' not in properties and 'height' in properties:
                properties['min_height'] = properties['height']
        return properties

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        if self.ncols:
            width = int(float(self.width)/self.ncols)
        else:
            width = 0

        if self.nrows:
            height = int(float(self.height)/self.nrows)
        else:
            height = 0

        children = []
        for (y0, x0, y1, x1), obj in self.objects.items():
            x0 = 0 if x0 is None else x0
            x1 = (self.ncols) if x1 is None else x1
            y0 = 0 if y0 is None else y0
            y1 = (self.nrows) if y1 is None else y1
            r, c, h, w = (y0, x0, y1-y0, x1-x0)

            if self.sizing_mode in ['fixed', None]:
                properties = {'width': w*width, 'height': h*height}
            else:
                properties = {'sizing_mode': self.sizing_mode}
            obj.set_param(**properties)
            model = obj._get_model(doc, root, model, comm)

            if isinstance(model, BkMarkup) and self.sizing_mode not in ['fixed', None]:
                if model.style is None:
                    model.style = {}
                style = {}
                if 'width' not in model.style:
                    style['width'] = '100%'
                if 'height' not in model.style:
                    style['height'] = '100%'
                if style:
                    model.style.update(style)

            if isinstance(model, BkBox) and len(model.children) == 1:
                model.children[0].update(**properties)
            else:
                model.update(**properties)
            children.append((model, r, c, h, w))

        new_objects = list(self.objects.values())
        if isinstance(old_objects, dict):
            old_objects = list(old_objects.values())
        for old in old_objects:
            if old not in new_objects:
                old._cleanup(root)
        return children

    @property
    def _xoffset(self):
        min_xidx = [x0 for (_, x0, _, _) in self.objects if x0 is not None]
        return min(min_xidx) if min_xidx and len(min_xidx) == len(self.objects) else 0

    @property
    def _yoffset(self):
        min_yidx = [y0 for (y0, x0, _, _) in self.objects if y0 is not None]
        return min(min_yidx) if min_yidx and len(min_yidx) == len(self.objects) else 0

    @property
    def _object_grid(self):
        grid = np.full((self.nrows, self.ncols), None)
        for i, ((y0, x0, y1, x1), obj) in enumerate(self.objects.items()):
            l = 0 if x0 is None else x0
            r = self.ncols if x1 is None else x1
            t = 0 if y0 is None else y0
            b = self.nrows if y1 is None else y1
            for y in range(t, b):
                for x in range(l, r):
                    grid[y, x] = {((y0, x0, y1, x1), obj)}
        return grid

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @property
    def nrows(self):
        max_yidx = [y1 for (_, _, y1, _) in self.objects if y1 is not None]
        return max(max_yidx) if max_yidx else 0

    @property
    def ncols(self):
        max_xidx = [x1 for (_, _, _, x1) in self.objects if x1 is not None]
        return max(max_xidx) if max_xidx else 0

    @property
    def grid(self):
        grid = np.zeros((self.nrows, self.ncols), dtype='uint8')
        for (y0, x0, y1, x1) in self.objects:
            x0 = 0 if x0 is None else x0
            x1 = self.ncols if x1 is None else x1
            y0 = 0 if y0 is None else y0
            y1 = self.nrows if y1 is None else y1
            grid[y0:y1, x0:x1] += 1
        return grid

    def clone(self, **params):
        """
        Makes a copy of the GridSpec sharing the same parameters.

        Arguments
        ---------
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned GridSpec object
        """
        p = dict(self.param.get_param_values(), **params)
        return type(self)(**p)

    def __iter__(self):
        for obj in self.objects.values():
            yield obj

    def __delitem__(self, index, trigger=True):
        if isinstance(index, tuple):
            yidx, xidx = index
        else:
            yidx, xidx = index, slice(None)

        subgrid = self._object_grid[yidx, xidx]
        if isinstance(subgrid, np.ndarray):
            deleted = OrderedDict([list(o)[0] for o in subgrid.flatten()])
        else:
            deleted = [list(subgrid)[0][0]]
        if deleted:
            for key in deleted:
                del self.objects[key]
            if trigger:
                self.param.trigger('objects')

    def __getitem__(self, index):
        if isinstance(index, tuple):
            yidx, xidx = index
        else:
            yidx, xidx = index, slice(None)

        subgrid = self._object_grid[yidx, xidx]
        if isinstance(subgrid, np.ndarray):
            params = dict(self.get_param_values())
            params['objects'] = OrderedDict([list(o)[0] for o in subgrid.flatten()])
            gspec = GridSpec(**params)
            xoff, yoff = gspec._xoffset, gspec._yoffset
            adjusted = []
            for (y0, x0, y1, x1), obj in gspec.objects.items():
                if y0 is not None: y0 -= yoff
                if y1 is not None: y1 -= yoff
                if x0 is not None: x0 -= xoff
                if x1 is not None: x1 -= xoff
                if ((y0, x0, y1, x1), obj) not in adjusted:
                    adjusted.append(((y0, x0, y1, x1), obj))
            gspec.objects = OrderedDict(adjusted)
            width_scale = gspec.ncols/float(self.ncols)
            height_scale = gspec.nrows/float(self.nrows)
            if gspec.width:
                gspec.width = int(gspec.width * width_scale)
            if gspec.height:
                gspec.height = int(gspec.height * height_scale)
            if gspec.max_width:
                gspec.max_width = int(gspec.max_width * width_scale)
            if gspec.max_height:
                gspec.max_height = int(gspec.max_height * height_scale)
            return gspec
        else:
            return list(subgrid)[0][1]

    def __setitem__(self, index, obj):
        from .pane.base import Pane
        if not isinstance(index, tuple):
            raise IndexError('Must supply a 2D index for GridSpec assignment.')

        yidx, xidx = index
        if isinstance(xidx, slice):
            x0, x1 = (xidx.start, xidx.stop)
        else:
            x0, x1 = (xidx, xidx+1)

        if isinstance(yidx, slice):
            y0, y1 = (yidx.start, yidx.stop)
        else:
            y0, y1 = (yidx, yidx+1)

        l = 0 if x0 is None else x0
        r = self.nrows if x1 is None else x1
        t = 0 if y0 is None else y0
        b = self.ncols if y1 is None else y1

        key = (y0, x0, y1, x1)
        overlap = key in self.objects
        clone = self.clone(mode='override')
        if not overlap:
            clone.objects[key] = Pane(obj)
            grid = clone.grid
        else:
            grid = clone.grid
            grid[t:b, l:r] += 1

        overlap_grid = grid>1
        if (overlap_grid).any():
            overlapping = ''
            objects = []
            for (yidx, xidx) in zip(*np.where(overlap_grid)):
                old_obj = self[yidx, xidx]
                if old_obj not in objects:
                    objects.append(old_obj)
                    overlapping += '    (%d, %d): %s\n\n' % (yidx, xidx, old_obj)
            overlap_text = ('Specified region overlaps with the following '
                            'existing object(s) in the grid:\n\n'+overlapping+
                            'The following shows a view of the grid '
                            '(empty: 0, occupied: 1, overlapping: 2):\n\n'+
                            str(grid.astype('uint8')))
            if self.mode == 'error':
                raise IndexError(overlap_text)
            elif self.mode == 'warn':
                self.param.warning(overlap_text)
            self.__delitem__(index, False)
        self.objects[key] = Pane(obj)
        self.param.trigger('objects')


class Spacer(Reactive):
    """Empty object used to control formatting (using positive or negative space)"""

    _bokeh_model = BkSpacer

    def _get_model(self, doc, root=None, parent=None, comm=None):
        properties = self._process_param_change(self._init_properties())
        model = self._bokeh_model(**properties)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model


class VSpacer(Spacer):
    """
    Spacer which automatically fills all available vertical space.
    """

    sizing_mode = param.Parameter(default='stretch_height', readonly=True)


class HSpacer(Spacer):
    """
    Spacer which automatically fills all available horizontal space.
    """

    sizing_mode = param.Parameter(default='stretch_width', readonly=True)
