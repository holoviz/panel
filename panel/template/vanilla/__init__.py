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
    VanillaTemplate is built on top of Vanilla web components.
    """

    design = param.ClassSelector(class_=Design, default=Native, constant=True,
                                 is_instance=False, instantiate=False, doc="""
        A Design applies a specific design system to a template.""")

    _css = pathlib.Path(__file__).parent / 'vanilla.css'

    _template = pathlib.Path(__file__).parent / 'vanilla.html'

    def _apply_root(self, name, model, tags):
        if 'main' in tags:
            model.margin = (10, 15, 10, 10)
