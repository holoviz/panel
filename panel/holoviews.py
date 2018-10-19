"""
HoloViews integration for Panel including a Pane to render HoloViews
objects and their widgets and support for Links
"""

from __future__ import absolute_import

import sys
from collections import OrderedDict

import param
from bokeh.layouts import Row as _BkRow, Column as _BkColumn

from .layout import Layout, WidgetBox
from .pane import PaneBase, Pane
from .viewable import Viewable
from .widgets import Player


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

    widget_type = param.ObjectSelector(default='individual',
                                       objects=['individual', 'scrubber'], doc=""")
        Whether to generate individual widgets for each dimension or
        on global scrubber.""")

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
        widgets, values = self.widgets_from_dimensions(self.object, self.widgets, self.widget_type)
        self._values = values
        layout = model
        if widgets:
            self.widget_box.objects = widgets
            if self.show_widgets:
                wbox = self.widget_box._get_model(doc, root, parent, comm)
                if self.widget_type == 'individual':
                    layout = _BkRow()
                else:
                    layout = _BkColumn()
                layout.children = [model, wbox]
            self._link_widgets(widgets, child_pane, layout, plot, comm)
        self._link_object(layout, doc, root, parent, comm)
        self._plots[layout.ref['id']] = plot
        return layout

    def _link_widgets(self, widgets, pane, model, plot, comm):
        from holoviews.core.util import cross_index

        def update_plot(change):
            from holoviews.plotting.bokeh.plot import BokehPlot
            if self.widget_type == 'scrubber':
                key = cross_index([v for v in self._values.values()], widgets[0].value)
            else:
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
    def widgets_from_dimensions(cls, object, widget_types={}, widgets_type='individual'):
        from holoviews.core import Dimension
        from holoviews.core.util import isnumeric, unicode
        from holoviews.core.traversal import unique_dimkeys
        from .widgets import Widget, DiscreteSlider, Select, FloatSlider

        dims, keys = unique_dimkeys(object)
        if dims == [Dimension('Frame')] and keys == [(0,)]:
            return []

        nframes = 1
        values = dict(zip(dims, zip(*keys)))
        dim_values = OrderedDict()
        widgets = []
        for dim in dims:
            widget_type = None
            vals = dim.values or values.get(dim, None)
            dim_values[dim.name] = vals
            if widgets_type == 'scrubber':
                if not vals:
                    raise ValueError('Scrubber widget may only be used if all dimensions define values.')
                nframes *= len(vals)
            elif dim.name in widget_types:
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
        if widgets_type == 'scrubber':
            widgets = [Player(length=nframes)]
        return widgets, dim_values



def is_bokeh_element_plot(plot):
    """
    Checks whether plotting instance is a HoloViews ElementPlot rendered
    with the bokeh backend.
    """
    from holoviews.plotting.plot import GenericElementPlot, GenericOverlayPlot 
    return (plot.renderer.backend == 'bokeh' and isinstance(plot, GenericElementPlot)
            and not isinstance(plot, GenericOverlayPlot))


def find_links(root_view, root_model):
    """
    Traverses the supplied Viewable searching for Links between any
    HoloViews based panes.
    """
    if not isinstance(root_view, Layout):
        return

    hv_views = root_view.select(HoloViews)
    root_plots = [plot for view in hv_views for plot in view._plots.values()
                  if plot.root is root_model]

    if not root_plots:
        return

    try:
        from holoviews.plotting.links import Link
        from holoviews.plotting.bokeh.callbacks import LinkCallback
    except:
        return

    plots = [(plot, root_plot) for root_plot in root_plots
             for plot in root_plot.traverse(lambda x: x, [is_bokeh_element_plot])]

    potentials = [(LinkCallback.find_link(plot), root_plot)
                  for plot, root_plot in plots]
    source_links = [p for p in potentials if p[0] is not None]
    found = []
    for (plot, links), root_plot in source_links:
        for link in links:
            if link.target is None:
                # If link has no target don't look further
                found.append((link, plot, None))
                continue
            potentials = [LinkCallback.find_link(plot, link) for plot, inner_root in plots
                          if inner_root is not root_plot]
            tgt_links = [p for p in potentials if p is not None]
            if tgt_links:
                found.append((link, plot, tgt_links[0][0]))

    callbacks = []
    for link, src_plot, tgt_plot in found:
        cb = Link._callbacks['bokeh'][type(link)]
        callbacks.append(cb(root_model, link, src_plot, tgt_plot))
    return callbacks


Viewable._preprocessing_hooks.append(find_links)
