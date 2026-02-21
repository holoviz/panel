# UX Reactivity Design: AnyWidget Pane Parameter Exposure

## 1. The Core Question

When a user wraps an anywidget with `pn.pane.AnyWidget(widget)`, how should they interact with the anywidget's state using familiar Panel/param patterns (`param.watch`, `pn.bind`, `.rx`, `.link`, etc.)?

The anywidget has traitlets (e.g. `value = traitlets.Int().tag(sync=True)`). Panel users expect to work with `param.Parameter` objects. This report evaluates six design options and recommends one.

---

## 2. Evaluation of All Options

### Option A: Direct param attributes on the pane

Dynamically add `param.Parameter` objects directly to the `AnyWidget` pane class/instance so that `pane.value`, `pane.param.value`, etc. work.

```python
widget = SomeAnyWidget()
pane = pn.pane.AnyWidget(widget)
pane.value            # reads the synced trait
pane.param.value      # param.Parameter object
pane.param.watch(cb, ['value'])
pn.bind(fn, pane.param.value)
```

**Pros:**
- Most ergonomic: identical to native Panel `Widget` usage (`slider.value`, `slider.param.value`)
- Works with all param/Panel reactive primitives out of the box
- No new concepts for users to learn

**Cons:**
- **Name collisions**: The pane inherits params from `Pane`, `PaneBase`, `Layoutable`, `Reactive`, `Syncable`, `Viewable` -- including `object`, `name`, `width`, `height`, `margin`, `sizing_mode`, `stylesheets`, `design`, `loading`, `visible`, `tags`, `css_classes`, `align`, `aspect_ratio`, `min_width`, `max_width`, `min_height`, `max_height`, `width_policy`, `height_policy`, `styles`. An anywidget that defines a trait named `width` or `height` would collide.
- Dynamic param addition on instances is fragile. Param Parameters are class-level descriptors. Using `param.parameterized.add_parameter()` at instance creation would work for param operations but would NOT update the `_data_model` (Bokeh DataModel), which is created at class definition time by the metaclass. The synced traits would be accessible as params but would NOT sync to the Bokeh frontend.
- To avoid the DataModel issue, we'd need to create a dynamic **class** per anywidget type and instantiate it. But panes are not typically the Bokeh model source themselves -- the pane wraps an internal component. Putting synced params on the pane AND having them sync through to the internal `AnyWidgetComponent` creates a confusing two-layer param system.

**Verdict: Not recommended as the primary approach due to name collisions and DataModel limitations.**

---

### Option B: Proxy via `.object` traitlets

Users access the traitlets directly on the wrapped anywidget: `pane.object.value`.

```python
pane = pn.pane.AnyWidget(widget)
pane.object.value = 42       # traitlet set
pane.object.observe(cb, names=['value'])  # traitlet observe
```

**Pros:**
- Zero abstraction: users work with the anywidget's native API
- No name collision issues
- No dynamic param creation needed

**Cons:**
- **Not Panel-idiomatic**: `pane.object.observe(...)` is the traitlets API, not `param.watch(...)` or `pn.bind(...)`. Users cannot use `pn.bind(fn, pane.object.value)` because `pane.object.value` is just a plain Python value, not a reactive reference.
- Cannot use `@param.depends`, `.rx`, `.link`, `jslink` or any Panel reactive primitive
- Inconsistent with every other Panel component
- Users must learn traitlets API alongside Panel API

**Verdict: Not recommended. Does not meet the goal of Panel-native reactivity.**

---

### Option C: Separate `.widget_params` namespace

A `param.Parameterized` sub-object holds the synced params:

```python
pane = pn.pane.AnyWidget(widget)
pane.widget_params.value          # param-backed value
pane.widget_params.param.value    # param.Parameter
pn.bind(fn, pane.widget_params.param.value)
```

**Pros:**
- Clean namespace separation: no collision with pane params
- Proper param.Parameters that work with all reactive primitives
- Could be a lightweight `param.Parameterized` instance without Bokeh model overhead

**Cons:**
- **Non-standard**: No other Panel component uses a `.widget_params` sub-object. Users must discover and learn this pattern.
- Verbose: `pane.widget_params.param.value` vs `pane.param.value`
- The sub-object's param changes still need to be wired to the internal `AnyWidgetComponent` and the anywidget traitlets. This creates a three-object sync chain (widget_params <-> AnyWidgetComponent <-> Bokeh model) which is complex.
- The sub-object is not itself a Viewable, so it cannot be linked directly with `.link()` or `.jslink()`.

**Verdict: Not recommended. Adds complexity and a non-standard pattern.**

---

### Option D: `.rx` accessor only

Provide reactive accessors like `pane.rx.value` without adding param Parameters:

```python
pane = pn.pane.AnyWidget(widget)
pane.rx.value      # reactive expression
```

**Pros:**
- Lightweight, no param Parameters needed

**Cons:**
- `.rx` in param/Panel is an accessor on existing `param.Parameter` objects (`pane.param.value.rx`). You cannot have `.rx` without having the underlying param Parameters. This option is not independently viable -- it requires one of the other options as a foundation.
- Even if we built a custom `.rx`-like accessor, it would not integrate with `param.watch`, `pn.bind`, `@param.depends`, `.link` etc.

**Verdict: Not viable as a standalone option. `.rx` is a consequence of having proper param Parameters, not a substitute.**

---

### Option E: Subclass pattern with `_anywidget_class`

Users define a Panel subclass that declares which anywidget to wrap:

```python
class MyMap(pn.pane.AnyWidget):
    _anywidget_class = lonboard.Map

map_widget = MyMap(center=[40.7, -74.0], zoom=10)
map_widget.param.watch(callback, ['zoom'])
pn.bind(fn, map_widget.param.center)
```

**Pros:**
- Truly Panel-native: the resulting class IS a Panel component with proper params
- Works with all reactive primitives
- Explicit, discoverable, typed
- Could auto-generate param Parameters from the anywidget's traitlets at class creation time

**Cons:**
- Requires an extra step: users must define a subclass before using the widget. This is burdensome for quick prototyping or one-off usage.
- Conflicts with the "wrap any object with `pn.panel(widget)`" pattern
- Cannot be used for dynamic/ad-hoc wrapping

**Verdict: Excellent for library authors who want to create reusable Panel-native wrappers, but too heavy for ad-hoc usage. Should be supported as an advanced pattern, not the primary API.**

---

### Option F: Expose the internal `AnyWidgetComponent` (Recommended)

The architecture report (architecture.md) establishes that the pane internally creates a dynamic `AnyWidgetComponent` subclass with proper param Parameters for each synced traitlet. This component IS a `Reactive` Panel component with a `_data_model` and full Bokeh sync.

Expose this component to users via `pane.component`:

```python
widget = SomeAnyWidget(value=10)
pane = pn.pane.AnyWidget(widget)

# Access the internal component with proper param Parameters
pane.component.value              # 10
pane.component.param.value        # param.Integer
pane.component.param.watch(cb, ['value'])
pn.bind(fn, pane.component.param.value)
pane.component.param.value.rx()   # reactive expression
```

