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


# ---------------------------------------------------------------
# Traitlet -> param helpers
# ---------------------------------------------------------------

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
        p = param.Selector(default=default, objects=list(trait.values))
        if getattr(trait, 'allow_none', False):
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

    # --- Special-case: Instance -> param.ClassSelector ------------
    # Checked after TRAITLET_MAP walk because Container subclasses
    # (List, Set, Tuple, Dict) inherit from Instance.
    if isinstance(trait, traitlets.Instance):
        try:
            default = trait.default()
        except Exception:
            default = None
        klass = getattr(trait, 'klass', None) or object
        p = param.ClassSelector(default=default, class_=klass, is_instance=True)
        if getattr(trait, 'allow_none', False):
            p.allow_None = True
        return p

    # Fallback for unknown types (including Union)
    try:
        default = trait.default()
    except Exception:
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
    sync_traits = _get_synced_traits(widget)
    collision_names = set(AnyWidgetComponent.param)

    params: dict[str, param.Parameter] = {}
    trait_name_map: dict[str, str] = {}  # traitlet name -> param name
    for name, trait in sync_traits.items():
        param_name = f'w_{name}' if name in collision_names else name
        params[param_name] = _traitlet_to_param(trait)
        trait_name_map[name] = param_name

    # --- Build class dict ----------------------------------------------
    class_dict: dict[str, Any] = {
        '_esm': esm or '',
        '_trait_name_map': trait_name_map,
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
            model = BkSpacer()
            self._models[root.ref['id']] = (model, parent)
            return model

        if self._component is None:
            self._component = self._create_component()

        model = self._component._get_model(doc, root, parent, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

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
                init_values[param_name] = getattr(widget, trait_name)

        component = component_cls(**init_values)

        # Wire bidirectional sync
        self._setup_trait_sync(widget, component, sync_traits, trait_name_map)
        return component

    # ------------------------------------------------------------------
    # Bidirectional sync:  anywidget traitlets <-> component params
    # ------------------------------------------------------------------

    def _setup_trait_sync(self, widget, component, sync_traits, trait_name_map):
        trait_names = list(sync_traits.keys())
        reverse_map = {v: k for k, v in trait_name_map.items()}

        # traitlet -> component param
        def _on_traitlet_change(change):
            name = change['name']
            if name in self._trait_changing:
                return
            param_name = trait_name_map.get(name, name)
            try:
                self._trait_changing.add(name)
                if param_name in component.param:
                    component.param.update(**{param_name: change['new']})
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
                    setattr(widget, trait_name, event.new)
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

    def _teardown_trait_sync(self):
        """Remove all traitlet observers and param watchers."""
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
