"""
Pane to render anywidget instances natively in Panel.

Instead of relying on the ipywidgets comm infrastructure, this module
extracts an anywidget's ESM source and traitlet definitions, creates
a dynamic ``AnyWidgetComponent`` subclass, and renders it through
Panel's ReactiveESM pipeline.  The result is full Panel reactivity
(``param.watch``, ``pn.bind``, ``.rx``) for any anywidget.
"""
from __future__ import annotations

import logging
import pathlib

from collections import OrderedDict
from typing import TYPE_CHECKING, Any, ClassVar

import param

from ..custom import AnyWidgetComponent
from .base import Pane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------
# Module-level cache: anywidget class -> dynamic component class
# Bounded to prevent unbounded memory growth.  When the cache
# exceeds _CACHE_MAX_SIZE the least-recently-used entry is evicted.
# ---------------------------------------------------------------
_CACHE_MAX_SIZE = 256
_COMPONENT_CACHE: OrderedDict[type, type[AnyWidgetComponent]] = OrderedDict()

# Framework / internal traits that should never be synced
_FRAMEWORK_TRAITS = frozenset({
    '_esm', '_css', '_anywidget_id', '_model_data',
    '_model_name', '_view_name',
    '_model_module', '_view_module',
    '_model_module_version', '_view_module_version',
    '_view_count', '_dom_classes',
    'comm', 'keys', 'layout', 'log', 'tabbable', 'tooltip',
})

# BokehJS reserved attribute names that cannot be used as DataModel properties.
# These exist on the HasProps/Model/Signalable prototype chain in BokehJS and
# cause "attempted to redefine attribute 'ClassName.name'" errors if a dynamic
# DataModel tries to define a property with the same name.  Traitlets with
# these names are renamed to w_<name> (same as Panel layout param collisions).
_BOKEH_RESERVED = frozenset({
    # Signalable mixin
    'connect', 'disconnect',
    # HasProps class
    'assert_initialized', 'attach_document', 'attributes', 'changed_for',
    'clone', 'connect_signals', 'constructor', 'define', 'destroy',
    'detach_document', 'dirty_attributes', 'disconnect_signals',
    'finalize', 'get', 'initialize', 'initialize_props', 'internal',
    'is_syncable', 'mixins', 'on_change', 'override', 'override_options',
    'patch_to', 'property', 'ref', 'references', 'set', 'setv',
    'stream_to', 'super', 'toString', 'type',
    # Model class
    'get_one', 'on_event', 'select', 'select_one', 'trigger_event',
    # Bokeh model properties
    'js_event_callbacks', 'js_property_callbacks', 'name',
    'subscribed_events', 'syncable', 'tags',
    # Python-level Model methods
    'document', 'id', 'trigger', 'update',
})


# ---------------------------------------------------------------
# Traitlet -> param helpers
# ---------------------------------------------------------------

def _is_json_safe(value):
    """Check if a value can be safely serialized by Bokeh (JSON-compatible)."""
    return value is None or isinstance(value, (bool, int, float, str, bytes, list, tuple, dict))


def _serialize_instance(obj):
    """
    Attempt to serialize a non-serializable Instance value to a dict.

    Supports dataclasses, msgspec Structs, pydantic models, attrs classes,
    and objects with ``__dict__``.  Returns the original object unchanged
    if none of the strategies apply.
    """
    if obj is None or isinstance(obj, (dict, int, float, str, bool, list)):
        return obj
    import dataclasses
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    try:
        import msgspec
        if isinstance(obj, msgspec.Struct):
            return msgspec.to_builtins(obj)
    except ImportError:
        pass
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    if hasattr(obj, 'dict') and callable(obj.dict):
        return obj.dict()
    if hasattr(obj, '__attrs_attrs__'):
        try:
            import attr
            return attr.asdict(obj)
        except ImportError:
            pass
    if hasattr(obj, '__dict__'):
        return dict(obj.__dict__)
    return obj


_MAX_SERIALIZE_DEPTH = 10


