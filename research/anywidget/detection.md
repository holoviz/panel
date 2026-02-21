# Detection & Priority Strategy for AnyWidget Pane

## 1. How `get_pane_type()` Works

When a user calls `pn.panel(obj)`, Panel resolves which `Pane` subclass should render the object via `PaneBase.get_pane_type()` (`panel/pane/base.py:237-283`). The algorithm:

1. **Viewable short-circuit** (line 251-252): If `isinstance(obj, Viewable)`, return `type(obj)` immediately. This means Panel's own `ReactiveESM`, `AnyWidgetComponent`, `Viewer`, etc. are never subject to pane resolution. This is critical -- it means any Panel subclass with `_esm` is excluded from our detection before we even get to priority checking.

2. **Collect candidates**: For each concrete `PaneBase` descendent:
   - If `priority is None`, call `applies()` immediately and use the return value as priority.
   - If `priority` is a float, store it but defer `applies()` check.

3. **Sort by priority descending**, then iterate:
   - Call `applies()` (if not already called) to confirm the pane handles this object.
   - Return the first pane type where `applies()` returns truthy.

## 2. Identifying AnyWidget Objects

### Candidate Detection Attributes

| Attribute | What it detects | False positives? |
|-----------|----------------|-----------------|
| `hasattr(type(obj), '_esm')` | Any class with `_esm` on the class | Panel's `ReactiveESM` subclasses (but caught by Viewable check) |
| `hasattr(obj, 'traits')` | Any traitlets `HasTraits` instance | All ipywidgets, matplotlib figures with traitlets |
| `isinstance(obj, anywidget.AnyWidget)` | Exactly anywidget instances | None, but requires import |
| `obj._view_module == 'anywidget'` | Widgets whose frontend is anywidget | Exact match, but relies on ipywidgets internals |

### The AnyWidget Class Signature

From the actual anywidget source (`/tmp/anywidget-src/anywidget/widget.py`), `AnyWidget` extends `ipywidgets.DOMWidget` and provides:

```python
class AnyWidget(ipywidgets.DOMWidget):
    _model_name = t.Unicode("AnyModel").tag(sync=True)
    _model_module = t.Unicode("anywidget").tag(sync=True)
    _model_module_version = t.Unicode(_ANYWIDGET_SEMVER_VERSION).tag(sync=True)
    _view_name = t.Unicode("AnyView").tag(sync=True)
    _view_module = t.Unicode("anywidget").tag(sync=True)
    _view_module_version = t.Unicode(_ANYWIDGET_SEMVER_VERSION).tag(sync=True)
```

Key attributes:
- **`_esm`** (class attribute, key `"_esm"`): ESM JavaScript/TypeScript source or file path. Dynamically converted to a `t.Unicode(...).tag(sync=True)` traitlet in `__init__()` via `self.add_traits()`. On the class it may be a string or a `FileContents` object.
- **`_css`** (class attribute, key `"_css"`): Optional CSS styling, same dynamic trait pattern.
- **`_anywidget_id`**: A dynamically added Unicode trait containing the fully-qualified class name (`f"{cls.__module__}.{cls.__name__}"`).
- **`__init_subclass__`**: Coerces `_esm` and `_css` to `FileContents` objects if they look like file paths.
- Standard ipywidgets infrastructure: `traits()`, `get_manager_state()`, `comm`, `observe()`, `unobserve()` etc.

**Important nuance**: `_esm` starts as a class-level attribute (string or FileContents), then is dynamically added as a Unicode traitlet via `self.add_traits()` in `__init__()`. So `hasattr(type(obj), '_esm')` checks the class attribute, while `hasattr(obj, '_esm')` would also match after `add_traits()` promotes it to a trait on the instance. For detection, checking the **class** (`type(obj)`) is the right approach because subclasses always define `_esm` at class level.

