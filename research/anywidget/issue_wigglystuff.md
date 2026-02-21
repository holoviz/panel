# Feature Request: Support external model changes in TangleSlider ESM

## Summary

`wigglystuff.TangleSlider` does not respond to external changes of the `amount` traitlet. When `amount` is changed from Python (or from another framework's model layer), the browser-side TangleSlider display does not update. This is because the ESM `render()` function reads `amount` once at initialization but never registers a `model.on("change:amount", ...)` handler to listen for external updates.

## Reproduction

### Minimal reproducible example (Panel)

```bash
pip install wigglystuff panel
```

```python
# wigglystuff_bug.py
import panel as pn
from wigglystuff import TangleSlider

pn.extension()

widget = TangleSlider(amount=50, min_value=0, max_value=100, step=1)
pane = pn.pane.AnyWidget(widget)

slider = pn.widgets.FloatSlider(name="Set amount", start=0, end=100, step=1, value=50)

# Sync: dragging Panel slider updates the traitlet
slider.param.watch(lambda e: setattr(widget, 'amount', e.new), 'value')

# Sync: dragging TangleSlider updates the Panel slider
widget.observe(lambda change: setattr(slider, 'value', change['new']), 'amount')

# Display
amount_display = pn.pane.Markdown(f"**Traitlet value:** {widget.amount}")
widget.observe(
    lambda change: setattr(amount_display, 'object', f"**Traitlet value:** {change['new']}"),
    'amount'
)

pn.Column(
    "# wigglystuff TangleSlider — missing model.on handler",
    "Drag TangleSlider -> Panel slider updates (works).",
    "Drag Panel slider -> TangleSlider does NOT update (broken).",
    pn.Spacer(width=200),
    pane,
    amount_display,
    slider,
).servable()
```

```bash
panel serve wigglystuff_bug.py
```

### Expected behavior

- Dragging the **TangleSlider** updates the Panel slider and the traitlet value display (works)
- Dragging the **Panel slider** updates the TangleSlider's displayed value (does NOT work)

### Actual behavior

- TangleSlider -> Panel: **Works** (the ESM calls `model.set("amount", ...)` and `model.save_changes()`)
- Panel -> TangleSlider: **Does not work** (the traitlet IS updated in Python, but the TangleSlider display in the browser stays at its initial value)

## Root Cause

The TangleSlider ESM reads `amount` once at render time:

```javascript
let amount = model.get("amount");
```

But it never registers a change handler:

```javascript
// This is MISSING from the ESM:
model.on("change:amount", () => {
    amount = model.get("amount");
    renderValue();
});
```

Without `model.on("change:amount", ...)`, the ESM has no way to know when the model value changes externally.

## Suggested Fix

Add a `model.on("change:amount", ...)` handler in the `render()` function. Here's the minimal change needed:

```javascript
function render({model, el}) {
    // ... existing code ...

    let amount = model.get("amount");

    // ADD THIS: listen for external changes to amount
    model.on("change:amount", () => {
        amount = model.get("amount");
        renderValue();
    });

    // ... rest of existing code ...
}
```

This would also fix the same issue for `min_value`, `max_value`, `step`, `prefix`, `suffix`, and `digits` — all of which are read once at render time but never updated on external changes. To handle all of them:

```javascript
["amount", "min_value", "max_value", "step", "prefix", "suffix", "digits"].forEach(name => {
    model.on(`change:${name}`, () => {
        config.minValue = model.get("min_value");
        config.maxValue = model.get("max_value");
        config.stepSize = model.get("step");
        config.prefix = model.get("prefix");
        config.suffix = model.get("suffix");
        config.digits = model.get("digits");
        config.pixelsPerStep = model.get("pixels_per_step");
        amount = model.get("amount");
        renderValue();
    });
});
```

## Environment

- wigglystuff version: 0.2.30
- anywidget version: 0.9.x
- Panel version: 1.x (development branch with AnyWidget pane)
- Python: 3.12
- Browser: Chromium
- OS: Linux

## Notes

- This same limitation exists in Marimo and any other framework that uses the anywidget model API to set values externally
- The anywidget spec explicitly supports external changes via `model.on("change:...", ...)` — this is a standard pattern that most anywidgets implement
- Other TangleSlider properties (`min_value`, `max_value`, `step`, etc.) have the same issue — they are read once during `render()` but never updated
