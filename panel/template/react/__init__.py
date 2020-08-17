"""
React template 
"""
import pathlib

import param

from ...layout import Card
from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme
from ...layout import ListLike

from jinja2 import environment
import random
import string

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
        self.data_grid = []

    def define_id(s):   
        s = s[6:-7] # 
        return  'panelID_' + dict([i.split('=') for i in s.split(' ')])['data-root-id'].replace('"','').replace('-','')

    environment.DEFAULT_FILTERS['define_id'] = define_id

    def _apply_root(self, name, model, tags):
        if 'main' in tags:
            model.margin = (10, 15, 10, 10)

    

    def add_data_grid(self, name, value):
        """
        Add parameters to the template, which may then be referenced
        by the given name in the Jinja2 template.

        Arguments
        ---------
        name : str
          The name to refer to the panel by in the template
        value : object
          Any valid Jinja2 variable type.
        """
     
        self.data_grid.append(value)

        if name in self._render_variables:
            raise ValueError('The name %s has already been used for '
                             'another variable. Ensure each variable '
                             'has a unique name by which it can be '
                             'referenced in the template.' % name)
        self._render_variables['data_grid'] = self.data_grid


class ReactDefaultTheme(DefaultTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'default.css')

    _template = ReactTemplate


class ReactDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = ReactTemplate