**Pros:**
- **Full param/Panel integration**: The component is a real `Reactive` subclass. All param operations (`watch`, `bind`, `depends`, `rx`, `link`, `jslink`) work natively.
- **No name collisions**: The component's params are the anywidget's synced traits. The `AnyWidgetComponent` base class inherits from `ReactComponent` -> `ReactiveESM` -> `Reactive`, but its param namespace is explicitly constructed to include only the synced trait params (base Reactive params like `width`/`height` are excluded from `_data_model` by the metaclass ignore list). If a collision occurs with a base param (e.g. `name`), the component's `_data_model` construction already skips `name`. For others like `width`/`height`, they can be prefixed (see Section 3).
- **Consistent with architecture**: The component already exists internally for rendering. Exposing it is zero-cost.
- **Bidirectional sync already handled**: The sync report (sync.md) describes traitlet <-> param <-> Bokeh sync. The component's params ARE the sync target. No extra sync layer needed -- the pane sets up traitlet <-> component.param sync, and the component's existing Syncable machinery handles param <-> Bokeh.
- **Lightweight for users**: `pane.component.value` is only slightly more verbose than `pane.value`, and it makes the mental model clear: the pane wraps the component, the component has the params.

**Cons:**
- One level of indirection: `pane.component.value` vs `pane.value`
- Users need to know about `.component`
- The component is a dynamically-created class, so IDE autocompletion won't show its params

**Verdict: Recommended. Best balance of correctness, ergonomics, and simplicity.**

---

## 3. Name Collision Resolution Strategy

### The Collision Problem

The `AnyWidgetComponent` base class inherits from `ReactComponent` -> `ReactiveESM` -> `Reactive` -> `Syncable` -> `Viewable` -> `Layoutable`. The inherited param names include:

**From Layoutable**: `align`, `aspect_ratio`, `css_classes`, `design`, `height`, `margin`, `max_height`, `max_width`, `min_height`, `min_width`, `sizing_mode`, `styles`, `stylesheets`, `tags`, `visible`, `width`, `width_policy`, `height_policy`

**From Reactive/Syncable**: `loading`, `name`

**From ReactiveESM**: (none that users would define)

If an anywidget defines a trait called `width`, `height`, `name`, `margin`, or `loading`, it collides with an inherited param.

### Resolution: Prefix Colliding Names

When constructing the dynamic `AnyWidgetComponent` subclass, detect collisions and prefix the anywidget's trait with `w_`:

```python
RESERVED_PARAMS = set(AnyWidgetComponent.param) | {'name', 'object'}

def _resolve_param_name(trait_name: str) -> str:
    """Resolve trait name to param name, avoiding collisions."""
    if trait_name in RESERVED_PARAMS:
        return f'w_{trait_name}'
    return trait_name
```

This means:
- `widget.value` -> `component.value` (no collision, identity mapping)
- `widget.width` -> `component.w_width` (collision with Layoutable.width)
- `widget.height` -> `component.w_height` (collision with Layoutable.height)
- `widget.name` -> `component.w_name` (collision with Parameterized.name)

The pane maintains a `_trait_to_param` mapping for bidirectional sync:

```python
# If anywidget has traits: value, width, zoom
_trait_to_param = {
    'value': 'value',
    'width': 'w_width',   # collided, prefixed
    'zoom': 'zoom',
}
```

### Why `w_` Prefix?

- Short and mnemonic: "w" for "widget"
- Unlikely to collide with real trait names (anywidgets almost never prefix with `w_`)
- Clear signal that renaming happened

### Collision Frequency in Practice

In practice, collisions are **rare**. The most common anywidget trait names are domain-specific (`value`, `data`, `center`, `zoom`, `layers`, `spec`, `config`). The `width`/`height` collision is the most likely, and some anywidgets do use these (e.g., widgets that size themselves). The prefix strategy handles this gracefully.

---

## 4. Ergonomic Code Examples

### Setup

```python
import panel as pn
import param

# Assume SomeAnyWidget has: value=Int, label=Unicode, data=Dict (all sync=True)
widget = SomeAnyWidget(value=10, label="Hello", data={"key": "val"})
pane = pn.pane.AnyWidget(widget)
```

### 4.1 `pn.bind` — Bind a function to a trait-backed param

```python
def on_value_change(value):
    return f"Value is now: {value}"

# Bind to the component's param
display = pn.bind(on_value_change, pane.component.param.value)
pn.Column(pane, display).servable()
```

### 4.2 `@param.depends` — Decorator-based reactivity

```python
class Dashboard(pn.Viewable):
    def __init__(self, anywidget):
        self.pane = pn.pane.AnyWidget(anywidget)
        super().__init__()

    @param.depends('pane.component.value')
    def status(self):
        return pn.pane.Markdown(f"## Current value: {self.pane.component.value}")
```

### 4.3 `.rx` — Reactive expressions

```python
# Create a reactive expression from the param
value_rx = pane.component.param.value.rx()

# Transform reactively
doubled = value_rx * 2
label = value_rx.rx.pipe(lambda v: f"Value: {v}")

# Use in Panel layout
pn.Column(
    pane,
    pn.pane.Str(doubled),
    pn.pane.Markdown(label),
).servable()
```

### 4.4 `.link` — Link two components

```python
# Link anywidget's value to a Panel widget
slider = pn.widgets.IntSlider(name="Mirror", start=0, end=100)
pane.component.link(slider, value='value')

# Or link two anywidget panes
pane1 = pn.pane.AnyWidget(widget1)
pane2 = pn.pane.AnyWidget(widget2)
pane1.component.link(pane2.component, value='value')
```

### 4.5 `param.watch` — Explicit callback

```python
def on_change(*events):
    for event in events:
        print(f"{event.name}: {event.old} -> {event.new}")

pane.component.param.watch(on_change, ['value', 'label'])
```

### 4.6 Direct attribute access

```python
# Read
current_value = pane.component.value

# Write (propagates to traitlet AND to browser)
pane.component.value = 42
```

### 4.7 Subclass pattern (`_anywidget_class`) for reusable wrappers

```python
class PanelMap(pn.pane.AnyWidget):
    """A Panel-native wrapper for lonboard.Map."""
    _anywidget_class = lonboard.Map

# Now PanelMap auto-generates params from lonboard.Map's synced traitlets.
# The dynamic AnyWidgetComponent is created at class definition time.
map_widget = PanelMap(center=[40.7, -74.0], zoom=10)
map_widget.component.param.watch(cb, ['zoom'])

# Or even shorter -- the subclass pattern could forward params to component:
map_widget = PanelMap(center=[40.7, -74.0], zoom=10)
# zoom is forwarded to component.zoom at init time
```

---

## 5. Comparison with Existing Patterns

### 5.1 `IPyWidget` Pane (`panel/pane/ipywidget.py`)

The current `IPyWidget` pane does **not** expose traits as params. It uses `ipywidgets_bokeh` to serialize the entire widget state and render it via the ipywidgets JS runtime. The only reactive bridge is `_ipywidget_transform()` (line 128-143), which:
- Creates a one-way traitlet -> param sync for `.value` only
- Uses `param.parameterized_class()` to create a throwaway Parameterized with a single `value` param
- Only activated when an ipywidget is used as a param reference

This is very limited: only `value`, only one-way, no `param.watch`/`pn.bind` support on arbitrary traits.

**Our AnyWidget pane is a significant upgrade**: full bidirectional sync on ALL synced traits, proper param Parameters, full reactive integration.

### 5.2 Native Panel `Widget` (`panel/widgets/base.py`)

Native widgets define params directly on the class:

