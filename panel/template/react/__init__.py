"""
React template
"""
from __future__ import annotations

import json
import math
import pathlib

import param

from ...config import config
from ...depends import depends
from ...io.resources import CSS_URLS
from ...layout import GridSpec
from ..base import BasicTemplate


class ReactTemplate(BasicTemplate):
    """
    ReactTemplate is built on top of React Grid Layout web components.
    """

    compact = param.Selector(default=None, objects=[None, 'vertical', 'horizontal', 'both'])

    cols = param.Dict(default={'lg': 12, 'md': 10, 'sm': 6, 'xs': 4, 'xxs': 2})

    breakpoints = param.Dict(default={'lg': 1200, 'md': 996, 'sm': 768, 'xs': 480, 'xxs': 0})

    main = param.ClassSelector(class_=GridSpec, constant=True, doc="""
        A list-like container which populates the main area.""")

    row_height = param.Integer(default=150)

    dimensions = param.Dict(default={'minW': 0, 'maxW': float('inf'), 'minH': 0, 'maxH': float('inf')},
                            doc="""A dictionary of minimum/maximum width/height in grid units.""")

    prevent_collision = param.Boolean(default=False, doc="Prevent collisions between items.")

    save_layout = param.Boolean(default=False, doc="Save layout to local storage.")

    _css = [pathlib.Path(__file__).parent / 'react.css']

    _template = pathlib.Path(__file__).parent / 'react.html'

    _resources = {
        'js': {
            'react': f"{config.npm_cdn}/react@17/umd/react.production.min.js",
            'react-dom': f"{config.npm_cdn}/react-dom@17/umd/react-dom.production.min.js",
            'babel': f"{config.npm_cdn}/babel-standalone@latest/babel.min.js",
            'react-grid': f"{config.npm_cdn}/react-grid-layout@1.3.4/dist/react-grid-layout.min.js"
        },
        'css': {
            'font-awesome': CSS_URLS['font-awesome']
        }
    }

    def __init__(self, **params):
        if 'main' not in params:
            params['main'] = GridSpec(ncols=12, mode='override')
        super().__init__(**params)
        self._update_render_vars()

    def _update_render_items(self, event: param.parameterized.Event):
        super()._update_render_items(event)
        if event.obj is not self.main:
            return
        layouts = []
        for i, ((y0, x0, y1, x1), v) in enumerate(self.main.objects.items()):
            if x0 is None: x0 = 0
            if x1 is None: x1 = 12
            if y0 is None: y0 = 0
            if y1 is None: y1 = self.main.nrows
            elem = {'x': x0, 'y': y0, 'w': x1-x0, 'h': y1-y0, 'i': str(i+1)}
            elem.update({d: v for d, v in self.dimensions.items() if not math.isinf(v)})
            layouts.append(elem)
        self._render_variables['layouts'] = json.dumps({'lg': layouts, 'md': layouts})

    @depends('cols', 'breakpoints', 'row_height', 'compact', 'dimensions', 'prevent_collision',
             'save_layout', watch=True)
    def _update_render_vars(self):
        self._render_variables['breakpoints'] = self.breakpoints
        self._render_variables['cols'] = self.cols
        self._render_variables['rowHeight'] = self.row_height
        self._render_variables['compact'] = self.compact
        self._render_variables['dimensions'] = self.dimensions
        self._render_variables['preventCollision'] = self.prevent_collision
        self._render_variables['saveLayout'] = self.save_layout
