"""
jupyter-tldraw Example — All Widget Classes in Panel
=====================================================

This example demonstrates ALL widget classes from the jupyter-tldraw package
with Panel's AnyWidget pane, organized into tabs.

The tldraw package provides a rich set of drawing, annotation, and export
widgets powered by the tldraw SDK.

GitHub: https://github.com/nickvdyck/tldraw-python
Docs:   https://tldraw.dev/

Widget classes tested (13 total):
    1.  TldrawWidget            — Basic infinite canvas
    2.  TldrawDebug             — Canvas with debug rectangle (rec_x/y/width/height)
    3.  TldrawWidgetCoordinates — Captures drawing coordinates
    4.  TldrawImage             — Image display in tldraw
    5.  TldrawImageArray        — Base64-encoded PNG image display
    6.  TldrawMakeStaticSVG     — Export canvas as SVG
    7.  TldrawMakeStaticPNG     — Export canvas as PNG
    8.  TldrawMakeStaticTldraw  — Export/import canvas as JSON state
    9.  TldrawMakeStaticToMarkdown — Export canvas as Markdown
    10. ReactiveColorPicker     — Color picker with tldraw canvas
    11. FlowerPlot              — Flower data visualizer
    12. TldrawSetImage          — Set and manage images on canvas
    13. MakeReal                — AI-powered "Make Real" (requires API key)

NOTE: tldraw's `width` and `height` traits collide with Panel's Layoutable
params. They are renamed to `w_width` and `w_height` on the component.

Required package:
    pip install tldraw

Run with:
    panel serve research/anywidget/examples/ext_tldraw.py
"""

import base64
import struct
import zlib

from tldraw import (
    FlowerPlot, MakeReal, ReactiveColorPicker, TldrawDebug, TldrawImage,
    TldrawImageArray, TldrawMakeStaticPNG, TldrawMakeStaticSVG,
    TldrawMakeStaticTldraw, TldrawMakeStaticToMarkdown, TldrawSetImage,
    TldrawWidget, TldrawWidgetCoordinates,
)

import panel as pn

pn.extension()

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 450


# ---------------------------------------------------------------------------
# Helper: create a small test PNG image (gradient)
# ---------------------------------------------------------------------------

def _make_test_png(width=40, height=40):
    """Create a small RGB gradient PNG for testing image widgets."""
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b""
    for y in range(height):
        raw += b"\x00"  # filter: none
        for x in range(width):
            r = int(255 * x / width)
            g = int(255 * y / height)
            b = 128
            raw += bytes([r, g, b])
    compressed = zlib.compress(raw)

    def chunk(ctype, data):
        c = ctype + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + c + struct.pack(">I", crc)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr_data)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    return "data:image/png;base64," + base64.b64encode(png).decode()


B64_TEST_IMAGE = _make_test_png()


# ===========================================================================
# Tab 1: TldrawWidget — Basic Canvas
# ===========================================================================

