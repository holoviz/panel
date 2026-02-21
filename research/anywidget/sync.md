# Bidirectional Sync Strategy: AnyWidget Traitlets <-> Panel Params <-> Bokeh Model

## 1. Overview

The AnyWidget pane needs three-way synchronization:

```
anywidget traitlets  <-->  Panel params  <-->  Bokeh model properties
       (1)                     (2)                    (3)
```

Layer (2) <-> (3) is already handled by Panel's `Syncable` base class (`_link_props`, `_process_events`, `_update_model`). We only need to add layer (1) <-> (2): syncing anywidget traitlets with Panel params.

## 2. Existing Patterns to Learn From

### 2.1 The `create_linked_datamodel()` Guard Pattern

`panel/io/datamodel.py:216-295` provides the canonical example of bidirectional sync with recursion prevention. Key design:

```python
_changing = []  # Shared mutable guard list

def cb_bokeh(attr, old, new):
    if attr in _changing:
        return                    # Skip if WE caused this change
    try:
        _changing.append(attr)    # Mark as "we're changing this"
        obj.param.update(**{attr: new})
    finally:
        _changing.remove(attr)    # Unmark

def cb_param(*events):
    update = {
        event.name: event.new for event in events
        if event.name not in _changing  # Skip if Bokeh caused this
    }
    try:
        _changing.extend(list(update))
        model.update(**update)
    finally:
        for attr in update:
            _changing.remove(attr)
```

**Key insight**: A single `_changing` list is shared between both callbacks. When one side initiates a change, it adds the attribute name to `_changing` before propagating. The other side checks `_changing` and skips if the attribute is present.

### 2.2 The `_ipywidget_transform()` Pattern

`panel/pane/ipywidget.py:126-145` shows existing one-directional traitlet -> param observation:

```python
def _ipywidget_transform(obj):
    if isinstance(obj, Model) or not (IPyWidget.applies(obj) and hasattr(obj, 'value')):
        return obj
    name = type(obj).__name__
    ipy_param = param.parameterized_class(name, {'value': param.Parameter()})
    ipy_inst = ipy_param(value=obj.value)
    # One-way: traitlet -> param only
    obj.observe(lambda event: ipy_inst.param.update(value=event['new']), 'value')
    return ipy_inst.param.value
```

This only does one-way sync (traitlet -> param) and only for the `value` trait. Our solution needs:
- **Bidirectional** sync (traitlet <-> param)
- **All user-defined traits**, not just `value`
- Recursion prevention

### 2.3 The `Syncable._changing` Pattern in `reactive.py`

`panel/reactive.py` uses `self._changing` (a `dict[str, list[str]]` keyed by root ref ID) to prevent Bokeh model -> param recursion:

```python
# In _update_model (param -> Bokeh direction):
self._changing[ref] = attrs = []
# ... track which attrs are being changed ...
model.update(**msg)

# In _server_change / _comm_change (Bokeh -> param direction):
if attr in self._changing.get(ref, []):
    self._changing[ref].remove(attr)
    return  # Skip, this change originated from param side
```

## 3. Proposed Bidirectional Sync Design

### 3.1 Architecture

```
anywidget instance               AnyWidget pane               Bokeh model
  (traitlets)                    (Panel params)               (JS frontend)
       |                              |                             |
       |--observe(cb_traitlet)------->|                             |
       |                              |--_link_props()------------->|
       |<--setattr(trait, val)--------|                             |
       |                              |<--_process_events()---------|
       |                              |                             |
       |          _changing (shared guard list)                     |
```

### 3.2 The Guard Pattern

We need a `_changing` guard specifically for the traitlet <-> param sync layer. This is separate from the existing `self._changing` dict used for param <-> Bokeh sync (which is keyed by root ref ID).

```python
class AnyWidget(Pane):

    def __init__(self, object=None, **params):
        # Guard list for traitlet <-> param recursion prevention
        self._trait_changing: list[str] = []
        # Store observer references for cleanup
        self._trait_watchers: list[tuple] = []
        super().__init__(object=object, **params)
```

### 3.3 Traitlet -> Param Sync

When an anywidget traitlet changes, propagate to the Panel param:

```python
def _cb_traitlet(self, change):
    """Called when an anywidget traitlet value changes."""
    name = change['name']
    if name in self._trait_changing:
        return  # This change originated from param side, skip

    new_value = change['new']
    try:
        self._trait_changing.append(name)
        # Map traitlet name to param name (may differ)
        param_name = self._trait_to_param.get(name, name)
        if param_name in self.param:
            self.param.update(**{param_name: new_value})
    finally:
        if name in self._trait_changing:
            self._trait_changing.remove(name)
```