The combination of `_esm` on the class AND ipywidget traits (`traits`, `comm`) is unique to anywidgets. Panel's own `ReactiveESM` has `_esm` but does NOT have `traits()` or `comm` because it inherits from `Viewable`, not `ipywidgets.DOMWidget`.

### Recommended Approach: Hybrid Duck-Typing

```python
@classmethod
def applies(cls, obj: Any) -> float | bool | None:
    # Duck-type check: must look like an ipywidget AND have _esm
    if not (hasattr(obj, 'traits') and hasattr(obj, 'comm')):
        return False
    if not hasattr(type(obj), '_esm'):
        return False
    return True
```

**Why this approach:**

1. **Duck-typing over `isinstance`**: Avoids hard dependency on `anywidget` package at import time. Users who don't have `anywidget` installed won't get import errors.

2. **`hasattr(type(obj), '_esm')` (class-level check)**: Checks the *class*, not the instance, because `_esm` is defined as a class attribute in anywidget subclasses. This avoids false positives from objects that happen to have an `_esm` instance attribute for other reasons.

3. **`hasattr(obj, 'traits') and hasattr(obj, 'comm')`**: Confirms the object is an ipywidget-like object. This filters out any non-widget objects that might have an `_esm` attribute.

4. **No conflict with Panel's ReactiveESM**: Panel components inherit from `Viewable`, so `isinstance(obj, Viewable)` returns `True` at line 251 of `get_pane_type()`, and they are returned directly as `type(obj)` before pane resolution ever runs. The `applies()` method is never called for them.

### Alternative: Optional isinstance Check (More Precise)

```python
@classmethod
def applies(cls, obj: Any) -> float | bool | None:
    try:
        from anywidget import AnyWidget
        return isinstance(obj, AnyWidget)
    except ImportError:
        # Fallback to duck typing if anywidget not installed
        if not (hasattr(obj, 'traits') and hasattr(obj, 'comm')):
            return False
        return hasattr(type(obj), '_esm')
```

This is more precise but adds a try/except on every `applies()` call. Since `applies()` may be called for every `pn.panel()` invocation, the duck-typing approach is more efficient. The `isinstance` check is only worthwhile if there are edge cases where the duck-typing produces false positives.

**Recommendation**: Use the duck-typing approach. It is simpler, has no import overhead, and the false-positive risk is negligible given the Viewable short-circuit.

## 3. Priority Value

### Current Priority Landscape

| Pane | Priority | Notes |
|------|----------|-------|
| `Textual` | 1.0 | Highest |
| `Matplotlib` | 0.8 | Tied highest tier |
| `HoloViews` | 0.8 | |
| `Plotly` | 0.8 | |
| `Vega` | 0.8 | |
| `IPyLeaflet` | **0.7** | Specialized ipywidget |
| `IPyWidget` | **0.6** | Generic ipywidget |
| `PaneBase` | 0.5 | Default |
| `Bokeh` | 0.5 | |

### Requirement

The AnyWidget pane must have `priority > 0.7` so it wins over `IPyLeaflet` (0.7) and `IPyWidget` (0.6). An anywidget IS an ipywidget (it extends `DOMWidget`), so `IPyWidget.applies()` would also return `True` for it. The new pane must win by having higher priority.

### Recommended: `priority = 0.8`

```python
priority: ClassVar[float | bool | None] = 0.8
```

**Rationale:**
- `0.8 > 0.7` (IPyLeaflet) -- anywidgets route to the new pane, not IPyLeaflet
- `0.8 > 0.6` (IPyWidget) -- anywidgets route here, not the generic IPyWidget
- `0.8` ties with Matplotlib/HoloViews/Plotly/Vega, but those panes' `applies()` methods won't match anywidget objects, so no conflict
- Using `0.8` rather than a higher value (like `0.9`) is conservative -- it doesn't override truly specialized panes

## 4. Conflict Analysis

### Scenario 1: AnyWidget instance passed to `pn.panel()`