def _is_dataframe(obj):
    """Check if *obj* is a pandas or polars DataFrame (without importing)."""
    cls = type(obj)
    name = cls.__qualname__
    if name != 'DataFrame':
        return False
    mod = cls.__module__ or ''
    return mod == 'pandas' or mod.startswith(('pandas.', 'polars.'))


def _dataframe_to_records(obj):
    """Convert a pandas/polars DataFrame to list-of-dicts (records) format."""
    if hasattr(obj, 'to_dicts'):  # polars
        return obj.to_dicts()
    if hasattr(obj, 'to_dict'):   # pandas
        return obj.to_dict(orient='records')
    return repr(obj)


def _deep_serialize(obj, _seen=None, _depth=0):
    """
    Recursively serialize non-JSON-safe values in *obj*.

    Walks dicts and lists to ensure all leaf values are JSON-serializable.
    Non-JSON-safe leaf objects are converted via ``_serialize_instance``.
    A *_seen* set prevents infinite recursion from circular references,
    and *_depth* prevents unbounded expansion of complex object trees
    (e.g. logging.Logger, which contains handlers, managers, locks, etc.).

    Pandas DataFrames are converted to records (list-of-dicts) format
    to match what most anywidget ESM modules expect.

    Binary values (memoryview, bytes, bytearray) are base64-encoded with
    a ``_pnl_bytes`` marker so the TS adapter can decode them back to
    DataView objects.  numpy ndarrays are converted to plain lists.
    """
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    # bytes at the top level (_depth == 0) are passed through for Bokeh's
    # native bp.Bytes serializer to handle (e.g. standalone param.Bytes
    # properties).  However, bytes *nested* inside dicts/lists (_depth > 0)
    # must be base64-encoded because Bokeh's serializer wraps them in its
    # own Buffer structure, which BokehJS deserializes as an empty object
    # when nested inside a Dict property — breaking widgets like pyobsplot
    # that expect raw binary data (Arrow IPC).
    #
    # memoryview values (produced by ipywidgets to_json serializers like
    # jupyter-scatter's array_to_binary) are always base64-encoded
    # regardless of depth.
    if isinstance(obj, memoryview):
        import base64
        return {'_pnl_bytes': base64.b64encode(bytes(obj)).decode('ascii')}
    if isinstance(obj, bytes):
        if _depth > 0:
            import base64
            return {'_pnl_bytes': base64.b64encode(obj).decode('ascii')}
        return obj
    # numpy arrays: convert to lists for JSON serialization.
    # If the trait has a to_json serializer (handled by _serialize_trait),
    # the array will already have been converted to {view: memoryview, ...}
    # before reaching here.  This branch handles the fallback case.
    try:
        import numpy as np
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except ImportError:
        pass
    # Pandas DataFrames: convert to records (list-of-dicts) for ESM consumption
    if _is_dataframe(obj):
        return _dataframe_to_records(obj)
    if _depth >= _MAX_SERIALIZE_DEPTH:
        return None  # prevent unbounded expansion
    if _seen is None:
        _seen = set()
    obj_id = id(obj)
    if obj_id in _seen:
        return None  # break circular reference
    _seen.add(obj_id)
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            # JSON dict keys must be strings; stringify non-string keys
            # (e.g. Logger objects used as keys in logging.Manager.loggerDict)
            if not isinstance(k, str):
                k = repr(k)
            result[k] = _deep_serialize(v, _seen, _depth + 1)
        return result
    if isinstance(obj, (list, tuple)):
        result = [_deep_serialize(v, _seen, _depth + 1) for v in obj]
        return type(obj)(result) if isinstance(obj, tuple) else result
    # Non-JSON-safe leaf: try to serialize, then recurse on result
    serialized = _serialize_instance(obj)
    if serialized is obj:
        # _serialize_instance couldn't convert it; stringify as fallback
        return repr(obj)
    return _deep_serialize(serialized, _seen, _depth + 1)


