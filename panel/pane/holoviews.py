"""
HoloViews integration for Panel including a Pane to render HoloViews
objects and their widgets and support for Links
"""
from __future__ import absolute_import, division, unicode_literals

import sys

from collections import OrderedDict, defaultdict
from functools import partial

import param
from bokeh.models import Spacer as _BkSpacer

from ..io import state
from ..layout import Panel, Column
from ..viewable import Viewable
from ..widgets import Player
from .base import PaneBase, Pane
from .plot import Bokeh, Matplotlib
from .plotly import Plotly


class HoloViews(PaneBase):
    """
    HoloViews panes render any HoloViews object to a corresponding
    Bokeh model while respecting the currently selected backend.
    """

    backend = param.ObjectSelector(
        default=None, objects=['bokeh', 'plotly', 'matplotlib'], doc="""
        The HoloViews backend used to render the plot (if None defaults
        to the currently selected renderer).""")

    widget_type = param.ObjectSelector(default='individual',
                                       objects=['individual', 'scrubber'], doc=""")
        Whether to generate individual widgets for each dimension or
        on global scrubber.""")

    widgets = param.Dict(default={}, doc="""
        A mapping from dimension name to a widget instance which will
        be used to override the default widgets.""")

    priority = 0.8

    _rerender_params = ['object', 'widgets', 'backend', 'widget_type']

    _panes = {'bokeh': Bokeh, 'matplotlib': Matplotlib, 'plotly': Plotly}

    _rename = {'backend': None, 'widget_type': None, 'widgets': None}

    def __init__(self, object=None, **params):
        super(HoloViews, self).__init__(object, **params)
        self.widget_box = Column()
        self._update_widgets()
        self._plots = {}
        self.param.watch(self._update_widgets, self._rerender_params)

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    def _update_widgets(self, *events):
        if self.object is None:
            widgets, values = [], []
        else:
            widgets, values = self.widgets_from_dimensions(self.object, self.widgets,
                                                           self.widget_type)
        self._values = values

        # Clean up anything models listening to the previous widgets
        for cb in list(self._callbacks):
            if cb.inst in self.widget_box.objects:
                cb.inst.param.unwatch(cb)
                self._callbacks.remove(cb)

        # Add new widget callbacks
        for widget in widgets:
            watcher = widget.param.watch(self._widget_callback, 'value')
            self._callbacks.append(watcher)

        self.widget_box.objects = widgets
        if widgets and not self.widget_box in self.layout.objects:
            self.layout.append(self.widget_box)
        elif not widgets and self.widget_box in self.layout.objects:
            self.layout.pop(self.widget_box)

    def _update_plot(self, plot, pane):
        from holoviews.core.util import cross_index

        widgets = self.widget_box.objects
        if not widgets:
            return
        elif self.widget_type == 'scrubber':
            key = cross_index([v for v in self._values.values()], widgets[0].value)
        else:
            key = tuple(w.value for w in widgets)

        if plot.backend == 'bokeh':
            if plot.comm or state._unblocked(plot.document):
                plot.update(key)
                if plot.comm and 'embedded' not in plot.root.tags:
                    plot.push()
            else:
                plot.document.add_next_tick_callback(partial(plot.update, key))
        else:
            plot.update(key)
            pane.object = plot.state

    def _widget_callback(self, event):
        for _, (plot, pane) in self._plots.items():
            self._update_plot(plot, pane)

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if root is None:
            return self.get_root(doc, comm)
        ref = root.ref['id']
        if self.object is None:
            model = _BkSpacer()
        else:
            plot = self._render(doc, comm, root)
            child_pane = self._panes.get(self.backend, Pane)(plot.state)
            self._update_plot(plot, child_pane)
            model = child_pane._get_model(doc, root, parent, comm)
            if ref in self._plots:
                old_plot, old_pane = self._plots[ref]
                old_plot.comm = None # Ensure comm does not cleaned up
                old_plot.cleanup()
            self._plots[ref] = (plot, child_pane)
        self._models[ref] = (model, parent)
        return model

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

    def _cleanup(self, root):
        """
        Traverses HoloViews object to find and clean up any streams
        connected to existing plots.
        """
        old_plot, old_pane = self._plots.pop(root.ref['id'], (None, None))
        if old_plot:
            old_plot.cleanup()
        if old_pane:
            old_pane._cleanup(root)
        super(HoloViews, self)._cleanup(root)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @classmethod
    def applies(cls, obj):
        if 'holoviews' not in sys.modules:
            return False
        from holoviews.core.dimension import Dimensioned
        return isinstance(obj, Dimensioned)

    @classmethod
    def widgets_from_dimensions(cls, object, widget_types={}, widgets_type='individual'):
        from holoviews.core import Dimension
        from holoviews.core.util import isnumeric, unicode, datetime_types
        from holoviews.core.traversal import unique_dimkeys
        from holoviews.plotting.util import get_dynamic_mode
        from ..widgets import Widget, DiscreteSlider, Select, FloatSlider, DatetimeInput

        dynamic, bounded = get_dynamic_mode(object)
        dims, keys = unique_dimkeys(object)
        if dims == [Dimension('Frame')] and keys == [(0,)]:
            return [], {}

        nframes = 1
        values = dict() if dynamic else dict(zip(dims, zip(*keys)))
        dim_values = OrderedDict()
        widgets = []
        for dim in dims:
            widget_type, widget, widget_kwargs = None, None, {}
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
                elif isinstance(widget, dict):
                    widget_type = widget.get('type', widget_type)
                    widget_kwargs = widget
                elif isinstance(widget, type) and issubclass(widget, Widget):
                    widget_type = widget
                else:
                    raise ValueError('Explicit widget definitions expected '
                                     'to be a widget instance or type, %s '
                                     'dimension widget declared as %s.' %
                                     (dim, widget))
            if vals:
                if all(isnumeric(v) or isinstance(v, datetime_types) for v in vals) and len(vals) > 1:
                    vals = sorted(vals)
                    labels = [unicode(dim.pprint_value(v)) for v in vals]
                    options = OrderedDict(zip(labels, vals))
                    widget_type = widget_type or DiscreteSlider
                else:
                    options = list(vals)
                    widget_type = widget_type or Select
                default = vals[0] if dim.default is None else dim.default
                widget_kwargs = dict(dict(name=dim.label, options=options, value=default), **widget_kwargs)
                widget = widget_type(**widget_kwargs)
            elif dim.range != (None, None):
                if dim.range[0] == dim.range[1]:
                    continue
                default = dim.range[0] if dim.default is None else dim.default
                step = 0.1 if dim.step is None else dim.step
                widget_type = widget_type or FloatSlider
                if isinstance(default, datetime_types):
                    widget_type = DatetimeInput
                widget_kwargs = dict(dict(step=step, name=dim.label, start=dim.range[0],
                                          end=dim.range[1], value=default),
                                     **widget_kwargs)
                widget = widget_type(**widget_kwargs)
            if widget is not None:
                widgets.append(widget)
        if widgets_type == 'scrubber':
            widgets = [Player(length=nframes)]
        return widgets, dim_values


