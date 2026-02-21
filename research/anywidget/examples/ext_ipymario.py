"""
ipymario Example - Known Limitation
====================================

This example demonstrates the ipymario library and explains why it doesn't
fully render in Panel's AnyWidget pane due to binary trait serialization.

Required package:
    pip install ipymario

Run with:
    panel serve research/anywidget/examples/ext_ipymario.py
"""

from ipymario import Widget

import panel as pn

pn.extension()

# Create the ipymario Widget
mario_widget = Widget()

# Wrap it with Panel's AnyWidget pane
# ipymario renders a small 16x16 sprite canvas — set explicit sizing
anywidget_pane = pn.pane.AnyWidget(mario_widget, min_height=200, sizing_mode="stretch_width")

# Layout
header = pn.pane.Markdown("""
# ipymario — Binary Traitlet Limitation in AnyWidget Pane

## About ipymario

**ipymario** is a third-party anywidget from the anywidget community that plays
the iconic Mario chime. It's a fun example of what anywidgets can do!

## The Limitation: Binary Trait Serialization

ipymario uses a `traitlets.Bytes` trait called `_box` to store a 16x16 RGBA
Mario sprite (binary data). Panel's `AnyWidget` pane serializes traitlets as
JSON strings, but the ESM widget code expects a typed array with a `.buffer`
property.

### ipymario Traits

| Trait | Type | Status |
|-------|------|--------|
| `gain` | Float | Works with Panel |
| `duration` | Float | Works with Panel |
| `size` | Int | Works with Panel |
| `animate` | Bool | Works with Panel |
| `_box` | **Bytes** | Panel can't serialize binary data |

### Browser Error

You'll see: `TypeError: Cannot read properties of undefined (reading 'buffer')`

This happens because `_box` is sent as a JSON string, but ipymario's ESM expects
`_box.buffer` (an ArrayBuffer from a typed array).

## Can It Be Fixed?

**Yes, but it requires changes to Panel's AnyWidgetComponent TypeScript model.**

The fix would involve:
1. **Detect `Bytes`/`param.Bytes` parameters** in the component class
2. **Encode as base64** when serializing Python -> JSON (in `_process_param_change`)
3. **Decode in the TS model** from base64 string back to `ArrayBuffer`/`DataView`
4. **Reverse for browser -> Python**: encode `ArrayBuffer` as base64, decode in Python

### Difficulty: Medium

- The Python side is straightforward: base64 encode/decode in `_process_param_change`
  and `_process_events` methods
- The TypeScript side needs modification to `anywidget_component.ts`:
  the `get()` method should detect base64-encoded bytes and return a `DataView`,
  and `set()` should convert `ArrayBuffer` back to base64
- Scope: ~50-100 lines of code across 2-3 files
- Risk: low — isolated to Bytes-type params, no impact on existing widgets

### Workaround

For now, anywidgets that rely on `Bytes` traitlets won't render correctly.
Use `ipywidgets_bokeh` bridge for these widgets, or wait for the binary
serialization enhancement.

## What You'll See

The widget below will attempt to render, but you'll see an error in
the browser console because `_box` (the sprite data) isn't properly serialized.
""")

widget_section = pn.pane.Markdown("""
### Rendered Widget (with Known Limitation)

The widget below will display, but interaction may be limited due to
the binary trait issue described above.
""")

pn.Column(
    header,
    pn.layout.Divider(),
    widget_section,
    anywidget_pane,
).servable()
