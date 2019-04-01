"""
Defines Links which allow declaring links between bokeh properties.
"""
from __future__ import absolute_import, division, unicode_literals

import param
import weakref
import sys

from .viewable import Viewable, Reactive
from .layout import Panel
from .pane.holoviews import HoloViews, generate_panel_bokeh_map, is_bokeh_element_plot
from .util import unicode_repr
from .widgets import CompositeWidget

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
        if not isinstance(root_view, (Panel, CompositeWidget)) or not root_model:
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


class GenericLink(Link):
    """
    Links two panel object using generic source and target
    specifications, which either map from a source model property
    to a target model property or from a source model property to
    a JS code snippet to be executed.
    """

    code = param.Dict(default=None, doc="""
        A dictionary mapping from a source specication to a JS code
        snippet to be executed if the source property changes.""")

    properties = param.Dict(default={}, doc="""
        A dictionary mapping between source specification to target
        specification.""")

    # Whether the link requires a target
    _requires_target = True


class LinkCallback(param.Parameterized):

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

    def __init__(self, root_model, link, source, target=None):
        self.root_model = root_model
        self.link = link
        self.source = source
        self.target = target
        self.validate()
        specs = self._get_specs(link, source, target)
        for src_spec, tgt_spec, code in specs:
            self._init_callback(root_model, link, source, src_spec, target, tgt_spec, code)

    def _init_callback(self, root_model, link, source, src_spec, target, tgt_spec, code):
        references = {k: v for k, v in link.get_param_values()
                      if k not in ('source', 'target', 'name', 'code')}

        src_model = self._resolve_model(root_model, source, src_spec[0])
        link_id = id(link)
        if any(link_id in cb.tags for cbs in src_model.js_property_callbacks.values() for cb in cbs):
            # Skip registering callback if already registered
            return
        references['source'] = src_model

        tgt_model = self._resolve_model(root_model, target, tgt_spec[0])
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

        self._initialize_models(link, source, src_model, src_spec[1], target, tgt_model, tgt_spec[1])
        self._process_references(references)

        if code is None:
            code = self._get_code(link, source, src_spec[1], target, tgt_spec[1])

        src_cb = CustomJS(args=references, code=code, tags=[link_id])
        changes, events = self._get_triggers(link, src_spec)
        for ch in changes:
            src_model.js_on_change(ch, src_cb)
        for ev in events:
            src_model.js_on_event(ev, src_cb)

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

    def _initialize_models(self, link, src_model, tgt_model):
        """
        Applies any necessary initialization to the source and target
        models.
        """
        pass

    def validate(self):
        pass


class GenericLinkCallback(LinkCallback):

    def _get_specs(self, link, source, target):
        if link.code:
            for src_spec, code in link.code.items():
                src_specs = src_spec.split('.')
                if len(src_specs) > 1:
                    src_spec = ('.'.join(src_specs[:-1]), src_specs[-1])
                else:
                    src_prop = src_specs[0]
                    if isinstance(source, Reactive):
                        src_prop = source._rename.get(src_prop, src_prop)
                    src_spec = (None, src_prop)
            return [(src_spec, (None, None), code)]

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
            setattr(tgt_model, tgt_spec, getattr(src_model, src_spec))
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
        return ("value = source[{src_repr}];"
                "try {{ property = target.properties[{tgt_repr}];"
                "if (property !== undefined) {{ property.validate(value); }} }}"
                "catch(err) {{ console.log('WARNING: Could not set {tgt} on target, raised error: ' + err); return; }}"
                "target[{tgt_repr}] = value".format(
                    tgt=tgt_spec, tgt_repr=unicode_repr(tgt_spec),
                    src=src_spec, src_repr=unicode_repr(src_spec)))

    def _get_triggers(self, link, src_spec):
        return [src_spec[1]], []


GenericLink.register_callback(callback=GenericLinkCallback)

Viewable._preprocessing_hooks.append(Link._process_links)
