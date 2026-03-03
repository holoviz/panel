# drawdata: `circle_brush` initialization error on first render

## Summary

When rendering a drawdata `ScatterWidget` in Panel's AnyWidget pane (or any non-Jupyter environment), the browser console shows:

```
TypeError: Cannot read properties of undefined (reading 'circle_brush')
```

This occurs during the widget's initialization phase. The widget still renders and functions correctly after the initial error, but the console error is visible.

## Context

We are working on Panel's `AnyWidget` pane ([PR #8428](https://github.com/holoviz/panel/pull/8428)) which renders anywidget-based components. The drawdata `ScatterWidget` works correctly with the pane — drawing, clearing, and syncing data all function as expected. However, the initialization error in the console is confusing for users.

## Minimal Reproducible Example

```python
from drawdata import ScatterWidget
import panel as pn

pn.extension()

widget = ScatterWidget()
pn.pane.AnyWidget(widget, height=500, width=600).servable()
```

Running with `panel serve example.py`:

```
TypeError: Cannot read properties of undefined (reading 'circle_brush')
```

The error appears in the console during initialization but does not prevent the widget from working.

## Root Cause

The drawdata ESM attempts to access `circle_brush` on a configuration object that has not been fully initialized yet during the first render cycle. This is a timing issue in the widget's initialization code, not related to the hosting environment.

## Workaround

The error can be safely ignored — the widget functions correctly after initialization completes.

## Environment

- drawdata: latest
- Panel: 1.x (AnyWidget pane)
- Browser: Chrome, Firefox

## Expected Behavior

The widget should initialize without console errors, or the initialization code should gracefully handle the case where `circle_brush` is not yet available.
