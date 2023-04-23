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

    sidebar_width = param.Integer(default=20, constant=True, doc="""
        The width of the sidebar in percent.""")

    _css = pathlib.Path(__file__).parent / 'golden.css'

    _template = pathlib.Path(__file__).parent / 'golden.html'

    _resources = {
        'css': {
            'goldenlayout': f"{config.npm_cdn}/golden-layout@1.5.9/dist/css/goldenlayout-base.css",
            'golden-layout': f"{config.npm_cdn}/golden-layout@1.5.9/dist/css/theme/goldenlayout-dark-theme.css"
        },
        'js': {
            'jquery': JS_URLS['jQuery'],
            'goldenlayout': f"{config.npm_cdn}/golden-layout@1.5.9/dist/goldenlayout.min.js"
        }
    }

    def _apply_root(self, name, model, tags):
        if 'main' in tags:
            model.margin = (10, 15, 10, 10)
