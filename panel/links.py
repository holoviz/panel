"""
"""
import param
import weakref
import sys

from .layout import Viewable, Panel
from .widgets import Widget
from .holoviews import HoloViews, generate_panel_bokeh_map, is_bokeh_element_plot
from .pane import Bokeh

from collections import defaultdict
from bokeh.models import (CustomJS, Widget as BkWidget, Model as BkModel)


class PanelLink(param.Parameterized):
    """
    A Link defines some connection between a source and target object 
    in their visualization. It allows defining callbacks in response 
    to some change or event on the source object. Instead a Link directly 
    causes some action to occur on the target, for JS based backends 
    this usually means that a corresponding JS callback will effect some 
    change on the target in response to a change on the source.

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
        super(PanelLink, self).__init__(**params)
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


class WidgetLink(PanelLink):
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
    
    @classmethod
    def make_links(cls, root_view, root_model):
        if not isinstance(root_view, Panel) or not root_model:
            return
        
        linkable_sources = []
        linkable_sources += root_view.select(Widget)
        linkable_sources += [bokeh_model for bk_pane in root_view.select(Bokeh) 
                             for bokeh_model in bk_pane._models[root_model.ref['id']].select({'type' : BkWidget})]
        
        if not linkable_sources:
            return
        
        linkable_targets = []
        linkable_targets += [bokeh_model for bk_pane in root_view.select(Bokeh) 
                             for bokeh_model in bk_pane._models[root_model.ref['id']].select({'type' : BkModel})]
        
        found = [(link, src, link.target) for src in linkable_sources if src in cls.registry 
                     for link in cls.registry[src] if link.target in linkable_targets]
        
        if 'holoviews' in sys.modules:
            hv_views = root_view.select(HoloViews)
            map_hve_bk = generate_panel_bokeh_map(root_model, hv_views)
            found += [(link, src, tgt) for src in linkable_sources if src in cls.registry
                      for link in cls.registry[src]
                      for tgt in map_hve_bk[link.target]]
        
        callbacks = []
        for link, src, tgt in found:
            cb = WidgetLink._callbacks['bokeh'][type(link)]
            if src is None or (getattr(link, '_requires_target', False)
                                    and tgt is None):
                continue
            callbacks.append(cb(root_model, link, src, tgt))
        return callbacks

    
class WidgetLinkCallback(param.Parameterized):

    source_handles = []
    target_handles = []

    on_source_changes = ['value']

    source_code = """
       target['{value}'] = source.value
    """

    def __init__(self, root_model, link, source, target=None):
        self.root_model = root_model
        self.link = link
        self.source = source
        self.target = target
        self.validate()
        
        references = {k: v for k, v in link.get_param_values()
                      if k not in ('source', 'target', 'name')}

        if isinstance(source, BkWidget):
            src_model = source
        elif isinstance(source, Widget):
            src_model = source._models[root_model.ref['id']]
        else:
            raise TypeError('Source of class {} not handle'.format(source.__class__))
            
        references['source'] = src_model
        
        if self.target and isinstance(self.target, BkModel):
            if link.target_model:
                if hasattr(self.target, link.target_model):
                    tgt_model = getattr(self.target, link.target_model)
                else:
                    raise AttributeError('target as not {} attributes'.format(link.target_model))
            else:
                tgt_model = self.target
            references['target'] = tgt_model
            if link.target_property:
                setattr(tgt_model, link.target_property, src_model.value)
            
        elif self.target and 'holoviews' in sys.modules and is_bokeh_element_plot(self.target): 
            if link.target_model:
                if link.target_model in self.target.handles:
                    tgt_model = self.target.handles[link.target_model]
                else:
                    tgt_model = getattr(self.target.state, self.target_model)
                references['target'] = tgt_model
                if link.target_property:
                    setattr(tgt_model, link.target_property, src_model.value)
            else:
                for k, v in self.target.handles.items():
                    # print(k, v)
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
    

WidgetLink.register_callback(backend='bokeh',
                             callback=WidgetLinkCallback)

Viewable._preprocessing_hooks.append(WidgetLink.make_links)
