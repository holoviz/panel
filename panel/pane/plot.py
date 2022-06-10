"""
Pane class which render plots from different libraries
"""
from __future__ import annotations

import sys

from contextlib import contextmanager
from io import BytesIO
from typing import (
    TYPE_CHECKING, Any, ClassVar, Mapping, Optional,
)

import param

from bokeh.models import (
    CustomJS, LayoutDOM, Model, Spacer as BkSpacer,
)
from bokeh.themes import Theme

from ..io import remove_root
from ..io.notebook import push
from ..util import escape
from ..viewable import Layoutable
from .base import PaneBase
from .image import PNG
from .ipywidget import IPyWidget
from .markup import HTML

if TYPE_CHECKING:
    from bokeh.document import Document
    from pyviz_comms import Comm

FOLIUM_BEFORE = '<div style="width:100%;"><div style="position:relative;width:100%;height:0;padding-bottom:60%;">'
FOLIUM_AFTER = '<div style="width:100%;height:100%"><div style="position:relative;width:100%;height:100%;padding-bottom:0%;">'

@contextmanager
def _wrap_callback(cb, wrapped, doc, comm, callbacks):
    """
    Wraps a bokeh callback ensuring that any events triggered by it
    appropriately dispatch events in the notebook. Also temporarily
    replaces the wrapped callback with the real one while the callback
    is exectuted to ensure the callback can be removed as usual.
    """
    hold = doc.callbacks.hold_value
    doc.hold('combine')
    if wrapped in callbacks:
        index = callbacks.index(wrapped)
        callbacks[index] = cb
    yield
    if cb in callbacks:
        index = callbacks.index(cb)
        callbacks[index] = wrapped
    push(doc, comm)
    doc.hold(hold)


class Bokeh(PaneBase):
    """
    The Bokeh pane allows displaying any displayable Bokeh model inside a
    Panel app.

    Reference: https://panel.holoviz.org/reference/panes/Bokeh.html

    :Example:

    >>> Bokeh(some_bokeh_figure)
    """

    autodispatch = param.Boolean(default=True, doc="""
        Whether to automatically dispatch events inside bokeh on_change
        and on_event callbacks in the notebook.""")

    theme = param.ClassSelector(default=None, class_=(Theme, str), doc="""
        Bokeh theme to apply to the plot.""")

    priority: ClassVar[float | bool | None] = 0.8

    _rename: ClassVar[Mapping[str, str | None]] = {'autodispatch': None, 'theme': None}

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return isinstance(obj, LayoutDOM)

    @classmethod
    def _property_callback_wrapper(cls, cb, doc, comm, callbacks):
        def wrapped_callback(attr, old, new):
            with _wrap_callback(cb, wrapped_callback, doc, comm, callbacks):
                cb(attr, old, new)
        return wrapped_callback

    @classmethod
    def _event_callback_wrapper(cls, cb, doc, comm, callbacks):
        def wrapped_callback(event):
            with _wrap_callback(cb, wrapped_callback, doc, comm, callbacks):
                cb(event)
        return wrapped_callback

    @classmethod
    def _wrap_bokeh_callbacks(cls, root, bokeh_model, doc, comm):
        for model in bokeh_model.select({'type': Model}):
            for key, cbs in model._callbacks.items():
                callbacks = model._callbacks[key]
                callbacks[:] = [
                    cls._property_callback_wrapper(cb, doc, comm, callbacks)
                    for cb in cbs
                ]
            for key, cbs in model._event_callbacks.items():
                callbacks = model._event_callbacks[key]
                callbacks[:] = [
                    cls._event_callback_wrapper(cb, doc, comm, callbacks)
                    for cb in cbs
                ]

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        if root is None:
            return self.get_root(doc, comm)

        if self.object is None:
            model = BkSpacer()
        else:
            model = self.object

        properties = {}
        for p, value in self.param.values().items():
            if (p not in Layoutable.param or p == 'name' or
                value is self.param[p].default):
                continue
            properties[p] = value
        model.update(**properties)
        if comm and self.autodispatch:
            self._wrap_bokeh_callbacks(root, model, doc, comm)

        ref = root.ref['id']
        for js in model.select({'type': CustomJS}):
            js.code = js.code.replace(model.ref['id'], ref)

        if model._document and doc is not model._document:
            remove_root(model, doc)

        self._models[ref] = (model, parent)

        if self.theme:
            doc.theme = self.theme

        return model


