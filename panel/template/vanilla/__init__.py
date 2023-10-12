"""
Vanilla template
"""
import pathlib

from typing import ClassVar, Dict

import param

from ...theme import Design
from ...theme.native import Native
from ..base import BasicTemplate


class VanillaTemplate(BasicTemplate):
    """
    VanillaTemplate is built on top of Vanilla web components.
    """

    design = param.ClassSelector(class_=Design, default=Native,
                                 is_instance=False, instantiate=False, doc="""
        A Design applies a specific design system to a template.""")

    _css = pathlib.Path(__file__).parent / 'vanilla.css'

    _resources: ClassVar[Dict[str, Dict[str, str]]] = {
        'css': {
            'lato': "https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext"
        }
    }

    _template = pathlib.Path(__file__).parent / 'vanilla.html'