```python
class IntSlider(Widget):
    value = param.Integer(default=0)
    start = param.Integer(default=0)
    end = param.Integer(default=10)
```

Users interact via `slider.value`, `slider.param.value`, `slider.param.watch(...)`, etc. The `_data_model` and `_link_props` handle bidirectional Bokeh sync.

**Our component's interface mirrors this exactly**: `pane.component.value`, `pane.component.param.value`, etc. The only difference is the `.component` indirection.

### 5.3 `AnyWidgetComponent` — User-defined (`panel/custom.py`)

Users define their own `AnyWidgetComponent` subclasses with explicit param declarations:

```python
class CounterWidget(pn.custom.AnyWidgetComponent):
    _esm = """..."""
    value = param.Integer()
```

These work identically to native widgets: `counter.value`, `counter.param.value`, etc. The `ReactiveESMMetaclass` creates the `_data_model` automatically.

**Our dynamic subclass reuses this exact mechanism**: we programmatically create what the user would manually define. The pane's `.component` IS an `AnyWidgetComponent` instance.

---

## 6. Implementation Sketch

### 6.1 Dynamic Class Creation

```python
from panel.custom import AnyWidgetComponent

_ANYWIDGET_CLASS_CACHE: dict[type, type[AnyWidgetComponent]] = {}

RESERVED_PARAMS = set(AnyWidgetComponent.param) | {'name', 'object'}

EXCLUDED_TRAITS = {
    '_model_name', '_model_module', '_model_module_version',
    '_view_name', '_view_module', '_view_module_version',
    '_dom_classes', '_view_count',
    '_esm', '_css', '_anywidget_id',
}

def _get_or_create_component_class(anywidget_cls):
    """Create a dynamic AnyWidgetComponent subclass for the given anywidget class."""
    if anywidget_cls in _ANYWIDGET_CLASS_CACHE:
        return _ANYWIDGET_CLASS_CACHE[anywidget_cls]

    # Extract ESM and CSS
    esm = str(getattr(anywidget_cls, '_esm', '') or '')
    css = getattr(anywidget_cls, '_css', None)
    if css:
        css = str(css)

    # Build param dict from synced traitlets
    sync_traits = anywidget_cls.class_traits(sync=True)
    params = {}
    trait_to_param = {}

    for trait_name, trait in sync_traits.items():
        if trait_name in EXCLUDED_TRAITS or trait_name.startswith('_'):
            continue
        param_name = trait_name if trait_name not in RESERVED_PARAMS else f'w_{trait_name}'
        param_obj = traitlet_to_param(trait_name, trait)  # from traitlet-mapping.md
        params[param_name] = param_obj
        trait_to_param[trait_name] = param_name

    class_dict = {
        '_esm': esm,
        '_trait_to_param_map': trait_to_param,
        **params,
    }
    if css:
        class_dict['_stylesheets'] = [css]

    panel_cls = type(
        anywidget_cls.__name__,
        (AnyWidgetComponent,),
        class_dict,
    )
    _ANYWIDGET_CLASS_CACHE[anywidget_cls] = panel_cls
    return panel_cls
```

### 6.2 The Pane Class

```python
class AnyWidget(Pane):
    """
    Renders anywidget instances natively in Panel with full param reactivity.

    Access the widget's synced traits as param Parameters via `pane.component`:

        pane = pn.pane.AnyWidget(some_anywidget)
        pane.component.value              # read trait value
        pane.component.value = 42         # write (syncs to traitlet + browser)
        pane.component.param.watch(cb, ['value'])
        pn.bind(fn, pane.component.param.value)
    """

    priority: ClassVar[float | bool | None] = 0.8

    _updates: ClassVar[bool] = True

    component = param.ClassSelector(
        class_=AnyWidgetComponent, constant=True, doc="""
        The internal AnyWidgetComponent instance with param Parameters
        for each synced traitlet. Use this for reactive operations.""")

    def __init__(self, object=None, **params):
        self._trait_changing: list[str] = []
        self._trait_watchers: list = []
        super().__init__(object=object, **params)
        if self.object is not None:
            self._initialize_component(self.object)

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if not (hasattr(obj, 'traits') and hasattr(obj, 'comm')):
            return False
        return hasattr(type(obj), '_esm')

    def _initialize_component(self, widget):
        """Create the internal AnyWidgetComponent and wire up sync."""
        panel_cls = _get_or_create_component_class(type(widget))

        # Initialize component with current traitlet values
        trait_to_param = panel_cls._trait_to_param_map
        init_values = {}
        for trait_name, param_name in trait_to_param.items():
            init_values[param_name] = getattr(widget, trait_name)

        with param.edit_constant(self):
            self.component = panel_cls(**init_values)

        self._setup_trait_sync(widget)

    def _setup_trait_sync(self, widget):
        """Bidirectional sync: traitlet <-> component.param."""
        trait_to_param = self.component._trait_to_param_map

        # Traitlet -> param
        for trait_name in trait_to_param:
            widget.observe(self._cb_traitlet, names=[trait_name])
            self._trait_watchers.append((widget, trait_name))

        # Param -> traitlet
        param_names = list(trait_to_param.values())
        if param_names:
            watcher = self.component.param.watch(self._cb_param, param_names)
            self._trait_watchers.append(('param', watcher))

    def _cb_traitlet(self, change):
        """Traitlet -> component.param with recursion guard."""
        name = change['name']
        if name in self._trait_changing:
            return
        param_name = self.component._trait_to_param_map.get(name)
        if param_name is None:
            return
        try:
            self._trait_changing.append(name)
            self.component.param.update(**{param_name: change['new']})
        finally:
            if name in self._trait_changing:
                self._trait_changing.remove(name)

    def _cb_param(self, *events):
        """Component.param -> traitlet with recursion guard."""
        param_to_trait = {v: k for k, v in self.component._trait_to_param_map.items()}
        for event in events:
            trait_name = param_to_trait.get(event.name)
            if trait_name is None or trait_name in self._trait_changing:
                continue
            try:
                self._trait_changing.append(trait_name)
                setattr(self.object, trait_name, event.new)
            finally:
                if trait_name in self._trait_changing:
                    self._trait_changing.remove(trait_name)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """Delegate rendering to the internal component."""
        model = self.component._get_model(doc, root, parent, comm)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _teardown_trait_sync(self):
        for item in self._trait_watchers:
            if item[0] == 'param':
                self.component.param.unwatch(item[1])
            else:
                widget, trait_name = item
                try:
                    widget.unobserve(self._cb_traitlet, names=[trait_name])
                except Exception:
                    pass
        self._trait_watchers.clear()
        self._trait_changing.clear()

    def _cleanup(self, root=None):
        super()._cleanup(root)
        if not self._models:
            self._teardown_trait_sync()
```

### 6.3 Rendering Flow

```
pn.pane.AnyWidget(widget)
    |
    v
_get_or_create_component_class(type(widget))
    |-- Extract _esm, _css from anywidget class
    |-- Map synced traitlets to param Parameters (with collision resolution)
    |-- type('WidgetName', (AnyWidgetComponent,), {...})
    |       -> ReactiveESMMetaclass.__init__ runs
    |       -> _data_model created with Bokeh properties
    v
component = DynamicClass(**trait_values)
    |
    v
_setup_trait_sync(widget)
    |-- widget.observe(cb, names=[...])     # traitlet -> param
    |-- component.param.watch(cb, [...])    # param -> traitlet
    v
_get_model(doc, root, parent, comm)
    |-- component._get_model(...)           # AnyWidgetComponent renders
    |       -> Creates Bokeh AnyWidgetComponent model
    |       -> _link_props wires param <-> Bokeh model
    v
Three-way sync active:
    traitlet <-> component.param <-> Bokeh model <-> browser JS
```