def make_tab_tldraw_widget():
    widget = TldrawWidget(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    width_slider = pn.widgets.IntSlider(
        name="Canvas Width (w_width)", start=400, end=1200,
        value=CANVAS_WIDTH, width=300,
    )
    height_slider = pn.widgets.IntSlider(
        name="Canvas Height (w_height)", start=200, end=800,
        value=CANVAS_HEIGHT, width=300,
    )

    # Panel -> Widget
    width_slider.param.watch(
        lambda e: setattr(component, "w_width", e.new), "value"
    )
    height_slider.param.watch(
        lambda e: setattr(component, "w_height", e.new), "value"
    )

    # Widget -> Panel
    def on_change(*events):
        for ev in events:
            if ev.name == "w_width":
                width_slider.value = ev.new
            elif ev.name == "w_height":
                height_slider.value = ev.new

    component.param.watch(on_change, ["w_width", "w_height"])

    dim_display = pn.pane.Markdown(
        pn.bind(
            lambda w, h: f"**Current dimensions:** {w} x {h} px",
            component.param.w_width,
            component.param.w_height,
        )
    )

    info = pn.pane.Markdown("""
### TldrawWidget — Basic Infinite Canvas

The simplest tldraw widget. Provides a full drawing canvas with tools for
freehand drawing, shapes, text, arrows, sticky notes, and more.

**Synced traits:** `w_width`, `w_height` (renamed from `width`/`height`)

**How to test:**
1. Draw shapes using the toolbar (pen, rectangle, arrow, text, etc.)
2. Drag the width/height sliders — the canvas should resize
3. The "Current dimensions" display should update in real time
""")

    return pn.Column(
        info,
        pn.Row(width_slider, height_slider),
        dim_display,
        pane,
    )


# ===========================================================================
# Tab 2: TldrawDebug — Debug Canvas with Rectangle
# ===========================================================================

def make_tab_tldraw_debug():
    widget = TldrawDebug()
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    # Sliders for rectangle properties
    rec_x = pn.widgets.IntSlider(
        name="rec_x", start=0, end=500, value=100, width=250,
    )
    rec_y = pn.widgets.IntSlider(
        name="rec_y", start=0, end=500, value=100, width=250,
    )
    rec_w = pn.widgets.IntSlider(
        name="rec_width", start=10, end=500, value=100, width=250,
    )
    rec_h = pn.widgets.IntSlider(
        name="rec_height", start=10, end=500, value=100, width=250,
    )

    # Panel -> Widget
    rec_x.param.watch(lambda e: setattr(component, "rec_x", e.new), "value")
    rec_y.param.watch(lambda e: setattr(component, "rec_y", e.new), "value")
    rec_w.param.watch(lambda e: setattr(component, "rec_width", e.new), "value")
    rec_h.param.watch(lambda e: setattr(component, "rec_height", e.new), "value")

    # Widget -> Panel
    def on_change(*events):
        for ev in events:
            if ev.name == "rec_x":
                rec_x.value = ev.new
            elif ev.name == "rec_y":
                rec_y.value = ev.new
            elif ev.name == "rec_width":
                rec_w.value = ev.new
            elif ev.name == "rec_height":
                rec_h.value = ev.new

    component.param.watch(on_change, ["rec_x", "rec_y", "rec_width", "rec_height"])

    rect_display = pn.pane.Markdown(
        pn.bind(
            lambda x, y, w, h: f"**Rectangle:** x={x}, y={y}, w={w}, h={h}",
            component.param.rec_x,
            component.param.rec_y,
            component.param.rec_width,
            component.param.rec_height,
        )
    )

    info = pn.pane.Markdown("""
### TldrawDebug — Debug Canvas with Rectangle

A tldraw canvas that shows a debug rectangle whose position and size are
synced as traitlets.

**Synced traits:** `rec_x`, `rec_y`, `rec_width`, `rec_height`

**How to test:**
1. The canvas should show a blue rectangle on load
2. Drag the sliders to change rectangle position/size — the rectangle in the
   canvas should update
3. If you resize the rectangle in the canvas, the sliders should update
""")

    return pn.Column(
        info,
        pn.Row(
            pn.Column(rec_x, rec_y),
            pn.Column(rec_w, rec_h),
        ),
        rect_display,
        pane,
    )


# ===========================================================================
# Tab 3: TldrawWidgetCoordinates — Coordinate Capture
# ===========================================================================

def make_tab_coordinates():
    widget = TldrawWidgetCoordinates(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    coord_display = pn.pane.Str(
        "No coordinates captured yet. Draw something on the canvas.",
        width=600,
    )
    length_display = pn.pane.Markdown("**Length:** 0")
    value_display = pn.pane.Markdown("**Value:** 0")

    def on_change(*events):
        for ev in events:
            if ev.name == "coord":
                coords = ev.new
                if coords:
                    # Show last few coordinate entries
                    preview = str(coords[-5:]) if len(coords) > 5 else str(coords)
                    coord_display.object = f"Coordinates ({len(coords)} points, last 5): {preview}"
                else:
                    coord_display.object = "No coordinates captured yet."
            elif ev.name == "length":
                length_display.object = f"**Length:** {ev.new}"
            elif ev.name == "value":
                value_display.object = f"**Value:** {ev.new}"

    component.param.watch(on_change, ["coord", "length", "value"])

    info = pn.pane.Markdown("""
### TldrawWidgetCoordinates — Coordinate Capture

A tldraw canvas that captures drawing coordinates and syncs them back to Python.

**Synced traits:** `coord` (list), `length` (int), `points_new` (list), `value` (int)

**How to test:**
1. Draw freehand strokes on the canvas
2. Watch the coordinate display update with captured points
3. The length counter should increment as you draw
""")

    return pn.Column(
        info,
        pn.Row(length_display, value_display),
        coord_display,
        pane,
    )


# ===========================================================================
# Tab 4: TldrawImage — Image Display
# ===========================================================================

def make_tab_image():
    widget = TldrawImage()
    pane = pn.pane.AnyWidget(widget)

    info = pn.pane.Markdown("""
### TldrawImage — Image Display in Tldraw

A tldraw canvas designed for displaying images. This widget does not expose
image-related traitlets — the image is managed client-side within the tldraw
editor.

**Synced traits:** None (no user-facing traitlets beyond layout)

**How to test:**
1. The canvas should render with the tldraw "Page 1" interface
2. You can use the canvas tools to draw over the image area
3. This is primarily used for displaying images set programmatically in Jupyter
""")

    return pn.Column(info, pane)


# ===========================================================================
# Tab 5: TldrawImageArray — Base64 Image Display
# ===========================================================================

def make_tab_image_array():
    widget = TldrawImageArray(base64img=B64_TEST_IMAGE)
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    dims_display = pn.pane.Markdown(
        pn.bind(
            lambda w, h: f"**Image dimensions:** {w} x {h}",
            component.param.image_width,
            component.param.image_height,
        )
    )

    info = pn.pane.Markdown("""
### TldrawImageArray — Base64-Encoded Image Display

Displays a base64-encoded PNG image within a tldraw canvas. The image can be
drawn over using the tldraw tools.

**Synced traits:** `base64img` (str), `image_width` (int), `image_height` (int)

**How to test:**
1. A small gradient test image should be loaded into the canvas
2. The image dimensions should display below
3. You can draw over the image using the tldraw tools
4. Use the style palette (colors, sizes) to customize your annotations
""")

    return pn.Column(info, dims_display, pane)


# ===========================================================================
# Tab 6: TldrawMakeStaticSVG — Export as SVG
# ===========================================================================

def make_tab_export_svg():
    widget = TldrawMakeStaticSVG(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    value_display = pn.pane.Markdown("**Export trigger count:** 0")

    def on_change(*events):
        for ev in events:
            if ev.name == "value":
                value_display.object = f"**Export trigger count:** {ev.new}"

    component.param.watch(on_change, ["value"])

    info = pn.pane.Markdown("""
### TldrawMakeStaticSVG — Export as SVG

A tldraw canvas with a "Convert to SVG" button. Clicking the button exports the
current canvas content as SVG.

**Synced traits:** `value` (int — export trigger counter)

**How to test:**
1. Draw some shapes on the canvas
2. Click the **"Convert to SVG"** button (appears inside the canvas)
3. The export trigger count should increment
4. Note: The actual SVG content is handled client-side; the `value` trait
   acts as a trigger counter, not the SVG data itself
""")

    return pn.Column(info, value_display, pane)


# ===========================================================================
# Tab 7: TldrawMakeStaticPNG — Export as PNG
# ===========================================================================

def make_tab_export_png():
    widget = TldrawMakeStaticPNG(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    value_display = pn.pane.Markdown("**Export trigger count:** 0")

    def on_change(*events):
        for ev in events:
            if ev.name == "value":
                value_display.object = f"**Export trigger count:** {ev.new}"

    component.param.watch(on_change, ["value"])

    info = pn.pane.Markdown("""
### TldrawMakeStaticPNG — Export as PNG

A tldraw canvas with a "Convert to PNG" button. Clicking the button exports the
current canvas content as PNG.

**Synced traits:** `value` (int — export trigger counter)

**How to test:**
1. Draw some shapes on the canvas
2. Click the **"Convert to PNG"** button
3. The export trigger count should increment
""")

    return pn.Column(info, value_display, pane)


# ===========================================================================
# Tab 8: TldrawMakeStaticTldraw — Export/Import JSON State
# ===========================================================================

def make_tab_export_tldraw():
    widget = TldrawMakeStaticTldraw(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    value_display = pn.pane.Markdown("**State save/load trigger count:** 0")

    def on_change(*events):
        for ev in events:
            if ev.name == "value":
                value_display.object = f"**State save/load trigger count:** {ev.new}"

    component.param.watch(on_change, ["value"])

    info = pn.pane.Markdown("""
### TldrawMakeStaticTldraw — Export/Import JSON State

A tldraw canvas with "Save .json state" and "Load .json state" buttons.
Allows serializing and restoring the full canvas state as JSON.

**Synced traits:** `value` (int — trigger counter)

**How to test:**
1. Draw some shapes on the canvas
2. Click **"Save .json state"** — the trigger count should increment
3. Clear the canvas and click **"Load .json state"** to restore
""")

    return pn.Column(info, value_display, pane)


# ===========================================================================
# Tab 9: TldrawMakeStaticToMarkdown — Export as Markdown
# ===========================================================================

def make_tab_export_markdown():
    widget = TldrawMakeStaticToMarkdown(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    value_display = pn.pane.Markdown("**Export trigger count:** 0")
    snapshot_display = pn.pane.Str("Snapshot: (empty)", width=600)

    def on_change(*events):
        for ev in events:
            if ev.name == "value":
                value_display.object = f"**Export trigger count:** {ev.new}"
            elif ev.name == "snapshot":
                preview = ev.new[:200] + "..." if len(ev.new) > 200 else ev.new
                snapshot_display.object = f"Snapshot: {preview}" if ev.new else "Snapshot: (empty)"

    component.param.watch(on_change, ["value", "snapshot"])

    info = pn.pane.Markdown("""
### TldrawMakeStaticToMarkdown — Export as Markdown

A tldraw canvas with a "Paste to Markdown" button. Exports the canvas content
in a format suitable for Markdown documents.

**Synced traits:** `value` (int — trigger counter), `snapshot` (str)

**How to test:**
1. Draw some shapes on the canvas
2. Click **"Paste to Markdown"**
3. The trigger count should increment and snapshot data may appear
""")

    return pn.Column(info, value_display, snapshot_display, pane)


# ===========================================================================
# Tab 10: ReactiveColorPicker — Color Picker
# ===========================================================================

def make_tab_color_picker():
    widget = ReactiveColorPicker()
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    color_display = pn.pane.Markdown("**Selected color:** (none)")

    def on_change(*events):
        for ev in events:
            if ev.name == "color":
                color_val = ev.new
                if color_val:
                    color_display.object = f"**Selected color:** `{color_val}`"
                else:
                    color_display.object = "**Selected color:** (none)"

    component.param.watch(on_change, ["color"])

    info = pn.pane.Markdown("""
### ReactiveColorPicker — Color Picker

A tldraw canvas that acts as a reactive color picker. Selecting a color in the
canvas updates the `color` trait.

**Synced traits:** `color` (list/any)

**How to test:**
1. The canvas should render with a tldraw toolbar
2. Select different colors using the color tools
3. The "Selected color" display should update when a color is picked
""")

    return pn.Column(info, color_display, pane)


# ===========================================================================
# Tab 11: FlowerPlot — Flower Data Visualizer
# ===========================================================================

def make_tab_flower_plot():
    widget = FlowerPlot()
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    value_display = pn.pane.Markdown("**Value:** 0")
    data_display = pn.pane.Str("Flower data: (empty)", width=600)

    def on_change(*events):
        for ev in events:
            if ev.name == "value":
                value_display.object = f"**Value:** {ev.new}"
            elif ev.name == "flower_data":
                data = ev.new
                if data:
                    preview = str(data[:3]) + "..." if len(data) > 3 else str(data)
                    data_display.object = f"Flower data ({len(data)} items): {preview}"
                else:
                    data_display.object = "Flower data: (empty)"

    component.param.watch(on_change, ["value", "flower_data"])

    info = pn.pane.Markdown("""
### FlowerPlot — Flower Data Visualizer

A tldraw-based widget for visualizing flower data. The widget syncs flower
data and a value counter.

**Synced traits:** `flower_data` (list), `value` (int)

**How to test:**
1. The canvas should render with the tldraw interface
2. Interact with the canvas — flower data may update as you draw
3. Watch the data display for any changes
""")

    return pn.Column(info, value_display, data_display, pane)


# ===========================================================================
# Tab 12: TldrawSetImage — Set and Manage Images
# ===========================================================================

def make_tab_set_image():
    widget = TldrawSetImage()
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    coord_display = pn.pane.Str("Coordinates: (empty)", width=600)
    dims_display = pn.pane.Markdown("**Image dimensions:** (0, 0)")
    length_display = pn.pane.Markdown("**Length:** 0")

    def on_change(*events):
        for ev in events:
            if ev.name == "coord":
                coords = ev.new
                if coords:
                    preview = str(coords[-5:]) if len(coords) > 5 else str(coords)
                    coord_display.object = f"Coordinates ({len(coords)} pts): {preview}"
                else:
                    coord_display.object = "Coordinates: (empty)"
            elif ev.name == "image_dimensions":
                dims_display.object = f"**Image dimensions:** {ev.new}"
            elif ev.name == "length":
                length_display.object = f"**Length:** {ev.new}"

    component.param.watch(on_change, ["coord", "image_dimensions", "length"])

    info = pn.pane.Markdown("""
### TldrawSetImage — Set and Manage Images

A tldraw canvas for setting and managing images. Supports image placement with
coordinate tracking.

**Synced traits:** `base64img` (str), `coord` (list), `image_dimensions` (tuple),
`length` (int)

**How to test:**
1. The canvas should render with the full tldraw toolbar
2. Draw on the canvas — coordinates and length may update
3. The image dimensions display shows the current image size
""")

    return pn.Column(info, pn.Row(dims_display, length_display), coord_display, pane)


# ===========================================================================
# Tab 13: MakeReal — AI-Powered "Make Real"
# ===========================================================================

def make_tab_make_real():
    widget = MakeReal()
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    # Display rectangle properties (same as TldrawDebug)
    rect_display = pn.pane.Markdown(
        pn.bind(
            lambda x, y, w, h: f"**Rectangle:** x={x}, y={y}, w={w}, h={h}",
            component.param.rec_x,
            component.param.rec_y,
            component.param.rec_width,
            component.param.rec_height,
        )
    )

    prompt_display = pn.pane.Markdown(
        pn.bind(
            lambda p: f"**Prompt:** `{p}`" if p else "**Prompt:** (empty)",
            component.param.prompt,
        )
    )

    info = pn.pane.Markdown("""
### MakeReal — AI-Powered "Make Real"

A tldraw canvas with a "Make Real" button that uses an AI model to convert
drawings into code. Requires an OpenAI API key to function fully.

**Synced traits:** `api_key`, `prompt`, `snapshot`, `rec_x`, `rec_y`,
`rec_width`, `rec_height`, `run_next_cell`

**How to test:**
1. The canvas should render with a **"Make Real"** button
2. Draw a UI mockup (buttons, forms, etc.)
3. The "Make Real" button will attempt to convert it to code
4. Without a valid API key (set via `api_key` trait), the AI call will fail,
   but the canvas and drawing tools should work fine

**Note:** The API key defaults to `'KEY'`. Set a valid OpenAI API key via
`widget.api_key = 'sk-...'` for full functionality.
""")

    return pn.Column(info, rect_display, prompt_display, pane)


# ===========================================================================
# Assemble all tabs
# ===========================================================================

tabs = pn.Tabs(
    ("TldrawWidget", make_tab_tldraw_widget()),
    ("TldrawDebug", make_tab_tldraw_debug()),
    ("Coordinates", make_tab_coordinates()),
    ("Image", make_tab_image()),
    ("ImageArray", make_tab_image_array()),
    ("Export SVG", make_tab_export_svg()),
    ("Export PNG", make_tab_export_png()),
    ("Export JSON", make_tab_export_tldraw()),
    ("Export MD", make_tab_export_markdown()),
    ("ColorPicker", make_tab_color_picker()),
    ("FlowerPlot", make_tab_flower_plot()),
    ("SetImage", make_tab_set_image()),
    ("MakeReal", make_tab_make_real()),
    dynamic=True,
)

# ---------------------------------------------------------------------------
# Status banner
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 15px; margin: 8px 0 0 0;">
<strong>All 13 tldraw widget classes render successfully in Panel.</strong>
Width/height traits are renamed to <code>w_width</code>/<code>w_height</code>
to avoid collision with Panel's Layoutable params. Rectangle properties
(<code>rec_x</code>, <code>rec_y</code>, etc.) and coordinate traits sync
bidirectionally. However, export widgets (SVG/PNG/JSON/Markdown) use a trigger
counter as their <code>value</code> trait &mdash; the actual exported content
is handled client-side and may not be accessible from Python.
<strong>MakeReal</strong> requires a valid OpenAI API key.
</p>
</div>
""", sizing_mode="stretch_width")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# jupyter-tldraw — All Widget Classes in Panel

**tldraw** is a free whiteboard / infinite canvas powered by the
[tldraw SDK](https://tldraw.dev/). The `tldraw` Python package provides
**13 widget classes** covering drawing, annotation, image management, data
export, color picking, and AI-powered code generation.

Each tab below demonstrates one widget class with its synced traits and
Panel controls. Click a tab to test that widget.

## Trait Collision Note

tldraw's `width` and `height` traitlets collide with Panel's `Layoutable`
parameters. They are automatically renamed to `w_width` and `w_height` on
the component. Access them via `pane.component.w_width`.
""", sizing_mode="stretch_width")

# ---------------------------------------------------------------------------
# Final layout
# ---------------------------------------------------------------------------

pn.Column(
    status,
    header,
    tabs,
    sizing_mode="stretch_width",
    max_width=1100,
).servable()