### 3.4 Param -> Traitlet Sync

When a Panel param changes, propagate to the anywidget traitlet:

```python
def _cb_param(self, *events):
    """Called when a Panel param value changes."""
    for event in events:
        name = event.name
        if name in self._trait_changing:
            continue  # This change originated from traitlet side, skip

        trait_name = self._param_to_trait.get(name, name)
        try:
            self._trait_changing.append(name)
            setattr(self.object, trait_name, event.new)
        finally:
            if name in self._trait_changing:
                self._trait_changing.remove(name)
```

### 3.5 Wiring It Up

```python
def _setup_trait_sync(self, widget):
    """Set up bidirectional sync between traitlets and params."""
    # Determine which traits to sync
    sync_traits = self._get_syncable_traits(widget)

    for trait_name, param_name in sync_traits.items():
        # Traitlet -> Param
        widget.observe(self._cb_traitlet, names=[trait_name])
        self._trait_watchers.append((widget, trait_name))

    # Param -> Traitlet (single watcher for all synced params)
    param_names = list(sync_traits.values())
    if param_names:
        watcher = self.param.watch(self._cb_param, param_names)
        self._trait_watchers.append(('param', watcher))
```

### 3.6 Trait-to-Param Name Mapping

Anywidget traits may map to Panel params with the same name or different names. The default should be identity mapping, with overrides possible:

```python
@property
def _trait_to_param(self) -> dict[str, str]:
    """Map from traitlet names to param names. Override for custom mapping."""
    return {name: name for name in self._syncable_traits}

@property
def _param_to_trait(self) -> dict[str, str]:
    """Reverse mapping from param names to traitlet names."""
    return {v: k for k, v in self._trait_to_param.items()}
```

## 4. Anywidget's Own Sync Mechanism (Important Context)

From the actual anywidget source (`/tmp/anywidget-src/anywidget/_descriptor.py`), anywidget has its own sync system for non-ipywidgets objects. The `_descriptor.py` file reveals:

### 4.0.1 How anywidget detects syncable traits

Anywidget uses `obj.traits(sync=True)` to find which traits should be synced. Only traits tagged with `.tag(sync=True)` are included. This is the ipywidgets convention.

From `_descriptor.py:647-669`:
```python
_TRAITLETS_SYNC_FLAG = "sync"

def _get_traitlets_state(obj, include):
    kwargs = {_TRAITLETS_SYNC_FLAG: True}
    return obj.trait_values(**kwargs)
```

And the traitlet observer connection (`_descriptor.py:672-698`):
```python
def _connect_traitlets(obj, send_state):
    def _on_trait_change(change):
        send_state({change["name"]})
    obj.observe(_on_trait_change, names=list(obj.traits(sync=True)))
    obj_ref = weakref.ref(obj)
    def _disconnect():
        obj = obj_ref()
        if obj is not None:
            obj.unobserve(_on_trait_change)
    return _disconnect
```

### 4.0.2 Implications for our sync design

1. **Use `widget.traits(sync=True)` to discover syncable traits**, matching anywidget's own convention.
2. **`widget.unobserve(handler)` (no names arg)** removes the handler from ALL traits. The `_connect_traitlets` cleanup uses this simpler form. We should use the same pattern in our teardown.
3. The `_get_syncable_traits` in our prototype should use `widget.traits(sync=True)` directly rather than manually filtering by prefix/name, and then exclude known internal ipywidget traits from that result.

### 4.0.3 Revised `_get_syncable_traits`

```python
def _get_syncable_traits(self, widget):
    """
    Returns dict of {traitlet_name: param_name} for user-defined traits to sync.
    Uses the sync=True tag convention from ipywidgets/anywidget.
    """
    EXCLUDED = {
        # ipywidgets internal infrastructure
        '_model_name', '_model_module', '_model_module_version',
        '_view_name', '_view_module', '_view_module_version',
        '_dom_classes', '_view_count',
        # anywidget internal
        '_esm', '_css', '_anywidget_id',
    }
    sync_traits = widget.traits(sync=True)
    return {
        name: name
        for name in sync_traits
        if name not in EXCLUDED
    }
```

This is cleaner than the prefix-based filtering and exactly matches how anywidget itself identifies syncable traits.

## 5. Thread Safety Considerations

### 4.1 Traitlet Observer Threading Model