---

## 7. Convenience: `__getattr__` Forwarding (Optional Enhancement)

For ergonomics, the pane could forward attribute access to the component for synced trait params:

```python
def __getattr__(self, name):
    # Only forward if component exists and name is a synced param
    component = self.__dict__.get('component')
    if component is not None and name in getattr(component, '_trait_to_param_map', {}).values():
        return getattr(component, name)
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

def __setattr__(self, name, value):
    component = self.__dict__.get('component')
    if component is not None and name in getattr(component, '_trait_to_param_map', {}).values():
        setattr(component, name, value)
        return
    super().__setattr__(name, value)
```

This would allow `pane.value` as a shortcut for `pane.component.value`. However:

- **Risk**: Attribute forwarding can be confusing when names partially overlap with pane params. If a user does `pane.width`, should they get the pane's layout width or the forwarded anywidget trait?
- **Recommendation**: Do NOT add `__getattr__` forwarding in the initial implementation. Keep the explicit `.component` access. If user feedback indicates the indirection is too verbose, add forwarding later with clear collision rules.

---

## 8. Summary

### Recommended Approach: Option F (Expose Internal Component)

| Aspect | Decision |
|--------|----------|
| Primary access | `pane.component.value`, `pane.component.param.value` |
| Reactive primitives | All work: `param.watch`, `pn.bind`, `@param.depends`, `.rx`, `.link` |
| Name collisions | Prefix with `w_` for colliding trait names |
| Architecture | Dynamic `AnyWidgetComponent` subclass (per architecture.md) |
| Sync | Traitlet <-> component.param bidirectional (per sync.md) |
| Advanced pattern | Subclass with `_anywidget_class` for reusable wrappers (Option E) |
| `__getattr__` forwarding | Deferred -- not in initial implementation |

### Why Not the Others

| Option | Why not |
|--------|---------|
| A (direct params on pane) | Name collisions; DataModel mismatch; confusing two-layer sync |
| B (proxy via .object) | Not Panel-idiomatic; no reactive primitive support |
| C (separate .widget_params) | Non-standard pattern; verbose; complex sync chain |
| D (.rx only) | Not independently viable; requires underlying params |
| E (subclass only) | Too heavy for ad-hoc use; good as secondary pattern |

---

## 9. Revised Name Collision Analysis

### 9.1 The Question

The current proposal (Section 3) uses `w_` prefixing for colliding trait names. Can we do better? This section evaluates three alternative strategies in depth and provides a revised recommendation.

### 9.2 Full Inventory of Collision-Prone Params

The `AnyWidgetComponent` inherits from `ReactComponent` -> `ReactiveESM` -> `Reactive` -> `Syncable` -> `Viewable` -> `Layoutable`. The complete set of inherited params that an anywidget trait could collide with:

**From `Layoutable`** (CSS layout sizing):
`align`, `aspect_ratio`, `css_classes`, `design`, `height`, `margin`, `max_height`, `max_width`, `min_height`, `min_width`, `sizing_mode`, `styles`, `stylesheets`, `tags`, `visible`, `width`, `width_policy`, `height_policy`

**From `Viewable`**: `loading`

**From `param.Parameterized`**: `name`

**From `ReactComponent`**: `use_shadow_dom`

Total: 21 reserved names.

### 9.3 Real-World Collision Frequency

Examining popular anywidget-based packages:

| Package | Colliding Synced Traits | Non-colliding Synced Traits |
|---------|------------------------|-----------------------------|
| **drawdata** `ScatterWidget` | `width`, `height` | `data`, `brushsize`, `n_classes` |
| **drawdata** `BarWidget` | `width`, `height` | `data`, `y_min`, `y_max`, `n_bins`, `collection_names` |
| **lonboard** `Map` | `height` | `view_state`, `layers`, `controls`, `show_tooltip`, `picking_radius`, `basemap`, `selected_bounds`, etc. |

**Conclusion**: Collisions are **not rare**. The `width`/`height` collision is a real, recurring problem. The `drawdata` package -- a popular anywidget -- uses both `width` and `height` as synced traits to control canvas rendering dimensions, which is entirely unrelated to CSS layout sizing.

The `name`, `loading`, `visible`, `tags`, `styles`, `margin`, and `css_classes` collisions are less likely in practice but possible for domain-specific widgets.

### 9.4 Strategy A: Sync with the Existing Inherited Param (Override Approach)

**Idea**: When an anywidget defines `width = traitlets.Int().tag(sync=True)`, simply override the inherited `Layoutable.width` param with a new `param.Integer()` on the dynamic subclass, and let the anywidget's width sync through that param.

**Investigation results**:

1. **Metaclass behavior**: When we define `width = param.Integer(default=500)` on a dynamic `AnyWidgetComponent` subclass, the `ReactiveESMMetaclass.__init__` correctly detects that the param's owner is the new subclass (which IS a `ReactiveESMMetaclass` instance). This means `width` is NOT in the metaclass `ignored` list and IS included in the `_data_model`. This works at class creation time.

2. **`_get_properties` double-ignore problem**: The `ReactiveESM._get_properties()` method (custom.py lines 463-468) has a **second** ignore check:

   ```python
   ignored = [
       p for p in Reactive.param
       if not issubclass(cls.param[p].owner, ReactiveESM) or
       (p in Viewable.param and p not in ('name', 'use_shadow_dom')
        and type(Reactive.param[p]) is type(cls.param[p]))
   ]
   ```

   The second condition checks whether the **param type** is the same as the inherited one. Since both `Layoutable.width` and our override are `param.Integer`, the type IS the same, so `width` is still ignored. This means `width` would be included in `_data_model` at class creation time but then **excluded from the data props** at render time. The value would never reach the frontend data model.

3. **Type mismatch workaround**: If we use a *different* param type (e.g., `param.Number` instead of `param.Integer`), the type check fails and `width` would be included in data props. But this is a fragile hack -- it depends on internal type comparison logic.

4. **`_update_model` routing problem**: Even if we solved the `_get_properties` issue, the `_update_model` method (custom.py line 596-598) routes updates based on whether the prop name is in `Reactive.param`:

   ```python
   if prop in list(Reactive.param)+['esm', 'importmap']:
       model_msg[prop] = v  # Goes to outer Bokeh model (CSS layout)
   else:
       data_msg[prop] = v  # Goes to inner data model (ESM widget)
   ```

   Since `width` IS in `Reactive.param`, runtime changes to `width` would be sent to the **Bokeh LayoutDOM model** (controlling CSS layout), NOT to the inner data model (where the ESM widget reads it). The anywidget's JavaScript would never see the update.

5. **Semantic confusion**: `Layoutable.width` controls CSS sizing of the Bokeh component container. An anywidget's `width` (e.g., `drawdata.ScatterWidget.width`) controls the canvas rendering width inside the widget. These are fundamentally different things. Setting `component.width = 800` should set the canvas width, not the CSS container width. But with a shared param, both would change simultaneously, leading to unpredictable layout behavior.

