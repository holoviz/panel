"""
GoldenTemplate based on the golden-layout library.
"""
import pathlib

import param

from ...config import config
from ...io.resources import JS_URLS
from ..base import BasicTemplate


class GoldenTemplate(BasicTemplate):
    """
    GoldenTemplate is built on top of golden-layout library.
    """
    sidebar_width = param.Integer(20, doc="""
        The width of the sidebar in percent. Default is 20.""")

    _css = pathlib.Path(__file__).parent / 'golden.css'

    _template = pathlib.Path(__file__).parent / 'golden.html'

    _resources = {
        'css': {
            'goldenlayout': f"{config.npm_cdn}/golden-layout@1.5.9/src/css/goldenlayout-base.css",
        },
        'js': {
            'jquery': JS_URLS['jQuery'],
            'goldenlayout': f"{config.npm_cdn}/golden-layout@1.5.9/dist/goldenlayout.min.js"
        }
    }

    def _apply_root(self, name, model, tags):
        if 'main' in tags:
            model.margin = (10, 15, 10, 10)
