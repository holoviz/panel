"""
React template
"""
import pathlib

import param

from ...depends import depends
from ...layout import Card, GridSpec
from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme


class ReactTemplate(BasicTemplate):
    """
    ReactTemplate is built on top of React Grid Layout web components.
    """

    compact = param.ObjectSelector(default=None, objects=[None, 'vertical', 'horizontal', 'both'])

    cols = param.Dict(default={'lg': 12, 'md': 10, 'sm': 6, 'xs': 4, 'xxs': 2})

    breakpoints = param.Dict(default={'lg': 1200, 'md': 996, 'sm': 768, 'xs': 480, 'xxs': 0})

    main = param.ClassSelector(class_=GridSpec, constant=True, doc="""
        A list-like container which populates the main area.""")

    row_height = param.Integer(default=150)

    _css = pathlib.Path(__file__).parent / 'react.css'

    _template = pathlib.Path(__file__).parent / 'react.html'

    _modifiers = {
        Card: {
            'children': {'margin': (20, 20)},
            'margin': (10, 5)
        }
    }

    _resources = {
        'js': {
            'react': "https://unpkg.com/react@16/umd/react.development.js",
            'react-dom': "https://unpkg.com/react-dom@16/umd/react-dom.development.js",
            'babel': "https://unpkg.com/babel-standalone@latest/babel.min.js",
            'react-grid': "https://cdnjs.cloudflare.com/ajax/libs/react-grid-layout/1.1.1/react-grid-layout.min.js"
        },
        'css': {
            'bootstrap': "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css",
            'font-awesome': "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"
        }
    }

    def __init__(self, **params):
        if 'main' not in params:
            params['main'] = GridSpec(ncols=12, mode='override')
        super().__init__(**params)
        self._update_render_vars()

    def _update_render_items(self, event):
        super()._update_render_items(event)
        if event.obj is not self.main:
            return
        layouts = []
        for i, ((y0, x0, y1, x1), v) in enumerate(self.main.objects.items()):
            if x0 is None: x0 = 0
            if x1 is None: x1 = 12
            if y0 is None: y0 = 0
            if y1 is None: y1 = self.main.nrows
            layouts.append({'x': x0, 'y': y0, 'w': x1-x0, 'h': y1-y0, 'i': str(i+1)})
        self._render_variables['layouts'] = {'lg': layouts, 'md': layouts}

    @depends('cols', 'breakpoints', 'row_height', 'compact', watch=True)
    def _update_render_vars(self):
        self._render_variables['breakpoints'] = self.breakpoints
        self._render_variables['cols'] = self.cols
        self._render_variables['rowHeight'] = self.row_height
        self._render_variables['compact'] = self.compact


class ReactDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = ReactTemplate


class ReactDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = ReactTemplate