**Verdict: Not viable.** The `_get_properties` double-ignore and `_update_model` routing logic both hardcode `Reactive.param` names as "outer model" properties. Overriding them does not redirect their sync path to the data model. Fixing this would require non-trivial changes to `ReactiveESM._get_properties` and `_update_model`, and would still create semantic confusion.

### 9.5 Strategy B: Prefix ALL Anywidget Params

**Idea**: Instead of selective prefixing, prefix ALL anywidget trait params with a namespace like `widget_` or `w_` (e.g., `widget_value`, `widget_width`, `widget_zoom`).

**Evaluation**:

| Aspect | Assessment |
|--------|-----------|
| Collision safety | Excellent -- complete namespace isolation |
| Verbosity | Bad for common case. `pane.component.widget_value` is verbose compared to `pane.component.value`. Every user pays the verbosity cost even though most traits do not collide. |
| Consistency with Panel UX | Poor. Native Panel widgets use `slider.value`, not `slider.widget_value`. The `component` indirection already provides namespace isolation; adding a prefix on top is double-namespacing. |
| Predictability | Good -- users always know the naming rule |
| Precedent | No Panel precedent. No significant Python GUI framework uses universal prefixing for wrapped widget params. |

**Verdict: Not recommended.** The verbosity cost is too high for the common case. The `pane.component` level already provides sufficient namespace isolation for most traits. Universal prefixing optimizes for the rare collision case at the expense of everyday ergonomics.

### 9.6 Strategy C: Use `_property_mapping` to Disconnect Inherited Params

**Idea**: Set `_rename = {'width': None, 'height': None, ...}` on the dynamic subclass to disconnect inherited Layoutable params from the Bokeh model, then override them with new params that sync to the data model.

**Investigation results**:

The `construct_data_model` function (datamodel.py line 186-189) applies `_property_mapping` to remap param names:

```python
if isinstance(parameterized, Syncable) or ...:
    pname = parameterized._property_mapping.get(pname, pname)
if pname == 'name' or pname is None:
    continue
```

If `_property_mapping['width'] = None`, then `pname` becomes `None`, and the param is **skipped entirely** from the data model. This means `_rename = {'width': None}` excludes `width` from BOTH the Bokeh layout model AND the data model. The param would exist on Python but never sync to the frontend at all.

**Verdict: Not viable.** `_property_mapping` is not granular enough to say "disconnect from outer model but keep in data model." It is a single mapping that controls both.

### 9.7 Strategy D: Separate Namespace via `_property_mapping` Rename

**Idea**: Instead of `None`, rename the param in the data model to avoid collision: `_rename = {'width': 'widget_width'}`. This would map the Python param `width` to a Bokeh property named `widget_width`.

**Investigation**: This would create `model.data.widget_width` on the Bokeh side. But the `_update_model` routing still checks `prop in list(Reactive.param)`, so the Python param `width` would still be routed to the outer Bokeh model, not the data model. The rename only affects the property name on the Bokeh side, not the routing logic.

**Verdict: Not viable** for the same routing reason as Strategy A.

### 9.8 Why `w_` Prefixing (Section 3 Proposal) Is Actually the Right Approach

After thorough investigation, the `w_` prefix strategy from Section 3 is the correct approach because it works *with* the existing architecture rather than against it:

1. **Clean routing**: A param named `w_width` is NOT in `Reactive.param`, so `_update_model` correctly routes it to the data model (`data_msg`).

2. **Clean data model inclusion**: `w_width` is not in the metaclass `ignored` list (since its owner is the dynamic subclass), and it passes the `_get_properties` type check (since there is no `Reactive.param['w_width']` to compare against).

3. **No Bokeh layout interference**: `w_width` does not exist on the Bokeh `LayoutDOM` model, so there is no collision at the Bokeh property level.

4. **The Layoutable params remain functional**: Users can still control the CSS layout of the anywidget component via `component.width` (the Layoutable param) while the anywidget's internal width is available as `component.w_width`.

### 9.9 Refinements to the `w_` Strategy

While the `w_` prefix is architecturally correct, there are improvements we can make:

#### 9.9.1 Minimize collision set

