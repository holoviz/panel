from collections import OrderedDict

import param

from ..io.resources import bundled_files
from ..reactive import ReactiveHTML
from ..util import classproperty
from .grid import GridSpec


class GridStack(ReactiveHTML, GridSpec):
    """
    The `GridStack` layout allows arranging multiple Panel objects in a grid
    using a simple API to assign objects to individual grid cells or to a grid
    span.

    Other layout containers function like lists, but a `GridSpec` has an API
    similar to a 2D array, making it possible to use 2D assignment to populate,
    index, and slice the grid.

    Reference: https://panel.holoviz.org/reference/layouts/GridStack.html

    :Example:

    >>> pn.extension('gridstack')
    >>> gstack = GridStack(sizing_mode='stretch_both')
    >>> gstack[ : , 0: 3] = pn.Spacer(background='red',    margin=0)
    >>> gstack[0:2, 3: 9] = pn.Spacer(background='green',  margin=0)
    >>> gstack[2:4, 6:12] = pn.Spacer(background='orange', margin=0)
    >>> gstack[4:6, 3:12] = pn.Spacer(background='blue',   margin=0)
    >>> gstack[0:2, 9:12] = pn.Spacer(background='purple', margin=0)
    """

    allow_resize = param.Boolean(default=True, doc="""
        Allow resizing the grid cells.""")

    allow_drag = param.Boolean(default=True, doc="""
        Allow dragging the grid cells.""")

    state = param.List(doc="""
        Current state of the grid (updated as items are resized and
        dragged).""")

    width = param.Integer(default=None)

    height = param.Integer(default=None)

    _extension_name = 'gridstack'

    _template = """
    <div id="grid" class="grid-stack">
    {% for key, obj in objects.items() %}
      <div data-id="{{ id(obj) }}" class="grid-stack-item" gs-h="{{ (key[2] or nrows)-(key[0] or 0) }}" gs-w="{{ (key[3] or ncols)-(key[1] or 0) }}" gs-y="{{ (key[0] or 0) }}" gs-x="{{ (key[1] or 0) }}">
        <div id="content" class="grid-stack-item-content">${obj}</div>
      </div>
    {% endfor %}
    </div>
    """ # noqa

    _scripts = {
        'render': ["""
        const options = {
          column: data.ncols,
          disableResize: !data.allow_resize,
          disableDrag: !data.allow_drag,
          margin: 0
        }
        if (data.nrows)
          options.row = data.nrows
          if (model.height)
            options.cellHeight = Math.floor(model.height/data.nrows)
        const gridstack = GridStack.init(options, grid);
        function sync_state() {
          const items = []
          for (const node of gridstack.engine.nodes) {
            items.push({id: node.el.getAttribute('data-id'), x0: node.x, y0: node.y, x1: node.x+node.w, y1: node.y+node.h})
          }
          data.state = items
        }
        gridstack.on('resizestop', (event, el) => {
          window.dispatchEvent(new Event("resize"));
          sync_state()
        })
        gridstack.on('dragstop', (event, el) => {
          sync_state()
        })
        sync_state()
        state.gridstack = gridstack
        """],
        'allow_drag':   ["state.gridstack.enableMove(data.allow_drag)"],
        'allow_resize': ["state.gridstack.enableResize(data.allow_resize)"],
        'ncols':        ["state.gridstack.column(data.ncols)"],
        'nrows':        ["""
          state.gristack.opts.row = data.nrows
          if (data.nrows && model.height)
            state.gridstack.cellHeight(Math.floor(model.height/data.nrows))
          else
            state.gridstack.cellHeight('auto')
        """]
    }

    __css_raw__ = [
        'https://cdn.jsdelivr.net/npm/gridstack@4.2.5/dist/gridstack.min.css',
        'https://cdn.jsdelivr.net/npm/gridstack@4.2.5/dist/gridstack-extra.min.css'
    ]

    __javascript_raw__ = [
        'https://cdn.jsdelivr.net/npm/gridstack@4.2.5/dist/gridstack-h5.js'
    ]

    __js_require__ = {
        'paths': {
            'gridstack': 'https://cdn.jsdelivr.net/npm/gridstack@4.2.5/dist/gridstack-h5'
        },
        'exports': {
            'gridstack': 'GridStack'
        },
        'shim': {
            'gridstack': {
                'exports': 'GridStack'
            }
        }
    }

    @classproperty
    def __js_skip__(cls):
        return {
            'GridStack': cls.__javascript__[0:1],
        }

    _rename = {}

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    @param.depends('state', watch=True)
    def _update_objects(self):
        objects = OrderedDict()
        object_ids = {str(id(obj)): obj for obj in self}
        for p in self.state:
            objects[(p['y0'], p['x0'], p['y1'], p['x1'])] = object_ids[p['id']]
        self.objects.clear()
        self.objects.update(objects)
        self._update_sizing()

    @param.depends('objects', watch=True)
    def _update_sizing(self):
        if self.ncols:
            width = int(float(self.width)/self.ncols)
        else:
            width = 0

        if self.nrows:
            height = int(float(self.height)/self.nrows)
        else:
            height = 0

        for i, ((y0, x0, y1, x1), obj) in enumerate(self.objects.items()):
            x0 = 0 if x0 is None else x0
            x1 = (self.ncols) if x1 is None else x1
            y0 = 0 if y0 is None else y0
            y1 = (self.nrows) if y1 is None else y1
            h, w = y1-y0, x1-x0

            if self.sizing_mode in ['fixed', None]:
                properties = {'width': w*width, 'height': h*height}
            else:
                properties = {'sizing_mode': self.sizing_mode}
                if 'width' in self.sizing_mode:
                    properties['height'] = h*height
                elif 'height' in self.sizing_mode:
                    properties['width'] = w*width
            obj.param.update(**{
                k: v for k, v in properties.items()
                if not obj.param[k].readonly
            })
