# AnyWidget Pane — Iteration Plan

This document details the 4 remaining iterations for the Panel AnyWidget pane (`panel/pane/anywidget.py`), building on the completed POC, test suite, examples, and eager component creation work.

Draft PR: https://github.com/holoviz/panel/pull/8428

---

## Iteration 1: Edge Cases & Hardening

### Scope

Harden the existing implementation to handle real-world anywidget patterns that the POC does not yet cover. This includes file-based ESM/CSS, additional traitlet types, improved error handling, and defensive checks identified in the code review.

### Deliverables

1. **`_get_model` None handling** — When `object is None`, return a `BkSpacer` (matching the pattern in `panel/pane/plot.py:171` and `panel/pane/holoviews.py:477`) instead of delegating to a bare `AnyWidgetComponent()`.

2. **`_COMPONENT_CACHE` eviction** — Add a bounded cache (e.g., `maxsize=256`) or use `weakref` to prevent unbounded memory growth when many dynamic anywidget classes are created. Consider using an LRU dict or `functools.lru_cache` wrapper. Document the eviction strategy in a code comment.

3. **`_on_param_change` exception handling** — Replace the bare `except Exception: pass` in `_on_param_change` (line 372) with a specific `except traitlets.TraitError` catch, and add `logging.warning()` for unexpected errors. This prevents silent swallowing of real bugs.

4. **`applies()` tightening** — The current duck-typing check (`hasattr(obj, 'traits') and hasattr(type(obj), '_esm')`) can false-positive on non-anywidget objects that happen to have a `traits` method and a class-level `_esm`. Tighten by also checking that `obj` has a `class_traits` method (specific to `traitlets.HasTraits`) or checking `isinstance(obj, traitlets.HasTraits)` with a guarded import.

