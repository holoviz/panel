# Pane Class Design: `AnyWidget` Pane

This document synthesizes findings from all research tracks to produce a complete class skeleton for the `AnyWidget` pane.

## 1. Design Decisions

### 1.1 Base Class: `Pane` (not `PaneBase`)

The `AnyWidget` pane should extend `Pane` (`panel/pane/base.py:286`), which itself extends `PaneBase` and `Reactive`. This gives us:

- `object` parameter (the anywidget instance being wrapped)
- `_rerender_params` / `_update_pane` mechanism for object changes
- `_get_model` / `_update_object` lifecycle
- All `Reactive` syncing machinery (though the pane delegates model creation to the internal component)
- Priority-based pane resolution via `applies()` and `priority`

We do NOT extend `PaneBase` directly because we need `Reactive`'s event handling and model syncing.

### 1.2 Architecture: Delegation to Dynamic `AnyWidgetComponent` Subclass

Per the architecture validation (Track 3), the pane creates a dynamic `AnyWidgetComponent` subclass for each anywidget class, then instantiates it and delegates model creation. The dynamic subclass gets a proper `_data_model` via `ReactiveESMMetaclass.__init__`.

```
AnyWidget Pane (Pane subclass)
    |
    +-- object: anywidget instance
    |
    +-- _component: AnyWidgetComponent subclass instance
    |       |
    |       +-- _esm (from anywidget._esm)
    |       +-- param.Integer, param.String, etc. (from anywidget traitlets)
    |       +-- _data_model (auto-created by metaclass)
    |
    +-- bidirectional sync: anywidget traitlets <-> component params
```

### 1.3 `_updates = False`

The pane does NOT support in-place model updates when `object` changes. When the user assigns a new anywidget instance to `pane.object`, the entire model is rebuilt via `_update_object` -> `_get_model`. This is simpler and safer than trying to diff traitlets between old and new widgets.

Within a single `object` lifetime, traitlet changes are synced bidirectionally through the component's params, which flow to the Bokeh model automatically via Panel's existing `Syncable` machinery.

---

## 2. Class Cache

A module-level cache maps anywidget classes to their dynamic `AnyWidgetComponent` subclasses:

```python
_COMPONENT_CACHE: dict[type, type[AnyWidgetComponent]] = {}
```

This uses a regular `dict` (not `WeakKeyDictionary`) because:
- Classes are singletons — they persist for the process lifetime
- We want to avoid re-running the metaclass for the same anywidget class
- Name counter inflation is avoided (each anywidget class gets exactly one DataModel)

---

## 3. Complete Class Skeleton

