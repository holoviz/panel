"""
"""
import param

from .layout import Viewable, Panel
from .widgets import Widget
from .holoviews import HoloViews

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
    
def find_links(root_view, root_model):
    if not isinstance(root_view, Panel):
        return
    
    from collections import defaultdict
    
    widget_views = root_view.select(Widget)
    hv_views = root_view.select(HoloViews)
    if not widget_views or not hv_views:
        return
    
    #mapping holoview element -> bokeh plot
    map_hve_bk = defaultdict(list)
    for hv_view in hv_views:
        if root_model.ref['id'] in hv_view._plots: 
            map_hve_bk[hv_view.object].append(hv_view._plots[root_model.ref['id']]) 
                    
    found = [(link, src_widget, tgt_bk) for src_widget in widget_views if src_widget in Link.registry
             for link in Link.registry[src_widget]
             for tgt_bk in map_hve_bk[link.target]]
    
    callbacks = []
    for link, src_widget, tgt_bk in found:
        cb = Link._callbacks['bokeh'][type(link)]
        if src_widget is None or (getattr(link, '_requires_target', False)
                                and tgt_bk is None):
            continue
        callbacks.append(cb(root_model, link, src_widget, tgt_bk))
    return callbacks


             
WidgetLink.register_callback(backend='bokeh',
                             callback = WidgetLinkCallback)

Viewable._preprocessing_hooks.append(find_links)
