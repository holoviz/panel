"""
Tesseract PDF.js Example — PDF Viewer with OCR
================================================

This example demonstrates using jupyter-anywidget-tesseract-pdfjs with Panel's
AnyWidget pane. The widget provides a PDF viewer with Tesseract.js OCR
capabilities, all running in the browser.

GitHub: https://github.com/nickmcintyre/jupyter-anywidget-tesseract-pdfjs

Key traitlets:
    - value (Int): Counter/state value for the widget

Required package:
    pip install jupyter-anywidget-tesseract-pdfjs

Run with:
    panel serve research/anywidget/examples/ext_tesseract.py
"""

from jupyter_anywidget_tesseract_pdfjs import Widget as TesseractWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create the Tesseract PDF.js widget
# ---------------------------------------------------------------------------

widget = TesseractWidget()

# Wrap with Panel's AnyWidget pane
anywidget_pane = pn.pane.AnyWidget(widget, height=600, sizing_mode="stretch_width")
component = anywidget_pane.component

# ---------------------------------------------------------------------------
# 2. Controls
# ---------------------------------------------------------------------------

value_display = pn.pane.Markdown(
    pn.bind(
        lambda v: f"**Widget value:** {v}",
        component.param.value,
    ),
    sizing_mode="stretch_width",
)

# ---------------------------------------------------------------------------
# 3. Layout
# ---------------------------------------------------------------------------

status = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
The Tesseract PDF.js widget provides a PDF viewer with OCR capabilities,
all running client-side in the browser via WebAssembly.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# jupyter-anywidget-tesseract-pdfjs — PDF Viewer with OCR

[GitHub](https://github.com/nickmcintyre/jupyter-anywidget-tesseract-pdfjs)

View PDFs and run OCR (Optical Character Recognition) directly in the browser
using Tesseract.js and PDF.js compiled to WebAssembly.

## How to Test

1. The widget should render a PDF viewer interface.
2. Use the built-in controls to navigate pages.
3. The OCR functionality processes text from PDF pages.
""", sizing_mode="stretch_width")

pn.Column(
    status,
    header,
    pn.pane.Markdown("### PDF Viewer"),
    anywidget_pane,
    value_display,
    sizing_mode="stretch_width",
    max_width=1200,
).servable()