def _serialize_trait(widget, trait_name, value):
    """
    Serialize a traitlet value for JSON transport.

    If the traitlet has a ``to_json`` metadata entry (ipywidgets custom
    serialization protocol), use it to produce the canonical serialized
    form before passing through ``_deep_serialize``.  This is essential
    for traits that use binary serialization (e.g. jupyter-scatter's
    ``points`` trait which uses ``array_to_binary`` to produce
    ``{view: memoryview, dtype: str, shape: tuple}``).

    The resulting memoryview values are base64-encoded by ``_deep_serialize``
    with a ``_pnl_bytes`` marker, which the TypeScript adapter decodes back
    to DataView objects on the browser side.
    """
    trait_obj = widget.traits().get(trait_name)
    if trait_obj:
        to_json_fn = trait_obj.metadata.get('to_json')
        if to_json_fn and callable(to_json_fn):
            try:
                value = to_json_fn(value, widget)
            except Exception:
                pass
    return _deep_serialize(value)


def _deserialize_instance(klass, value):
    """
    Attempt to reconstruct an Instance of *klass* from a dict *value*.

    Tries ``from_dict`` (classmethod), ``msgspec.convert``, and direct
    ``klass(**value)`` construction.  Returns the raw value if conversion
    fails.
    """
    if value is None or not isinstance(value, dict):
        return value
    if hasattr(klass, 'from_dict') and callable(klass.from_dict):
        try:
            return klass.from_dict(value)
        except Exception:
            pass
    try:
        import msgspec
        if issubclass(klass, msgspec.Struct):
            return msgspec.convert(value, type=klass)
    except (ImportError, TypeError):
        pass
    if hasattr(klass, 'model_validate'):
        try:
            return klass.model_validate(value)
        except Exception:
            pass
    try:
        return klass(**value)
    except Exception:
        return value


def _traitlet_to_param(trait):
    """Convert a single traitlet to a ``param.Parameter``."""
    import traitlets

    TRAITLET_MAP = {
        traitlets.Bool:    param.Boolean,
        traitlets.CBool:   param.Boolean,
        traitlets.Int:     param.Integer,
        traitlets.CInt:    param.Integer,
        traitlets.Integer: param.Integer,
        traitlets.Long:    param.Integer,
        traitlets.CLong:   param.Integer,
        traitlets.Float:   param.Number,
        traitlets.CFloat:  param.Number,
        traitlets.Unicode: param.String,
        traitlets.CUnicode: param.String,
        traitlets.Bytes:   param.Bytes,
        traitlets.CBytes:  param.Bytes,
        traitlets.List:    param.List,
        traitlets.Set:     param.List,  # approximate Set as List
        traitlets.Tuple:   param.Tuple,
        traitlets.Dict:    param.Dict,
    }

    # --- Special-case: Enum -> param.Selector with objects --------
    if isinstance(trait, traitlets.Enum):
        try:
            default = trait.default()
        except Exception:
            default = None
        # traitlets.Undefined is returned for Enum traits without explicit
        # defaults (e.g. xarray-fancy-repr's _obj_type).  It is not a valid
        # Selector value, so fall back to None and allow_None.
        if default is traitlets.Undefined:
            default = None
        objects = list(trait.values)
        allow_none = getattr(trait, 'allow_none', False) or default is None
        p = param.Selector(default=default, objects=objects)
        if allow_none:
            p.allow_None = True
        return p

    # Walk MRO for custom traitlet subclasses (before Instance check
    # because Container subclasses like Set, List, Tuple inherit from
    # Instance and would otherwise be caught by the Instance case).
    for cls in type(trait).__mro__:
        if cls in TRAITLET_MAP:
            param_type = TRAITLET_MAP[cls]
            try:
                default = trait.default()
            except Exception:
                default = param_type().default
            # Convert set defaults to list for param.List compatibility
            if param_type is param.List and isinstance(default, set):
                default = list(default)
            p = param_type(default=default)
            if getattr(trait, 'allow_none', False):
                p.allow_None = True
            return p

    # --- Special-case: Instance -> param.Dict ---------------------
    # Bokeh cannot serialize arbitrary Python objects, so Instance
    # traits are mapped to param.Dict.  The sync layer converts
    # between the Instance type and dict as needed.
    if isinstance(trait, traitlets.Instance):
        try:
            default = _serialize_instance(trait.default())
        except Exception:
            default = None
        p = param.Dict(default=default if isinstance(default, (dict, type(None))) else None)
        if getattr(trait, 'allow_none', False):
            p.allow_None = True
        return p

    # Fallback for unknown types (including Union)
    try:
        default = trait.default()
    except Exception:
        default = None
    # Ensure the default is JSON-safe so it can be used as a Bokeh
    # property default in the DataModel class definition (which is
    # serialized as part of document `defs`).  Non-safe objects like
    # logging.Logger would crash Bokeh's serializer.
    if not _is_json_safe(default):
        default = None
    p = param.Parameter(default=default)
    if getattr(trait, 'allow_none', False):
        p.allow_None = True
    return p