Not all 21 inherited params are equally likely to collide. We should only prefix when there is an ACTUAL collision -- i.e., when the anywidget class actually defines a synced trait with that name. The current proposal already does this (Section 3's `_resolve_param_name` only prefixes if `trait_name in RESERVED_PARAMS`). This is correct.

#### 9.9.2 Discoverability: `_trait_to_param` mapping

Users need to know when a prefix was applied. The `_trait_to_param_map` on the component class (Section 6.1) provides this. Additionally, we should:

- Log a warning when a collision is resolved: `"AnyWidget trait 'width' renamed to 'w_width' to avoid collision with Panel's Layoutable.width (CSS layout sizing)"`
- Provide a `.trait_params` property or method that returns the mapping for inspection:

```python
>>> pane.component.trait_params
{'value': 'value', 'width': 'w_width', 'height': 'w_height', 'zoom': 'zoom'}
```

#### 9.9.3 Alternative prefix: consider `aw_`

The `w_` prefix is short but could be confused with "width" in some contexts. Consider `aw_` ("anywidget") as an alternative:

| Prefix | Example | Mnemonic | Length | Risk of confusion |
|--------|---------|----------|--------|-------------------|
| `w_`   | `w_width` | "widget" | short | moderate -- "w_width" might be read as "w width" |
| `aw_`  | `aw_width` | "anywidget" | medium | low |
| `trait_` | `trait_width` | "trait" | long | low |

Recommendation: **Keep `w_`**. It is short, and the confusion risk is mitigated by the warning message and the `_trait_to_param_map` introspection.

#### 9.9.4 Consider `__getattr__` forwarding with original names

For the case where users want to use the original trait name, the pane could support a `__getattr__` fallback that maps the original trait name through to the component:

```python
# On the pane, not the component:
pane.width      # Layoutable width (CSS)
pane["width"]   # Anywidget trait value (could use __getitem__)
```

However, this adds API surface and complexity. Defer this to a future enhancement based on user feedback.

### 9.10 Summary and Recommendation

| Strategy | Viable? | Why |
|----------|---------|-----|
| Override inherited param | No | `_get_properties` double-ignore and `_update_model` routing both prevent data model sync |
| `_property_mapping = None` | No | Excludes param from both outer model AND data model |
| `_property_mapping` rename | No | `_update_model` routing still sends to outer model |
| Prefix ALL params | Yes but bad UX | Double-namespacing; verbosity penalty for every user |
| **Selective `w_` prefix** | **Yes** | Works with architecture; minimal UX impact; only affects colliding names |

**Final recommendation: Keep the `w_` prefix strategy from Section 3**, with the following refinements:

1. Only prefix when there is an actual collision (already proposed).
2. Emit a clear warning message when a collision is resolved.
3. Expose the trait-to-param mapping via `component.trait_params` for discoverability.
4. Document the collision strategy clearly in the `AnyWidget` pane docstring and reference docs.

The key insight from this analysis is that the "just sync the existing param" approach **cannot work** without significant refactoring of `ReactiveESM._get_properties()` and `_update_model()`, because those methods use hardcoded checks against `Reactive.param` to determine whether a property belongs to the outer Bokeh model (CSS layout) or the inner data model (ESM widget). The `w_` prefix sidesteps this entirely by creating a new param name that the existing routing logic correctly identifies as a data model property.

---

## 10. Typing and Language Server Discoverability

### 10.1 The Problem

The AnyWidget pane dynamically creates `AnyWidgetComponent` subclasses via `type('Name', (AnyWidgetComponent,), {params...})`. These dynamic classes have `param.Parameter` descriptors for each synced traitlet. Users access them via `pane.component.value`, `pane.component.param.value`, etc.

**The problem: dynamic classes have no static type information.** IDEs (VS Code, PyCharm), language servers (Pylance, Pyright, mypy), and autocomplete systems cannot discover the params on these classes. This significantly impacts developer experience for the recommended `pane.component.value` access pattern.

### 10.2 Current State of Typing in param and Panel

#### 10.2.1 param's `__signature__` Support

The `ParameterizedMetaclass` defines a `__signature__` property (in `parameterized.py`, line 3586-3616) that dynamically generates an `inspect.Signature` from the class's Parameters. This works correctly even for dynamically created classes:

```python
DynClass = type('DynClass', (AnyWidgetComponent,), {
    'value': param.Integer(default=0),
    'data': param.Dict(default={}),
})
inspect.signature(DynClass)
# => (*, data, value, use_shadow_dom, loading, align, ..., name)
```

**Critical limitation:** Pyright/Pylance **do not use PEP 362 `__signature__`** for type inference. Pyright is a fully static analyzer -- it never instantiates classes or evaluates runtime properties. The runtime signature is useful for IPython/Jupyter `?` help and `inspect.signature()` calls, but it provides **zero benefit** for IDE autocomplete or type checking.

Reference: [holoviz/param#587](https://github.com/holoviz/param/issues/587) -- "Pyright does not instantiate classes to inspect them. It uses static analysis only."

#### 10.2.2 param Has No `.pyi` Stubs or `py.typed` Marker

The `param` package has neither `.pyi` stub files nor a `py.typed` PEP 561 marker. This means type checkers rely entirely on the inline Python source, which does not use type annotations for Parameters. The `param.Parameterized.__init__` signature is `def __init__(self, **params)`, which tells type checkers nothing about accepted keyword arguments.

#### 10.2.3 Panel Has `py.typed` But No `.pyi` Stubs

Panel declares `py.typed` (indicating inline typing support) but has no `.pyi` stub files. Panel's classes use `from __future__ import annotations` and have some type annotations in method signatures, but param Parameters themselves remain opaque to static analysis.

#### 10.2.4 `construct_data_model()` Does Not Produce Typed Results

The `construct_data_model()` function in `panel/io/datamodel.py` dynamically creates Bokeh `DataModel` subclasses using `type(name, (DataModel,), properties)`. Like the `AnyWidgetComponent` dynamic classes, these have no static type information.

#### 10.2.5 `param.parameterized_class()` in `ipywidget.py`

The `_ipywidget_transform` function in `panel/pane/ipywidget.py` (line 139) uses `param.parameterized_class(name, {'value': param.Parameter()})` to create a throwaway Parameterized class. This is similarly untyped.

### 10.3 Why Static Type Checkers Cannot See Dynamic Attributes

Static type checkers (Pyright, mypy, Pylance) operate on the **source text** of Python files. They parse the AST, resolve imports, and trace type annotations. They fundamentally **cannot** analyze:

1. **`type()` calls** that create classes at runtime -- the fields are only known when the code executes.
2. **Runtime `__signature__` properties** -- these are evaluated by calling Python code, which static analyzers do not do.
3. **`__annotations__` set at runtime** -- type checkers read annotations from the AST, not from runtime attribute lookup.
4. **`__getattr__` / `__getitem__` forwarding** -- type checkers can partially model `__getattr__` (returning `Any`), but cannot determine specific attribute names or types.

This is a **fundamental limitation of static analysis**, not a bug or missing feature. Any library that creates classes dynamically (pydantic's `create_model`, SQLAlchemy's dynamic mappers, Django's ORM metaclass magic) faces the same constraint.

### 10.4 Approaches Evaluated

#### 10.4.1 Approach A: `dataclass_transform` (PEP 681)

**How it works:** PEP 681 introduced `@typing.dataclass_transform()`, which can be applied to a metaclass, base class, or decorator function. When applied, type checkers treat classes using that metaclass/base as dataclass-like, recognizing annotated class variables as fields and synthesizing `__init__` signatures.

**Applicability to param:**

`dataclass_transform` requires fields to be declared with **PEP 526 type annotations**:

```python
# This is what dataclass_transform expects:
class Foo(Base):
    x: int = field(default=0)

# This is what param uses:
class Foo(param.Parameterized):
    x = param.Integer(default=0)  # NO type annotation
```

Type checkers only recognize fields that have `name: type` annotations. Bare assignments like `x = param.Integer(default=0)` are invisible to `dataclass_transform`. This is a **fundamental incompatibility** with param's current API.

**For AnyWidgetComponent subclasses specifically:** Even if we applied `@dataclass_transform(field_specifiers=(param.Parameter,))` to `ReactiveESMMetaclass`, the dynamically created classes would not have type annotations on their fields (since we add params via `type(name, bases, {'value': param.Integer()})`, not `value: int = param.Integer()`).

**For manual subclasses** (the `class MyMap(pn.pane.AnyWidget)` pattern), users could theoretically add type annotations alongside the dynamically-added params. But this requires duplicating type information that already exists in the anywidget's traitlets -- a poor user experience.

**Upstream dependency:** Full `dataclass_transform` support would need to be implemented in `param` itself, which is tracked as a wishlist item: [holoviz/param#587](https://github.com/holoviz/param/issues/587) and [holoviz/param#376](https://github.com/holoviz/param/issues/376). This is a significant undertaking that would likely require param users to adopt annotation-based field declarations.

**Verdict: Not viable for dynamically created classes. Potentially useful long-term if param adopts annotation-based field declarations, but this is a param-level concern, not an AnyWidget pane concern.**

#### 10.4.2 Approach B: `.pyi` Stub Files

**How it works:** Stub files (`.pyi`) provide static type information separate from runtime code. Type checkers prioritize `.pyi` files over `.py` files. A stub for the dynamic component could declare attributes with proper type annotations.

**Example stub for a hypothetical lonboard wrapper:**

```python
# panel/pane/anywidget.pyi (or panel-stubs/pane/anywidget.pyi)
from typing import Any
from panel.custom import AnyWidgetComponent

class MapComponent(AnyWidgetComponent):
    view_state: dict
    layers: list
    height: int
    show_tooltip: bool
    picking_radius: int

    def __init__(
        self,
        *,
        view_state: dict = ...,
        layers: list = ...,
        height: int = ...,
        show_tooltip: bool = ...,
        picking_radius: int = ...,
        **kwargs: Any,
    ) -> None: ...
```

**Challenges:**

1. **Stubs must be pre-generated for each anywidget class.** Since the component class is created dynamically based on the specific anywidget being wrapped, a single `.pyi` file cannot cover all possible anywidgets.
2. **Maintenance burden:** Stubs must be updated whenever the anywidget package updates its traitlets.
3. **Distribution:** Stubs would need to be in a separate `panel-stubs` package or bundled with each anywidget package.

**Possible implementation: stub generation CLI tool:**

```bash
# Generate stubs for popular anywidget packages
panel generate-stubs lonboard ipyleaflet drawdata
# Outputs: panel/pane/_anywidget_stubs/lonboard.pyi, etc.
```

The traitlet-to-Python-type mapping is straightforward:

| Traitlet Type | Python Type |
|---------------|-------------|
| `Int` / `Integer` | `int` |
| `Float` | `float` |
| `Bool` | `bool` |
| `Unicode` | `str` |
| `Bytes` | `bytes` |
| `List` | `list` |
| `Dict` | `dict` |
| `Tuple` | `tuple` |
| `Set` | `set` |
| `Any` | `Any` |
| `Instance(Cls)` | `Cls` |

**Verdict: Technically viable for known popular anywidgets. High maintenance burden. Best suited as a community-contributed package or a code generation tool, not a core Panel feature.**

#### 10.4.3 Approach C: `__init__` Signature Rewriting

**How other libraries do it:**

- **`attrs` and `dataclasses`**: These work because they process classes at **definition time** via decorators or metaclasses. The decorator/metaclass synthesizes an `__init__` method with explicit parameter annotations. Type checkers see these annotations in the source code (or via `dataclass_transform`). This is **not** the same as runtime `__signature__` -- the actual `__init__` function exists in the source with proper annotations.

- **Pydantic**: Uses `@dataclass_transform()` on `ModelMetaclass` so that Pyright treats `BaseModel` subclasses as dataclass-like. For `create_model()` (the dynamic equivalent), typing **does not work** -- the return type is just `type[ModelT]` and Pyright cannot see the fields. This is the exact same limitation we face.

**Could we rewrite `__init__` on the dynamic class?**

We could generate an `__init__` method with explicit parameter annotations:

```python
def make_init(param_names, param_types):
    # Build a function with typed parameters
    params_str = ', '.join(f'{n}: {t.__name__} = ...' for n, t in zip(param_names, param_types))
    code = f'def __init__(self, *, {params_str}, **kwargs): super().__init__(**kwargs)'
    exec(code)
    ...
```

**But this does not help type checkers.** Pyright analyzes source code, not runtime-generated functions. An `__init__` created via `exec()` or dynamically constructed is invisible to static analysis. The `__init__` would need to be in a `.py` file or `.pyi` stub to be visible.

**Verdict: Not viable for dynamic classes. Only works when the `__init__` exists in parseable source code.**

#### 10.4.4 Approach D: `Generic[T]` Type Parameter

**Idea:** Use `AnyWidgetPane[SomeAnyWidgetClass]` as a generic to carry the widget type:

```python
T = TypeVar('T')

class AnyWidgetPane(PaneBase, Generic[T]):
    object: T
    component: AnyWidgetComponent  # Still untyped for specific params
```

**Limitation:** `Generic[T]` preserves the **widget type** but does not expose the widget's **attributes** on `.component`. The component is a dynamically created `AnyWidgetComponent` subclass, and its params cannot be derived from `T` by a static type checker. `Generic[T]` would only help if someone wanted to check `isinstance(pane.object, SomeWidget)` -- it does not solve the autocomplete problem.

**Verdict: Marginal benefit. Does not solve the core problem of attribute discoverability on `.component`.**

#### 10.4.5 Approach E: Runtime `__annotations__` on the Dynamic Class

**Idea:** When creating the dynamic class, set `__annotations__` to map param names to their Python types:

```python
class_dict = {
    'value': param.Integer(default=0),
    'center': param.List(default=[0.0, 0.0]),
    '__annotations__': {
        'value': int,
        'center': list[float],
    },
}
DynClass = type('MapComponent', (AnyWidgetComponent,), class_dict)
```

**Testing confirms** that `__annotations__` is set correctly on the dynamic class:

```python
DynClass.__annotations__
# => {'value': int, 'center': list[float]}
```

**But this does not help type checkers.** Pyright reads `__annotations__` from the source AST, not from runtime attribute lookup. Setting `__annotations__` at runtime via `type()` is invisible to static analysis.

**Runtime benefit:** `typing.get_type_hints()` and `inspect.get_annotations()` would return the annotations, which helps runtime introspection tools and documentation generators. This is worth doing regardless of type checker support.

**Verdict: No benefit for static type checkers. Modest benefit for runtime introspection. Worth including as a low-cost improvement.**

#### 10.4.6 Approach F: `typing.Protocol` Classes

**Idea:** Define Protocol classes that describe the interface of known anywidget wrappers:

```python
from typing import Protocol

class MapComponentProtocol(Protocol):
    view_state: dict
    layers: list
    zoom: int
    center: list[float]
```

**Limitation:** Protocols are useful for type-checking function parameters ("does this object have `.zoom`?") but do not help with attribute discovery on an object whose type is `AnyWidgetComponent`. The pane would need to declare `component: MapComponentProtocol` specifically, which requires knowing the anywidget type at class definition time -- defeating the purpose of dynamic wrapping.

**Verdict: Not useful for dynamic wrapping. Could be useful for the manual subclass pattern if users define their own Protocols.**

#### 10.4.7 Approach G: Mypy/Pyright Plugin

**How other libraries do it:**

- **Pydantic**: Ships a mypy plugin (`pydantic.mypy`) that teaches mypy about `BaseModel` field semantics. This provides full typing support for statically-defined models but does NOT help with `create_model()`.
- **Django**: `django-stubs` includes a mypy plugin that understands `Model` metaclass magic.
- **SQLAlchemy**: Uses `dataclass_transform` plus a mypy plugin for full support.

**Could Panel ship a Pyright/mypy plugin?**

Technically possible, but:
1. **Pyright does not support plugins.** Pyright/Pylance's extension mechanism is limited to `dataclass_transform` and built-in special-casing. There is no plugin API.
2. **Mypy plugins** could be written but would only benefit mypy users, not Pylance/Pyright users (the majority of VS Code users).
3. **Maintenance cost** is very high -- plugins must be updated for each mypy/Pyright version.

**Verdict: Not practical. Pyright has no plugin API, and a mypy-only plugin serves a small subset of users.**

### 10.5 What Other Frameworks Do

| Framework | Dynamic Creation | Typing Strategy | Dynamic Model Typing? |
|-----------|-----------------|-----------------|----------------------|
| **Pydantic** | `create_model()` | `@dataclass_transform` on `ModelMetaclass` | **No** -- `create_model()` returns `type[ModelT]`, fields unknown to type checkers |
| **SQLAlchemy** | Dynamic mappers | `@dataclass_transform` + mypy plugin | **No** for dynamic mappers; **Yes** for declarative classes with `Mapped` annotations |
| **Django** | `Model` metaclass | `django-stubs` mypy plugin + third-party Pyright stubs | **Partial** -- works for statically-defined models only |
| **attrs** | `attr.make_class()` | `@dataclass_transform` | **No** -- `make_class()` returns untyped; `@attr.s` on static classes works |
| **traitlets** | `HasTraits` metaclass | `py.typed` marker, no stubs | **No** -- traitlets have no static typing support for trait attributes |

**Key insight:** No major Python framework has solved typing for dynamically created classes with custom fields. Every framework that supports typing does so only for **statically defined** classes where fields appear in source code. Dynamic creation (`create_model`, `make_class`, `type()`) is universally untyped.

### 10.6 Practical Recommendations

Given the fundamental limitation that static type checkers cannot analyze dynamically created classes, the following tiered strategy provides the best developer experience:

#### Tier 1: Excellent Runtime Introspection (Required -- Implement Now)

These are achievable within the AnyWidget pane implementation with no external dependencies:

1. **Set `__annotations__` on the dynamic class.** Even though type checkers cannot use runtime annotations, they benefit:
   - `typing.get_type_hints()` and documentation generators will show types.
   - Runtime introspection tools (Jupyter `?`, `help()`, `inspect`) can display them.
   - If future type checkers add runtime annotation support, we're ready.

   ```python
   # In _get_or_create_component_class:
   annotations = {}
   for trait_name, param_name in trait_to_param.items():
       annotations[param_name] = traitlet_to_python_type(sync_traits[trait_name])
   class_dict['__annotations__'] = annotations
   ```

2. **Ensure `__signature__` includes type annotations.** Extend param's `__signature__` generation to include type annotations from `__annotations__`, so that `inspect.signature()` returns typed parameters:

   ```python
   # Could be done as a post-creation step:
   import inspect
   sig = inspect.signature(panel_cls)
   new_params = []
   for name, p in sig.parameters.items():
       if name in annotations:
           p = p.replace(annotation=annotations[name])
       new_params.append(p)
   panel_cls.__signature__ = sig.replace(parameters=new_params)
   ```

3. **Provide a `.trait_params` property** for discovering the trait-to-param name mapping:

   ```python
   pane.component.trait_params
   # => {'value': 'value', 'width': 'w_width', 'zoom': 'zoom'}
   ```

4. **Comprehensive `__doc__`** on the dynamic class listing all params with types and defaults:

   ```python
   panel_cls.__doc__ = f"AnyWidgetComponent wrapper for {anywidget_cls.__name__}.\n\nParams:\n"
   for trait_name, param_name in trait_to_param.items():
       p = panel_cls.param[param_name]
       panel_cls.__doc__ += f"  {param_name} ({type(p).__name__}): default={p.default}\n"
   ```

5. **Tab completion in IPython/Jupyter works automatically** because param's `__dir__` includes all parameter names. Verified: dynamically created params appear in `dir(instance)`.

#### Tier 2: The Typed Subclass Pattern (Support -- Low Cost)

For users who want IDE autocomplete, provide a documented pattern for creating typed wrappers:

```python
from typing import TYPE_CHECKING
import panel as pn

class MapPane(pn.pane.AnyWidget):
    _anywidget_class = lonboard.Map

    if TYPE_CHECKING:
        # Type hints for IDE autocomplete (not evaluated at runtime)
        class component:
            view_state: dict
            layers: list
            zoom: int
            center: list[float]
```

This is a pragmatic "lie" to the type checker (as recommended by [Pyright maintainers](https://github.com/microsoft/pyright/discussions/3774): "There are times when you need to 'lie' to a type checker about the implementation to accommodate some non-standard runtime behavior"). The `TYPE_CHECKING` block is never executed at runtime, so it has no performance or correctness impact.

**Alternative: `.pyi` companion file** for the user's module:

```python
# my_widgets.pyi
from panel.custom import AnyWidgetComponent

class MapComponent(AnyWidgetComponent):
    view_state: dict
    layers: list
    zoom: int
    center: list[float]
```

Document both patterns in the AnyWidget pane reference guide.

#### Tier 3: Stub Generation Tool (Future Enhancement)

A CLI tool that generates `.pyi` stubs for anywidget wrappers:

```bash
panel generate-anywidget-stubs lonboard ipyleaflet drawdata
```

This would:
1. Import the anywidget class.
2. Inspect its synced traitlets.
3. Map traitlets to Python types (using the mapping in Section 10.4.2).
4. Generate a `.pyi` file with the component class, `__init__` signature, and attribute types.
5. Apply the `w_` collision prefix logic for colliding names.

**Scope:** This is a convenience tool, not a core feature. It could be a separate `panel-stubs` package or a `panel` CLI subcommand. The generated stubs would be static files that users check into their repos.

**Cost:** Low implementation cost (the traitlet-to-type mapping already exists for param conversion). The tricky part is distribution and keeping stubs in sync with upstream anywidget updates.

#### Tier 4: Upstream param Typing (Long-Term -- Out of Scope)

The fundamental solution is for `param` to adopt `@dataclass_transform` on `ParameterizedMetaclass`, which would make ALL Parameterized subclasses (including dynamically created ones with annotations) visible to type checkers. This is tracked in:

- [holoviz/param#587 -- Support Intellisense/dataclass_transforms](https://github.com/holoviz/param/issues/587)
- [holoviz/param#376 -- Support static typing](https://github.com/holoviz/param/issues/376)

This would require param users to add type annotations to their Parameter declarations (e.g., `x: int = param.Integer(default=0)` instead of `x = param.Integer(default=0)`). This is a significant API evolution. If/when param implements this, the AnyWidget pane could set `__annotations__` on dynamic classes and they would automatically be recognized by type checkers.

**This is not something the AnyWidget pane can solve on its own.** It depends on upstream `param` changes.

### 10.7 Summary: What We Can and Cannot Achieve

| Use Case | Autocomplete? | Type Checking? | Strategy |
|----------|--------------|----------------|----------|
| **Ad-hoc wrapping:** `pn.pane.AnyWidget(widget)` | IPython/Jupyter: **Yes** (tab completion via `dir()`) | Static: **No** | Tier 1 runtime introspection |
| | Pylance/Pyright: **No** | | |
| **Subclass pattern:** `class MyMap(pn.pane.AnyWidget)` | IPython/Jupyter: **Yes** | Static: **No** (without manual annotations) | Tier 1 + Tier 2 `TYPE_CHECKING` block |
| | Pylance/Pyright: **Yes** (with `TYPE_CHECKING` hints) | Static: **Yes** (with `TYPE_CHECKING` hints) | |
| **Known anywidgets with generated stubs** | Pylance/Pyright: **Yes** | Static: **Yes** | Tier 3 stub generation |
| **All param classes** (if param adopts `dataclass_transform`) | Pylance/Pyright: **Yes** | Static: **Yes** | Tier 4 upstream param |

### 10.8 Recommended Implementation Priority

1. **Do now (Tier 1):** Set `__annotations__`, generate `__doc__`, expose `trait_params`. Zero cost, improves runtime experience.
2. **Document now (Tier 2):** Write a guide showing the `TYPE_CHECKING` stub pattern for users who need IDE autocomplete.
3. **Consider later (Tier 3):** Build a stub generation CLI if there is user demand for typed wrappers of popular anywidgets.
4. **Track upstream (Tier 4):** Monitor param's progress on `dataclass_transform` support. When param supports it, update the dynamic class creation to include annotations.

### 10.9 Key Takeaway

**No Python framework has solved typing for dynamically created classes.** Pydantic's `create_model()`, attrs' `make_class()`, and SQLAlchemy's dynamic mappers all face the same limitation. The fundamental constraint is that static type checkers analyze source text, not runtime behavior.

For the AnyWidget pane, the practical approach is: make runtime introspection excellent (Tier 1), document the typed subclass escape hatch (Tier 2), and wait for the ecosystem to evolve (Tiers 3-4). The `.component` access pattern already provides full param reactivity at runtime -- the typing gap is a discoverability concern, not a functionality one.