In **Jupyter**, traitlet observers fire on the **main thread** when triggered by:
- Python code calling `widget.trait_name = value` (same thread)
- Frontend comm messages arriving via `widget.comm` (IO thread, dispatched to main thread via event loop)

In **Panel server** (Bokeh/Tornado):
- The Bokeh document has its own event loop
- Traitlet observers fire on the thread that sets the trait value
- If the Panel param callback sets a traitlet, the observer fires on the Bokeh callback thread

### 4.2 Thread Safety of the Guard

The `_trait_changing` list is a simple Python list, which is NOT thread-safe for concurrent modifications. However:

1. **In Jupyter**: All callbacks run on the main thread (event loop), so no concurrent access.
2. **In Panel server**: Document callbacks are serialized by the Bokeh document lock. The `_changing` guard only needs to prevent recursion within a single callback chain, not across threads.

If we need true thread safety in the future, we can use `threading.local()` or a lock:

```python
import threading
self._trait_lock = threading.Lock()
```

For now, the simple list approach (matching `create_linked_datamodel`) is sufficient.

### 4.3 Document Lock Interaction

When propagating param -> traitlet changes, we may need to be careful about the Bokeh document lock. If the param change was triggered by a Bokeh model event (which holds the doc lock), and the traitlet observer tries to schedule a doc update, it could deadlock.

The guard pattern prevents this: if the change originated from Bokeh (model -> param via `_process_events`), and the param watcher fires `_cb_param`, that callback would try to set the traitlet. The traitlet observer `_cb_traitlet` would then fire, but it sees the name in `_trait_changing` and returns immediately, preventing any further propagation back to the Bokeh model.

## 5. Lifecycle Management

### 5.1 Setup

Trait sync should be set up when the pane's `object` is set (in `__init__` or when `object` changes):

```python
def __init__(self, object=None, **params):
    self._trait_changing = []
    self._trait_watchers = []
    super().__init__(object=object, **params)
    if self.object is not None:
        self._setup_trait_sync(self.object)
```

### 5.2 Object Change

When the pane's `object` param changes, tear down old sync and set up new:

```python
@param.depends('object', watch=True)
def _update_object(self):
    self._teardown_trait_sync()
    if self.object is not None:
        self._setup_trait_sync(self.object)
```

### 5.3 Cleanup on Destroy

When the pane is destroyed (via `_cleanup()`), unregister all traitlet observers to prevent memory leaks and stale callbacks.

```python
def _cleanup(self, root=None):
    super()._cleanup(root)
    if not self._models:
        self._teardown_trait_sync()

def _teardown_trait_sync(self):
    """Remove all traitlet observers and param watchers."""
    if self._trait_watchers:
        widget = self._trait_watchers[0][0]
        try:
            widget.unobserve(self._cb_traitlet)
        except Exception:
            pass
    self._trait_watchers.clear()
    if self._param_watcher is not None:
        self.param.unwatch(self._param_watcher)
        self._param_watcher = None
    self._trait_changing.clear()
```

**Important**: `widget.unobserve(handler)` (without `names=`) removes the handler from ALL traits at once. This matches anywidget's own disconnect pattern (`_descriptor.py:693-696`). The callback must be the same object reference (not a lambda or partial), so we use `self._cb_traitlet` as a bound method.

### 5.4 Multiple Roots

The existing `_cleanup(root)` pattern in `Syncable` handles per-root cleanup. For traitlet sync, we have one set of watchers per pane instance (not per root), so we should only tear down traitlet sync when the LAST root is cleaned up (i.e., `self._models` is empty after cleanup):

```python
def _cleanup(self, root=None):
    super()._cleanup(root)
    # Only teardown trait sync when no more models exist
    if not self._models:
        self._teardown_trait_sync()
```

## 7. Full Prototype (Updated)

