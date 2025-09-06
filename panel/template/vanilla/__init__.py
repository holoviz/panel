"""
Vanilla template
"""
import pathlib

import param

from ...theme import Design
from ...theme.native import Native
from ..base import BasicTemplate


class VanillaTemplate(BasicTemplate):
    """
    The VanillaTemplate is a basic template that depends solely on
    vanilla HTML and JS, i.e. does not require any specific framework.
    """

    design = param.ClassSelector(class_=Design, default=Native,
                                 is_instance=False, instantiate=False, doc="""
        A Design applies a specific design system to a template.""")

    _css = [pathlib.Path(__file__).parent / 'vanilla.css']

    _resources = {
        'css': {
            'lato': "https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext"
        }
    }

    _template = pathlib.Path(__file__).parent / 'vanilla.html'
