"""
HoloViews integration for Panel including a Pane to render HoloViews
objects and their widgets and support for Links
"""
import sys

from collections import OrderedDict, defaultdict
from distutils.version import LooseVersion
from functools import partial

import param

from bokeh.models import Spacer as _BkSpacer, Range1d
from bokeh.themes.theme import Theme

from ..io import state, unlocked
from ..layout import Column, WidgetBox, HSpacer, VSpacer, Row
from ..viewable import Layoutable, Viewable
from ..widgets import Player
from .base import PaneBase, Pane, RerenderError
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

    center = param.Boolean(default=False, doc="""
        Whether to center the plot.""")

    linked_axes = param.Boolean(default=True, doc="""
        Whether to use link the axes of bokeh plots inside this pane
        across a panel layout.""")

    renderer = param.Parameter(default=None, doc="""
        Explicit renderer instance to use for rendering the HoloViews
        plot. Overrides the backend.""")

    theme = param.ClassSelector(default=None, class_=(Theme, str),
                                allow_None=True, doc="""
        Bokeh theme to apply to the HoloViews plot.""")

    widget_location = param.ObjectSelector(default='right_top', objects=[
        'left', 'bottom', 'right', 'top', 'top_left', 'top_right',
        'bottom_left', 'bottom_right', 'left_top', 'left_bottom',
        'right_top', 'right_bottom'], doc="""
        The layout of the plot and the widgets. The value refers to the
        position of the widgets relative to the plot.""")

    widget_layout = param.ObjectSelector(
        objects=[WidgetBox, Row, Column], constant=True, default=WidgetBox, doc="""
        The layout object to display the widgets in.""")

    widget_type = param.ObjectSelector(default='individual',
                                       objects=['individual', 'scrubber'], doc=""")
        Whether to generate individual widgets for each dimension or
        on global scrubber.""")

    widgets = param.Dict(default={}, doc="""
        A mapping from dimension name to a widget instance which will
        be used to override the default widgets.""")

    priority = 0.8

    _panes = {'bokeh': Bokeh, 'matplotlib': Matplotlib, 'plotly': Plotly}

    _rename = {
        'backend': None, 'center': None, 'linked_axes': None,
        'renderer': None, 'theme': None, 'widgets': None,
        'widget_layout': None, 'widget_location': None,
        'widget_type': None
    }

    _rerender_params = ['object', 'backend']

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._initialized = False
        self._responsive_content = False
        self._restore_plot = None
        self.widget_box = self.widget_layout()
        self._widget_container = []
        self._update_widgets()
        self._plots = {}
        self.param.watch(self._update_widgets, self._rerender_params)
        self._initialized = True

    @param.depends('center', 'widget_location', watch=True)
    def _update_layout(self):
        loc = self.widget_location
        if not len(self.widget_box):
            widgets = []
        elif loc in ('left', 'right'):
            widgets = Column(VSpacer(), self.widget_box, VSpacer())
        elif loc in ('top', 'bottom'):
            widgets = Row(HSpacer(), self.widget_box, HSpacer())
        elif loc in ('top_left', 'bottom_left'):
            widgets = Row(self.widget_box, HSpacer())
        elif loc in ('top_right', 'bottom_right'):
            widgets = Row(HSpacer(), self.widget_box)
        elif loc in ('left_top', 'right_top'):
            widgets = Column(self.widget_box, VSpacer())
        elif loc in ('left_bottom', 'right_bottom'):
            widgets = Column(VSpacer(), self.widget_box)

        center = self.center and not self._responsive_content

        self._widget_container = widgets
        if not widgets:
            if center:
                components = [HSpacer(), self, HSpacer()]
            else:
                components = [self]
        elif center:
            if loc.startswith('left'):
                components = [widgets, HSpacer(), self, HSpacer()]
            elif loc.startswith('right'):
                components = [HSpacer(), self, HSpacer(), widgets]
            elif loc.startswith('top'):
                components = [HSpacer(), Column(widgets, Row(HSpacer(), self, HSpacer())), HSpacer()]
            elif loc.startswith('bottom'):
                components = [HSpacer(), Column(Row(HSpacer(), self, HSpacer()), widgets), HSpacer()]
        else:
            if loc.startswith('left'):
                components = [widgets, self]
            elif loc.startswith('right'):
                components = [self, widgets]
            elif loc.startswith('top'):
                components = [Column(widgets, self)]
            elif loc.startswith('bottom'):
                components = [Column(self, widgets)]
        self.layout[:] = components

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    @param.depends('theme', watch=True)
    def _update_theme(self, *events):
        if self.theme is None:
            return
        for (model, _) in self._models.values():
            if model.document:
                model.document.theme = self.theme

    @param.depends('widget_type', 'widgets', watch=True)
    def _update_widgets(self, *events):
        if self.object is None:
            widgets, values = [], []
        else:
            widgets, values = self.widgets_from_dimensions(
                self.object, self.widgets, self.widget_type)
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

        self.widget_box[:] = widgets
        if ((widgets and self.widget_box not in self._widget_container) or
            (not widgets and self.widget_box in self._widget_container) or
            not self._initialized):
            self._update_layout()

    def _update_plot(self, plot, pane):
        from holoviews.core.util import cross_index, wrap_tuple_streams

        widgets = self.widget_box.objects
        if not widgets:
            return
        elif self.widget_type == 'scrubber':
            key = cross_index([v for v in self._values.values()], widgets[0].value)
        else:
            key = tuple(w.value for w in widgets)
            if plot.dynamic:
                widget_dims = [w.name for w in widgets]
                key = [key[widget_dims.index(kdim)] if kdim in widget_dims else None
                       for kdim in plot.dimensions]
                key = wrap_tuple_streams(tuple(key), plot.dimensions, plot.streams)

        if plot.backend == 'bokeh':
            if plot.comm or state._unblocked(plot.document):
                with unlocked():
                    plot.update(key)
                if plot.comm and 'embedded' not in plot.root.tags:
                    plot.push()
            else:
                if plot.document.session_context:
                    plot.document.add_next_tick_callback(partial(plot.update, key))
                else:
                    plot.update(key)
        else:
            plot.update(key)
            if hasattr(plot.renderer, 'get_plot_state'):
                pane.object = plot.renderer.get_plot_state(plot)
            else:
                # Compatibility with holoviews<1.13.0
                pane.object = plot.state

    def _widget_callback(self, event):
        for _, (plot, pane) in self._plots.items():
            self._update_plot(plot, pane)

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _get_model(self, doc, root=None, parent=None, comm=None):
        from holoviews.plotting.plot import Plot
        if root is None:
            return self.get_root(doc, comm)
        ref = root.ref['id']
        if self.object is None:
            model = _BkSpacer()
            self._models[ref] = (model, parent)
            return model

        if self._restore_plot is not None:
            plot = self._restore_plot
            self._restore_plot = None
        elif isinstance(self.object, Plot):
            plot = self.object
        else:
            plot = self._render(doc, comm, root)

        plot.pane = self
        backend = plot.renderer.backend
        if hasattr(plot.renderer, 'get_plot_state'):
            state = plot.renderer.get_plot_state(plot)
        else:
            # Compatibility with holoviews<1.13.0
            state = plot.state

        # Ensure rerender if content is responsive but layout is centered
        if (backend == 'bokeh' and self.center and
            state.sizing_mode not in ('fixed', None)
            and not self._responsive_content):
            self._responsive_content = True
            self._update_layout()
            self._restore_plot = plot
            raise RerenderError()
        else:
            self._responsive_content = False

        kwargs = {p: v for p, v in self.param.get_param_values()
                  if p in Layoutable.param and p != 'name'}
        child_pane = self._panes.get(backend, Pane)(state, **kwargs)
        self._update_plot(plot, child_pane)
        model = child_pane._get_model(doc, root, parent, comm)
        if ref in self._plots:
            old_plot, old_pane = self._plots[ref]
            old_plot.comm = None # Ensures comm does not get cleaned up
            old_plot.cleanup()
        self._plots[ref] = (plot, child_pane)
        self._models[ref] = (model, parent)
        return model

    def _render(self, doc, comm, root):
        import holoviews as hv
        from holoviews import Store, renderer as load_renderer

        if self.renderer:
            renderer = self.renderer
            backend = renderer.backend
        else:
            if not Store.renderers:
                loaded_backend = (self.backend or 'bokeh')
                load_renderer(loaded_backend)
                Store.current_backend = loaded_backend
            backend = self.backend or Store.current_backend
            renderer = Store.renderers[backend]
        mode = 'server' if comm is None else 'default'
        if backend == 'bokeh':
            params = {}
            if self.theme is not None:
                params['theme'] = self.theme
            if mode != renderer.mode:
                params['mode'] = mode
            if params:
                renderer = renderer.instance(**params)

        kwargs = {'margin': self.margin}
        if backend == 'bokeh' or LooseVersion(str(hv.__version__)) >= str('1.13.0'):
            kwargs['doc'] = doc
            kwargs['root'] = root
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
        super()._cleanup(root)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @classmethod
    def applies(cls, obj):
        if 'holoviews' not in sys.modules:
            return False
        from holoviews.core.dimension import Dimensioned
        from holoviews.plotting.plot import Plot
        return isinstance(obj, Dimensioned) or isinstance(obj, Plot)

    @classmethod
    def widgets_from_dimensions(cls, object, widget_types=None, widgets_type='individual'):
        from holoviews.core import Dimension, DynamicMap
        from holoviews.core.options import SkipRendering
        from holoviews.core.util import isnumeric, unicode, datetime_types, unique_iterator
        from holoviews.core.traversal import unique_dimkeys
        from holoviews.plotting.plot import Plot, GenericCompositePlot
        from holoviews.plotting.util import get_dynamic_mode
        from ..widgets import Widget, DiscreteSlider, Select, FloatSlider, DatetimeInput, IntSlider

        if widget_types is None:
            widget_types = {}

        if isinstance(object, GenericCompositePlot):
            object = object.layout
        elif isinstance(object, Plot):
            object = object.hmap

        if isinstance(object, DynamicMap) and object.unbounded:
            dims = ', '.join('%r' % dim for dim in object.unbounded)
            msg = ('DynamicMap cannot be displayed without explicit indexing '
                   'as {dims} dimension(s) are unbounded. '
                   '\nSet dimensions bounds with the DynamicMap redim.range '
                   'or redim.values methods.')
            raise SkipRendering(msg.format(dims=dims))

        dynamic, bounded = get_dynamic_mode(object)
        dims, keys = unique_dimkeys(object)
        if ((dims == [Dimension('Frame')] and keys == [(0,)]) or
            (not dynamic and len(keys) == 1)):
            return [], {}

        nframes = 1
        values = dict() if dynamic else dict(zip(dims, zip(*keys)))
        dim_values = OrderedDict()
        widgets = []
        dims = [d for d in dims if values.get(d) is not None or
                d.values or d.range != (None, None)]

        for i, dim in enumerate(dims):
            widget_type, widget, widget_kwargs = None, None, {}

            if widgets_type == 'individual':
                if i == 0 and i == (len(dims)-1):
                    margin = (20, 20, 20, 20)
                elif i == 0:
                    margin = (20, 20, 5, 20)
                elif i == (len(dims)-1):
                    margin = (5, 20, 20, 20)
                else:
                    margin = (0, 20, 5, 20)
                kwargs = {'margin': margin, 'width': 250}
            else:
                kwargs = {}

            vals = dim.values or values.get(dim, None)
            if vals is not None:
                vals = list(unique_iterator(vals))
            dim_values[dim.name] = vals
            if widgets_type == 'scrubber':
                if not vals:
                    raise ValueError('Scrubber widget may only be used if all dimensions define values.')
                nframes *= len(vals)
            elif dim.name in widget_types:
                widget = widget_types[dim.name]
                if isinstance(widget, Widget):
                    widget.param.set_param(**kwargs)
                    if not widget.name:
                        widget.name = dim.label
                    widgets.append(widget)
                    continue
                elif isinstance(widget, dict):
                    widget_type = widget.get('type', widget_type)
                    widget_kwargs = dict(widget)
                elif isinstance(widget, type) and issubclass(widget, Widget):
                    widget_type = widget
                else:
                    raise ValueError('Explicit widget definitions expected '
                                     'to be a widget instance or type, %s '
                                     'dimension widget declared as %s.' %
                                     (dim, widget))
            widget_kwargs.update(kwargs)

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
                start, end = dim.range
                if start == end:
                    continue
                default = start if dim.default is None else dim.default
                if widget_type is not None:
                    pass
                elif all(isinstance(v, int) for v in (start, end, default)):
                    widget_type = IntSlider
                    step = 1 if dim.step is None else dim.step
                elif isinstance(default, datetime_types):
                    widget_type = DatetimeInput
                else:
                    widget_type = FloatSlider
                    step = 0.1 if dim.step is None else dim.step
                widget_kwargs = dict(dict(step=step, name=dim.label, start=dim.range[0],
                                          end=dim.range[1], value=default),
                                     **widget_kwargs)
                widget = widget_type(**widget_kwargs)
            if widget is not None:
                widgets.append(widget)
        if widgets_type == 'scrubber':
            widgets = [Player(length=nframes, width=550)]
        return widgets, dim_values