class Matplotlib(PNG, IPyWidget):
    """
    The `Matplotlib` pane allows displaying any displayable Matplotlib figure
    inside a Panel app.

    - It will render the plot to PNG at the declared DPI and then embed it.
    - If you find the figure to be clipped on the edges, you can set `tight=True`
    to automatically resize objects to fit within the pane.
    - If you have installed `ipympl` you will also be able to use the
    interactive backend.

    Reference: https://panel.holoviz.org/reference/panes/Matplotlib.html

    :Example:

    >>> Matplotlib(some_matplotlib_figure, dpi=144)
    """

    dpi = param.Integer(default=144, bounds=(1, None), doc="""
        Scales the dpi of the matplotlib figure.""")

    high_dpi = param.Boolean(default=True, doc="""
        Whether to optimize output for high-dpi displays.""")

    interactive = param.Boolean(default=False, constant=True, doc="""
        Whether to render interactive matplotlib plot with ipympl.""")

    tight = param.Boolean(default=False, doc="""
        Automatically adjust the figure size to fit the
        subplots and other artist elements.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'object': 'text', 'interactive': None, 'dpi': None,  'tight': None, 'high_dpi': None
    }

    _rerender_params = PNG._rerender_params + ['object', 'dpi', 'tight']

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if 'matplotlib' not in sys.modules:
            return False
        from matplotlib.figure import Figure
        is_fig = isinstance(obj, Figure)
        if is_fig and obj.canvas is None:
            raise ValueError('Matplotlib figure has no canvas and '
                             'cannot be rendered.')
        return is_fig

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._managers = {}

    def _get_widget(self, fig):
        import matplotlib.backends
        old_backend = getattr(matplotlib.backends, 'backend', 'agg')

        from ipympl.backend_nbagg import Canvas, FigureManager, is_interactive
        from matplotlib._pylab_helpers import Gcf

        matplotlib.use(old_backend)

        def closer(event):
            Gcf.destroy(0)

        canvas = Canvas(fig)
        fig.patch.set_alpha(0)
        manager = FigureManager(canvas, 0)

        if is_interactive():
            fig.canvas.draw_idle()

        canvas.mpl_connect('close_event', closer)
        return manager

    def _update_dimensions(self):
        w, h = self.object.get_size_inches()
        dpi = self.dpi / 2. if self.high_dpi else self.dpi
        with param.discard_events(self):
            self.width = self.width or int(dpi * w)
            self.height = self.height or int(dpi * h)

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        self._update_dimensions()
        if not self.interactive:
            model = PNG._get_model(self, doc, root, parent, comm)
            return model
        self.object.set_dpi(self.dpi)
        manager = self._get_widget(self.object)
        props = self._process_param_change(self._init_params())
        kwargs = {k: v for k, v in props.items()
                  if k not in self._rerender_params+['interactive']}
        kwargs['width'] = self.width
        kwargs['height'] = self.height
        kwargs['sizing_mode'] = self.sizing_mode
        model = self._get_ipywidget(
            manager.canvas, doc, root, comm, **kwargs
        )
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        self._managers[root.ref['id']] = manager
        return model

    def _update(self, ref: str, model: Model) -> None:
        if not self.interactive:
            self._update_dimensions()
            model.update(**self._get_properties())
            return
        manager = self._managers[ref]
        if self.object is not manager.canvas.figure:
            self.object.set_dpi(self.dpi)
            self.object.patch.set_alpha(0)
            manager.canvas.figure = self.object
            self.object.set_canvas(manager.canvas)
            event = {'width': manager.canvas._width,
                     'height': manager.canvas._height}
            manager.canvas.handle_resize(event)
        manager.canvas.draw_idle()

    def _data(self):
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
    def applies(cls, obj: Any) -> float | bool | None:
        return type(obj).__name__ == 'GGPlot' and hasattr(obj, 'r_repr')

    def _img(self):
        from rpy2 import robjects
        from rpy2.robjects.lib import grdevices
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

    priority: ClassVar[float | bool | None] = 0.5

    @classmethod
    def applies(cls, obj: bool) -> float | bool | None:
        return (getattr(obj, '__module__', '').startswith('yt.') and
                hasattr(obj, "plots") and
                hasattr(obj, "_repr_html_"))

    def _get_properties(self):
        p = super()._get_properties()
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


class Folium(HTML):
    """
    The Folium pane wraps Folium map components.
    """

    sizing_mode = param.ObjectSelector(default='stretch_width', objects=[
        'fixed', 'stretch_width', 'stretch_height', 'stretch_both',
        'scale_width', 'scale_height', 'scale_both', None])

    priority: ClassVar[float | bool | None] = 0.6

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return (getattr(obj, '__module__', '').startswith('folium.') and
                hasattr(obj, "_repr_html_"))

    def _get_properties(self):
        properties = super()._get_properties()
        text = '' if self.object is None else self.object
        if hasattr(text, '_repr_html_'):
            text = text._repr_html_().replace(FOLIUM_BEFORE, FOLIUM_AFTER)
        return dict(properties, text=escape(text))
