"""
Defines Links which allow declaring links between bokeh properties.
"""
import param
import weakref
import sys

from .reactive import Reactive
from .viewable import Viewable

from bokeh.models import (CustomJS, Model as BkModel)


class Callback(param.Parameterized):
    """
    A Callback defines some callback to be triggered when a property
    changes on the source object. A Callback can execute arbitrary
    Javascript code and will make all objects referenced in the args
    available in the JS namespace.
    """

    args = param.Dict(default={}, allow_None=True, doc="""
        A mapping of names to Python objects. These objects are made
        available to the callback's code snippet as the values of
        named parameters to the callback.""")

    code = param.Dict(default=None, doc="""
        A dictionary mapping from a source specication to a JS code
        snippet to be executed if the source property changes.""")

    # Mapping from a source id to a Link instance
    registry = weakref.WeakKeyDictionary()

    # Mapping to define callbacks by backend and Link type.
    # e.g. Callback._callbacks[Link] = Callback
    _callbacks = {}

    # Whether the link requires a target
    _requires_target = False

    def __init__(self, source, target=None, **params):
        if source is None:
            raise ValueError('%s must define a source' % type(self).__name__)
        # Source is stored as a weakref to allow it to be garbage collected
        self._source = None if source is None else weakref.ref(source)
        super().__init__(**params)
        self.init()

    def init(self):
        """
        Registers the Callback
        """
        if self.source in self.registry:
            links = self.registry[self.source]
            params = {
                k: v for k, v in self.param.get_param_values() if k != 'name'}
            for link in links:
                link_params = {
                    k: v for k, v in link.param.get_param_values() if k != 'name'}
                if not hasattr(link, 'target'):
                    pass
                elif (type(link) is type(self) and link.source is self.source
                    and link.target is self.target and params == link_params):
                    return
            self.registry[self.source].append(self)
        else:
            self.registry[self.source] = [self]

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

    @classmethod
    def _process_callbacks(cls, root_view, root_model):
        if not root_model:
            return

        linkable = root_view.select(Viewable)
        linkable += root_model.select({'type' : BkModel})

        if not linkable:
            return

        found = [(link, src, getattr(link, 'target', None)) for src in linkable
                 for link in cls.registry.get(src, [])
                 if not link._requires_target or link.target in linkable]

        arg_overrides = {}
        if 'holoviews' in sys.modules:
            from .pane.holoviews import HoloViews, generate_panel_bokeh_map

            hv_views = root_view.select(HoloViews)
            map_hve_bk = generate_panel_bokeh_map(root_model, hv_views)
            for src in linkable:
                for link in cls.registry.get(src, []):
                    if hasattr(link, 'target'):
                        for tgt in map_hve_bk.get(link.target, []):
                            found.append((link, src, tgt))
                    arg_overrides[id(link)] = {}
                    for k, v in link.args.items():
                        # Not all args are hashable
                        try:
                            hv_objs = map_hve_bk.get(v, [])
                        except Exception:
                            continue
                        for tgt in hv_objs:
                            arg_overrides[id(link)][k] = tgt

        ref = root_model.ref['id']
        callbacks = []
        for link, src, tgt in found:
            cb = cls._callbacks[type(link)]
            if ((src is None or ref not in getattr(src, '_models', [ref])) or
                (getattr(link, '_requires_target', False) and tgt is None) or
                (tgt is not None and ref not in getattr(tgt, '_models', [ref]))):
                continue
            overrides = arg_overrides.get(id(link), {})
            callbacks.append(cb(root_model, link, src, tgt,
                                arg_overrides=overrides))
        return callbacks


class Link(Callback):
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

    bidirectional = param.Boolean(default=False, doc="""
        Whether to link source and target in both directions.""")

    properties = param.Dict(default={}, doc="""
        A dictionary mapping between source specification to target
        specification.""")

    # Whether the link requires a target
    _requires_target = True

    def __init__(self, source, target=None, **params):
        if self._requires_target and target is None:
            raise ValueError('%s must define a target.' % type(self).__name__)
        # Source is stored as a weakref to allow it to be garbage collected
        self._target = None if target is None else weakref.ref(target)
        super().__init__(source, **params)

    @property
    def target(self):
        return self._target() if self._target else None

    def link(self):
        """
        Registers the Link
        """
        self.init()
        if self.source in self.registry:
            links = self.registry[self.source]
            params = {
                k: v for k, v in self.param.get_param_values() if k != 'name'}
            for link in links:
                link_params = {
                    k: v for k, v in link.param.get_param_values() if k != 'name'}
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



