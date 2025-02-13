"""
Defines Links which allow declaring links between bokeh properties.
"""
from __future__ import annotations

import difflib
import sys
import weakref

from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, Any, TypeAlias

import param

from bokeh.models import CustomJS, LayoutDOM, Model as BkModel

from .io.datamodel import create_linked_datamodel
from .io.loading import LOADING_INDICATOR_CSS_CLASS
from .models import ReactiveESM, ReactiveHTML
from .reactive import Reactive
from .util.warnings import warn
from .viewable import Viewable

if TYPE_CHECKING:
    from bokeh.model import Model

    try:
        from holoviews.core.dimension import Dimensioned
        JSLinkTarget: TypeAlias = Reactive | BkModel | Dimensioned
    except Exception:
        JSLinkTarget: TypeAlias = Reactive | BkModel # type: ignore
    SourceModelSpec = tuple[str | None, str]
    TargetModelSpec = tuple[str | None, str | None]


def assert_source_syncable(source: Reactive, properties: Iterable[str]) -> None:
    for prop in properties:
        if prop.startswith('event:'):
            continue
        elif hasattr(source, 'object') and isinstance(source.object, LayoutDOM):
            current = source.object
            for attr in prop.split('.'):
                if hasattr(current, attr):
                    current = getattr(current, attr)
                    continue
                raise ValueError(
                    f"Could not resolve {prop} on {source.object} model. "
                    "Ensure you jslink an attribute that exists on the "
                    "bokeh model."
                )
        elif (prop not in source.param and prop not in list(source._rename.values())):
            matches = difflib.get_close_matches(prop, list(source.param))
            if matches:
                matches_repr = f' Similar parameters include: {matches!r}'
            else:
                matches_repr = ''
            raise ValueError(
                f"Could not jslink {prop!r} parameter (or property) "
                f"on {type(source).__name__} object because it was not "
                f"found. Similar parameters include: {matches_repr}."
            )
        elif (source._source_transforms.get(prop, False) is None or
              source._rename.get(prop, False) is None):
            raise ValueError(
                f"Cannot jslink {prop!r} parameter on {type(source).__name__} "
                "object, the parameter requires a live Python kernel "
                "to have an effect."
            )