```python
class AnyWidget(Pane):
    """
    Renders anywidget instances natively in Panel.
    """

    priority: ClassVar[float | bool | None] = 0.8

    def __init__(self, object=None, **params):
        self._trait_changing: list[str] = []
        self._trait_watchers: list = []
        self._param_watcher = None
        super().__init__(object=object, **params)
        if self.object is not None:
            self._setup_trait_sync(self.object)

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if not (hasattr(obj, 'traits') and hasattr(obj, 'comm')):
            return False
        return hasattr(type(obj), '_esm')

    def _get_syncable_traits(self, widget):
        """
        Returns dict of {traitlet_name: param_name} for user-defined traits to sync.
        Uses the sync=True tag convention from ipywidgets/anywidget.
        Matches anywidget's own _get_traitlets_state() and _connect_traitlets().
        """
        EXCLUDED = {
            # ipywidgets internal infrastructure
            '_model_name', '_model_module', '_model_module_version',
            '_view_name', '_view_module', '_view_module_version',
            '_dom_classes', '_view_count',
            # anywidget internal
            '_esm', '_css', '_anywidget_id',
        }
        sync_traits = widget.traits(sync=True)
        return {
            name: name
            for name in sync_traits
            if name not in EXCLUDED
        }

    def _setup_trait_sync(self, widget):
        """Set up bidirectional traitlet <-> param sync."""
        sync_traits = self._get_syncable_traits(widget)

        for trait_name in sync_traits:
            widget.observe(self._cb_traitlet, names=[trait_name])
            self._trait_watchers.append((widget, trait_name))

        param_names = [
            pname for pname in sync_traits.values()
            if pname in self.param
        ]
        if param_names:
            self._param_watcher = self.param.watch(
                self._cb_param, param_names
            )

    def _cb_traitlet(self, change):
        """Traitlet -> Param propagation with guard."""
        name = change['name']
        if name in self._trait_changing:
            return
        try:
            self._trait_changing.append(name)
            if name in self.param:
                self.param.update(**{name: change['new']})
        finally:
            if name in self._trait_changing:
                self._trait_changing.remove(name)

    def _cb_param(self, *events):
        """Param -> Traitlet propagation with guard."""
        for event in events:
            name = event.name
            if name in self._trait_changing:
                continue
            try:
                self._trait_changing.append(name)
                setattr(self.object, name, event.new)
            finally:
                if name in self._trait_changing:
                    self._trait_changing.remove(name)

    def _teardown_trait_sync(self):
        """Remove all traitlet observers and param watchers."""
        if self._trait_watchers:
            # Use unobserve(handler) without names= to remove from ALL traits
            # This matches anywidget's own _disconnect pattern in _descriptor.py:693-696
            widget = self._trait_watchers[0][0]
            try:
                widget.unobserve(self._cb_traitlet)
            except Exception:
                pass
        self._trait_watchers.clear()
        if self._param_watcher is not None:
            self.param.unwatch(self._param_watcher)
            self._param_watcher = None
        self._trait_changing.clear()

    def _cleanup(self, root=None):
        super()._cleanup(root)
        if not self._models:
            self._teardown_trait_sync()
```

## 8. Integration with Existing Panel Sync

The traitlet <-> param sync layer operates independently from the param <-> Bokeh model sync. The flow for a change originating from the anywidget's Python side:

```
1. User code: widget.value = 42
2. Traitlet observer fires: _cb_traitlet({'name': 'value', 'new': 42})
3. Guard: 'value' not in _trait_changing, proceed
4. _trait_changing = ['value']
5. self.param.update(value=42)
6. Panel's existing machinery: param change -> _process_param_change -> Bokeh model update
7. Bokeh model update -> JS frontend re-renders
8. Meanwhile: param watcher _cb_param fires, sees 'value' in _trait_changing, skips
9. _trait_changing.remove('value')
```

For a change originating from the JS frontend:

```
1. User clicks button in browser
2. Bokeh model property changes
3. _process_events() fires: param.update(value=43)
4. Param watcher _cb_param fires: 'value' not in _trait_changing
5. _trait_changing = ['value']
6. setattr(self.object, 'value', 43)  # Update traitlet
7. Traitlet observer _cb_traitlet fires, sees 'value' in _trait_changing, skips
8. _trait_changing.remove('value')
```

This ensures changes propagate in one direction without recursion, regardless of where they originate.

## 9. Open Questions

1. **Initial value sync**: When the pane is first created, should we copy traitlet values to params or vice versa? The pane should be constructed with the anywidget's current trait values, so traitlet -> param is the right direction at init time.

2. **Complex trait types**: Binary buffers, nested dicts, numpy arrays -- these may need custom serialization when passing between traitlets and params. The `_process_param_change` and `_process_events` methods handle Bokeh serialization, but the traitlet <-> param layer may need its own transforms.

3. **Trait validation**: Traitlets have their own validation. If a param change produces a value that fails traitlet validation, we need to handle the `TraitError` gracefully (log warning, revert param value).

4. **Comm-based widgets in Jupyter**: In notebook context, the anywidget also has its own comm channel to the frontend. If we're rendering via Panel's Bokeh model, we should consider whether the anywidget's own comm should be disabled to prevent double-rendering. This is more of an architecture question than a sync question.