```python
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, ClassVar

import param

from ..custom import AnyWidgetComponent
from .base import Pane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

# --- Module-level cache ---
_COMPONENT_CACHE: dict[type, type[AnyWidgetComponent]] = {}

# --- Traitlet-to-Param mapping ---
# (Defined separately, imported from a utility module in production)

def _traitlet_to_param(name, trait):
    """Convert a single traitlet to a param.Parameter."""
    import traitlets
    TRAITLET_MAP = {
        traitlets.Bool:      param.Boolean,
        traitlets.CBool:     param.Boolean,
        traitlets.Int:       param.Integer,
        traitlets.CInt:      param.Integer,
        traitlets.Integer:   param.Integer,
        traitlets.Long:      param.Integer,
        traitlets.CLong:     param.Integer,
        traitlets.Float:     param.Number,
        traitlets.CFloat:    param.Number,
        traitlets.Unicode:   param.String,
        traitlets.CUnicode:  param.String,
        traitlets.Bytes:     param.Bytes,
        traitlets.CBytes:    param.Bytes,
        traitlets.List:      param.List,
        traitlets.Tuple:     param.Tuple,
        traitlets.Dict:      param.Dict,
    }
    # Walk MRO for custom traitlet subclasses
    for cls in type(trait).__mro__:
        if cls in TRAITLET_MAP:
            param_type = TRAITLET_MAP[cls]
            p = param_type(default=trait.default())
            if getattr(trait, 'allow_none', False):
                p.allow_None = True
            return p
    # Fallback for unknown types
    p = param.Parameter(default=trait.default())
    if getattr(trait, 'allow_none', False):
        p.allow_None = True
    return p


def _get_synced_traits(widget_class):
    """Extract sync-tagged, user-facing traits from an anywidget class."""
    SKIP = {
        '_esm', '_css', '_anywidget_id',
        '_model_name', '_view_name',
        '_model_module', '_view_module',
        '_model_module_version', '_view_module_version',
        '_view_count', '_dom_classes', '_model_data',
    }
    sync_traits = widget_class.class_traits(sync=True)
    return {
        name: trait for name, trait in sync_traits.items()
        if name not in SKIP and not name.startswith('_')
    }


def _get_or_create_component_class(anywidget_cls):
    """
    Get or create a dynamic AnyWidgetComponent subclass for an anywidget class.

    The returned class has:
    - _esm set from the anywidget's _esm
    - _stylesheets set from the anywidget's _css (if present)
    - param Parameters mapped from the anywidget's sync-tagged traitlets
    """
    if anywidget_cls in _COMPONENT_CACHE:
        return _COMPONENT_CACHE[anywidget_cls]

    # Extract ESM
    esm = getattr(anywidget_cls, '_esm', None)
    if esm is not None:
        esm = str(esm)  # Handles str, FileContents, VirtualFileContents

    # Extract CSS
    css = getattr(anywidget_cls, '_css', None)
    if css is not None:
        css = str(css)

    # Map traitlets to param Parameters
    sync_traits = _get_synced_traits(anywidget_cls)
    params = {}
    for name, trait in sync_traits.items():
        params[name] = _traitlet_to_param(name, trait)

    # Build class dict
    class_dict = {'_esm': esm or '', **params}
    if css:
        class_dict['_stylesheets'] = [css]

    # Create dynamic subclass (triggers ReactiveESMMetaclass.__init__)
    component_cls = type(
        anywidget_cls.__name__,
        (AnyWidgetComponent,),
        class_dict,
    )

    _COMPONENT_CACHE[anywidget_cls] = component_cls
    return component_cls


class AnyWidget(Pane):
    """
    The AnyWidget pane renders anywidget instances natively in Panel.

    Instead of using the ipywidgets comm infrastructure, this pane
    extracts the anywidget's ESM code and traitlet definitions, creates
    a dynamic AnyWidgetComponent subclass, and renders it using Panel's
    native ReactiveESM pipeline. This provides full Panel reactivity
    including param.watch, pn.bind, and .rx support.

    Reference: https://panel.holoviz.org/reference/panes/AnyWidget.html

    :Example:

    >>> import anywidget
    >>> import traitlets
    >>> class CounterWidget(anywidget.AnyWidget):
    ...     _esm = \"\"\"
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
    ...     \"\"\"
    ...     value = traitlets.Int(0).tag(sync=True)
    >>>
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
        # Guard list for traitlet <-> param recursion prevention
        self._trait_changing: list[str] = []
        # Observer references for cleanup
        self._trait_watchers: list = []
        # The internal AnyWidgetComponent instance
        self._component: AnyWidgetComponent | None = None
        super().__init__(object=object, **params)

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        """Detect anywidget instances via duck typing."""
        if not (hasattr(obj, 'traits') and hasattr(obj, 'comm')):
            return False
        return hasattr(type(obj), '_esm')

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        if root is None:
            return self.get_root(doc, comm)

        # Create or retrieve the component
        if self._component is None:
            self._component = self._create_component()

        # Delegate model creation to the component
        model = self._component._get_model(doc, root, parent, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _create_component(self) -> AnyWidgetComponent:
        """
        Create the internal AnyWidgetComponent from the anywidget object.

        Steps:
        1. Get or create a dynamic AnyWidgetComponent subclass
        2. Read current traitlet values from the anywidget instance
        3. Instantiate the component with those values
        4. Set up bidirectional traitlet <-> param sync
        """
        widget = self.object
        component_cls = _get_or_create_component_class(type(widget))

        # Read current traitlet values
        sync_traits = _get_synced_traits(type(widget))
        init_values = {}
        for trait_name in sync_traits:
            if trait_name in component_cls.param:
                init_values[trait_name] = getattr(widget, trait_name)

        # Instantiate
        component = component_cls(**init_values)

        # Set up bidirectional sync
        self._setup_trait_sync(widget, component, sync_traits)

        return component

    # ------------------------------------------------------------------
    # Bidirectional sync: anywidget traitlets <-> component params
    # ------------------------------------------------------------------

    def _setup_trait_sync(self, widget, component, sync_traits):
        """
        Wire bidirectional sync between anywidget traitlets and
        component params. Uses a shared guard list to prevent recursion.
        """
        trait_names = list(sync_traits.keys())

        # Traitlet -> Component param
        def cb_traitlet(change):
            name = change['name']
            if name in self._trait_changing:
                return
            try:
                self._trait_changing.append(name)
                if name in component.param:
                    component.param.update(**{name: change['new']})
            finally:
                if name in self._trait_changing:
                    self._trait_changing.remove(name)

        widget.observe(cb_traitlet, names=trait_names)
        self._trait_watchers.append(('traitlet', widget, cb_traitlet, trait_names))

        # Component param -> Traitlet
        def cb_param(*events):
            for event in events:
                name = event.name
                if name in self._trait_changing:
                    continue
                try:
                    self._trait_changing.append(name)
                    setattr(widget, name, event.new)
                except Exception:
                    pass  # Traitlet validation may reject the value
                finally:
                    if name in self._trait_changing:
                        self._trait_changing.remove(name)

        param_names = [n for n in trait_names if n in component.param]
        if param_names:
            watcher = component.param.watch(cb_param, param_names)
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
                pass  # Widget or component may already be destroyed
        self._trait_watchers.clear()
        self._trait_changing.clear()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def _cleanup(self, root: Model | None = None) -> None:
        if self._component is not None:
            self._component._cleanup(root)
        super()._cleanup(root)
        # Only teardown trait sync when no more models exist
        if not self._models:
            self._teardown_trait_sync()
            self._component = None
```

