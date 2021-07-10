"""
Layout components to lay out objects in a grid.
"""
import math

from collections import OrderedDict, namedtuple
from functools import partial

import numpy as np
import param

from bokeh.models import Box as BkBox, GridBox as BkGridBox

from ..io.model import hold
from .base import _col, _row, ListPanel, Panel



class GridBox(ListPanel):
    """
    List-like Grid which wraps depending on the specified number of
    rows or columns.
    """

    nrows = param.Integer(default=None, bounds=(0, None), doc="""
      Number of rows to reflow the layout into.""")

    ncols = param.Integer(default=None, bounds=(0, None),  doc="""
      Number of columns to reflow the layout into.""")

    _bokeh_model = BkGridBox

    _rename = {'objects': 'children', 'nrows': None, 'ncols': None}

    _source_transforms = {'scroll': None, 'objects': None}

    @classmethod
    def _flatten_grid(cls, layout, nrows=None, ncols=None):
        Item = namedtuple("Item", ["layout", "r0", "c0", "r1", "c1"])
        Grid = namedtuple("Grid", ["nrows", "ncols", "items"])

        def gcd(a, b):
            a, b = abs(a), abs(b)
            while b != 0:
                a, b = b, a % b
            return a

        def lcm(a, *rest):
            for b in rest:
                a = (a*b) // gcd(a, b)
            return a

        nonempty = lambda child: child.nrows != 0 and child.ncols != 0

        def _flatten(layout, nrows=None, ncols=None):
            _flatten_ = partial(_flatten, nrows=nrows, ncols=ncols)
            if isinstance(layout, _row):
                children = list(filter(nonempty, map(_flatten_, layout.children)))
                if not children:
                    return Grid(0, 0, [])

                nrows = lcm(*[ child.nrows for child in children ])
                if not ncols: # This differs from bokeh.layout.grid
                    ncols = sum([ child.ncols for child in children ])

                items = []
                offset = 0
                for child in children:
                    factor = nrows//child.nrows

                    for (layout, r0, c0, r1, c1) in child.items:
                        items.append((layout, factor*r0, c0 + offset, factor*r1, c1 + offset))

                    offset += child.ncols

                return Grid(nrows, ncols, items)
            elif isinstance(layout, _col):
                children = list(filter(nonempty, map(_flatten_, layout.children)))
                if not children:
                    return Grid(0, 0, [])

                if not nrows: # This differs from bokeh.layout.grid
                    nrows = sum([ child.nrows for child in children ])
                ncols = lcm(*[ child.ncols for child in children ])

                items = []
                offset = 0
                for child in children:
                    factor = ncols//child.ncols

                    for (layout, r0, c0, r1, c1) in child.items:
                        items.append((layout, r0 + offset, factor*c0, r1 + offset, factor*c1))

                    offset += child.nrows

                return Grid(nrows, ncols, items)
            else:
                return Grid(1, 1, [Item(layout, 0, 0, 1, 1)])

        grid = _flatten(layout, nrows, ncols)

        children = []
        for (layout, r0, c0, r1, c1) in grid.items:
            if layout is not None:
                children.append((layout, r0, c0, r1 - r0, c1 - c0))
        return children

    @classmethod
    def _get_children(cls, children, nrows=None, ncols=None):
        """
        This is a copy of parts of the bokeh.layouts.grid implementation
        to avoid distributing non-filled columns.
        """
        if nrows is not None or ncols is not None:
            N = len(children)
            if ncols is None:
                ncols = int(math.ceil(N/nrows))
            layout = _col([ _row(children[i:i+ncols]) for i in range(0, N, ncols) ])
        else:
            def traverse(children, level=0):
                if isinstance(children, list):
                    container = _col if level % 2 == 0 else _row
                    return container([ traverse(child, level+1) for child in children ])
                else:
                    return children
            layout = traverse(children)
        return cls._flatten_grid(layout, nrows, ncols)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._bokeh_model()
        if root is None:
            root = model
        objects = self._get_objects(model, [], doc, root, comm)
        properties = self._process_param_change(self._init_params())
        properties['children'] = self._get_children(objects, self.nrows, self.ncols)
        model.update(**properties)
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, self._linked_props, doc, root, comm)
        return model

    def _update_model(self, events, msg, root, model, doc, comm=None):
        from ..io import state

        msg = dict(msg)
        preprocess = any(self._rename.get(k, k) in self._preprocess_params for k in msg)
        if self._rename['objects'] in msg or 'ncols' in msg or 'nrows' in msg:
            if 'objects' in events:
                old = events['objects'].old
            else:
                old = self.objects
            objects = self._get_objects(model, old, doc, root, comm)
            children = self._get_children(objects, self.nrows, self.ncols)
            msg[self._rename['objects']] = children

        with hold(doc):
            msg = {k: v for k, v in msg.items() if k not in ('nrows', 'ncols')}
            update = Panel._batch_update
            Panel._batch_update = True
            try:
                super(Panel, self)._update_model(events, msg, root, model, doc, comm)
                if update:
                    return
                ref = root.ref['id']
                if ref in state._views and preprocess:
                    state._views[ref][0]._preprocess(root)
            finally:
                Panel._batch_update = update


