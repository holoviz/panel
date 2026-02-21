# Add native AnyWidget pane (bypass ipywidgets_bokeh)

## Summary

- Add `AnyWidget` pane that renders anywidget instances natively via ReactiveESM, bypassing `ipywidgets_bokeh`
- Extract ESM/CSS and map traitlets to param Parameters with bidirectional sync and re-entrancy guards
- Duck-typing detection with priority 0.8 (above IPyWidget's 0.6) for automatic `pn.panel()` routing
- Eager `pane.component` creation enables `param.watch`, `pn.bind`, and `.rx` before first render
- Handle name collisions (`w_` prefix), class caching, underscore-prefixed sync traits (e.g. Altair), and proper cleanup on object replacement

## Files Changed

| File | Change |
|---|---|
| `panel/pane/anywidget.py` | New — core AnyWidget pane implementation (~495 lines) |
| `panel/pane/__init__.py` | Import and export `AnyWidget` |
| `panel/tests/pane/test_anywidget.py` | New — 40 unit tests (detection, sync, type mapping, CSS, collisions, cache, cleanup, underscore traits) |
| `panel/tests/pane/test_base.py` | Add `AnyWidget` to `SKIP_PANES` |
| `examples/reference/panes/AnyWidget.ipynb` | New — reference notebook for pane gallery |
| `pixi.toml` | Add `anywidget-examples` feature with third-party deps |
| `research/anywidget/` | Research docs, 26 examples (8 inline + 18 third-party), 3 upstream issue drafts |

## Test Plan

```bash
# Run AnyWidget-specific tests (40 tests)
pixi run -e test-312 -- pytest panel/tests/pane/test_anywidget.py -x -v -p no:playwright

# Verify no regressions in pane base tests
pixi run -e test-312 -- pytest panel/tests/pane/test_base.py -x -v -p no:playwright

# Manual: serve counter example
pixi run -e test-312 -- panel serve research/anywidget/examples/counter.py

# Manual: serve all examples (requires anywidget-examples env)
pixi run -e anywidget -- panel serve research/anywidget/examples/*.py
```

## Known Limitations

| Limitation | Description | Status |
|---|---|---|
| Binary traitlets (`Bytes`) | Not JSON-serializable — widgets like `ipymario` render blank | Future iteration |
| Large ESM bundles (>5MB) | Exceed WebSocket message limits (e.g., `anymap-ts`, `rerun`) | Library should use CDN imports |
| Missing `model.on("change:...")` | Some widgets don't listen for external changes (e.g., `wigglystuff`) | Upstream library bug |
| UI tests | Playwright browser tests not yet added | Future iteration |

## Traitlet Type Mapping

| Traitlet Type | Param Type | Notes |
|---|---|---|
| Bool, CBool | param.Boolean | |
| Int, CInt, Integer, Long, CLong | param.Integer | |
| Float, CFloat | param.Number | |
| Unicode, CUnicode | param.String | |
| Bytes, CBytes | param.Bytes | |
| List | param.List | |
| Set | param.List | Approximated as List |
| Tuple | param.Tuple | |
| Dict | param.Dict | |
| Enum | param.Selector | With `objects` from enum values |
| Instance | param.ClassSelector | Via `klass` attribute |
| Union | param.Parameter | Generic fallback |

## Research & Examples

The `research/anywidget/` directory contains:

- 8 research documents covering architecture, sync, detection, ESM handling, etc.
- 26 runnable example scripts (8 inline ESM + 18 third-party `ext_*`)
- 3 upstream issue drafts for third-party widget bugs discovered during testing

This should be removed before merging but is valuable during implementation and review.

## Upstream Issues Filed

- [anymap-ts#92](https://github.com/opengeos/anymap-ts/issues/92) — 17MB ESM bundle
- [drawdata#34](https://github.com/koaning/drawdata/issues/34) — `circle_brush` ReferenceError
- [wigglystuff#135](https://github.com/koaning/wigglystuff/issues/135) — Missing `model.on("change:amount")`