def _get_synced_traits(widget_or_class):
    """
    Return ``{name: trait}`` for sync-tagged, user-facing traits.

    Works with both an anywidget *class* (``class_traits``) and
    an anywidget *instance* (``traits``).

    Note: underscore-prefixed traits that are explicitly tagged
    ``sync=True`` are included (e.g. Altair's ``_vl_selections``,
    ``_params``).  Only traits in ``_FRAMEWORK_TRAITS`` are excluded.
    """
    if isinstance(widget_or_class, type):
        sync_traits = widget_or_class.class_traits(sync=True)
    else:
        sync_traits = widget_or_class.traits(sync=True)
    return {
        name: trait for name, trait in sync_traits.items()
        if name not in _FRAMEWORK_TRAITS
    }


def _resolve_text(value):
    """
    Resolve an ESM or CSS value to a plain string.

    Handles: ``None``, plain strings, ``pathlib.PurePath``,
    ``anywidget.experimental.FileContents``, and
    ``anywidget._file_contents.VirtualFileContents``.
    All non-``None`` values are coerced via ``str()``.
    ``pathlib.PurePath`` instances are read from disk.
    """
    if value is None:
        return None
    if isinstance(value, pathlib.PurePath):
        return pathlib.Path(value).read_text(encoding='utf-8')
    return str(value)


def _find_original_class(widget):
    """
    Find the original user-defined class for an anywidget instance.

    ``anywidget.AnyWidget.__init__`` calls ``add_traits()`` which creates
    a dynamic subclass (with the same ``__name__``).  After that,
    ``type(widget)`` is the dynamic subclass whose ``_esm`` is a traitlet
    descriptor, not a string.  We walk the MRO to find the original
    user-defined class whose ``_esm`` is still a plain string or path.
    """
    for cls in type(widget).__mro__:
        if '_esm' not in cls.__dict__:
            continue
        val = cls.__dict__['_esm']
        # The original class has _esm as a string, Path, or similar —
        # NOT a traitlet descriptor.
        if isinstance(val, (str, pathlib.PurePath)):
            return cls
    # Fallback: use the immediate parent of the dynamic subclass
    bases = type(widget).__bases__
    if bases:
        return bases[0]
    return type(widget)