1. `isinstance(obj, Viewable)` -> `False` (anywidgets don't inherit from Viewable)
2. Candidates collected:
   - `AnyWidgetPane`: priority=0.8
   - `IPyLeaflet`: priority=0.7
   - `IPyWidget`: priority=0.6
3. Sorted: AnyWidgetPane (0.8), IPyLeaflet (0.7), IPyWidget (0.6)
4. `AnyWidgetPane.applies()` checks `_esm` + `traits` + `comm` -> `True`
5. **Result: AnyWidgetPane wins** -- correct

### Scenario 2: Non-anywidget ipywidget (e.g., `ipywidgets.IntSlider`)

1. `isinstance(obj, Viewable)` -> `False`
2. Candidates:
   - `AnyWidgetPane`: priority=0.8
   - `IPyWidget`: priority=0.6
3. `AnyWidgetPane.applies()` checks `hasattr(type(obj), '_esm')` -> `False` (IntSlider has no `_esm`)
4. Falls through to `IPyWidget.applies()` -> `True`
5. **Result: IPyWidget wins** -- correct

### Scenario 3: IPyLeaflet Map widget

1. `isinstance(obj, Viewable)` -> `False`
2. Candidates include AnyWidgetPane (0.8), IPyLeaflet (0.7), IPyWidget (0.6)
3. `AnyWidgetPane.applies()` checks `hasattr(type(obj), '_esm')` -> `False` (leaflet maps don't have `_esm`)
4. Falls through to `IPyLeaflet.applies()` -> `True` (checks `_view_module == 'jupyter-leaflet'`)
5. **Result: IPyLeaflet wins** -- correct

### Scenario 4: Panel ReactiveESM subclass

1. `isinstance(obj, Viewable)` -> `True` (ReactiveESM inherits from Viewable)
2. Returns `type(obj)` immediately -- pane resolution never runs
3. **Result: ReactiveESM handles itself** -- correct, no conflict

### Scenario 5: Panel AnyWidgetComponent subclass

1. `isinstance(obj, Viewable)` -> `True` (AnyWidgetComponent inherits from ReactComponent -> Viewable)
2. Returns `type(obj)` immediately
3. **Result: AnyWidgetComponent handles itself** -- correct, no conflict

## 5. Edge Cases

### Objects with `_esm` that are NOT anywidgets

- **Panel's ReactiveESM/AnyWidgetComponent**: Caught by `isinstance(obj, Viewable)` check at line 251-252, never reach pane resolution. No conflict.
- **Random objects with `_esm` attribute**: Would need BOTH `_esm` on the class AND `traits`/`comm` attributes. This combination is extremely unlikely outside of actual anywidget subclasses.

### Anywidget installed but object not a true AnyWidget

If a third-party library creates a class that has `_esm`, `traits`, and `comm` but doesn't actually extend `AnyWidget`, the duck-type check would match it. In practice this is unlikely, and even if it happens, the new pane would attempt to render it. If the duck-type approach proves problematic, we can add an additional check:

```python
# Extra guard: check _view_module trait if available
if hasattr(obj, '_view_module') and obj._view_module == 'anywidget':
    return True
```

This would make the check even more specific to actual anywidget instances.

## 6. Final Recommendation

```python
class AnyWidget(Pane):
    """
    Renders anywidget instances natively in Panel using their ESM code.
    """

    priority: ClassVar[float | bool | None] = 0.8

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        # Must be an ipywidget-like object (has traitlets infrastructure)
        if not (hasattr(obj, 'traits') and hasattr(obj, 'comm')):
            return False
        # Must have _esm on the class (anywidget's defining characteristic)
        return hasattr(type(obj), '_esm')
```

This is clean, efficient, and correctly routes:
- AnyWidget instances -> AnyWidget pane (priority 0.8)
- IPyLeaflet instances -> IPyLeaflet pane (priority 0.7, `_esm` check fails)
- Plain ipywidgets -> IPyWidget pane (priority 0.6, `_esm` check fails)
- Panel Viewable subclasses -> themselves (short-circuit before priority resolution)
