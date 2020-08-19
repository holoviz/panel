"""
React template 
"""
import pathlib

import param

from ...layout import Card
from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme

from jinja2 import environment

class ReactTemplate(BasicTemplate):
    """
    ReactTemplate is built on top of React Grid Layout web components.
    """

    _css = pathlib.Path(__file__).parent / 'react.css'

    _template = pathlib.Path(__file__).parent / 'react.html'

    _modifiers = {
        Card: {
            'children': {'margin': (0, 10)}
        }
    }

    def __init__(self, **params):
        super(ReactTemplate, self).__init__(**params)
        self.layouts = {}
        self.breakpoints = {}
        self.cols = {}
        self.rowHeight = {}

    def define_id(s):   
        s = s[6:-7] # 
        return  'panelID_' + dict([i.split('=') for i in s.split(' ')])['data-root-id'].replace('"','').replace('-','')

    environment.DEFAULT_FILTERS['define_id'] = define_id

    def _apply_root(self, name, model, tags):
        if 'main' in tags:
            model.margin = (10, 15, 10, 10)

    
    def config_layout(self, layouts, breakpoints,cols,rowHeight=30):
        """
        Configure layout of the responsive
        react grid layout component

        class MyResponsiveGrid ..........
        // {lg: layout1, md: layout2, ...}
        const layouts = getLayoutsFromSomewhere();
        return (
        <ResponsiveGridLayout className="layout" layouts={layouts}
        breakpoints={{lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0}}
        cols={{lg: 12, md: 10, sm: 6, xs: 4, xxs: 2}}>
        <div key="1">1</div>
        <div key="2">2</div>
        <div key="3">3</div>
      </ResponsiveGridLayout>
       where for each breakpoint you need define a layout 
       for each card
        // layout is an array of objects, see the demo for more complete usage
        const layout = [
        {i: 'a', x: 0, y: 0, w: 1, h: 2, static: true},
        {i: 'b', x: 1, y: 0, w: 3, h: 2, minW: 2, maxW: 4},
        {i: 'c', x: 4, y: 0, w: 1, h: 2}
        """

        self._render_variables['layouts'] = layouts
        self._render_variables['breakpoints'] = breakpoints
        self._render_variables['cols'] = cols
        self._render_variables['rowHeight'] = rowHeight


class ReactDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = ReactTemplate


class ReactDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = ReactTemplate
