from collections import OrderedDict

import param

from ..config import config
from ..io.resources import bundled_files

from ..reactive import ReactiveHTML
from ..util import classproperty
from .grid import GridSpec


class GridStack(ReactiveHTML, GridSpec):
    """
    The GridStack layout builds on the GridSpec component and
    gridstack.js to allow resizing and dragging items in the grid.
    """

    allow_resize = param.Boolean(default=True, doc="""
        Allow resizing the grid cells.""")

    allow_drag = param.Boolean(default=True, doc="""
        Allow dragging the grid cells.""")

    ncols = param.Integer(default=12, doc="""
        The number of columns in the grid.""")

    nrows = param.Integer(default=0, doc="""
        The number of columns in the grid.""")

    state = param.List()

    width = param.Integer(default=None)

    height = param.Integer(default=None)

    _template = """
    <div id="grid" class="grid-stack">
    {% for key, obj in objects.items() %}
      <div class="grid-stack-item" gs-h="{{ (key[2] or nrows)-(key[0] or 0) }}" gs-w="{{ (key[3] or ncols)-(key[1] or 0) }}" gs-y="{{ (key[0] or 0) }}" gs-x="{{ (key[1] or 0) }}">
        <div id="content" class="grid-stack-item-content">${obj}</div>
      </div>
    {% endfor %}
    </div>
    """

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
            items.push({x0: node.x, y0: node.y, x1: node.x+node.w, y1: node.y+node.h})
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
        for p, obj in zip(self.state, self):
            objects[(p['y0'], p['x0'], p['y1'], p['x1'])] = obj
        self.objects.clear()
        self.objects.update(objects)