class GridSpec(Panel):

    objects = param.Dict(default={}, doc="""
        The dictionary of child objects that make up the grid.""")

    mode = param.ObjectSelector(default='warn', objects=['warn', 'error', 'override'], doc="""
        Whether to warn, error or simply override on overlapping assignment.""")

    ncols = param.Integer(default=None, bounds=(0, None), doc="""
        Limits the number of columns that can be assigned.""")

    nrows = param.Integer(default=None, bounds=(0, None), doc="""
        Limits the number of rows that can be assigned.""")

    width = param.Integer(default=600)

    height = param.Integer(default=600)

    _bokeh_model = BkGridBox

    _source_transforms = {'objects': None, 'mode': None}

    _rename = {'objects': 'children', 'mode': None, 'ncols': None, 'nrows': None}

    _preprocess_params = ['objects']

    def __init__(self, **params):
        if 'objects' not in params:
            params['objects'] = OrderedDict()
        super().__init__(**params)
        self._updating = False
        self._update_nrows()
        self._update_ncols()
        self._update_grid_size()

    @param.depends('nrows', watch=True)
    def _update_nrows(self):
        if not self._updating:
            self._rows_fixed = bool(self.nrows)

    @param.depends('ncols', watch=True)
    def _update_ncols(self):
        if not self._updating:
            self._cols_fixed = self.ncols is not None

    @param.depends('objects', watch=True)
    def _update_grid_size(self):
        self._updating = True
        if not self._cols_fixed:
            max_xidx = [x1 for (_, _, _, x1) in self.objects if x1 is not None]
            self.ncols = max(max_xidx) if max_xidx else (1 if len(self.objects) else 0)
        if not self._rows_fixed:
            max_yidx = [y1 for (_, _, y1, _) in self.objects if y1 is not None]
            self.nrows = max(max_yidx) if max_yidx else (1 if len(self.objects) else 0)
        self._updating = False

    def _init_params(self):
        params = super()._init_params()
        if self.sizing_mode not in ['fixed', None]:
            if 'min_width' not in params and 'width' in params:
                params['min_width'] = params['width']
            if 'min_height' not in params and 'height' in params:
                params['min_height'] = params['height']
        return params

    def _get_objects(self, model, old_objects, doc, root, comm=None):
        from ..pane.base import RerenderError

        if self.ncols:
            width = int(float(self.width)/self.ncols)
        else:
            width = 0

        if self.nrows:
            height = int(float(self.height)/self.nrows)
        else:
            height = 0

        current_objects = list(self.objects.values())
        if isinstance(old_objects, dict):
            old_objects = list(old_objects.values())

        for old in old_objects:
            if old not in current_objects:
                old._cleanup(root)

        children = []
        for i, ((y0, x0, y1, x1), obj) in enumerate(self.objects.items()):
            x0 = 0 if x0 is None else x0
            x1 = (self.ncols) if x1 is None else x1
            y0 = 0 if y0 is None else y0
            y1 = (self.nrows) if y1 is None else y1
            r, c, h, w = (y0, x0, y1-y0, x1-x0)

            if self.sizing_mode in ['fixed', None]:
                properties = {'width': w*width, 'height': h*height}
            else:
                properties = {'sizing_mode': self.sizing_mode}
                if 'width' in self.sizing_mode:
                    properties['height'] = h*height
                elif 'height' in self.sizing_mode:
                    properties['width'] = w*width
            obj.param.set_param(**{k: v for k, v in properties.items()
                                   if not obj.param[k].readonly})

            if obj in old_objects:
                child, _ = obj._models[root.ref['id']]
            else:
                try:
                    child = obj._get_model(doc, root, model, comm)
                except RerenderError:
                    return self._get_objects(model, current_objects[:i], doc, root, comm)

            if isinstance(child, BkBox) and len(child.children) == 1:
                child.children[0].update(**properties)
            else:
                child.update(**properties)
            children.append((child, r, c, h, w))
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
        grid = np.full((self.nrows, self.ncols), None, dtype=object)
        for i, ((y0, x0, y1, x1), obj) in enumerate(self.objects.items()):
            l = 0 if x0 is None else x0
            r = self.ncols if x1 is None else x1
            t = 0 if y0 is None else y0
            b = self.nrows if y1 is None else y1
            for y in range(t, b):
                for x in range(l, r):
                    grid[y, x] = {((y0, x0, y1, x1), obj)}
        return grid

    def _cleanup(self, root):
        super()._cleanup(root)
        for p in self.objects.values():
            p._cleanup(root)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @property
    def grid(self):
        grid = np.zeros((self.nrows, self.ncols), dtype='uint8')
        for (y0, x0, y1, x1) in self.objects:
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
        if not self._cols_fixed:
            del p['ncols']
        if not self._rows_fixed:
            del p['nrows']
        return type(self)(**p)

    def __iter__(self):
        for obj in self.objects.values():
            yield obj

    def __delitem__(self, index):
        if isinstance(index, tuple):
            yidx, xidx = index
        else:
            yidx, xidx = index, slice(None)

        subgrid = self._object_grid[yidx, xidx]
        if isinstance(subgrid, np.ndarray):
            deleted = OrderedDict([list(o)[0] for o in subgrid.flatten()])
        else:
            deleted = [list(subgrid)[0][0]]
        for key in deleted:
            del self.objects[key]
        self.param.trigger('objects')

    def __getitem__(self, index):
        if isinstance(index, tuple):
            yidx, xidx = index
        else:
            yidx, xidx = index, slice(None)

        subgrid = self._object_grid[yidx, xidx]
        if isinstance(subgrid, np.ndarray):
            params = dict(self.param.get_param_values())
            params['objects'] = OrderedDict([list(o)[0] for o in subgrid.flatten()])
            gspec = type(self)(**params)
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
        from ..pane.base import panel
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
        r = self.ncols if x1 is None else x1
        t = 0 if y0 is None else y0
        b = self.nrows if y1 is None else y1

        if self._cols_fixed and (l >= self.ncols or r > self.ncols):
            raise IndexError('Assigned object to column(s) out-of-bounds '
                             'of the grid declared by `ncols`. which '
                             f'was set to {self.ncols}.')
        if self._rows_fixed and (t >= self.nrows or b > self.nrows):
            raise IndexError('Assigned object to column(s) out-of-bounds '
                             'of the grid declared by `nrows`, which '
                             f'was set to {self.nrows}.')

        key = (y0, x0, y1, x1)
        overlap = key in self.objects
        clone = self.clone(objects=OrderedDict(self.objects), mode='override')
        if not overlap:
            clone.objects[key] = panel(obj)
            clone._update_grid_size()
            grid = clone.grid
        else:
            grid = clone.grid
            grid[t:b, l:r] += 1

        overlap_grid = grid > 1
        new_objects = OrderedDict(self.objects)
        if overlap_grid.any():
            overlapping = ''
            objects = []
            for (yidx, xidx) in zip(*np.where(overlap_grid)):
                try:
                    old_obj = self[yidx, xidx]
                except Exception:
                    continue
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

            subgrid = self._object_grid[index]
            if isinstance(subgrid, set):
                objects = [list(subgrid)[0][0]] if subgrid else []
            else:
                objects = [list(o)[0][0] for o in subgrid.flatten()]
            for dkey in set(objects):
                try:
                    del new_objects[dkey]
                except KeyError:
                    continue
        new_objects[key] = panel(obj)
        self.objects = new_objects