def is_bokeh_element_plot(plot):
    """
    Checks whether plotting instance is a HoloViews ElementPlot rendered
    with the bokeh backend.
    """
    from holoviews.plotting.plot import GenericElementPlot, GenericOverlayPlot, Plot
    if not isinstance(plot, Plot):
        return False
    return (plot.renderer.backend == 'bokeh' and isinstance(plot, GenericElementPlot)
            and not isinstance(plot, GenericOverlayPlot))


def generate_panel_bokeh_map(root_model, panel_views):
    """
    mapping panel elements to its bokeh models
    """
    map_hve_bk = defaultdict(list)
    ref = root_model.ref['id']
    for pane in panel_views:
        if root_model.ref['id'] in pane._models:
            plot, subpane = pane._plots.get(ref, (None, None))
            if plot is None:
                continue
            bk_plots = plot.traverse(lambda x: x, [is_bokeh_element_plot])
            for plot in bk_plots:
                for hv_elem in plot.link_sources:
                    map_hve_bk[hv_elem].append(plot)
    return map_hve_bk


def find_links(root_view, root_model):
    """
    Traverses the supplied Viewable searching for Links between any
    HoloViews based panes.
    """
    if not isinstance(root_view, Panel):
        return

    hv_views = root_view.select(HoloViews)
    root_plots = [plot for view in hv_views for plot, _ in view._plots.values()
                  if getattr(plot, 'root', None) is root_model]

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

    new_found = set(found) - root_view._found_links
    callbacks = []
    for link, src_plot, tgt_plot in new_found:
        cb = Link._callbacks['bokeh'][type(link)]
        if src_plot is None or (getattr(link, '_requires_target', False)
                                and tgt_plot is None):
            continue
        callbacks.append(cb(root_model, link, src_plot, tgt_plot))
    root_view._found_links.update(new_found)
    return callbacks


Viewable._preprocessing_hooks.append(find_links)
