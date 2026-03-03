# AnyWidget Examples — Test Summary

**Last updated**: 2026-03-03. 82 unit tests passing. 48 gallery examples across all compatibility tiers. 62 Playwright test files (all 48 examples covered). 14 issue files. 75 anywidget gallery widgets fully triaged (48 examples + 27 SKIP). Using `pixi run -e anywidget` for all dev/testing.

## Gallery Examples (48 total)

### WORKS (Green Banner) — 27 examples

| Example | Sync | Notes |
|---------|------|-------|
| ext_altair.py | Py→Br | Vega-Lite chart with brush selection |
| ext_codeinput.py | Py↔Br | CodeMirror editor. `name` trait → `w_name` |
| ext_cosmograph.py | Py↔Br | Graph visualization with GPU |
| ext_d2widget.py | Py↔Br | D2 diagram renderer |
| ext_graphviz.py | Py↔Br | DOT→SVG via WASM |
| ext_ipyclipboard.py | Br→Py | Browser clipboard paste button |
| ext_ipymafs.py | Py↔Br | Mafs.dev math visualizations (Line, Bezier, Ellipse) |
| ext_ipymolstar.py | Py→Br | Molecular structure viewer |
| ext_ipyscore.py | Py→Br | Music score renderer |
| ext_itables.py | Py→Br | Interactive DataFrames with DataTables.js |
| ext_mapwidget.py | Py↔Br | MapLibre GL maps with lat/lon/zoom sync |
| ext_modraw.py | Py↔Br | Drawing canvas widget |
| ext_mopaint.py | Py→Br | Paint/drawing tool |
| ext_mosaic.py | msg | DuckDB-WASM vega-lite with brush selection |
| ext_moutils.py | Py↔Br | Copy-to-clipboard utility |
| ext_navio.py | Py→Br | Network graph exploration |
| ext_periodictable.py | Py↔Br | Periodic table element picker |
| ext_pyobsplot.py | Py→Br | Observable Plot via pyobsplot |
| ext_vitessce.py | Py→Br | Spatial biology data viewer |
| ext_weaswidget.py | Py↔Br | Crystal structure viewer |
| ext_wigglystuff.py | Py↔Br | 19 interactive widgets (sliders, dials, etc.) |
| ext_bandsplot.py | Py→Br | Electronic band structure plots |
| ext_ipyaladin.py | Py→Br | Sky atlas viewer. Console logs CDN errors from esm.sh (benign) |
| ext_chromospyce.py | Py→Br | 3D chromosome visualization via WebGL |
| ext_bzvisualizer.py | Py↔Br | Brillouin zone 3D viewer. `height`→`w_height`, `width`→`w_width` |
| ext_pglite.py | Py→Br | PostgreSQL WASM in browser |
| ext_tesseract.py | Py→Br | PDF viewer with Tesseract OCR |

### WORKS WITH CAVEATS (Yellow Banner) — 11 examples

| Example | Issue | Notes |
|---------|-------|-------|
| ext_drawdata.py | Console error | `circle_brush` init bug (upstream). Still functional |
| ext_ipymario.py | Headless GPU | Canvas invisible without GPU. Widget renders structurally |
| ext_ipymidi.py | Headless | No visible DOM. MIDI callbacks need Jupyter kernel |
| ext_ipyniivue.py | Compound | Volumes are IPY_MODEL_ refs. Scalar params sync |
| ext_pygv.py | Read-once | Config applied once at creation. Navigate by widget replacement |
| ext_pylifemap.py | Private API | Uses `_to_widget()` to extract anywidget |
| ext_quak.py | COOP/COEP | Full DuckDB profiler needs SharedArrayBuffer headers |
| ext_tldraw.py | Export | Renders, interactive, w/h sync. No drawing content export |
| ext_vizarr.py | CSS | Fixed layer controller text contrast via stylesheet injection |
| ext_xarray_repr.py | Upstream | May fail with newer xarray (`inline_index_repr` signature) |
| ext_pynodewidget.py | React | ReactFlow canvas may render blank. Needs investigation |

### DOES NOT RENDER (Red Banner) — 10 examples

