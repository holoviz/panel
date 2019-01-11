"""
"""
import param
import weakref
import sys

from .layout import Viewable, Panel
from .holoviews import HoloViews, generate_panel_bokeh_map, is_bokeh_element_plot

from bokeh.models import (CustomJS, Model as BkModel)


class Link(param.Parameterized):
    """
    A Link defines some connection between a source and target model.
    It allows defining callbacks in response to some change or event
    on the source object. Instead a Link directly causes some action
    to occur on the target, for JS based backends this usually means
    that a corresponding JS callback will effect some change on the
    target in response to a change on the source.

    A Link must define a source object which is what triggers events,
    but must not define a target. It is also possible to define bi-
    directional links between the source and target object.
    """

    # Mapping from a source id to a Link instance
    registry = weakref.WeakKeyDictionary()

    # Mapping to define callbacks by backend and Link type.
    # e.g. Link._callbacks[Link] = Callback
    _callbacks = {}

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
    def register_callback(cls, callback):
        """
        Register a LinkCallback providing the implementation for
        the Link for a particular backend.
        """
        cls._callbacks[cls] = callback

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
    
    @classmethod
    def _process_links(cls, root_view, root_model):
        if not isinstance(root_view, Panel) or not root_model:
            return

        linkable = root_view.select(Viewable)
        linkable += root_model.select({'type' : BkModel})

        if not linkable:
            return

        found = [(link, src, link.target) for src in linkable
                 for link in cls.registry.get(src, [])
                 if link.target in linkable or not link._requires_target]

        if 'holoviews' in sys.modules:
            hv_views = root_view.select(HoloViews)
            map_hve_bk = generate_panel_bokeh_map(root_model, hv_views)
            found += [(link, src, tgt) for src in linkable if src in cls.registry
                      for link in cls.registry[src]
                      for tgt in map_hve_bk[link.target]]

        callbacks = []
        for link, src, tgt in found:
            cb = cls._callbacks[type(link)]
            if src is None or (getattr(link, '_requires_target', False)
                                    and tgt is None):
                continue
            callbacks.append(cb(root_model, link, src, tgt))
        return callbacks


class WidgetLink(Link):
    """
    Links a panel Widget's value property to a property on the target
    model.

    The `target_model` and `target_property` define the bokeh model
    and property the widget value will be linked to.
    """

    code = param.String(default=None, doc="""
        Custom code to define a between the source and target model.""")

    target_model = param.String(default=None, doc="""
        The model spec defining the object to Link to.""")

    target_property = param.String(default=None, doc="""
        The property on the target_model to link to.""")

    # Whether the link requires a target
    _requires_target = True


class LinkCallback(param.Parameterized):

    @classmethod
    def _resolve_model(cls, root_model, obj, model_spec):
        """
        Resolves a model given the supplied object and a model_spec.

        Parameters
        ----------
        root_model: bokeh.model.Model
            The root bokeh model often used to index models
        obj: holoviews.plotting.ElementPlot or bokeh.model.Model or panel.Viewable
            The object to look the model up on
        model_spec: string
            A string defining how to look up the model, can be a single
            string defining the handle in a HoloViews plot or a path
            split by periods (.) to indicate a multi-level lookup.

        Returns
        -------
        model: bokeh.model.Model
            The resolved bokeh model
        """
        model = None
        if ('holoviews' in sys.modules and is_bokeh_element_plot(obj) and
            model_spec is not None):
            return obj.handles[model_spec]
        elif isinstance(obj, Viewable):
            model = obj._models[root_model.ref['id']]
        elif isinstance(obj, BkModel):
            model = obj
        if model_spec is not None:
            for spec in model_spec.split('.'):
                model = getattr(model, spec)
        return model

    def __init__(self, root_model, link, source, target=None):
        self.root_model = root_model
        self.link = link
        self.source = source
        self.target = target
        self.validate()

        references = {k: v for k, v in link.get_param_values()
                      if k not in ('source', 'target', 'name', 'code')}

        src_model = self._resolve_model(
            root_model, source, self._get_source_spec(link))
        references['source'] = src_model

        tgt_model = self._resolve_model(
            root_model, target, self._get_target_spec(link))
        if tgt_model is not None:
            references['target'] = tgt_model

        if 'holoviews' in sys.modules:
            if is_bokeh_element_plot(source):
                for k, v in source.handles.items():
                    if isinstance(v, BkModel):
                        references['source_' + k] = v
            if is_bokeh_element_plot(target):
                for k, v in target.handles.items():
                    if isinstance(v, BkModel):
                        references['target_' + k] = v

        self._initialize_models(link, src_model, tgt_model)
        self._process_references(references)

        code = self._get_code(link)

        src_cb = CustomJS(args=references, code=code)
        changes, events = self._get_triggers(link)
        for ch in changes:
            src_model.js_on_change(ch, src_cb)
        for ev in events:
            src_model.js_on_event(ev, src_cb)

    def _get_source_spec(self, link):
        """
        Returns the source model specification.
        """
        return None

    def _get_target_spec(self, link):
        """
        Returns the target model specification.
        """
        return None

    def _get_code(self, link):
        """
        Returns the code to be executed.
        """
        return ''

    def _get_triggers(self, link):
        """
        Returns the changes and events that trigger the callback.
        """
        return [], []

    def _initialize_models(self, link, src_model, tgt_model):
        """
        Applies any necessary initialization to the source and target
        models.
        """
        pass

    def validate(self):
        pass


class WidgetLinkCallback(LinkCallback):

    source_code = """
    target['{value}'] = source.value
    """

    def _get_target_spec(self, link):
        return link.target_model

    def _initialize_models(self, link, src_model, tgt_model):
        if link.target_property and tgt_model:
            setattr(tgt_model, link.target_property, src_model.value)
        if tgt_model is None and not link.code:
            raise ValueError('Model could not be resolved on target '
                             '%s and no custom code was specified.' % 
                             type(self.target).__name__)

    def _process_references(self, references):
        """
        Strips target_ prefix from references.
        """
        for k in list(references):
            if k == 'target' or not k.startswith('target_') or k[7:] in references:
                continue
            references[k[7:]] = references.pop(k)

    def _get_code(self, link):
        if link.code:
            code = link.code
        else:
            code = self.source_code.format(value=link.target_property)
        return code

    def _get_triggers(self, link):
        return ['value'], []


WidgetLink.register_callback(callback=WidgetLinkCallback)

Viewable._preprocessing_hooks.append(Link._process_links)