def assert_target_syncable(
    source: Reactive, target: JSLinkTarget, properties: dict[str, str]
) -> None:
    for k, p in properties.items():
        if k.startswith('event:'):
            continue
        elif p not in target.param and p not in list(target._rename.values()):
            matches = difflib.get_close_matches(p, list(target.param))
            if matches:
                matches_repr = f' Similar parameters include: {matches!r}'
            else:
                matches_repr = ''
            raise ValueError(
                f"Could not jslink {p!r} parameter (or property) "
                f"on {type(source).__name__} object because it was not "
                f"found. Similar parameters include: {matches_repr}"
            )
        elif (target._source_transforms.get(p, False) is None or
              target._rename.get(p, False) is None):
            raise ValueError(
                f"Cannot jslink {k!r} parameter on {type(source).__name__} "
                f"object to {p!r} parameter on {type(target).__name__}. "
                "It requires a live Python kernel to have an effect."
            )

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
        A dictionary mapping from a source specification to a JS code
        snippet to be executed if the source property changes.""")

    # Mapping from a source id to a Link instance
    registry: weakref.WeakKeyDictionary[Reactive | BkModel, list[Callback]] = weakref.WeakKeyDictionary()

    # Mapping to define callbacks by backend and Link type.
    # e.g. Callback._callbacks[Link] = Callback
    _callbacks: dict[type[Callback], type[CallbackGenerator]] = {}

    # Whether the link requires a target
    _requires_target: bool = False

    def __init__(
        self, source: Reactive, target: JSLinkTarget | None = None,
        args: dict[str, Any] | None = None, code: dict[str, str] | None = None,
        **params
    ):
        """
        A Callback defines some callback to be triggered when a
        property changes on the source object. A Callback can execute
        arbitrary Javascript code and will make all objects referenced
        in the args available in the JS namespace.

        Parameters
        ----------
        source (Reactive):
           The source object the callback is attached to.
        target (Reactive | Model, optional):
           An optional target to trigger some action on when the source
           property changes.
        args (Dict[str, Any], optional):
           Additional args to make available in the Javascript namespace
           indexed by name.
        code (Dict[str, str], optional):
           A dictionary mapping from the changed source property to
           a JS code snippet to execute.
        """
        if source is None:
            raise ValueError(f'{type(self).__name__} must define a source')
        # Source is stored as a weakref to allow it to be garbage collected
        self._source = None if source is None else weakref.ref(source)
        if not args:
            args={}
        super().__init__(args=args, code=code, **params)
        self.init()

    def init(self) -> None:
        """
        Registers the Callback
        """
        if Callback._process_callbacks not in Viewable._preprocessing_hooks:
            Viewable._preprocessing_hooks.append(Callback._process_callbacks)

        source = self.source
        if source is None:
            return
        if source in self.registry:
            links = self.registry[source]
            params = {
                k: v for k, v in self.param.values().items() if k != 'name'
            }
            for link in links:
                link_params = {
                    k: v for k, v in link.param.values().items() if k != 'name'
                }
                if not hasattr(link, 'target'):
                    pass
                elif (type(link) is type(self) and link.source is source
                    and link.target is self.target and params == link_params):
                    return
            self.registry[source].append(self)
        else:
            self.registry[source] = [self]

    @classmethod
    def register_callback(cls, callback: type[CallbackGenerator]) -> None:
        """
        Register a LinkCallback providing the implementation for
        the Link for a particular backend.
        """
        cls._callbacks[cls] = callback

    @property
    def source(self) -> Reactive | None:
        return self._source() if self._source else None

    @classmethod
    def _process_callbacks(
        cls, root_view: Viewable, root_model: BkModel, changed: Viewable | None = None, old_models=None
    ):
        if not root_model:
            return

        ref = root_model.ref['id']
        if changed is not None:
            inspect = root_view.select(Viewable)
            if ref in changed._models:
                inspect += changed._models[ref][0].select({'type' : BkModel})
            targets = [link.target for links in cls.registry.values() for link in links if isinstance(link, Link)]
            if not any(m in cls.registry or m in targets for m in inspect):
                return

        if root_view is changed:
            linkable = inspect
        else:
            linkable = (
                root_view.select(Viewable) + list(root_model.select({'type' : BkModel})) # type: ignore
            )

        if not linkable:
            return

        found = [
            (link, src, getattr(link, 'target', None)) for src in linkable
            for link in cls.registry.get(src, [])
            if not link._requires_target or link.target in linkable
            or isinstance(link.target, param.Parameterized)
        ]

        arg_overrides: dict[int, dict[str, Any]] = {}
        if 'holoviews' in sys.modules:
            from holoviews.core.dimension import Dimensioned

            from .pane.holoviews import HoloViews, generate_panel_bokeh_map
            found = [
                (link, src, tgt) for (link, src, tgt) in found
                if not (isinstance(src, Dimensioned) or isinstance(tgt, Dimensioned))
            ]
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

        for (link, src, tgt) in found:
            cb = cls._callbacks[type(link)]
            if ((src is None or ref not in getattr(src, '_models', [ref])) or
                (getattr(link, '_requires_target', False) and tgt is None) or
                (tgt is not None and ref not in getattr(tgt, '_models', [ref]))):
                continue
            overrides = arg_overrides.get(id(link), {})
            cb(root_model, link, src, tgt, arg_overrides=overrides)


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

    def __init__(self, source: Reactive, target: JSLinkTarget | None = None, **params):
        if self._requires_target and target is None:
            raise ValueError(f'{type(self).__name__} must define a target.')
        # Source is stored as a weakref to allow it to be garbage collected
        self._target = None if target is None else weakref.ref(target)
        super().__init__(source, **params)

    @property
    def target(self) -> JSLinkTarget | None:
        return self._target() if self._target else None

    def link(self) -> None:
        """
        Registers the Link
        """
        self.init()
        source = self.source
        if source is None:
            return

        if source in self.registry:
            links = self.registry[source]
            params = {
                k: v for k, v in self.param.values().items() if k != 'name'
            }
            for link in links:
                link_params = {
                    k: v for k, v in link.param.values().items() if k != 'name'
                }
                if (type(link) is type(self) and link.source is source
                    and link.target is self.target and params == link_params):
                    return
            self.registry[source].append(self)
        else:
            self.registry[source] = [self]

    def unlink(self) -> None:
        """
        Unregisters the Link
        """
        source = self.source
        if source is None:
            return
        links = self.registry.get(source, [])
        if self in links:
            links.remove(self)



class CallbackGenerator:

    error = True

    def __init__(
        self, root_model: Model, link: Link, source: Reactive,
        target: JSLinkTarget | None = None, arg_overrides: dict[str, Any] = {}
    ):
        self.root_model = root_model
        self.link = link
        self.source = source
        self.target = target
        self.arg_overrides = arg_overrides
        self.validate()
        specs = self._get_specs(link, source, target)
        for src_spec, tgt_spec, code in specs:
            if src_spec[1] and target is not None and src_spec[1].startswith('event:') and not tgt_spec[1]:
                continue
            try:
                self._init_callback(root_model, link, source, src_spec, target, tgt_spec, code)
            except Exception:
                if self.error:
                    raise
                else:
                    pass

    @classmethod
    def _resolve_model(
        cls, root_model: Model, obj: JSLinkTarget, model_spec: str | None
    ) -> Model | None:
        """
        Resolves a model given the supplied object and a model_spec.

        Parameters
        -----------
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
            model, _ = obj._models.get(root_model.ref['id'], (None, None))
        elif isinstance(obj, BkModel):
            model = obj
        elif isinstance(obj, param.Parameterized):
            model = create_linked_datamodel(obj, root_model)
        if model_spec is not None:
            for spec in model_spec.split('.'):
                model = getattr(model, spec)

        return model

    def _init_callback(
        self, root_model: Model, link: Link, source: Reactive,
        src_spec: SourceModelSpec, target: JSLinkTarget | None,
        tgt_spec: TargetModelSpec, code: str | None
    ) -> None:
        references = {k: v for k, v in link.param.values().items()
                      if k not in ('source', 'target', 'name', 'code', 'args')}

        src_model = self._resolve_model(root_model, source, src_spec[0])
        if src_model is None:
            return
        ref = root_model.ref['id']

        link_id = (id(link), src_spec, tgt_spec)
        callbacks = (
            list(src_model.js_property_callbacks.values()) + # type: ignore
            list(src_model.js_event_callbacks.values()) # type: ignore
        )
        # Skip registering callback if already registered
        if any(link_id in cb.tags for cbs in callbacks for cb in cbs):
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

            if isinstance(target, HoloViews) and ref in target._plots:
                tgt = target._plots[ref][0]
            else:
                tgt = target

            if is_bokeh_element_plot(tgt):
                for k, v in tgt.handles.items():
                    k = 'target_' + k
                    if isinstance(v, BkModel) and k not in references:
                        references[k] = v

        # Handle links with ReactiveHTML DataModel
        if isinstance(src_model, (ReactiveESM, ReactiveHTML)):
            if src_spec[1] in src_model.data.properties(): # type: ignore
                references['source'] = src_model = src_model.data # type: ignore

        if isinstance(tgt_model, (ReactiveESM, ReactiveHTML)):
            if tgt_spec[1] in tgt_model.data.properties(): # type: ignore
                references['target'] = tgt_model = tgt_model.data # type: ignore

        self._initialize_models(link, source, src_model, src_spec[1], target, tgt_model, tgt_spec[1])
        self._process_references(references)

        if code is None:
            code = self._get_code(link, source, src_spec[1], target, tgt_spec[1])
        else:
            code = f"try {{ {code} }} catch(err) {{ console.log(err) }}"

        src_cb = CustomJS(args=references, code=code, tags=[link_id])
        changes, events = self._get_triggers(link, src_spec)
        for ch in changes:
            src_model.js_on_change(ch, src_cb)
        for ev in events:
            src_model.js_on_event(ev, src_cb)

        tgt_prop = tgt_spec[1]
        if not getattr(link, 'bidirectional', False) or tgt_model is None or tgt_prop is None:
            return

        code = self._get_code(link, target, tgt_prop, source, src_spec[1])
        reverse_references = dict(references)
        reverse_references['source'] = tgt_model
        reverse_references['target'] = src_model
        tgt_cb = CustomJS(args=reverse_references, code=code, tags=[link_id])
        changes, events = self._get_triggers(link, (None, tgt_prop))
        properties = tgt_model.properties()
        for ch in changes:
            if ch not in properties:
                msg = f"Could not link non-existent property '{ch}' on {tgt_model} model"
                if self.error:
                    raise ValueError(msg)
                else:
                    warn(msg)
            tgt_model.js_on_change(ch, tgt_cb)
        for ev in events:
            tgt_model.js_on_event(ev, tgt_cb)

    def _process_references(self, references):
        """
        Method to process references in place.
        """

    def _get_specs(
        self, link: Link, source: Reactive, target: JSLinkTarget
    ) -> Sequence[tuple[SourceModelSpec, TargetModelSpec, str | None]]:
        """
        Return a list of spec tuples that define source and target
        models.
        """
        return []

    def _get_code(
        self, link: Link, source: JSLinkTarget, src_spec: str,
        target: JSLinkTarget | None, tgt_spec: str | None
    ) -> str:
        """
        Returns the code to be executed.
        """
        return ''

    def _get_triggers(
        self, link: Link, src_spec: SourceModelSpec
    ) -> tuple[list[str], list[str]]:
        """
        Returns the changes and events that trigger the callback.
        """
        return [], []

    def _initialize_models(
        self, link, source: Reactive, src_model: Model, src_spec: str,
        target: JSLinkTarget | None, tgt_model: Model | None, tgt_spec: str | None
    ) -> None:
        """
        Applies any necessary initialization to the source and target
        models.
        """

    def validate(self) -> None:
        pass



