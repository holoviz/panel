"""
Vanilla template
"""
import pathlib

from ..base import BasicTemplate


class VanillaTemplate(BasicTemplate):
    """
    VanillaTemplate is built on top of Vanilla web components.
    """

    _css = pathlib.Path(__file__).parent / 'vanilla.css'

    _template = pathlib.Path(__file__).parent / 'vanilla.html'

    def _apply_root(self, name, model, tags):
        if 'main' in tags:
            model.margin = (10, 15, 10, 10)
