"""
soupernova Example -- Astronomical Image Viewer
================================================

This example documents soupernova's compatibility status with Panel.

STATUS: NOT COMPATIBLE with ``pn.pane.AnyWidget``

Architecture issue
------------------
``soupernova.SouperNova`` is an **ipywidgets.VBox** (compound widget),
NOT a direct ``anywidget.AnyWidget``. It internally composes:

  - ``astrowidgets.ImageWidget`` -- a Ginga-based FITS image viewer
  - ``soupernova.blast.Detonator`` -- a trivial anywidget that fires
    canvas-confetti on click (no useful synced traits)

Panel's ``AnyWidget`` pane only supports flat anywidget instances, not
compound ``ipywidgets.VBox``/``HBox`` containers. For compound widgets,
use ``pn.pane.IPyWidget`` backed by ``ipywidgets_bokeh`` instead::

    pip install ipywidgets_bokeh
    pn.pane.IPyWidget(SouperNova(file="image.fits"))

Import issue (astrowidgets >= 0.4)
-----------------------------------
soupernova v0.1.0 imports ``from astrowidgets import ImageWidget``, but
astrowidgets v0.4.0 removed/renamed ``ImageWidget``, breaking the import.
Pinning ``astrowidgets<0.4`` fixes the import but doesn't help with the
VBox issue above.

GitHub: https://github.com/JuanCab/soupernova
PyPI:   https://pypi.org/project/soupernova/

Required packages:
    pip install soupernova astrowidgets astropy ipywidgets_bokeh

Run with:
    panel serve research/anywidget/examples/ext_soupernova.py
"""

import panel as pn

pn.extension()

# =====================================================================
# Attempt to import soupernova
# =====================================================================

import_error = None
try:
    from soupernova import SouperNova  # noqa: F401
except ImportError as exc:
    import_error = str(exc)

# =====================================================================
# Layout -- show status and explanation
# =====================================================================

status = pn.pane.Markdown("""
<div style="background-color: #f8d7da; border: 2px solid #dc3545; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #721c24; font-size: 20px; font-weight: bold; margin: 0;">
DOES NOT RENDER
</p>
<p style="color: #721c24; font-size: 14px; margin: 8px 0 0 0;">
<strong>soupernova.SouperNova</strong> is an <code>ipywidgets.VBox</code>
(compound widget), not a direct <code>anywidget.AnyWidget</code>.
Use <code>pn.pane.IPyWidget</code> with <code>ipywidgets_bokeh</code> instead.
</p>
</div>
""", sizing_mode="stretch_width")

details = pn.pane.Markdown(f"""
# soupernova -- Astronomical Image Viewer

[GitHub](https://github.com/JuanCab/soupernova) |
[PyPI](https://pypi.org/project/soupernova/)

## Why AnyWidget Pane Cannot Be Used

`SouperNova` is an **`ipywidgets.VBox`** that composes two child widgets:

1. **`astrowidgets.ImageWidget`** -- a Ginga-based FITS image viewer
2. **`soupernova.blast.Detonator`** -- a minimal anywidget that fires
   canvas-confetti on click (no useful synced traits)

Panel's `AnyWidget` pane only supports **flat anywidget instances**
(classes that directly extend `anywidget.AnyWidget`). It cannot render
compound `ipywidgets.VBox` or `HBox` containers because those require
Jupyter's widget manager to resolve `IPY_MODEL_` references between
parent and child widgets.

## How to Use With Panel

Use **`pn.pane.IPyWidget`** backed by the **`ipywidgets_bokeh`** package,
which provides full Jupyter widget support including compound widgets:

```python
pip install ipywidgets_bokeh

import panel as pn
from soupernova import SouperNova

pn.extension("ipywidgets")
widget = SouperNova(file="my_image.fits")
pn.pane.IPyWidget(widget).servable()
```

## Additional Issue: astrowidgets >= 0.4

{f'**Current status:** Import fails with `{import_error}`' if import_error else '**Current status:** Import succeeded.'}

soupernova v0.1.0 depends on `astrowidgets.ImageWidget`, which was
removed in astrowidgets v0.4.0. Pinning `astrowidgets<0.4` restores the
import, but the VBox issue above remains -- you still need `ipywidgets_bokeh`.

## Summary

| Aspect | Status |
|--------|--------|
| `pn.pane.AnyWidget` | Not supported (VBox, not a flat anywidget) |
| `pn.pane.IPyWidget` | Supported (with `ipywidgets_bokeh`) |
| astrowidgets >= 0.4 | Breaks import (pin `<0.4` or wait for upstream fix) |
| Detonator (child) | Trivial anywidget, no useful traits to sync |
""", sizing_mode="stretch_width")

pn.Column(
    status,
    details,
    sizing_mode="stretch_width",
    max_width=900,
).servable()
