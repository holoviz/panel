"""
pygv Example — Minimal Genome Browser with Panel AnyWidget Pane
================================================================

This example demonstrates rendering the pygv minimal genome browser
using Panel's AnyWidget pane. pygv is a lightweight, scriptable
genome browser built with anywidget that uses igv.js for rendering.

The pygv Browser is a genuine anywidget.AnyWidget subclass with a
synced `config` traitlet. The ESM is loaded from a bundled widget.js
file. The package is very small (~18 KB wheel) so ESM size should
not be a problem.

This example displays genome tracks from publicly available remote
URLs. pygv infers track types by file extension.

Required package:
    pip install pygv

Run with:
    panel serve research/anywidget/examples/ext_pygv.py
"""

import pygv

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create a pygv genome browser with remote data
# ---------------------------------------------------------------------------

# Set reference genome and initial locus
pygv.ref("hg38")
pygv.locus("chr8:127,735,434-127,742,951")

# Create a browser with a remote gene annotation track
# pygv.browse() returns a Browser widget (anywidget.AnyWidget subclass)
# with a synced `config` traitlet (Instance of Config)
browser = pygv.browse()

# ---------------------------------------------------------------------------
# 2. Wrap with Panel's AnyWidget pane
# ---------------------------------------------------------------------------

anywidget_pane = pn.pane.AnyWidget(browser, height=700, sizing_mode="stretch_width", styles={"border": "1px solid #ccc", "border-radius": "4px"})

# ---------------------------------------------------------------------------
# 3. Panel controls for genome navigation
# ---------------------------------------------------------------------------

component = anywidget_pane.component

# The `config` traitlet is the main synced state. Since it is an Instance
# type (not a simple dict/string), the param mapping may use a generic
# Parameter. We can display its current value.

config_display = pn.pane.JSON({}, name="Browser Config", height=200, width=400)

if hasattr(component.param, 'config'):
    def on_config_change(*events):
        for event in events:
            if event.name == "config" and event.new is not None:
                try:
                    import msgspec
                    config_dict = msgspec.to_builtins(event.new)
                except Exception:
                    config_dict = str(event.new)
                config_display.object = config_dict

    component.param.watch(on_config_change, ["config"])

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

header = pn.pane.Markdown("""
# pygv Genome Browser -- Panel AnyWidget Pane

This example renders the **pygv** minimal genome browser natively in Panel
using the `AnyWidget` pane. pygv is built with anywidget and uses
[igv.js](https://igv.org/doc/igvjs/) for rendering genomic data.

## How to Interact

- **Zoom:** Scroll wheel or use the +/- controls in the browser
- **Navigate:** Click and drag to pan along the genome
- **Search:** Use the locus search box to jump to a specific region

## About pygv

[pygv](https://github.com/manzt/pygv) is a minimal, scriptable genome
browser for Python by Trevor Manz (the creator of anywidget). It supports:
- Multiple reference genomes (hg38, hg19, mm10, etc.)
- Automatic track type inference from file extensions
- Remote URLs and indexed formats (BAM/BAI, CRAM/CRAI, etc.)
- Custom track configuration via `pygv.track()`

## Widget Details

- **Widget class:** `pygv.Browser` (extends `anywidget.AnyWidget`)
- **Synced traitlet:** `config` (Instance of Config, serialized via msgspec)
- **ESM:** Bundled widget.js (~18 KB package, uses igv.js)
""")

info_section = pn.Column(
    pn.pane.Markdown("### Browser Config State"),
    config_display,
    width=400,
)

pn.Column(
    header,
    anywidget_pane,
    info_section,
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
