# soupernova: VBox compound widget + astrowidgets import breakage

## Summary

Two issues prevent using soupernova with Panel's AnyWidget pane:

1. **Architecture**: `SouperNova` is an `ipywidgets.VBox`, not a direct `anywidget.AnyWidget`. Panel's AnyWidget pane only supports flat anywidget instances.
2. **Import breakage**: soupernova v0.1.0 imports `from astrowidgets import ImageWidget`, which no longer exists in astrowidgets >= 0.4.

## Issue 1: VBox compound widget (Panel limitation, not an upstream bug)

`SouperNova` inherits from `ipywidgets.VBox` and composes two child widgets:

- `astrowidgets.ImageWidget` -- Ginga-based FITS image viewer
- `soupernova.blast.Detonator` -- a trivial anywidget that fires canvas-confetti

Panel's `pn.pane.AnyWidget` only supports flat `anywidget.AnyWidget` instances. It cannot render compound `ipywidgets.VBox`/`HBox` containers because those require Jupyter's widget manager to resolve `IPY_MODEL_` references between parent and child widgets.

**Workaround**: Use `pn.pane.IPyWidget` with the `ipywidgets_bokeh` package:

```python
import panel as pn
from soupernova import SouperNova

pn.extension("ipywidgets")
widget = SouperNova(file="my_image.fits")
pn.pane.IPyWidget(widget).servable()
```

## Issue 2: astrowidgets >= 0.4 breaks import (upstream bug)

**Repo**: https://github.com/JuanCab/soupernova
**PyPI**: https://pypi.org/project/soupernova/

### Error

```
ImportError: cannot import name 'ImageWidget' from 'astrowidgets'
```

### Root Cause

soupernova v0.1.0's import chain:
```
soupernova/__init__.py
  -> from .blast import SouperNova
       -> from astrowidgets import ImageWidget   # <-- FAILS with astrowidgets >= 0.4
```

`ImageWidget` was removed or renamed in astrowidgets v0.4.0.

### Workaround

Pin astrowidgets to a compatible version:

```
pip install "astrowidgets<0.4"
```

### Suggested Upstream Fix

Either:
1. Update soupernova to use the current astrowidgets API
2. Add a version pin on astrowidgets in soupernova's dependencies: `astrowidgets<0.4`

## Environment

- soupernova: 0.1.0
- astrowidgets: 0.4.0 (broken), <0.4 (works)
- Panel: development branch (enhancement/any-widget)
- Python: 3.12

## Classification

| Category | Details |
|----------|---------|
| Panel AnyWidget compatible | No -- VBox, not a flat anywidget |
| Panel IPyWidget compatible | Yes -- with `ipywidgets_bokeh` |
| Upstream import bug | Yes -- astrowidgets >= 0.4 breaks import |
| Upstream repo | https://github.com/JuanCab/soupernova |