---

## 4. Detailed Flow Analysis

### 4.1 `_get_model()` Flow

```
pn.panel(anywidget_instance)
  |
  v
PaneBase.get_pane_type(obj)  # Priority 0.8, applies() matches
  |
  v
AnyWidget(object=anywidget_instance)
  |
  v
_get_model(doc, root, parent, comm)
  |
  +-- self._component is None -> _create_component()
  |     |
  |     +-- _get_or_create_component_class(type(widget))
  |     |     |
  |     |     +-- Cache miss -> type(name, (AnyWidgetComponent,), {_esm, params...})
  |     |     |     |
  |     |     |     +-- ReactiveESMMetaclass.__init__ -> construct_data_model()
  |     |     |     +-- Returns new AnyWidgetComponent subclass
  |     |     |
  |     |     +-- Cache hit -> return cached class
  |     |
  |     +-- Read traitlet values -> component_cls(**init_values)
  |     +-- _setup_trait_sync(widget, component, sync_traits)
  |     +-- Return component
  |
  +-- self._component._get_model(doc, root, parent, comm)
  |     |
  |     +-- ReactiveESM._get_model() -> creates Bokeh model
  |     +-- _render_esm() -> returns ESM string
  |     +-- _process_importmap() -> adds React to import map
  |     +-- _data_model(**props) -> creates DataModel with synced values
  |
  +-- self._models[ref] = (model, parent)
  +-- Return model
```

### 4.2 Traitlet Change Flow (Python-initiated)

```
user code: anywidget_instance.value = 42
  |
  v
traitlet observer cb_traitlet fires
  |
  +-- 'value' not in _trait_changing -> proceed
  +-- _trait_changing = ['value']
  +-- component.param.update(value=42)
  |     |
  |     v
  |     Panel's Syncable machinery:
  |       _process_param_change -> _update_model -> Bokeh model update
  |       -> JS frontend re-renders
  |
  +-- Meanwhile: component param watcher cb_param fires
  |     +-- 'value' in _trait_changing -> skip (prevents recursion)
  |
  +-- _trait_changing.remove('value')
```

### 4.3 Frontend Change Flow (JS-initiated)

```
User clicks button in browser
  |
  v
AnyWidgetAdapter.set('value', 43) + save_changes()
  |
  v
Bokeh model.data.value changes
  |
  v
component._process_events() -> component.param.update(value=43)
  |
  v
component param watcher cb_param fires
  +-- 'value' not in _trait_changing -> proceed
  +-- _trait_changing = ['value']
  +-- setattr(anywidget_instance, 'value', 43)
  |     |
  |     v
  |     traitlet observer cb_traitlet fires
  |       +-- 'value' in _trait_changing -> skip (prevents recursion)
  |
  +-- _trait_changing.remove('value')
```

### 4.4 `_cleanup()` Flow

```
pane._cleanup(root)
  |
  +-- component._cleanup(root)
  |     |
  |     +-- Removes Bokeh model references
  |     +-- Stops ESM file watchers
  |
  +-- super()._cleanup(root)  # Pane cleanup
  |
  +-- if not self._models:  # Last root cleaned up
        +-- _teardown_trait_sync()
        |     +-- widget.unobserve(cb_traitlet, names=[...])
        |     +-- component.param.unwatch(watcher)
        |     +-- Clear _trait_watchers and _trait_changing
        +-- self._component = None
```

### 4.5 `_update_object()` Flow (object replacement)

When `pane.object = new_anywidget_instance`:

```
Pane._update_pane fires (watches _rerender_params=['object'])
  |
  v
_update_object(ref, doc, root, parent, comm)
  |
  +-- _updates is False -> creates new model
  +-- _teardown_trait_sync()     # Clean up old sync
  +-- self._component = None     # Discard old component
  +-- _get_model(doc, root, parent, comm)
  |     +-- _create_component()  # Creates new component for new widget
  |     +-- Returns new Bokeh model
  +-- Replace old model in parent.children
```