class CallbackGenerator(object):

    def __init__(self, root_model, link, source, target=None, arg_overrides={}):
        self.root_model = root_model
        self.link = link
        self.source = source
        self.target = target
        self.arg_overrides = arg_overrides
        self.validate()
        specs = self._get_specs(link, source, target)
        for src_spec, tgt_spec, code in specs:
            try:
                self._init_callback(root_model, link, source, src_spec, target, tgt_spec, code)
            except Exception:
                pass
                
    @classmethod
    def _resolve_model(cls, root_model, obj, model_spec):
        """
        Resolves a model given the supplied object and a model_spec.

        Arguments
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
        from .pane.holoviews import is_bokeh_element_plot

        model = None
        if 'holoviews' in sys.modules and is_bokeh_element_plot(obj):
            if model_spec is None:
                return obj.state
            else:
                model_specs = model_spec.split('.')
                handle_spec = model_specs[0]
                if len(model_specs) > 1:
                    model_spec = '.'.join(model_specs[1:])
                else:
                    model_spec = None
                model = obj.handles[handle_spec]
        elif isinstance(obj, Viewable):
            model, _ = obj._models[root_model.ref['id']]
        elif isinstance(obj, BkModel):
            model = obj
        if model_spec is not None:
            for spec in model_spec.split('.'):
                model = getattr(model, spec)
        return model

    def _init_callback(self, root_model, link, source, src_spec, target, tgt_spec, code):
        references = {k: v for k, v in link.param.get_param_values()
                      if k not in ('source', 'target', 'name', 'code', 'args')}

        src_model = self._resolve_model(root_model, source, src_spec[0])
        ref = root_model.ref['id']
        link_id = id(link)
        if any(link_id in cb.tags for cbs in src_model.js_property_callbacks.values() for cb in cbs):
            # Skip registering callback if already registered
            return
        references['source'] = src_model

        tgt_model = None
        if link._requires_target:
            tgt_model = self._resolve_model(root_model, target, tgt_spec[0])
            if tgt_model is not None:
                references['target'] = tgt_model

        for k, v in dict(link.args, **self.arg_overrides).items():
            arg_model = self._resolve_model(root_model, v, None)
            if arg_model is not None:
                references[k] = arg_model
            elif not isinstance(v, param.Parameterized):
                references[k] = v

        if 'holoviews' in sys.modules:
            from .pane.holoviews import HoloViews, is_bokeh_element_plot

            if isinstance(source, HoloViews):
                src = source._plots[ref][0]
            else:
                src = source

            prefix = 'source_' if hasattr(link, 'target') else ''
            if is_bokeh_element_plot(src):
                for k, v in src.handles.items():
                    k = prefix + k
                    if isinstance(v, BkModel) and k not in references:
                        references[k] = v

            if isinstance(target, HoloViews):
                tgt = target._plots[ref][0]
            else:
                tgt = target

            if is_bokeh_element_plot(tgt):
                for k, v in tgt.handles.items():
                    k = 'target_' + k
                    if isinstance(v, BkModel) and k not in references:
                        references[k] = v

        self._initialize_models(link, source, src_model, src_spec[1], target, tgt_model, tgt_spec[1])
        self._process_references(references)

        if code is None:
            code = self._get_code(link, source, src_spec[1], target, tgt_spec[1])
        else:
            code = "try {{ {code} }} catch(err) {{ console.log(err) }}".format(code=code)

        src_cb = CustomJS(args=references, code=code, tags=[link_id])
        changes, events = self._get_triggers(link, src_spec)
        for ch in changes:
            src_model.js_on_change(ch, src_cb)
        for ev in events:
            src_model.js_on_event(ev, src_cb)

        if getattr(link, 'bidirectional', False):
            code = self._get_code(link, target, tgt_spec[1], source, src_spec[1])
            reverse_references = dict(references)
            reverse_references['source'] = tgt_model
            reverse_references['target'] = src_model
            tgt_cb = CustomJS(args=reverse_references, code=code, tags=[link_id])
            changes, events = self._get_triggers(link, tgt_spec)
            for ch in changes:
                tgt_model.js_on_change(ch, tgt_cb)
            for ev in events:
                tgt_model.js_on_event(ev, tgt_cb)

    def _process_references(self, references):
        """
        Method to process references in place.
        """

    def _get_specs(self, link):
        """
        Return a list of spec tuples that define source and target
        models.
        """
        return []

    def _get_code(self, link, source, target):
        """
        Returns the code to be executed.
        """
        return ''

    def _get_triggers(self, link, src_spec):
        """
        Returns the changes and events that trigger the callback.
        """
        return [], []

    def _initialize_models(self, link, source, src_model, src_spec, target, tgt_model, tgt_spec):
        """
        Applies any necessary initialization to the source and target
        models.
        """
        pass

    def validate(self):
        pass



class JSCallbackGenerator(CallbackGenerator):

    def _get_triggers(self, link, src_spec):
        if src_spec[1].startswith('event:'):
            return [], [src_spec[1].split(':')[1]]
        return [src_spec[1]], []

    def _get_specs(self, link, source, target):
        for src_spec, code in link.code.items():
            src_specs = src_spec.split('.')
            if src_spec.startswith('event:'):
                src_spec = (None, src_spec)
            elif len(src_specs) > 1:
                src_spec = ('.'.join(src_specs[:-1]), src_specs[-1])
            else:
                src_prop = src_specs[0]
                if isinstance(source, Reactive):
                    src_prop = source._rename.get(src_prop, src_prop)
                src_spec = (None, src_prop)
        return [(src_spec, (None, None), code)]



class JSLinkCallbackGenerator(JSCallbackGenerator):

    _link_template = """
    var value = source['{src_attr}'];
    value = {src_transform};
    value = {tgt_transform};
    try {{
      var property = target.properties['{tgt_attr}'];
      if (property !== undefined) {{ property.validate(value); }}
    }} catch(err) {{
      console.log('WARNING: Could not set {tgt_attr} on target, raised error: ' + err);
      return;
    }}
    try {{
      target['{tgt_attr}'] = value;
    }} catch(err) {{
      console.log(err)
    }}
    """

    def _get_specs(self, link, source, target):
        if link.code:
            return super()._get_specs(link, source, target)

        specs = []
        for src_spec, tgt_spec in link.properties.items():
            src_specs = src_spec.split('.')
            if len(src_specs) > 1:
                src_spec = ('.'.join(src_specs[:-1]), src_specs[-1])
            else:
                src_prop = src_specs[0]
                if isinstance(source, Reactive):
                    src_prop = source._rename.get(src_prop, src_prop)
                src_spec = (None, src_prop)
            tgt_specs = tgt_spec.split('.')
            if len(tgt_specs) > 1:
                tgt_spec = ('.'.join(tgt_specs[:-1]), tgt_specs[-1])
            else:
                tgt_prop = tgt_specs[0]
                if isinstance(target, Reactive):
                    tgt_prop = target._rename.get(tgt_prop, tgt_prop)
                tgt_spec = (None, tgt_prop)
            specs.append((src_spec, tgt_spec, None))
        return specs

    def _initialize_models(self, link, source, src_model, src_spec, target, tgt_model, tgt_spec):
        if tgt_model and src_spec and tgt_spec:
            src_reverse = {v: k for k, v in getattr(source, '_rename', {}).items()}
            src_param = src_reverse.get(src_spec, src_spec)
            if (hasattr(source, '_process_property_change') and
                src_param in source.param and hasattr(target, '_process_param_change')):
                tgt_reverse = {v: k for k, v in target._rename.items()}
                tgt_param = tgt_reverse.get(tgt_spec, tgt_spec)
                value = getattr(source, src_param)
                try:
                    msg = target._process_param_change({tgt_param: value})
                except Exception:
                    msg = {}
                if tgt_spec in msg:
                    value = msg[tgt_spec]
            else:
                value = getattr(src_model, src_spec)
            if value:
                setattr(tgt_model, tgt_spec, value)
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

    def _get_code(self, link, source, src_spec, target, tgt_spec):
        if isinstance(source, Reactive):
            src_reverse = {v: k for k, v in source._rename.items()}
            src_param = src_reverse.get(src_spec, src_spec)
            src_transform = source._source_transforms.get(src_param)
            if src_transform is None:
                src_transform = 'value'
        else:
            src_transform = 'value'
        if isinstance(target, Reactive):
            tgt_reverse = {v: k for k, v in target._rename.items()}
            tgt_param = tgt_reverse.get(tgt_spec, tgt_spec)
            tgt_transform = target._target_transforms.get(tgt_param)
            if tgt_transform is None:
                tgt_transform = 'value'
        else:
            tgt_transform = 'value'
        return self._link_template.format(
            src_attr=src_spec, tgt_attr=tgt_spec,
            src_transform=src_transform, tgt_transform=tgt_transform
        )

Callback.register_callback(callback=JSCallbackGenerator)
Link.register_callback(callback=JSLinkCallbackGenerator)

Viewable._preprocessing_hooks.append(Callback._process_callbacks)
