"""
pygv Example — Minimal Genome Browser with Panel AnyWidget Pane
================================================================

This example demonstrates rendering the pygv minimal genome browser
using Panel's AnyWidget pane. pygv is a lightweight, scriptable
genome browser built with anywidget that uses igv.js for rendering.

The pygv Browser is a genuine anywidget.AnyWidget subclass with a
synced `config` traitlet (Instance of a msgspec Struct). The ESM
loads igv.js from a CDN and creates the browser from the config.

GitHub: https://github.com/nicokant/pygv

KNOWN LIMITATION: pygv's ESM reads the config once at render time
and does not listen for `change:config` events. This means:
  - Navigating in the browser does NOT sync locus back to Python
  - Changing the config from Python does NOT navigate the browser
To "navigate" from Panel, the example replaces the entire AnyWidget
pane object, creating a fresh browser with the new config.

Required package:
    pip install pygv

Run with:
    panel serve research/anywidget/examples/ext_pygv.py
"""

import pygv

from pygv._config import Config

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Genome region presets
# ---------------------------------------------------------------------------

PRESETS = {
    "MYC (chr8)": Config(genome="hg38", locus="chr8:127,735,434-127,742,951"),
    "TP53 (chr17)": Config(genome="hg38", locus="chr17:7,571,720-7,590,868"),
    "BRCA1 (chr17)": Config(genome="hg38", locus="chr17:43,044,295-43,125,483"),
    "EGFR (chr7)": Config(genome="hg38", locus="chr7:55,019,017-55,211,628"),
}

# ---------------------------------------------------------------------------
# 2. Create a pygv genome browser and wrap with Panel
# ---------------------------------------------------------------------------

def make_browser(config):
    """Create a fresh pygv Browser with the given Config."""
    return pygv._browser.Browser(config=config)

initial_config = PRESETS["MYC (chr8)"]
browser = make_browser(initial_config)

browser_pane = pn.pane.AnyWidget(
    browser, height=700, sizing_mode="stretch_width",
    styles={"border": "1px solid #ccc", "border-radius": "4px"},
)

# ---------------------------------------------------------------------------
# 3. Panel controls: navigate to genome presets
# ---------------------------------------------------------------------------
# Because pygv's ESM is read-once, we replace `browser_pane.object`
# with a new Browser instance to "navigate".  Panel tears down the
# old component and creates a fresh one, which re-renders igv.js
# with the new config.

region_select = pn.widgets.Select(
    name="Gene Region",
    options=list(PRESETS.keys()),
    value="MYC (chr8)",
    width=250,
)

locus_input = pn.widgets.TextInput(
    name="Custom Locus",
    placeholder="e.g. chr1:1,000,000-2,000,000",
    width=300,
)

go_btn = pn.widgets.Button(name="Go", button_type="primary", width=60)

config_display = pn.pane.JSON({}, name="Current Config", depth=2, height=120)


def navigate_to_preset(event):
    """Navigate by replacing the widget with a fresh Browser."""
    config = PRESETS[event.new]
    browser_pane.object = make_browser(config)
    try:
        import msgspec
        config_display.object = msgspec.to_builtins(config)
    except Exception:
        config_display.object = {"genome": config.genome}

region_select.param.watch(navigate_to_preset, ["value"])


def navigate_to_locus(event):
    """Navigate to a custom locus typed by the user."""
    locus = locus_input.value.strip()
    if not locus:
        return
    config = Config(genome="hg38", locus=locus)
    browser_pane.object = make_browser(config)
    try:
        import msgspec
        config_display.object = msgspec.to_builtins(config)
    except Exception:
        config_display.object = {"genome": "hg38", "locus": locus}

go_btn.on_click(navigate_to_locus)

# Set initial config display
try:
    import msgspec
    config_display.object = msgspec.to_builtins(initial_config)
except Exception:
    config_display.object = {"genome": "hg38"}

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 15px; margin: 8px 0 0 0;">
<strong>Rendering and in-browser interaction work perfectly.</strong>
However, pygv's ESM reads the config once at render time and never syncs
navigation state back to Python.  To "navigate" from Panel, this example
replaces the entire widget, which re-creates the browser.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# pygv -- Genome Browser

An interactive genome browser powered by [igv.js](https://igv.org/doc/igvjs/)
showing the **human reference genome (hg38)**.

## How to Interact

### In the Browser (works immediately)
- **Zoom:** Scroll wheel, or the +/- buttons in the top-left corner
- **Pan:** Click and drag left/right
- **Search:** Type a gene name (e.g. `TP53`) or coordinates in the search box

### From Panel (navigates by re-creating the browser)
- **Gene Region dropdown:** Pick a preset to jump to a well-known cancer gene
- **Custom Locus:** Type coordinates and click **Go**

Note: Changing the region from Panel replaces the widget (brief flash), because
pygv's JavaScript doesn't listen for config updates after initial render.
""")

controls = pn.Column(
    pn.pane.Markdown("### Navigate"),
    region_select,
    pn.Row(locus_input, go_btn),
    pn.pane.Markdown("### Current Config"),
    config_display,
    width=350,
)

pn.Column(
    status,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Genome Browser"),
            browser_pane,
            sizing_mode="stretch_width",
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