def _get_or_create_component_class(widget):
    """
    Get or create a dynamic ``AnyWidgetComponent`` subclass for
    the given anywidget *instance*.

    The returned class has:

    * ``_esm`` set from the anywidget's ``_esm``
    * ``_stylesheets`` set from the anywidget's ``_css`` (if present)
    * ``param.Parameter`` instances mapped from sync-tagged traitlets

    ESM and CSS are read from the **instance** (not the class) because
    ``anywidget.AnyWidget.__init__`` converts ``_esm`` / ``_css`` into
    traitlet descriptors via ``add_traits()``, making class-level
    ``getattr`` return a descriptor object rather than a string.
    """
    # Cache by the original user-defined class, not the dynamic
    # subclass created by add_traits().
    original_cls = _find_original_class(widget)
    if original_cls in _COMPONENT_CACHE:
        _COMPONENT_CACHE.move_to_end(original_cls)
        return _COMPONENT_CACHE[original_cls]

    # --- Extract ESM (from instance for correct traitlet resolution) ---
    esm = _resolve_text(getattr(widget, '_esm', None))

    # --- Extract CSS (from instance) -----------------------------------
    css = _resolve_text(getattr(widget, '_css', None))

    # --- Map traitlets to param Parameters, handle collisions ----------
    import traitlets

    sync_traits = _get_synced_traits(widget)
    collision_names = set(AnyWidgetComponent.param) | _BOKEH_RESERVED

    params: dict[str, param.Parameter] = {}
    trait_name_map: dict[str, str] = {}  # traitlet name -> param name
    instance_traits: dict[str, type] = {}  # param name -> Instance klass
    renamed_traits: list[str] = []
    for name, trait in sync_traits.items():
        if name in collision_names:
            param_name = f'w_{name}'
            renamed_traits.append(f'{name!r} -> {param_name!r}')
        else:
            param_name = name
        params[param_name] = _traitlet_to_param(trait)
        trait_name_map[name] = param_name
        if isinstance(trait, traitlets.Instance):
            instance_traits[param_name] = getattr(trait, 'klass', None) or object
    if renamed_traits:
        logger.info(
            "AnyWidget %s: renamed traits to avoid collisions: %s. "
            "Access via pane.component.w_<name> or check "
            "pane.component._trait_name_map for full mapping.",
            original_cls.__name__, ', '.join(renamed_traits),
        )

    # --- Build class dict ----------------------------------------------
    class_dict: dict[str, Any] = {
        '_esm': esm or '',
        '_trait_name_map': trait_name_map,
        '_instance_traits': instance_traits,
        '_constants': {'_trait_name_map': trait_name_map},
        **params,
    }
    if css:
        class_dict['_stylesheets'] = [css]

    # Create dynamic subclass (triggers ReactiveESMMetaclass.__init__
    # which builds the _data_model automatically)
    component_cls = type(
        original_cls.__name__,
        (AnyWidgetComponent,),
        class_dict,
    )

    # Evict oldest entry if cache is full
    if len(_COMPONENT_CACHE) >= _CACHE_MAX_SIZE:
        _COMPONENT_CACHE.popitem(last=False)
    _COMPONENT_CACHE[original_cls] = component_cls
    return component_cls


# ---------------------------------------------------------------
# Pane
# ---------------------------------------------------------------