---

## 5. Key Design Decisions

### 5.1 Sync Layer Architecture

The sync operates between the **anywidget traitlets** and the **component params** (not the pane's params). This is because:

- The pane's `object` param holds the anywidget instance; it doesn't have individual params for each traitlet
- The component has the params that match traitlets (created dynamically)
- The component's params are already wired to the Bokeh model via Panel's existing `Syncable` machinery
- This avoids name collisions between pane params (width, height, margin, etc.) and traitlet names

### 5.2 Guard Pattern

We use a single `_trait_changing` list shared between both callbacks, following the same pattern as `create_linked_datamodel()` in `panel/io/datamodel.py:216-295`. This is simple, proven, and sufficient for the single-threaded callback model.

### 5.3 No `_bokeh_model` on the Pane

The `AnyWidget` pane does NOT define `_bokeh_model`. Instead, it delegates to `self._component._get_model()`. The component's `_bokeh_model` is `_BkAnyWidgetComponent` (inherited from `AnyWidgetComponent`). This is similar to how `PyComponent` delegates to `self._view__._get_model()`.

### 5.4 Component Lifecycle Tied to Pane

The `_component` is created lazily on first `_get_model()` call and destroyed when the last root is cleaned up or when `object` changes. This ensures:
- No component is created if the pane is never rendered
- Old components are properly cleaned up
- Each `object` gets a fresh component

---

## 6. Registration

The pane should be registered in `panel/pane/__init__.py`:

```python
# In panel/pane/__init__.py
from .ipywidget import AnyWidget  # Add alongside IPyWidget imports

# Add to __all__
__all__ = [
    ...,
    'AnyWidget',
    ...
]
```

The pane class lives in `panel/pane/ipywidget.py` alongside `IPyWidget` and `IPyLeaflet`, since they are all ipywidget-related panes. Alternatively, it could live in its own file `panel/pane/anywidget.py` for cleaner separation.

**Recommendation**: Place in `panel/pane/anywidget.py` to keep concerns separate. The file is small and self-contained.

---

## 7. Edge Cases and Mitigations

### 7.1 Remote URL `_esm`

If an anywidget's `_esm` is a URL like `"https://cdn.example.com/widget.js"`, `str(esm)` returns the URL string. Panel's `_render_esm()` would treat this as inline code (since `_esm_path()` returns `None` for non-path strings). This would fail.

**Mitigation**: In `_get_or_create_component_class`, detect URL strings and handle them:
```python
if esm and (esm.startswith('http://') or esm.startswith('https://')):
    # Wrap URL in a dynamic import
    esm = f'const mod = await import("{esm}"); export default mod.default;'
```

### 7.2 Traitlet Name Collisions with Pane Params

Since sync operates between traitlets and the **component** (not the pane), and the component inherits from `AnyWidgetComponent` (not `Pane`), the risk of collision is with `AnyWidgetComponent` params rather than `Pane` params. The `AnyWidgetComponent` base has very few params (primarily `stylesheets`, `use_shadow_dom`), so collisions are unlikely. If they occur, the traitlet param overrides the base class param in the dynamic subclass, which is the desired behavior.

### 7.3 Anywidget Without `sync=True` Traits

If an anywidget has no sync-tagged traits (only `_esm`), the component will have no custom params and will only render the ESM. The `_data_model` will only contain `esm_constants`. This is fine.

### 7.4 Multiple Pane Instances for Same Widget

If two panes wrap the same anywidget instance, both create their own component but share the same component *class* (from the cache). Each pane has its own bidirectional sync, so changes to the widget propagate to both panes. This is correct behavior.

### 7.5 Widget Destroyed Before Pane

If the anywidget instance is garbage collected before the pane, the traitlet observers will fail silently (caught by try/except in `_teardown_trait_sync`). The component and Bokeh model remain valid but no longer receive updates.

---

## 8. Summary

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Base class | `Pane` | Need Reactive + pane resolution |
| Architecture | Dynamic `AnyWidgetComponent` subclass | Reuses metaclass pipeline, TS adapter, full ESM pipeline |
| Cache | Module-level `dict[type, type]` | Classes are singletons, avoid metaclass re-runs |
| Sync target | Component params (not pane params) | Avoids name collisions, leverages existing Syncable |
| Guard pattern | Shared `_trait_changing` list | Proven pattern from `create_linked_datamodel` |
| Model updates | `_updates = False` (full rebuild) | Simpler, safer for object replacement |
| Priority | 0.8 | Wins over IPyWidget (0.6) and IPyLeaflet (0.7) |
| Detection | Duck-typing (`traits` + `comm` + `_esm`) | No import overhead, no false positives |
| File location | `panel/pane/anywidget.py` | Clean separation from ipywidget.py |
