"""
HoloViews integration for Panel including a Pane to render HoloViews
objects and their widgets and support for Links
"""

from __future__ import absolute_import

import sys
from collections import OrderedDict

import param
from bokeh.layouts import Row as _BkRow

from .layout import Layout, WidgetBox
from .pane import PaneBase, Pane
from .viewable import Viewable


class HoloViews(PaneBase):
    """
    HoloViews panes render any HoloViews object to a corresponding
    Bokeh model while respecting the currently selected backend.
    """

    backend = param.String(default=None, doc="""
        The HoloViews backend used to render the plot (if None defaults
        to the currently selected renderer).""")

    show_widgets = param.Boolean(default=True, doc="""
        Whether to display widgets for the object. If disabled the
        widget_box may be laid out manually.""")

    widgets = param.Dict(default={}, doc="""
        A mapping from dimension name to a widget instance which will
        be used to override the default widgets.""")

    precedence = 0.8

    def __init__(self, object, **params):
        super(HoloViews, self).__init__(object, **params)
        self.widget_box = WidgetBox()
        self._plots = {}

    @classmethod
    def applies(cls, obj):
        if 'holoviews' not in sys.modules:
            return False
        from holoviews import Dimensioned
        return isinstance(obj, Dimensioned)

    def _cleanup(self, model=None, final=False):
        """
        Traverses HoloViews object to find and clean up any streams
        connected to existing plots.
        """
        self._plots.pop(model.ref['id']).cleanup()
        super(HoloViews, self)._cleanup(model, final)

    def _render(self, doc, comm, root):
        from holoviews import Store, renderer
        if not Store.renderers:
            loaded_backend = (self.backend or 'bokeh')
            renderer(loaded_backend)
            Store.current_backend = loaded_backend
        backend = self.backend or Store.current_backend
        renderer = Store.renderers[backend]
        if backend == 'bokeh':
            renderer = renderer.instance(mode='server' if comm is None else 'default')
        kwargs = {'doc': doc, 'root': root} if backend == 'bokeh' else {}
        if comm:
            kwargs['comm'] = comm
        return renderer.get_plot(self.object, **kwargs)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the Bokeh model to be rendered.
        """
        plot = self._render(doc, comm, root)
        child_pane = Pane(plot.state, _temporary=True)
        model = child_pane._get_model(doc, root, parent, comm)
        widgets = self.widgets_from_dimensions(self.object, self.widgets)
        layout = model
        if widgets:
            self.widget_box.objects = widgets
            if self.show_widgets:
                layout = _BkRow()
                wbox = self.widget_box._get_model(doc, root, parent, comm)
                layout.children = [model, wbox]
            self._link_widgets(widgets, child_pane, layout, plot, comm)
        self._link_object(layout, doc, root, parent, comm)
        self._plots[layout.ref['id']] = plot
        return layout

    def _link_widgets(self, widgets, pane, model, plot, comm):
        def update_plot(change):
            from holoviews.plotting.bokeh.plot import BokehPlot
            key = tuple(w.value for w in widgets)
            if isinstance(plot, BokehPlot):
                if comm:
                    plot.update(key)
                    plot.push()
                else:
                    def update_plot():
                        plot.update(key)
                    plot.document.add_next_tick_callback(update_plot)
            else:
                plot.update(key)
                pane.object = plot.state

        for w in widgets:
            watcher = w.param.watch(update_plot, 'value')
            self._callbacks[model.ref['id']].append(watcher)

    @classmethod
    def widgets_from_dimensions(cls, object, widget_types={}):
        from holoviews.core import Dimension
        from holoviews.core.util import isnumeric, unicode
        from holoviews.core.traversal import unique_dimkeys
        from .widgets import Widget, DiscreteSlider, Select, FloatSlider

        dims, keys = unique_dimkeys(object)
        if dims == [Dimension('Frame')] and keys == [(0,)]:
            return []

        values = dict(zip(dims, zip(*keys)))
        widgets = []
        for dim in dims:
            widget_type = None
            vals = dim.values or values.get(dim, None)
            if dim.name in widget_types:
                widget = widget_types[dim.name]
                if isinstance(widget, Widget):
                    widgets.append(widget)
                    continue
                elif isinstance(widget, type) and issubclass(widget, Widget):
                    widget_type = widget
                else:
                    raise ValueError('Explicit widget definitions expected '
                                     'to be a widget instance or type, %s '
                                     'dimension widget declared as %s.' %
                                     (dim, widget))
            if vals:
                if all(isnumeric(v) for v in vals):
                    vals = sorted(vals)
                    labels = [unicode(dim.pprint_value(v)) for v in vals]
                    options = OrderedDict(zip(labels, vals))
                    widget_type = widget_type or DiscreteSlider
                else:
                    options = list(vals)
                    widget_type = widget_type or Select
                default = vals[0] if dim.default is None else dim.default
                widget = widget_type(name=dim.label, options=options, value=default)
            elif dim.range != (None, None):
                default = dim.range[0] if dim.default is None else dim.default
                step = 0.1 if dim.step is None else dim.step
                widget_type = widget_type or FloatSlider
                widget = widget_type(step=step, name=dim.label, start=dim.range[0],
                                     end=dim.range[1], value=default)
            widgets.append(widget)
        return widgets



def is_bokeh_element_plot(plot):
    from holoviews.plotting.plot import GenericElementPlot, GenericOverlayPlot 
    return (plot.renderer.backend == 'bokeh' and isinstance(plot, GenericElementPlot)
            and not isinstance(plot, GenericOverlayPlot))


def find_links(root_view, root_model):
    """
    Traverses the supplied plot and searches for any Links on
    the plotted objects.
    """
    if not isinstance(root_view, Layout):
        return

    from holoviews.plotting.links import Link
    from holoviews.plotting.bokeh.callbacks import LinkCallback

    hv_views = root_view.select(HoloViews)
    root_plots = [plot for view in hv_views for plot in view._plots.values()
                  if plot.root is root_model]
    plots = [plot for root_plot in root_plots
             for plot in root_plot.traverse(lambda x: x, [is_bokeh_element_plot])]
    potentials = [LinkCallback.find_link(plot) for plot in plots]
    source_links = [p for p in potentials if p is not None]
    found = []
    for plot, links in source_links:
        for link in links:
            if link.target is None:
                # If link has no target don't look further
                found.append((link, plot, None))
                continue
            potentials = [LinkCallback.find_link(plot, link) for plot in plots]
            tgt_links = [p for p in potentials if p is not None]
            if tgt_links:
                found.append((link, plot, tgt_links[0][0]))

    callbacks = []
    for link, src_plot, tgt_plot in found:
        cb = Link._callbacks['bokeh'][type(link)]
        callbacks.append(cb(root_model, link, src_plot, tgt_plot))
    return callbacks


Viewable._preprocessing_hooks.append(find_links)
