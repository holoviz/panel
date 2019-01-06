"""
"""
import param
import weakref

from .layout import Viewable, Panel
from .widgets import Widget
from .holoviews import HoloViews, is_bokeh_element_plot

from collections import defaultdict
from bokeh.models import CustomJS

class Link(param.Parameterized):
    """
    A Link defines some connection between a source and target object
    in their visualization. It is quite similar to a Stream as it
    allows defining callbacks in response to some change or event on
    the source object, however, unlike a Stream, it does not transfer
    data and make it available to user defined subscribers. Instead
    a Link directly causes some action to occur on the target, for JS
    based backends this usually means that a corresponding JS callback
    will effect some change on the target in response to a change on
    the source.

    A Link must define a source object which is what triggers events,
    but must not define a target. It is also possible to define bi-
    directional links between the source and target object.
    """

    # Mapping from a source id to a Link instance
    registry = weakref.WeakKeyDictionary()

    # Mapping to define callbacks by backend and Link type.
    # e.g. Link._callbacks['bokeh'][Stream] = Callback
    _callbacks = defaultdict(dict)

    # Whether the link requires a target
    _requires_target = False

    def __init__(self, source, target=None, **params):
        if source is None:
            raise ValueError('%s must define a source' % type(self).__name__)
        if self._requires_target and target is None:
            raise ValueError('%s must define a target.' % type(self).__name__)

        # Source is stored as a weakref to allow it to be garbage collected
        self._source = None if source is None else weakref.ref(source)
        self._target = None if target is None else weakref.ref(target)
        super(Link, self).__init__(**params)
        self.link()

    @classmethod
    def register_callback(cls, backend, callback):
        """
        Register a LinkCallback providing the implementation for
        the Link for a particular backend.
        """
        cls._callbacks[backend][cls] = callback

    @property
    def source(self):
        return self._source() if self._source else None

    @property
    def target(self):
        return self._target() if self._target else None

    def link(self):
        """
        Registers the Link
        """
        if self.source in self.registry:
            links = self.registry[self.source]
            params = {
                k: v for k, v in self.get_param_values() if k != 'name'}
            for link in links:
                link_params = {
                    k: v for k, v in link.get_param_values() if k != 'name'}
                if (type(link) is type(self) and link.source is self.source
                    and link.target is self.target and params == link_params):
                    return
            self.registry[self.source].append(self)
        else:
            self.registry[self.source] = [self]

    def unlink(self):
        """
        Unregisters the Link
        """
        links = self.registry.get(self.source)
        if self in links:
            links.pop(links.index(self))


class WidgetLink(Link):
    """
    Links a panel Widget value to the value on a target
    object. Currently only links between Widgets and
    HoloViews plots are supported.
    
    The `target_model` and `target_property` define the
    bokeh model and property the widget value will be
    linked to.
    """
    registry = weakref.WeakKeyDictionary()
    
    code = param.String(default=None)
    
    target_model = param.String(default=None)
    
    target_property = param.String(default=None)

class WidgetLinkCallback(param.Parameterized):

    source_handles = []
    target_handles = []

    on_source_changes = ['value']

    source_code = """
       target['{value}'] = source.value
    """

    def __init__(self, root_model, link, source_plot, target_plot=None):
        self.root_model = root_model
        self.link = link
        self.source_plot = source_plot
        self.target_plot = target_plot
        self.validate()

        references = {k: v for k, v in link.get_param_values()
                      if k not in ('source', 'target', 'name')}

        src_model = source_plot._models[root_model.ref['id']]
        references['source'] = src_model

        if target_plot is not None:
            if link.target_model:
                if link.target_model in target_plot.handles:
                    tgt_model = target_plot.handles[link.target_model]
                else:
                    tgt_model = getattr(target_plot.state, self.target_model)
                references['target'] = tgt_model
                if link.target_property:
                    setattr(tgt_model, link.target_property, src_model.value)
            else:
                for k, v in target_plot.handles.items():
                    #print(k, v)
                    if k not in ('source', 'target', 'name', 'color_dim'):
                        references[k] = v
                    
        if link.code:
            code = link.code
        else:
            code = self.source_code.format(value=link.target_property)
        src_cb = CustomJS(args=references, code=code)
        for ch in self.on_source_changes:
            src_model.js_on_change(ch, src_cb)
                
    def validate(self):
        pass


def generate_hvelems_bkplots_map(root_model, hv_views):
    #mapping holoview element -> bokeh plot
    map_hve_bk = defaultdict(list)
    for hv_view in hv_views:
        if root_model.ref['id'] in hv_view._plots: 
            bk_plots = hv_view._plots[root_model.ref['id']].traverse(lambda x: x, [is_bokeh_element_plot])
            for plot in bk_plots:
                for hv_elem in plot.link_sources:
                    map_hve_bk[hv_elem].append(plot) 
    return map_hve_bk

def find_widget_hv_links(root_view, root_model):
    if not isinstance(root_view, Panel) or not root_model:
        return
    
    widget_views = root_view.select(Widget)
    hv_views = root_view.select(HoloViews)
    if not widget_views or not hv_views:
        return
    
    map_hve_bk = generate_hvelems_bkplots_map(root_model, hv_views)
                    
    found = [(link, src_widget, tgt_bk) for src_widget in widget_views if src_widget in WidgetLink.registry
             for link in WidgetLink.registry[src_widget]
             for tgt_bk in map_hve_bk[link.target]]
    
    callbacks = []
    for link, src_widget, tgt_bk in found:
        cb = WidgetLink._callbacks['bokeh'][type(link)]
        if src_widget is None or (getattr(link, '_requires_target', False)
                                and tgt_bk is None):
            continue
        callbacks.append(cb(root_model, link, src_widget, tgt_bk))
    return callbacks

WidgetLink.register_callback(backend='bokeh',
                             callback = WidgetLinkCallback)

Viewable._preprocessing_hooks.append(find_widget_hv_links)