class Interactive(PaneBase):

    priority = None

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._update_layout()
        self.param.watch(self._update_layout_properties, list(Layoutable.param))

    @classmethod
    def applies(cls, object):
        if 'hvplot.interactive' not in sys.modules:
            return False
        from hvplot.interactive import Interactive
        return 0.8 if isinstance(object, Interactive) else False

    @param.depends('object')
    def _update_layout(self):
        if self.object is None:
            self._layout_panel = None
        else:
            self._layout_panel = self.object.layout()
            self._layout_panel.param.set_param(**{
                p: getattr(self, p) for p in Layoutable.param if p != 'name'
            })

    def _update_layout_properties(self, *events):
        if self._layout_panel is None:
            return
        self._layout_panel.param.set_param(**{e.name: e.new for e in events})

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if root is None:
            return self.get_root(doc, comm)
        if self._layout_panel is None:
            model = _BkSpacer(**{
                p: getattr(self, p) for p in Layoutable.param if p != 'name'
            })
        else:
            model = self._layout_panel._get_model(doc, root, parent, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _cleanup(self, root):
        if self._layout_panel is not None:
            self._layout_panel._cleanup(root)
        super()._cleanup(root)


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
    hv_views = root_view.select(HoloViews)
    root_plots = [plot for view in hv_views for plot, _ in view._plots.values()
                  if getattr(plot, 'root', None) is root_model]

    if not len(root_plots) > 1:
        return

    try:
        from holoviews.plotting.links import Link
        from holoviews.plotting.bokeh.callbacks import LinkCallback
    except Exception:
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


def link_axes(root_view, root_model):
    """
    Pre-processing hook to allow linking axes across HoloViews bokeh
    plots.
    """
    panes = root_view.select(HoloViews)

    if not panes:
        return

    from holoviews.core.options import Store
    from holoviews.core.util import unique_iterator, max_range
    from holoviews.plotting.bokeh.element import ElementPlot

    ref = root_model.ref['id']
    range_map = defaultdict(list)
    for pane in panes:
        if ref not in pane._plots:
            continue
        plot = pane._plots[ref][0]
        if (not pane.linked_axes or plot.renderer.backend != 'bokeh'
            or not getattr(plot, 'shared_axes', False)):
            continue
        for p in plot.traverse(specs=[ElementPlot]):
            if p.current_frame is None:
                continue

            axiswise = Store.lookup_options('bokeh', p.current_frame, 'norm').kwargs.get('axiswise')
            if not p.shared_axes or axiswise:
                continue

            fig = p.state
            if fig.x_range.tags:
                range_map[fig.x_range.tags[0]].append((fig, p, fig.xaxis[0], fig.x_range))
            if fig.y_range.tags:
                range_map[fig.y_range.tags[0]].append((fig, p, fig.yaxis[0], fig.y_range))

    for (tag), axes in range_map.items():
        fig, p, ax, axis = axes[0]
        if isinstance(axis, Range1d):
            start, end = max_range([
                (ax[-1].start, ax[-1].end) for ax in axes
                if isinstance(ax[-1], Range1d)
            ])
            if axis.start > axis.end:
                end, start = start, end
            axis.start = start
            axis.end = end
        for fig, p, pax, _ in axes[1:]:
            changed = []
            if  type(ax) is not type(pax):
                continue
            if tag in fig.x_range.tags and not axis is fig.x_range:
                if hasattr(axis, 'factors'):
                    axis.factors = list(unique_iterator(axis.factors+fig.x_range.factors))
                fig.x_range = axis
                p.handles['x_range'] = axis
                changed.append('x_range')
            if tag in fig.y_range.tags and not axis is fig.y_range:
                if hasattr(axis, 'factors'):
                    axis.factors = list(unique_iterator(axis.factors+fig.y_range.factors))
                fig.y_range = axis
                p.handles['y_range'] = axis
                changed.append('y_range')

            # Reinitialize callbacks linked to replaced axes
            subplots = getattr(p, 'subplots')
            if subplots:
                plots = subplots.values()
            else:
                plots = [p]

            for sp in plots:
                for callback in sp.callbacks:
                    if not any(c in callback.models or c in callback.extra_models for c in changed):
                        continue
                    if 'x_range' in changed:
                        sp.handles['x_range'] = p.handles['x_range']
                    if 'y_range' in changed:
                        sp.handles['y_range'] = p.handles['y_range']
                    callback.reset()
                    callback.initialize(plot_id=p.id) 


Viewable._preprocessing_hooks.append(link_axes)
Viewable._preprocessing_hooks.append(find_links)
