# Add native AnyWidget pane (bypass ipywidgets_bokeh)

## Summary

- Add `AnyWidget` pane that renders anywidget instances natively via ReactiveESM, bypassing `ipywidgets_bokeh`
- Extract ESM/CSS and map traitlets to param Parameters with bidirectional sync and re-entrancy guards
- Duck-typing detection with priority 0.8 (above IPyWidget's 0.6) for automatic `pn.panel()` routing
- Eager `pane.component` creation enables `param.watch`, `pn.bind`, and `.rx` before first render
- Handle name collisions (`w_` prefix), class caching, and proper cleanup on object replacement

## Files Changed

| File | Change |
|---|---|
| `panel/pane/anywidget.py` | New — core AnyWidget pane implementation (427 lines) |
| `panel/pane/__init__.py` | Import and export `AnyWidget` |
| `panel/tests/pane/test_anywidget.py` | New — 18 unit tests (detection, sync, CSS, collisions, cache, cleanup) |
| `panel/tests/pane/test_base.py` | Add `AnyWidget` to `SKIP_PANES` (uses custom detection, not standard pane init) |

## Test Plan

```bash
# Run AnyWidget-specific tests
pixi run -e test-312 -- pytest panel/tests/pane/test_anywidget.py -x -v -p no:playwright

# Verify no regressions in pane base tests
pixi run -e test-312 -- pytest panel/tests/pane/test_base.py -x -v -p no:playwright

# Manual: serve counter example
pixi run -e test-312 -- panel serve research/anywidget/examples/counter.py
```

## Known Limitations

| Limitation | Description | Status |
|---|---|---|
| Binary traitlets (`Bytes`) | Not JSON-serializable — widgets like `ipymario` render blank | Future iteration |
| Large ESM bundles (>5MB) | Exceed WebSocket message limits (e.g., `anymap-ts`) | Library should use CDN imports |
| Missing `model.on("change:...")` | Some widgets don't listen for external changes (e.g., `wigglystuff`) | Upstream library bug |
| Unmapped trait types | `Enum`, `Instance`, `Union`, `Set` fall back to generic `param.Parameter` | Future iteration |
| UI tests | Playwright browser tests not yet added | Future iteration |

## Research & Examples

The `research/anywidget/` directory contains:
- 8 research documents covering architecture, sync, detection, ESM handling, etc.
- 12 runnable example scripts (8 inline ESM + 4 third-party)
- 3 upstream issue drafts for third-party widget bugs discovered during testing
