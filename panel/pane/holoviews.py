"""
HoloViews integration for Panel including a Pane to render HoloViews
objects and their widgets and support for Links
"""
from __future__ import annotations

import sys

from collections import OrderedDict, defaultdict
from functools import partial
from typing import (
    TYPE_CHECKING, Any, ClassVar, Mapping, Optional, Tuple, Type,
)

import param

from bokeh.models import Range1d, Spacer as _BkSpacer
from bokeh.themes.theme import Theme
from packaging.version import Version

from ..io import state, unlocked
from ..layout import (
    Column, HSpacer, Row, WidgetBox,
)
from ..viewable import Layoutable, Viewable
from ..widgets import Player
from .base import PaneBase, RerenderError, panel
from .plot import Bokeh, Matplotlib
from .plotly import Plotly

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class HoloViews(PaneBase):
    """
    `HoloViews` panes render any `HoloViews` object using the
    currently selected backend ('bokeh' (default), 'matplotlib' or 'plotly').

    To be able to use the `plotly` backend you must add `plotly` to
    `pn.extension`.

    Reference: https://panel.holoviz.org/reference/panes/HoloViews.html

    :Example:

    >>> HoloViews(some_holoviews_object)
    """

    backend = param.ObjectSelector(
        default=None, objects=['bokeh', 'plotly', 'matplotlib'], doc="""
        The HoloViews backend used to render the plot (if None defaults
        to the currently selected renderer).""")

    center = param.Boolean(default=False, doc="""
        Whether to center the plot.""")

    linked_axes = param.Boolean(default=True, doc="""
        Whether to link the axes of bokeh plots inside this pane
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

    priority: ClassVar[float | bool | None] = 0.8

    _alignments = {
        'left': (Row, ('start', 'center'), True),
        'right': (Row, ('end', 'center'), False),
        'top': (Column, ('center', 'start'), True),
        'bottom': (Column, ('center', 'end'), False),
        'top_left': (Column, 'start', True),
        'top_right': (Column, ('end', 'start'), True),
        'bottom_left': (Column, ('start', 'end'), False),
        'bottom_right': (Column, 'end', False),
        'left_top': (Row, 'start', True),
        'left_bottom': (Row, ('start', 'end'), True),
        'right_top': (Row, ('end', 'start'), False),
        'right_bottom': (Row, 'end', False)
    }

    _panes: ClassVar[Mapping[str, Type[PaneBase]]] = {
        'bokeh': Bokeh, 'matplotlib': Matplotlib, 'plotly': Plotly
    }

    _rename: ClassVar[Mapping[str, str | None]] = {
        'backend': None, 'center': None, 'linked_axes': None,
        'renderer': None, 'theme': None, 'widgets': None,
        'widget_layout': None, 'widget_location': None,
        'widget_type': None
    }

    _rerender_params = ['object', 'backend']

    _skip_layoutable = (
        'background', 'css_classes', 'margin', 'name', 'sizing_mode',
        'width', 'height', 'max_width', 'max_height'
    )

    def __init__(self, object=None, **params):
        self._initialized = False
        self._height_responsive = None
        self._width_responsive = None
        self._restore_plot = None
        super().__init__(object, **params)
        self.widget_box = self.widget_layout()
        self._widget_container = []
        self._plots = {}
        self._syncing_props = False
        self._overrides = [
            p for p, v in params.items()
            if p in Layoutable.param and v != self.param[p].default
        ]
        watcher = self.param.watch(self._update_widgets, self._rerender_params)
        self._internal_callbacks.append(watcher)
        self._update_responsive()
        self._update_widgets()
        self._initialized = True

    def _param_change(self, *events: param.parameterized.Event) -> None:
        if self._object_changing:
            return
        self._track_overrides(*(e for e in events if e.name in Layoutable.param))
        super()._param_change(*(e for e in events if e.name in self._overrides+['css_classes']))

    @param.depends('backend', watch=True, on_init=True)
    def _load_backend(self):
        from holoviews import Store, extension
        if self.backend and self.backend not in Store.renderers:
            ext = extension._backends[self.backend]
            __import__(f'holoviews.plotting.{ext}')

    @property
    def _layout_sizing_mode(self):
        if self._width_responsive and self._height_responsive:
            smode = 'stretch_both'
        elif self._width_responsive:
            smode = 'stretch_width'
        elif self._height_responsive:
            smode = 'stretch_height'
        else:
            smode = None
        return smode

    @param.depends('center', 'widget_location', watch=True)
    def _update_layout(self):
        loc = self.widget_location
        center = self.center and not self._width_responsive
        layout, align, widget_first = self._alignments[loc]
        self.widget_box.align = align
        self._widget_container = self.widget_box
        smode = self._layout_sizing_mode
        layout_smode = 'stretch_width' if not smode and center else smode
        if not len(self.widget_box):
            if center:
                components = [HSpacer(), self, HSpacer()]
            else:
                components = [self]
            self.layout[:] = components
            self.layout.sizing_mode = layout_smode
            return

        items = (self.widget_box, self) if widget_first else (self, self.widget_box)
        kwargs = {'sizing_mode': smode}
        if not center:
            if self.default_layout is layout:
                components = list(items)
            else:
                components = [layout(*items, **kwargs)]
        elif layout is Column:
            components = [HSpacer(), layout(*items, **kwargs), HSpacer()]
        elif loc.startswith('left'):
            components = [self.widget_box, HSpacer(), self, HSpacer()]
        else:
            components = [HSpacer(), self, HSpacer(), self.widget_box]
        self.layout[:] = components
        self.layout.sizing_mode = layout_smode

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

    @param.depends('object', watch=True)
    def _update_responsive(self):
        from holoviews import HoloMap, Store
        from holoviews.plotting import Plot
        obj = self.object
        if isinstance(obj, Plot):
            if 'responsive' in obj.param:
                wresponsive = obj.responsive and not obj.width
                hresponsive = obj.responsive and not obj.height
            elif 'sizing_mode' in obj.param:
                mode = obj.sizing_mode
                if mode:
                    wresponsive = '_width' in mode or '_both' in mode
                    hresponsive = '_height' in mode or '_both' in mode
                else:
                    wresponsive = hresponsive = False
            else:
                wresponsive = hresponsive = False
            self._width_responsive = wresponsive
            self._height_responsive = hresponsive
            return

        obj = obj.last if isinstance(obj, HoloMap) else obj
        if obj is None or not Store.renderers:
            return
        backend = self.backend or Store.current_backend
        renderer = self.renderer or Store.renderers[backend]
        opts = obj.opts.get('plot', backend=backend).kwargs
        plot_cls = renderer.plotting_class(obj)
        if backend == 'matplotlib':
            self._width_responsive = self._height_responsive = False
        elif backend == 'plotly':
            responsive = opts.get('responsive', None)
            width = opts.get('width', None)
            height = opts.get('height', None)
            self._width_responsive = responsive and not width
            self._height_responsive = responsive and not height
        elif 'sizing_mode' in plot_cls.param:
            mode = opts.get('sizing_mode')
            if mode:
                self._width_responsive = '_width' in mode or '_both' in mode
                self._height_responsive = '_height' in mode or '_both' in mode
            else:
                self._width_responsive = False
                self._height_responsive = False
        else:
            responsive = opts.get('responsive', None)
            width = opts.get('width', None)
            frame_width = opts.get('frame_width', None)
            height = opts.get('height', None)
            frame_height = opts.get('frame_height', None)
            self._width_responsive = responsive and not width and not frame_width
            self._height_responsive = responsive and not height and not frame_height

    @param.depends('widget_type', 'widgets', watch=True)
    def _update_widgets(self, *events):
        if self.object is None:
            widgets, values = [], []
        else:
            widgets, values = self.widgets_from_dimensions(
                self.object, self.widgets, self.widget_type)
        self._values = values

        # Clean up anything models listening to the previous widgets
        for cb in list(self._internal_callbacks):
            if cb.inst in self.widget_box.objects:
                cb.inst.param.unwatch(cb)
                self._internal_callbacks.remove(cb)

        # Add new widget callbacks
        for widget in widgets:
            watcher = widget.param.watch(self._widget_callback, 'value')
            self._internal_callbacks.append(watcher)

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

    def _track_overrides(self, *events):
        if self._syncing_props:
            return
        overrides = list(self._overrides)
        for e in events:
            if e.name in overrides and self.param[e.name].default == e.new:
                overrides.remove(e.name)
            else:
                overrides.append(e.name)
        self._overrides = overrides

    def _sync_sizing_mode(self, plot):
        state = plot.state
        backend = plot.renderer.backend
        if backend == 'bokeh':
            params = {
                'sizing_mode': state.sizing_mode,
                'width': state.width,
                'height': state.height
            }
        elif backend == 'matplotlib':
            params = {
                'sizing_mode': None,
                'width': None,
                'height': None
            }
        elif backend == 'plotly':
            if state.get('config', {}).get('responsive'):
                sizing_mode = 'stretch_both'
            else:
                sizing_mode = None
            params = {
                'sizing_mode': sizing_mode,
                'width': None,
                'height': None
            }
        self._syncing_props = True
        try:
            self.param.update({k: v for k, v in params.items() if k not in self._overrides})
            if backend != 'bokeh':
                return
            plot_props = plot.state.properties()
            props = {
                o: getattr(self, o) for o in self._overrides
                if o in plot_props
            }
            if props:
                plot.state.update(**props)
        finally:
            self._syncing_props = False

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
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
        state = plot.renderer.get_plot_state(plot)

        # Ensure rerender if content is responsive but layout is centered
        # or update layout if plot is height responsive but layout wrapper
        # is not
        self._sync_sizing_mode(plot)
        responsive = self.sizing_mode not in ('fixed', None) and not self.width
        force_width = (self.center and responsive and not self._width_responsive)
        if force_width:
            self._update_responsive()
            self._width_responsive = True
            self._update_layout()
            self._restore_plot = plot
            raise RerenderError(layout=self.layout)
        elif self._height_responsive is None:
            self._update_responsive()
            loc = self.widget_location
            center = self.center and not self._width_responsive
            layout, _, _ = self._alignments[loc]
            smode = self._layout_sizing_mode
            layout_smode = 'stretch_width' if not smode and center else smode
            self.layout.sizing_mode = layout_smode
            if len(self.widget_box):
                if not center:
                    if self.default_layout is not layout:
                        self.layout[0].sizing_mode = smode
                elif layout is Column and len(self.layout) == 3:
                    self.layout[1].sizing_mode = smode

        kwargs = {p: v for p, v in self.param.values().items()
                  if p in Layoutable.param and p != 'name'}
        if self.sizing_mode and (self.sizing_mode.endswith('width') or self.sizing_mode.endswith('both')):
            del kwargs['width']
        if self.sizing_mode and (self.sizing_mode.endswith('height') or self.sizing_mode.endswith('both')):
            del kwargs['height']
        child_pane = self._get_pane(backend, state, **kwargs)
        self._update_plot(plot, child_pane)
        model = child_pane._get_model(doc, root, parent, comm)
        if ref in self._plots:
            old_plot, old_pane = self._plots[ref]
            old_plot.comm = None # Ensures comm does not get cleaned up
            old_plot.cleanup()
        self._plots[ref] = (plot, child_pane)
        self._models[ref] = (model, parent)
        return model

    def _get_pane(self, backend, state, **kwargs):
        pane_type = self._panes.get(backend, panel)
        if isinstance(pane_type, type):
            if issubclass(pane_type, Matplotlib):
                kwargs['tight'] = True
            if issubclass(pane_type, Bokeh):
                kwargs['autodispatch'] = False
        return pane_type(state, **kwargs)

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
            elif doc.theme and getattr(doc.theme, '_json') != {'attrs': {}}:
                params['theme'] = doc.theme
            elif self._design.theme.bokeh_theme:
                params['theme'] = self._design.theme.bokeh_theme
            if mode != renderer.mode:
                params['mode'] = mode
            if params:
                renderer = renderer.instance(**params)

        kwargs = {'margin': self.margin}
        if backend == 'bokeh' or Version(str(hv.__version__)) >= Version('1.13.0'):
            kwargs['doc'] = doc
            kwargs['root'] = root
            if comm:
                kwargs['comm'] = comm

        return renderer.get_plot(self.object, **kwargs)

    def _cleanup(self, root: Model | None = None) -> None:
        """
        Traverses HoloViews object to find and clean up any streams
        connected to existing plots.
        """
        if root:
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
    def applies(cls, obj: Any) -> float | bool | None:
        if 'holoviews' not in sys.modules:
            return False
        from holoviews.core.dimension import Dimensioned
        from holoviews.plotting.plot import Plot
        return isinstance(obj, (Dimensioned, Plot))

    def jslink(self, target, code=None, args=None, bidirectional=False, **links):
        if links and code:
            raise ValueError('Either supply a set of properties to '
                             'link as keywords or a set of JS code '
                             'callbacks, not both.')
        elif not links and not code:
            raise ValueError('Declare parameters to link or a set of '
                             'callbacks, neither was defined.')
        if args is None:
            args = {}

        from ..links import Link
        return Link(self, target, properties=links, code=code, args=args,
                    bidirectional=bidirectional)

    jslink.__doc__ = PaneBase.jslink.__doc__

    @classmethod
    def widgets_from_dimensions(cls, object, widget_types=None, widgets_type='individual'):
        from holoviews.core import Dimension, DynamicMap
        from holoviews.core.options import SkipRendering
        from holoviews.core.traversal import unique_dimkeys
        from holoviews.core.util import (
            datetime_types, isnumeric, unique_iterator,
        )
        from holoviews.plotting.plot import GenericCompositePlot, Plot
        from holoviews.plotting.util import get_dynamic_mode

        from ..widgets import (
            DatetimeInput, DiscreteSlider, FloatSlider, IntSlider, Select,
            Widget,
        )

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
        values = {} if dynamic else dict(zip(dims, zip(*keys)))
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
                    widget.param.update(**kwargs)
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
                    labels = [str(dim.pprint_value(v)) for v in vals]
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

    priority: ClassVar[float | bool | None] = None

    _ignored_refs: ClassVar[Tuple[str]] = ['object']

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._update_layout()
        self.param.watch(self._update_layout_properties, list(Layoutable.param))

    @classmethod
    def applies(cls, object: Any) -> float | bool | None:
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
            self._layout_panel.param.update(**{
                p: getattr(self, p) for p in Layoutable.param if p != 'name'
            })

    def _update_layout_properties(self, *events):
        if self._layout_panel is None:
            return
        self._layout_panel.param.update(**{e.name: e.new for e in events})

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
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

    def _cleanup(self, root: Model | None = None) -> None:
        if self._layout_panel is not None:
            self._layout_panel._cleanup(root)
        super()._cleanup(root)


def is_bokeh_element_plot(plot):
    """
    Checks whether plotting instance is a HoloViews ElementPlot rendered
    with the bokeh backend.
    """
    from holoviews.plotting.plot import (
        GenericElementPlot, GenericOverlayPlot, Plot,
    )
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
        try:
            from holoviews.plotting.bokeh.links import LinkCallback
        except Exception:
            from holoviews.plotting.bokeh.callbacks import LinkCallback
        from holoviews.plotting.links import Link
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
    from holoviews.core.util import max_range, unique_iterator
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
                tag = tuple(tuple(t) if isinstance(t, list) else t for t in fig.x_range.tags[0])
                range_map[tag].append((fig, p, fig.xaxis[0], fig.x_range))
            if fig.y_range.tags:
                tag = tuple(tuple(t) if isinstance(t, list) else t for t in fig.y_range.tags[0])
                range_map[tag].append((fig, p, fig.yaxis[0], fig.y_range))

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
            if tag in fig.x_range.tags and axis is not fig.x_range:
                if hasattr(axis, 'factors'):
                    axis.factors = list(unique_iterator(axis.factors+fig.x_range.factors))
                fig.x_range = axis
                p.handles['x_range'] = axis
                changed.append('x_range')
            if tag in fig.y_range.tags and axis is not fig.y_range:
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
                    models = callback.models
                    if hasattr(callback, 'extra_models'):
                        # No more extra_models in HoloViews 2.0
                        models += callback.extra_models
                    if not any(c in models for c in changed):
                        continue
                    if 'x_range' in changed:
                        sp.handles['x_range'] = p.handles['x_range']
                    if 'y_range' in changed:
                        sp.handles['y_range'] = p.handles['y_range']
                    callback.reset()
                    callback.initialize(plot_id=p.id)


Viewable._preprocessing_hooks.append(link_axes)
Viewable._preprocessing_hooks.append(find_links)
