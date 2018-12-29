"""
"""
import param
import weakref

from .layout import Viewable, Panel
from .widgets import Widget
from .holoviews import HoloViews, is_bokeh_element_plot

from holoviews.plotting.links import Link
from bokeh.models import CustomJS


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


class RangeAxesLink(Link):
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
        if target_plot is None:
            return
        if 'x' in link.axes:
            target_plot.handles['plot'].x_range = source_plot.handles['plot'].x_range
        if 'y' in link.axes:
            target_plot.handles['plot'].y_range = source_plot.handles['plot'].y_range


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


RangeAxesLink.register_callback(backend='bokeh',
                                callback = RangeAxesLinkCallback)
WidgetLink.register_callback(backend='bokeh',
                             callback = WidgetLinkCallback)

Viewable._preprocessing_hooks.append(find_widget_hv_links)
