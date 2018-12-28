"""
HoloViews integration for Panel including a Pane to render HoloViews
objects and their widgets and support for Links
"""

from __future__ import absolute_import

import sys
from collections import OrderedDict

import param
import weakref

from .layout import Panel, WidgetBox
from .pane import PaneBase, Pane
from .viewable import Viewable
from .widgets import Player

from functools import partial
from holoviews.plotting.links import Link as HvLink



class HoloViews(PaneBase):
    """
    HoloViews panes render any HoloViews object to a corresponding
    Bokeh model while respecting the currently selected backend.
    """

    backend = param.String(default=None, doc="""
        The HoloViews backend used to render the plot (if None defaults
        to the currently selected renderer).""")

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
        self._update_widgets()
        self._plots = {}

    @param.depends('object', 'widgets', watch=True)
    def _update_widgets(self):
        if self.object is None:
            widgets, values = []
        else:
            widgets, values = self.widgets_from_dimensions(self.object, self.widgets,
                                                           self.widget_type)
        self._values = values

        # Clean up anything models listening to the previous widgets
        for _, cbs in self._callbacks.items():
            for cb in list(cbs):
                if cb.inst in self.widget_box.objects:
                    print(cb)
                    cb.inst.param.unwatch(cb)
                    cbs.remove(cb)

        self.widget_box.objects = widgets
        if widgets and not self.widget_box in self.layout.objects:
            self.layout.append(self.widget_box)
        elif not widgets and self.widget_box in self.layout.objects:
            self.layout.pop(self.widget_box)

    @classmethod
    def applies(cls, obj):
        if 'holoviews' not in sys.modules:
            return False
        from holoviews.core.dimension import Dimensioned
        return isinstance(obj, Dimensioned)

    def _cleanup(self, root=None, final=False):
        """
        Traverses HoloViews object to find and clean up any streams
        connected to existing plots.
        """
        if root is not None:
            old_plot = self._plots.pop(root.ref['id'], None)
            if old_plot:
                old_plot.cleanup()
        super(HoloViews, self)._cleanup(root, final)

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
        plot = renderer.get_plot(self.object, **kwargs)
        ref = root.ref['id']
        if ref in self._plots:
            old_plot = self._plots[ref]
            old_plot.comm = None
            old_plot.cleanup()
        self._plots[root.ref['id']] = plot
        return plot

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the Bokeh model to be rendered.
        """
        ref = root.ref['id']
        plot = self._render(doc, comm, root)
        child_pane = Pane(plot.state, _temporary=True)
        model = child_pane._get_model(doc, root, parent, comm)
        self._models[ref] = model
        self._link_object(doc, root, parent, comm)
        if self.widget_box.objects:
            self._link_widgets(child_pane, root, comm)
        return model

    def _link_widgets(self, pane, root, comm):
        def update_plot(change):
            from holoviews.core.util import cross_index
            from holoviews.plotting.bokeh.plot import BokehPlot

            widgets = self.widget_box.objects
            if self.widget_type == 'scrubber':
                key = cross_index([v for v in self._values.values()], widgets[0].value)
            else:
                key = tuple(w.value for w in widgets)

            plot = self._plots[root.ref['id']]
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

        ref = root.ref['id']
        for w in self.widget_box.objects:
            watcher = w.param.watch(update_plot, 'value')
            self._callbacks[ref].append(watcher)

    @classmethod
    def widgets_from_dimensions(cls, object, widget_types={}, widgets_type='individual'):
        from holoviews.core import Dimension
        from holoviews.core.util import isnumeric, unicode
        from holoviews.core.traversal import unique_dimkeys
        from .widgets import Widget, DiscreteSlider, Select, FloatSlider

        dims, keys = unique_dimkeys(object)
        if dims == [Dimension('Frame')] and keys == [(0,)]:
            return [], {}

        nframes = 1
        values = dict(zip(dims, zip(*keys)))
        dim_values = OrderedDict()
        widgets = []
        for dim in dims:
            widget_type, widget = None, None
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
            if widget is not None:
                widgets.append(widget)
        if widgets_type == 'scrubber':
            widgets = [Player(length=nframes)]
        return widgets, dim_values


class PanelLink(HvLink):
    """
    Link between HoloViews elements containing Bokeh plots
    """
    
    registry = weakref.WeakKeyDictionary()


class RangeAxesLink(PanelLink):
    """
    The RangeAxesLink sets up a link between the axes of the source
    plot and the axes on the target plot. By default it will
    link along the x-axis but using the axes parameter both axes may
    be linked to the tool.
    """

    axes = param.ListSelector(default=['x', 'y'], objects=['x', 'y'], doc="""
        Which axes to link the tool to.""")


class RangeAxesLinkCallback(param.Parameterized):
    """
    Links source plot axes to the specified axes on the target plot
    """

    def __init__(self, root_model, link, source_plot, target_plot):
        if 'x' in link.axes:
            target_plot.handles['plot'].x_range = source_plot.handles['plot'].x_range
        if 'y' in link.axes:
            target_plot.handles['plot'].y_range = source_plot.handles['plot'].y_range


def is_bokeh_element_plot(plot):
    """
    Checks whether plotting instance is a HoloViews ElementPlot rendered
    with the bokeh backend.
    """
    from holoviews.plotting.plot import GenericElementPlot, GenericOverlayPlot
    return (plot.renderer.backend == 'bokeh' and isinstance(plot, GenericElementPlot)
            and not isinstance(plot, GenericOverlayPlot))


def generate_hvelems_bkplots_map(root_model, hv_views):
    #mapping holoview element -> bokeh plot
    from collections import defaultdict
    map_hve_bk = defaultdict(list)
    for hv_view in hv_views:
        if root_model.ref['id'] in hv_view._plots: 
            bk_plots = hv_view._plots[root_model.ref['id']].traverse(lambda x: x, [is_bokeh_element_plot])
            for plot in bk_plots:
                for hv_elem in plot.link_sources:
                    map_hve_bk[hv_elem].append(plot) 
    return map_hve_bk


def find_links(root_view, root_model, linker=HvLink):
    """
    Traverses the supplied Viewable searching for Links between any
    HoloViews based panes.
    """
    if not isinstance(root_view, Panel) or not root_model:
        return

    hv_views = root_view.select(HoloViews)
    
    if not hv_views:
        return
    
    map_hve_bk = generate_hvelems_bkplots_map(root_model, hv_views)
    
    from itertools import product
    found = [(link, src_plot, tgt_plot) for hv_elem in map_hve_bk.keys() 
             if hv_elem in linker.registry
             for link in linker.registry[hv_elem]
             for src_plot, tgt_plot in product(map_hve_bk[hv_elem], map_hve_bk[link.target])]

    callbacks = []
    for link, src_plot, tgt_plot in found:
        cb = linker._callbacks['bokeh'][type(link)]
        if src_plot is None or (getattr(link, '_requires_target', False)
                                and tgt_plot is None):
            continue
        callbacks.append(cb(root_model, link, src_plot, tgt_plot))
    return callbacks


RangeAxesLink.register_callback(backend='bokeh',
                                callback = RangeAxesLinkCallback)

Viewable._preprocessing_hooks.append(find_links)
Viewable._preprocessing_hooks.append(partial(find_links, linker=PanelLink))