class JSCallbackGenerator(CallbackGenerator):

    def _get_triggers(
        self, link: Link, src_spec: SourceModelSpec
    ) -> tuple[list[str], list[str]]:
        if src_spec[1].startswith('event:'):
            return [], [src_spec[1].split(':')[1]]
        return [src_spec[1]], []

    def _get_specs(
        self, link: Link, source: Reactive, target: JSLinkTarget
    ) -> Sequence[tuple[SourceModelSpec, TargetModelSpec, str | None]]:
        for spec in link.code:
            src_specs = spec.split('.')
            src_spec: tuple[str | None, str]
            if spec.startswith('event:'):
                src_spec = (None, spec)
            elif len(src_specs) > 1:
                src_spec = ('.'.join(src_specs[:-1]), src_specs[-1])
            else:
                src_prop = src_specs[0]
                if isinstance(source, Reactive):
                    src_prop = source._rename.get(src_prop, src_prop)
                src_spec = (None, src_prop)
        return [(src_spec, (None, None), link.code[spec])]



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

    _event_link_template = """
    var value = true
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

    _loading_link_template = """
    if ('{src_attr}'.startsWith('event:')) {{
      var value = true
    }} else {{
      var value = source['{src_attr}'];
      value = {src_transform};
    }}
    if (typeof value !== 'boolean' || source.labels !== ['Loading']) {{
      value = true
    }}
    var css_classes = target.css_classes.slice()
    var loading_css = ['{loading_css_class}', 'pn-{loading_spinner}']
    if (value) {{
      for (var css of loading_css) {{
        if (!(css in css_classes)) {{
          css_classes.push(css)
        }}
      }}
    }} else {{
     for (var css of loading_css) {{
        var index = css_classes.indexOf(css)
        if (index > -1) {{
          css_classes.splice(index, 1)
        }}
      }}
    }}
    target['css_classes'] = css_classes
    """

    def _get_specs(
        self, link: Link, source: Reactive, target: JSLinkTarget
    ) -> Sequence[tuple[SourceModelSpec, TargetModelSpec, str | None]]:
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

    def _initialize_models(
        self, link, source: Reactive, src_model: Model, src_spec: str,
        target: JSLinkTarget | None, tgt_model: Model | None, tgt_spec: str | None
    ) -> None:
        if tgt_model is not None and src_spec and tgt_spec:
            src_reverse = {v: k for k, v in getattr(source, '_rename', {}).items()}
            src_param = src_reverse.get(src_spec, src_spec)
            if src_spec.startswith('event:'):
                return
            if isinstance(source, Reactive) and src_param in source.param and isinstance(target, Reactive):
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
            if value and tgt_spec != 'value_throttled' and hasattr(tgt_model, tgt_spec):
                setattr(tgt_model, tgt_spec, value)
        if tgt_model is None and not link.code:
            raise ValueError('Model could not be resolved on target '
                             f'{type(self.target).__name__} and no custom code was specified.')

    def _process_references(self, references: dict[str, str]) -> None:
        """
        Strips target_ prefix from references.
        """
        for k in list(references):
            if k == 'target' or not k.startswith('target_') or k[7:] in references:
                continue
            references[k[7:]] = references.pop(k)

    def _get_code(
        self, link: Link, source: JSLinkTarget, src_spec: str,
        target: JSLinkTarget | None, tgt_spec: str | None
    ) -> str:
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
            if tgt_param is None or tgt_param not in target._target_transforms:
                tgt_transform = 'value'
            else:
                tgt_transform = target._target_transforms[tgt_param] or 'value'
        else:
            tgt_transform = 'value'
        if tgt_spec == 'loading':
            from .config import config
            return self._loading_link_template.format(
                src_attr=src_spec, src_transform=src_transform,
                loading_spinner=config.loading_spinner,
                loading_css_class=LOADING_INDICATOR_CSS_CLASS
            )
        else:
            if src_spec and src_spec.startswith('event:'):
                template = self._event_link_template
            else:
                template = self._link_template
            return template.format(
                src_attr=src_spec,
                tgt_attr=tgt_spec,
                src_transform=src_transform,
                tgt_transform=tgt_transform
            )

Callback.register_callback(callback=JSCallbackGenerator)
Link.register_callback(callback=JSLinkCallbackGenerator)

__all__ = (
    "Callback",
    "CallbackGenerator",
    "JSCallbackGenerator",
    "JSLinkCallbackGenerator",
    "Link"
)