class AnyWidget(Pane):
    """
    The ``AnyWidget`` pane renders `anywidget <https://anywidget.dev>`_
    instances natively in Panel.

    Instead of using the ipywidgets comm infrastructure, this pane
    extracts the anywidget's ESM code and traitlet definitions, creates
    a dynamic ``AnyWidgetComponent`` subclass, and renders it using
    Panel's native ReactiveESM pipeline.  This provides full Panel
    reactivity including ``param.watch``, ``pn.bind``, and ``.rx``
    support.

    Reference: https://panel.holoviz.org/reference/panes/AnyWidget.html

    :Example:

    >>> import anywidget, traitlets
    >>> class CounterWidget(anywidget.AnyWidget):
    ...     _esm = '''
    ...     function render({ model, el }) {
    ...         let btn = document.createElement("button");
    ...         btn.innerHTML = `count is ${model.get("value")}`;
    ...         btn.addEventListener("click", () => {
    ...             model.set("value", model.get("value") + 1);
    ...             model.save_changes();
    ...         });
    ...         model.on("change:value", () => {
    ...             btn.innerHTML = `count is ${model.get("value")}`;
    ...         });
    ...         el.appendChild(btn);
    ...     }
    ...     export default { render };
    ...     '''
    ...     value = traitlets.Int(0).tag(sync=True)
    >>> pn.pane.AnyWidget(CounterWidget())
    """

    object = param.Parameter(default=None, allow_refs=False, doc="""
        The anywidget instance being wrapped, which will be converted
        to a native Panel component.""")

    priority: ClassVar[float | bool | None] = 0.8

    _rename: ClassVar[dict[str, str | None]] = {
        'default_layout': None, 'loading': None, 'object': None,
    }

    _rerender_params: ClassVar[list[str]] = ['object']

    _updates: ClassVar[bool] = False

    def __init__(self, object=None, **params):
        self._trait_changing: set[str] = set()
        self._trait_watchers: list = []
        self._component: AnyWidgetComponent | None = None
        super().__init__(object=object, **params)
        # Eagerly create the component so that ``pane.component`` is
        # available immediately for ``param.bind``, ``param.depends``,
        # ``.param.watch``, and ``.rx`` patterns — no need to wait
        # until the first render.
        if self.object is not None and self._component is None:
            self._component = self._create_component()

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        """Detect anywidget instances via duck typing.

        Checks for ``traits`` (callable), ``class_traits`` (specific to
        ``traitlets.HasTraits``), and ``_esm`` on the class.
        """
        if not callable(getattr(obj, 'traits', None)):
            return False
        if not hasattr(obj, 'class_traits'):
            return False
        return hasattr(type(obj), '_esm')

    # ------------------------------------------------------------------
    # Component access
    # ------------------------------------------------------------------

    @property
    def component(self) -> AnyWidgetComponent | None:
        """The internal ``AnyWidgetComponent`` for param reactivity."""
        return self._component

    @property
    def trait_name_map(self) -> dict[str, str]:
        """Mapping from original traitlet names to component param names.

        When a traitlet name collides with a Panel layout parameter or
        a BokehJS reserved attribute name, it is renamed with a ``w_``
        prefix.  This property exposes the mapping so users can discover
        how traits were renamed.

        Returns
        -------
        dict[str, str]
            ``{traitlet_name: param_name}`` — e.g. ``{"width": "w_width"}``.
            Only includes traits that were renamed.
        """
        if self._component is None:
            return {}
        full_map = getattr(type(self._component), '_trait_name_map', {})
        return {k: v for k, v in full_map.items() if k != v}

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None,
    ) -> Model:
        if root is None:
            return self.get_root(doc, comm)

        if self.object is None:
            from bokeh.models import Spacer as BkSpacer
            model: Model = BkSpacer()
            self._models[root.ref['id']] = (model, parent)
            return model

        if self._component is None:
            self._component = self._create_component()

        component = self._component
        assert component is not None
        model = component._get_model(doc, root, parent, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    # Layout params forwarded from the AnyWidget pane to the inner component
    _LAYOUT_PARAMS: ClassVar[tuple[str, ...]] = (
        'align', 'aspect_ratio', 'css_classes', 'design', 'height',
        'min_width', 'min_height', 'max_width', 'max_height', 'margin',
        'styles', 'stylesheets', 'width', 'width_policy', 'height_policy',
        'sizing_mode', 'visible',
    )

    def _create_component(self) -> AnyWidgetComponent | None:
        """Build the internal ``AnyWidgetComponent`` from ``self.object``."""
        widget = self.object
        if widget is None:
            return None
        component_cls = _get_or_create_component_class(widget)

        trait_name_map: dict[str, str] = getattr(
            component_cls, '_trait_name_map', {}
        )

        # Read current traitlet values for initialisation
        sync_traits = _get_synced_traits(widget)
        init_values: dict[str, Any] = {}
        for trait_name in sync_traits:
            param_name = trait_name_map.get(trait_name, trait_name)
            if param_name in component_cls.param:
                value = _serialize_trait(
                    widget, trait_name, getattr(widget, trait_name),
                )
                init_values[param_name] = value

        # Forward layout params from the pane to the component
        for lp in self._LAYOUT_PARAMS:
            pane_val = getattr(self, lp, None)
            default_val = self.param[lp].default if lp in self.param else None
            if pane_val != default_val and lp in component_cls.param:
                init_values[lp] = pane_val

        # When the widget has height/width traits that were renamed due
        # to collision with Layoutable (e.g. height -> w_height), forward
        # their numeric values to the Layoutable height/width so the DOM
        # container gets actual pixel dimensions.  Without this, widgets
        # like jupyter-scatter crash because the canvas is 0px when
        # createScatterplot tries to compute the projection matrix.
        for dim in ('height', 'width'):
            param_name = trait_name_map.get(dim)
            if param_name and param_name != dim and dim not in init_values:
                value = init_values.get(param_name)
                if isinstance(value, (int, float)) and value > 0:
                    init_values[dim] = int(value)

        component = component_cls(**init_values)

        # Wire bidirectional sync
        self._setup_trait_sync(widget, component, sync_traits, trait_name_map)
        # Wire custom message routing (model.send / model.on("msg:custom"))
        self._setup_msg_routing(widget, component)
        return component

    # ------------------------------------------------------------------
    # Bidirectional sync:  anywidget traitlets <-> component params
    # ------------------------------------------------------------------

    def _setup_trait_sync(self, widget, component, sync_traits, trait_name_map):
        trait_names = list(sync_traits.keys())
        reverse_map = {v: k for k, v in trait_name_map.items()}
        instance_traits: dict[str, type] = getattr(
            type(component), '_instance_traits', {}
        )

        # Build set of renamed dimension traits whose numeric values should
        # be forwarded to the Layoutable height/width so the DOM container
        # always has actual pixel dimensions (see _create_component).
        _dim_forwarding: dict[str, str] = {}  # param_name -> layout dim
        for dim in ('height', 'width'):
            pn = trait_name_map.get(dim)
            if pn and pn != dim:
                _dim_forwarding[pn] = dim

        # traitlet -> component param
        def _on_traitlet_change(change):
            name = change['name']
            if name in self._trait_changing:
                return
            param_name = trait_name_map.get(name, name)
            try:
                self._trait_changing.add(name)
                if param_name in component.param:
                    value = _serialize_trait(widget, name, change['new'])
                    updates = {param_name: value}
                    # Also forward renamed height/width to Layoutable
                    layout_dim = _dim_forwarding.get(param_name)
                    if layout_dim and isinstance(value, (int, float)) and value > 0:
                        updates[layout_dim] = int(value)
                    component.param.update(**updates)
            finally:
                self._trait_changing.discard(name)

        widget.observe(_on_traitlet_change, names=trait_names)
        self._trait_watchers.append(
            ('traitlet', widget, _on_traitlet_change, trait_names)
        )

        # component param -> traitlet
        def _on_param_change(*events):
            import traitlets
            for event in events:
                param_name = event.name
                trait_name = reverse_map.get(param_name, param_name)
                if trait_name in self._trait_changing:
                    continue
                try:
                    self._trait_changing.add(trait_name)
                    value = event.new
                    if param_name in instance_traits:
                        value = _deserialize_instance(
                            instance_traits[param_name], value,
                        )
                    setattr(widget, trait_name, value)
                    # If a traitlet validator transformed the value,
                    # sync the validated value back to the component param
                    actual = _serialize_trait(
                        widget, trait_name, getattr(widget, trait_name),
                    )
                    if actual is not event.new and param_name in component.param:
                        component.param.update(**{param_name: actual})
                except traitlets.TraitError:
                    pass  # traitlet validation rejected the value
                except Exception:
                    logger.warning(
                        "Failed to sync param %r to traitlet %r: %s",
                        param_name, trait_name, event.new, exc_info=True,
                    )
                finally:
                    self._trait_changing.discard(trait_name)

        param_names = [
            trait_name_map.get(n, n) for n in trait_names
            if trait_name_map.get(n, n) in component.param
        ]
        if param_names:
            watcher = component.param.watch(_on_param_change, param_names)
            self._trait_watchers.append(('param', component, watcher))

    # ------------------------------------------------------------------
    # Custom message routing:  ESM <-> Python widget
    # ------------------------------------------------------------------
    # Some anywidgets (e.g. Mosaic) use a message-passing protocol where
    # the ESM sends queries to the Python backend via model.send() and
    # Python responds via widget.send().  Panel's ReactiveESM pipeline
    # handles this via DataEvent (ESM→Python) and ESMEvent (Python→ESM),
    # but the dynamic component's _handle_msg is a no-op and the widget's
    # send() tries to use the (non-existent) ipywidgets comm.
    #
    # This method bridges both directions:
    #   ESM → Python:  component.on_msg  →  widget._handle_custom_msg
    #   Python → ESM:  widget.send       →  component._send_msg
    #
    # Binary buffers (e.g. Mosaic's Arrow IPC query results) are
    # base64-encoded into the JSON message under `_b64_buffers` and
    # decoded back to DataView objects by the TS adapter.

    def _setup_msg_routing(self, widget, component):
        # ESM → Python: forward DataEvent messages to the widget
        # on_msg callbacks receive the full DataEvent object;
        # extract .data to pass to the widget's handler.
        # Binary buffers from ESM are base64-encoded under `_b64_buffers`
        # (by the TS adapter's send()) and decoded back to bytes here.
        def _on_component_msg(event):
            data = getattr(event, 'data', event)
            if hasattr(widget, '_handle_custom_msg'):
                buffers = []
                if isinstance(data, dict) and '_b64_buffers' in data:
                    import base64
                    for b64 in data['_b64_buffers']:
                        buffers.append(base64.b64decode(b64))
                    data = {k: v for k, v in data.items() if k != '_b64_buffers'}
                    if '_data' in data and len(data) == 1:
                        data = data['_data']
                widget._handle_custom_msg(data, buffers)

        component.on_msg(_on_component_msg)

        # Python → ESM: override widget.send() to route through Panel
        #
        # Panel's ESMEvent carries JSON only — no native binary channel.
        # When the widget sends binary buffers (e.g. Mosaic's Arrow IPC
        # query results), we base64-encode them into the JSON message
        # under the key `_b64_buffers`.  The TS adapter's msg:custom
        # wrapper decodes them back to DataView objects before passing
        # them to the ESM callback.
        def _send_override(content, buffers=None):
            if buffers:
                import base64
                encoded = []
                for buf in buffers:
                    if isinstance(buf, memoryview):
                        buf = bytes(buf)
                    encoded.append(base64.b64encode(buf).decode('ascii'))
                if isinstance(content, dict):
                    content = {**content, '_b64_buffers': encoded}
                else:
                    content = {'_data': content, '_b64_buffers': encoded}
            component._send_msg(content)

        # Store original send so we can restore it on cleanup
        self._original_widget_send = getattr(widget, 'send', None)
        widget.send = _send_override

    def _teardown_trait_sync(self):
        """Remove all traitlet observers and param watchers."""
        # Restore original widget.send if we overrode it
        if hasattr(self, '_original_widget_send') and self._original_widget_send is not None:
            widget = self.object
            if widget is not None:
                widget.send = self._original_widget_send
            self._original_widget_send = None
        for entry in self._trait_watchers:
            try:
                if entry[0] == 'traitlet':
                    _, widget, callback, names = entry
                    widget.unobserve(callback, names=names)
                elif entry[0] == 'param':
                    _, component, watcher = entry
                    component.param.unwatch(watcher)
            except Exception:
                pass
        self._trait_watchers.clear()
        self._trait_changing.clear()

    # ------------------------------------------------------------------
    # Re-render on object change
    # ------------------------------------------------------------------

    def _update_pane(self, *events) -> None:
        # Tear down old component before the base class re-renders
        self._teardown_trait_sync()
        self._component = None
        # Eagerly recreate the component for the new object
        if self.object is not None:
            self._component = self._create_component()
        super()._update_pane(*events)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def _cleanup(self, root: Model | None = None) -> None:
        if self._component is not None:
            self._component._cleanup(root)
        super()._cleanup(root)
        # Only discard everything when the last root is gone
        if not self._models:
            self._teardown_trait_sync()
            self._component = None
