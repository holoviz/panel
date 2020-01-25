"""
Pane class which render plots from different libraries
"""
from __future__ import absolute_import, division, unicode_literals

import sys

from io import BytesIO

import param

from bokeh.models import LayoutDOM, CustomJS, Spacer as BkSpacer

from ..io import remove_root
from ..viewable import Layoutable
from .base import PaneBase
from .markup import HTML
from .image import PNG


class Bokeh(PaneBase):
    """
    Bokeh panes allow including any Bokeh model in a panel.
    """

    priority = 0.8

    @classmethod
    def applies(cls, obj):
        return isinstance(obj, LayoutDOM)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if root is None:
            return self._get_root(doc, comm)

        if self.object is None:
            model = BkSpacer()
        else:
            model = self.object

        properties = {}
        for p, value in self.param.get_param_values():
            if (p not in Layoutable.param or p == 'name' or
                value is self.param[p].default):
                continue
            properties[p] = value
        model.update(**properties)

        ref = root.ref['id']
        for js in model.select({'type': CustomJS}):
            js.code = js.code.replace(model.ref['id'], ref)

        if model._document and doc is not model._document:
            remove_root(model, doc)

        self._models[ref] = (model, parent)
        return model


class Matplotlib(PNG):
    """
    A Matplotlib pane renders a matplotlib figure to png and wraps the
    base64 encoded data in a bokeh Div model. The size of the image in
    pixels is determined by scaling the size of the figure in inches
    by a dpi of 72, increasing the dpi therefore controls the
    resolution of the image not the displayed size.
    """

    dpi = param.Integer(default=144, bounds=(1, None), doc="""
        Scales the dpi of the matplotlib figure.""")

    tight = param.Boolean(default=False, doc="""
        Automatically adjust the figure size to fit the
        subplots and other artist elements.""")

    _rerender_params = PNG._rerender_params + ['object', 'dpi', 'tight']

    @classmethod
    def applies(cls, obj):
        if 'matplotlib' not in sys.modules:
            return False
        from matplotlib.figure import Figure
        is_fig = isinstance(obj, Figure)
        if is_fig and obj.canvas is None:
            raise ValueError('Matplotlib figure has no canvas and '
                             'cannot be rendered.')
        return is_fig

    def _imgshape(self, data):
        """Calculate and return image width,height"""
        w, h = self.object.get_size_inches()
        return int(w*72), int(h*72)

    def _img(self):
        self.object.set_dpi(self.dpi)
        b = BytesIO()

        if self.tight:
            bbox_inches = 'tight'
        else:
            bbox_inches = None

        self.object.canvas.print_figure(b, bbox_inches=bbox_inches)
        return b.getvalue()


class RGGPlot(PNG):
    """
    An RGGPlot pane renders an r2py-based ggplot2 figure to png
    and wraps the base64-encoded data in a bokeh Div model.
    """

    height = param.Integer(default=400)

    width = param.Integer(default=400)

    dpi = param.Integer(default=144, bounds=(1, None))

    _rerender_params = PNG._rerender_params + ['object', 'dpi', 'width', 'height']

    @classmethod
    def applies(cls, obj):
        return type(obj).__name__ == 'GGPlot' and hasattr(obj, 'r_repr')

    def _img(self):
        from rpy2.robjects.lib import grdevices
        from rpy2 import robjects
        with grdevices.render_to_bytesio(grdevices.png,
                 type="cairo-png", width=self.width, height=self.height,
                 res=self.dpi, antialias="subpixel") as b:
            robjects.r("print")(self.object)
        return b.getvalue()


class YT(HTML):
    """
    YT panes wrap plottable objects from the YT library.
    By default, the height and width are calculated by summing all
    contained plots, but can optionally be specified explicitly to
    provide additional space.
    """

    priority = 0.5

    @classmethod
    def applies(cls, obj):
        return (getattr(obj, '__module__', '').startswith('yt.') and
                hasattr(obj, "plots") and
                hasattr(obj, "_repr_html_"))

    def _get_properties(self):
        p = super(YT, self)._get_properties()
        if self.object is None:
            return p

        width = height = 0
        if self.width  is None or self.height is None:
            for k,v in self.object.plots.items():
                if hasattr(v, "_repr_png_"):
                    img = v._repr_png_()
                    w,h = PNG._imgshape(img)
                    height += h
                    width = max(w, width)

        if self.width  is None: p["width"]  = width
        if self.height is None: p["height"] = height

        return p