5. **`Enum` traitlet mapping** — Add `traitlets.Enum` to `TRAITLET_MAP`, mapping to `param.Selector` with `objects` populated from the enum values. Also handle:
   - `traitlets.Set` -> `param.List` (with a note that Set semantics are approximated)
   - `traitlets.Union` -> `param.Parameter` (generic fallback, since Union types are heterogeneous)
   - `traitlets.Instance` -> `param.ClassSelector` (with `class_` set to the instance's `klass`)

6. **File-based `_esm` / `_css` paths** — The current code handles `pathlib.PurePath` but should also handle:
   - `anywidget.experimental.FileContents` — a lazy file reader that acts like a string but watches for file changes. Extract the string value via `str()`.
   - `anywidget._file_contents.VirtualFileContents` — similar to `FileContents`. Extract via `str()`.
   - Plain string paths (e.g., `"./widget.js"`) — detect if the string looks like a file path and read it.
   - Add test coverage for `pathlib.Path` objects.

7. **Display-only widgets** — Some anywidgets have no sync-tagged traitlets (pure display). Ensure the pane handles this gracefully (empty `sync_traits` dict, no watchers set up, component still renders ESM).

### Files to Create/Modify

| File | Changes |
|------|---------|
| `panel/pane/anywidget.py` | Items 1-7 above |
| `panel/tests/pane/test_anywidget.py` | New tests for each item (est. 10-15 new tests) |

### Acceptance Criteria

- `AnyWidget(None).get_root(doc, comm=comm)` returns a valid model (BkSpacer), no error
- `_COMPONENT_CACHE` has a maximum size; old entries are evicted when exceeded
- Setting an invalid traitlet value logs a warning instead of silently passing
- `applies()` returns `False` for objects that have `traits` but are not anywidgets
- `traitlets.Enum`, `traitlets.Set`, `traitlets.Union`, `traitlets.Instance` traitlets are mapped correctly
- File-based `_esm` (pathlib.Path, FileContents) works correctly
- A display-only widget (no sync traits) renders without error
- All existing 20 tests still pass
- New tests pass: `pixi run -e test-312 -- pytest panel/tests/pane/test_anywidget.py -x -v -p no:playwright`

### Dependencies / Blockers

- None. This iteration is self-contained and only modifies the existing pane + tests.

### Estimated Complexity

Medium. 7 distinct changes, each small in scope. Most are 5-20 line changes plus corresponding tests. Total: ~150-200 lines of production code changes, ~200-300 lines of test code.

---

## Iteration 2: Third-Party Anywidget Smoke Tests

### Scope

Add pytest-based smoke tests that verify real third-party anywidget packages work with the AnyWidget pane. These tests validate that the pane correctly handles the diversity of real-world anywidget implementations (different traitlet types, ESM patterns, CSS, bundle sizes).

### Deliverables

1. **Test file**: `panel/tests/pane/test_anywidget_thirdparty.py` containing smoke tests for each supported third-party anywidget.

2. **Widgets to test** (each gated by `pytest.importorskip`):

   | Widget | Package | Key Traits | What to Verify |
   |--------|---------|------------|----------------|
   | `drawdata.ScatterWidget` | `drawdata` | `data` (Dict), `brushsize` (Int) | Instantiation, applies, model creation. Note: bidirectional sync limited by upstream `circle_brush` bug |
   | `ipymario.MarioWidget` | `ipymario` | (Bytes trait) | Instantiation, applies. Note: Bytes trait (`_box`) not JSON-serializable — document limitation |
   | `lonboard.Map` | `lonboard` | Complex nested traits | Instantiation, applies, model creation |
   | `jupyter_scatter.Scatter` | `jscatter` | `x`, `y` (arrays), `color`, `opacity` | Instantiation, applies, model creation, initial values |
   | `wigglystuff.TangleSlider` | `wigglystuff` | `amount` (Float) | Instantiation, applies, model creation. Note: one-way sync limitation |

3. **Test pattern** for each widget:
   ```python
   @pytest.mark.skipif(not importable("drawdata"), reason="drawdata not installed")
   def test_drawdata_smoke(document, comm):
       from drawdata import ScatterWidget
       widget = ScatterWidget()
       pane = AnyWidget(widget)
       assert AnyWidget.applies(widget)
       model = pane.get_root(document, comm=comm)
       assert model is not None
       assert pane.component is not None
   ```

4. **Limitations document**: Update `research/anywidget/todo.md` with a compatibility matrix showing which widgets work fully, partially, or not at all, and why.

### Files to Create/Modify

| File | Changes |
|------|---------|
| `panel/tests/pane/test_anywidget_thirdparty.py` | New file with smoke tests |
| `research/anywidget/todo.md` | Add compatibility matrix |
| `pixi.toml` | Add optional test dependencies for third-party anywidgets (in a dedicated feature or test environment) |

### Acceptance Criteria

- Each smoke test passes when the corresponding package is installed
- Each smoke test is cleanly skipped when the package is not installed
- Tests verify: `applies()`, `get_root()`, `component` creation, and initial trait values where applicable
- Known limitations are documented inline (as comments or `pytest.xfail`) with links to upstream issues
- Tests run with: `pixi run -e test-312 -- pytest panel/tests/pane/test_anywidget_thirdparty.py -x -v -p no:playwright`

### Dependencies / Blockers

- **Iteration 1** should be completed first so that `Enum`, file-based ESM, and other edge cases are handled. Some third-party widgets may exercise these code paths.
- Third-party packages must be installable in the test environment. Consider a separate pixi environment or make tests conditional.

### Estimated Complexity

Low-Medium. Each smoke test is ~15-25 lines. Total: ~150-250 lines of test code. The main challenge is ensuring the right packages are available and handling their diverse traitlet patterns.

---

## Iteration 3: Community Gallery Examples

### Scope

Create a `panel serve`-able example for each widget in the [anywidget community gallery](https://anywidget.dev/en/community/#widgets-gallery). These examples serve as manual integration tests, documentation assets, and a compatibility showcase.

### Deliverables

1. **One example file per widget** in `research/anywidget/examples/`, following the established pattern:
   - Graceful `ImportError` handling with install instructions
   - Explanatory text distinguishing anywidget vs Panel components
   - Run instructions in a comment header
   - Bidirectional sync demo where applicable (Panel widget + anywidget side by side)

2. **Widgets to cover** (top 15 from the gallery, plus already-completed ones):

   | # | Widget | Package | Status | Notes |
   |---|--------|---------|--------|-------|
   | 1 | altair | `altair` | New | Chart with `VegaLite` spec trait |
   | 2 | rerun | `rerun-sdk` | New | 3D visualization — may need special handling for binary data |
   | 3 | drawdata | `drawdata` | Exists | `drawdata_example.py` — update with any iteration 1 fixes |
   | 4 | mosaic | `mosaic-widget` | New | Database-linked visualization |
   | 5 | lonboard | `lonboard` | New | Geospatial vector data — complex nested traitlets |
   | 6 | jupyter-scatter | `jscatter` | New | 2D scatter with millions of points |
   | 7 | quak | `quak` | New | Data profiler |
   | 8 | jupyter-tldraw | `jupyter-tldraw` | New | Whiteboard |
   | 9 | pyobsplot | `pyobsplot` | New | Observable Plot |
   | 10 | vizarr | `vizarr` | New | Zarr image viewer |
   | 11 | ipyaladin | `ipyaladin` | New | Astronomy sky atlas |
   | 12 | higlass | `higlass-python` | New | Genomics visualization |
   | 13 | pygv | `pygv` | New | Genome browser |
   | 14 | vitessce | `vitessce` | New | Spatial single-cell viewer |
   | 15 | cev | `cev` | New | Embedding comparison |
   | 16 | ipymolstar | `ipymolstar` | New | Molecular structure viewer |
   | 17 | weas-widget | `weas-widget` | New | Atomistic structure viewer |
   | 18 | ipymario | `ipymario` | Exists | Update with any iteration 1 fixes |
   | 19 | wigglystuff | `wigglystuff` | Exists | Update with any iteration 1 fixes |
   | 20 | anymap-ts | `anymap-ts` | Exists | Update with any iteration 1 fixes |

3. **Example template**:
   ```python
   """
   Example: <Widget Name> with Panel AnyWidget Pane

   Requirements: pip install <package>
   Run: panel serve <filename>.py
   """
   import panel as pn
   pn.extension()

   try:
       from <package> import <Widget>
   except ImportError:
       # Show install instructions
       ...

   widget = <Widget>(...)
   pane = pn.pane.AnyWidget(widget)

   # Panel controls for bidirectional sync
   ...

   pn.Column(
       "# <Widget Name> — AnyWidget Pane Example",
       pane,
       ...,
   ).servable()
   ```

4. **Compatibility report**: `research/anywidget/compatibility_report.md` documenting the results of testing each widget, including:
   - Whether it renders correctly
   - Whether bidirectional sync works
   - Any errors or limitations
   - Screenshots (via `panel_inspect_app`)

### Files to Create/Modify

| File | Changes |
|------|---------|
| `research/anywidget/examples/<widget>_example.py` | ~15 new example files |
| `research/anywidget/examples/drawdata_example.py` | Update existing |
| `research/anywidget/examples/ipymario_example.py` | Update existing |
| `research/anywidget/examples/wigglystuff_example.py` | Update existing |
| `research/anywidget/examples/anymap_ts_example.py` | Update existing |
| `research/anywidget/compatibility_report.md` | New: compatibility matrix |

### Acceptance Criteria

- Each example file runs without error via `panel serve <file>.py` (when the dependency is installed)
- Each example gracefully handles `ImportError` when the dependency is not installed
- Bidirectional sync is demonstrated where the widget supports it
- Compatibility report documents render status, sync status, and any limitations for all widgets
- Screenshots captured for each working example

### Dependencies / Blockers

- **Iteration 1** must be completed (file-based ESM, Enum traitlets, etc. are exercised by real widgets)
- **Package installation**: Many of these packages have large dependency trees (e.g., `lonboard` requires `geopandas`, `pyarrow`; `rerun-sdk` requires Rust binaries). Some may not be installable in all environments.
- **Bundle size**: Some widgets (e.g., `anymap-ts`) have large ESM bundles that may exceed WebSocket limits. Document these as known limitations.
- **Upstream bugs**: Some widgets have known bugs (drawdata `circle_brush`, wigglystuff one-way sync). Document workarounds.

### Estimated Complexity

Medium-High. Each example is ~30-60 lines, but the real work is in installing packages, debugging rendering issues, and documenting compatibility. Total: ~500-1000 lines of example code, plus the compatibility report.

---

## Iteration 4: Documentation

### Scope

Write official Panel documentation for the AnyWidget pane: a reference page, a how-to guide for using third-party anywidgets, and a pane gallery entry. This makes the feature discoverable and usable by the Panel community.

### Deliverables

1. **Reference page** (`examples/reference/panes/AnyWidget.ipynb`)
   - Already exists as a draft from the POC phase. Needs to be refined:
   - Standard structure matching other pane reference pages (Parameters table, Basic example, Bidirectional sync example, CSS example, `pn.panel()` auto-detection)
   - Use the `CounterWidget` inline example from the docstring
   - Show `pane.component` for param reactivity

2. **How-to guide** (`doc/how_to/custom_components/anywidget_pane.md`)
   - Title: "Use Third-Party Anywidgets in Panel"
   - Sections:
     - Introduction: what the AnyWidget pane does and when to use it vs `AnyWidgetComponent` vs `IPyWidget`
     - Basic usage: `pn.pane.AnyWidget(some_widget)` and `pn.panel(some_widget)`
     - Bidirectional sync: accessing `pane.component` for `param.watch` / `pn.bind` / `.rx`
     - Name collisions: the `w_` prefix convention
     - Limitations and known issues
     - Comparison table: AnyWidget pane vs AnyWidgetComponent vs IPyWidget

3. **Pane gallery entry** (`doc/reference/panes/AnyWidget.md`)
   - Short description and thumbnail for the pane gallery index
   - Link to the full reference notebook

4. **Update `doc/how_to/custom_components/index.md`** to include the new how-to guide.

5. **Update `panel/pane/anywidget.py` docstring** — Ensure the class docstring is complete and follows the standard Panel docstring format (matches what appears on the reference page).

6. **API reference** — Ensure `AnyWidget` appears in the auto-generated API docs by verifying it's exported from `panel/pane/__init__.py` (already done in POC).

### Files to Create/Modify

| File | Changes |
|------|---------|
| `examples/reference/panes/AnyWidget.ipynb` | Refine existing draft |
| `doc/how_to/custom_components/anywidget_pane.md` | New how-to guide |
| `doc/reference/panes/AnyWidget.md` | New gallery entry |
| `doc/how_to/custom_components/index.md` | Add link to new guide |
| `panel/pane/anywidget.py` | Refine docstring |

### Acceptance Criteria

- Reference page renders correctly in the Panel documentation build
- How-to guide is accessible from the custom components section
- AnyWidget appears in the pane gallery with a description
- All code examples in the documentation are runnable
- Documentation builds without warnings: `pixi run -e docs docs-build` (or equivalent)
- Docstring matches the standard Panel format (visible in `help(pn.pane.AnyWidget)`)

### Dependencies / Blockers

- **Iterations 1-3** should be completed first so the documentation reflects the final API and known limitations.
- **Doc build environment**: Need access to the Panel docs build pipeline to verify rendering.
- **Screenshots**: May want to include screenshots from iteration 3 in the documentation.

### Estimated Complexity

Medium. Mostly prose writing with some notebook editing. Total: ~200-400 lines of markdown/notebook content.

---

## Summary & Order of Execution

| Iteration | Title | Depends On | Complexity | Est. Files Changed |
|-----------|-------|------------|------------|-------------------|
| 1 | Edge Cases & Hardening | None | Medium | 2 |
| 2 | Third-Party Smoke Tests | Iteration 1 | Low-Medium | 2-3 |
| 3 | Community Gallery Examples | Iteration 1 | Medium-High | ~20 |
| 4 | Documentation | Iterations 1-3 | Medium | 5 |

Iterations 2 and 3 can potentially be parallelized since they are largely independent (tests vs examples), but both depend on iteration 1's hardening work.