| Example | Root Cause |
|---------|------------|
| ext_anymap_ts.py | ~17 MB ESM bundle exceeds WebSocket limits |
| ext_cev.py | `ipywidgets.VBox`, not `anywidget.AnyWidget` |
| ext_higlass.py | Requires `widget_manager.get_model()` for sub-widgets |
| ext_ipydeck.py | React error #185 — `ReactDOM.render()` fails in shadow DOM |
| ext_ipyreactplayer.py | Bare `import React` + exports React component, not `render()` |
| ext_jbar.py | Upstream ESM issue |
| ext_jupyter_scatter.py | WebGL dimension forwarding fixed but GPU-dependent |
| ext_lonboard.py | Compound widget tree with `IPY_MODEL_` references |
| ext_rerun.py | ~31 MiB WASM bundle exceeds WebSocket limits |
| ext_soupernova.py | `ipywidgets.VBox` compound widget |

## Built-in Test Examples (8 total, all PASS)

| Example | Tests | Status |
|---------|-------|--------|
| counter.py | 3/3 | PASS |
| slider.py | 3/3 | PASS |
| multi_trait.py | 6/6 | PASS |
| styled_card.py | 4/4 | PASS |
| canvas_draw.py | 4/4 | PASS |
| toggle_theme.py | 3/3 | PASS |
| leaflet_map.py | 3/3 | PASS |
| todo_list.py | 5/5 | PASS |

## Protocol Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| model.get/set/save_changes | DONE | Full trait name translation |
| model.on("change:x", cb) | DONE | Value wrapping for Bokeh signals |
| model.on("change", cb) | DONE | Generic change event |
| model.on("msg:custom", cb) | DONE | With buffer decoding + initialize() queuing |
| model.off() | DONE | Full protocol (0, 1, or 2 args) |
| model.send(content, cb?, buffers?) | DONE | Both calling conventions |
| experimental.invoke() | DONE | Full RPC with AbortSignal |
| model.widget_manager | STUB | Warning + rejected Promise |
| Trait name collision | DONE | Panel params + Bokeh reserved names → `w_` prefix |
| Binary transfer (traits) | DONE | Via Bokeh bp.Bytes |
| Binary transfer (messages) | DONE | Via base64 encode/decode |
| Nested bytes in dicts | DONE | Via `_pnl_bytes` marker at depth > 0 |
| CSS support | DONE | Via _stylesheets param |
| Multiple widgets in layout | DONE | Fixed synchronous model restore in render |
| Headless widgets (no render) | DONE | Null guard for `view.render_fn` |
| Undefined value skip | DONE | `set()` skips `undefined` values for Bokeh serializer |

## Regression Test Results

| Test Suite | Count | Status |
|-----------|-------|--------|
| Unit tests (test_anywidget.py) | 82 | ALL PASS |
| Pane base tests (test_base.py) | 199 | ALL PASS |
| Custom component tests (test_custom.py) | 67 | ALL PASS |

## Core Bug Fixes (this branch)

1. **Multiple widgets in layout**: Synchronous model restore in `try/finally` instead of async `.then()`
2. **jupyter-scatter WebGL sizing**: Dimension forwarding for renamed height/width traits
3. **quak msg:custom during initialize()**: Queue handlers when `view=null`, flush on view init
4. **pyobsplot nested bytes**: Base64 encode at depth > 0 with `_pnl_bytes` marker
5. **Vitessce undefined values**: Skip `undefined` in `set()` to avoid Bokeh serialization crash
6. **Sucrase JSX fallback**: Only fall back to raw ESM on actual Sucrase bug patterns, not on `_optionalChain` presence
7. **Headless widgets**: Null guard for `view.render_fn` (ipymidi, etc.)

## Gallery Triage (75 widgets)

All 75 widgets from the [anywidget gallery](https://try.anywidget.dev/) are fully triaged:
- **48 examples** — with status banners, Playwright tests
- **27 SKIP** — documented reasons (not on PyPI, broken, niche, not anywidget, requires special infra/API keys)

## Key Files Modified

- `panel/models/anywidget_component.ts` — Core TS model (+395 lines)
- `panel/pane/anywidget.py` — Python pane implementation (+198 lines)
- `panel/tests/pane/test_anywidget.py` — Unit tests (+417 lines, 82 tests)
- `pixi.toml` — Added sidecar + example deps
