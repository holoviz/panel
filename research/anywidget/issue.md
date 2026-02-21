# Feature Request: Add native AnyWidget pane (bypass ipywidgets_bokeh)

## Motivation

Panel currently renders anywidget instances through `ipywidgets_bokeh`, which has several drawbacks:

- **Reliability**: `ipywidgets_bokeh` is not actively maintained and has known issues with bidirectional sync, widget lifecycle, and error handling.
- **No Panel reactivity**: Widgets rendered via `ipywidgets_bokeh` are opaque to Panel — `param.watch`, `pn.bind`, and `.rx` don't work on their traits.
- **Heavy dependency chain**: Requires `ipywidgets_bokeh`, `ipywidgets`, and the full Jupyter comm infrastructure.

Meanwhile, Panel already has `AnyWidgetComponent` (`panel/custom.py`) for *authoring* new widgets using the anywidget ESM/traitlets API. This means Panel already speaks the anywidget protocol — it just doesn't use it to *consume* third-party anywidget instances.

## Proposed Solution

Add a new `AnyWidget` pane (`panel/pane/anywidget.py`) that renders instantiated anywidget objects natively through Panel's ReactiveESM pipeline, **bypassing `ipywidgets_bokeh` entirely**.

### How it works

1. **Detection**: Duck-typing — checks for `traits()` method and `_esm` class attribute (no `anywidget` import required at detection time).
2. **ESM extraction**: Reads `_esm` and `_css` from the anywidget instance, handling both inline strings and `pathlib.Path` file references.
3. **Traitlet mapping**: Converts `sync=True` traitlets to `param.Parameter` types (Bool, Int, Float, Unicode, List, Dict, etc.) with correct defaults and `allow_None`.
4. **Dynamic component**: Creates a `AnyWidgetComponent` subclass with the mapped params and ESM, cached by the original user-defined class.
5. **Bidirectional sync**: Wires traitlet observers and param watchers with re-entrancy guards to prevent infinite loops.
6. **Priority**: `0.8` (higher than `IPyWidget`'s `0.6`) so `pn.panel()` routes anywidget instances here by default.
7. **Eager component**: `pane.component` is available immediately after construction (before render), enabling `param.watch`, `pn.bind`, and `.rx` patterns.

### Key features

- Full Panel reactivity via `pane.component` — use `param.watch`, `pn.bind`, `.rx`
- Name collision handling (`w_` prefix for traits like `name`, `width` that collide with Panel params)
- Proper cleanup of observers and watchers on object replacement or pane disposal
- Works in `panel serve`, Jupyter notebooks, and Pyodide

## Example

```python
import anywidget
import traitlets
import panel as pn

pn.extension()

class CounterWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        let btn = document.createElement("button");
        btn.innerHTML = `count is ${model.get("value")}`;
        btn.addEventListener("click", () => {
            model.set("value", model.get("value") + 1);
            model.save_changes();
        });
        model.on("change:value", () => {
            btn.innerHTML = `count is ${model.get("value")}`;
        });
        el.appendChild(btn);
    }
    export default { render };
    """
    value = traitlets.Int(0).tag(sync=True)

widget = CounterWidget(value=5)
pane = pn.pane.AnyWidget(widget)

# Full Panel reactivity — no ipywidgets_bokeh needed!
slider = pn.widgets.IntSlider(name="Value", start=0, end=100, value=5)
pane.component.param.watch(lambda e: setattr(slider, 'value', e.new), ['value'])
slider.param.watch(lambda e: setattr(pane.component, 'value', e.new), ['value'])

pn.Column(pane, slider).servable()
```

## POC

A working proof-of-concept is available on the `enhancement/any-widget` branch with:
- Core implementation: `panel/pane/anywidget.py`
- 18 passing unit tests: `panel/tests/pane/test_anywidget.py`
- 12 example scripts: `research/anywidget/examples/`

## Known Limitations (POC)

| Limitation | Description | Severity |
|---|---|---|
| Binary traits | `traitlets.Bytes` not JSON-serializable (e.g., `ipymario`) | Medium — needs base64 encode/decode |
| Large ESM bundles | Widgets with >5MB ESM (e.g., `anymap-ts`) exceed WebSocket limits | Low — library should use CDN imports |
| Missing change handlers | Some widgets don't implement `model.on("change:...")` (e.g., `wigglystuff`) | Low — library bug, not Panel's |
| Unmapped trait types | `Enum`, `Instance`, `Union`, `Set` fall back to `param.Parameter` | Low — functional, just less typed |
