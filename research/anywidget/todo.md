# Todo: Add AnyWidget Pane

Add a new `AnyWidget` pane (`panel/pane/anywidget.py`) that renders instantiated anywidget objects natively through Panel's ESM/ReactiveESM infrastructure, **bypassing `ipywidgets_bokeh` entirely**.

Draft PR in https://github.com/holoviz/panel/pull/8428

## Context

Panel currently has two anywidget-related mechanisms:

- **`AnyWidgetComponent`** (`panel/custom.py`): Lets you *author* new components using the AnyWidget API style (provide `_esm`/`_css` as class attributes). This is for *creating* widgets, not for consuming third-party anywidget instances.
- **`IPyWidget` pane** (`panel/pane/ipywidget.py`): Renders ipywidgets (including anywidgets) via `ipywidgets_bokeh`. This has reliability issues and `ipywidgets_bokeh` is not actively maintained.

The new `AnyWidget` pane fills the gap: take an **instantiated** third-party anywidget (e.g. `lonboard.Map()`, `drawdata.ScatterWidget()`) and render it using Panel's own Bokeh model layer.

## Design Decisions

- **Instantiated objects**: The pane accepts instantiated anywidget objects, e.g. `pn.pane.AnyWidget(some_widget)`. It extracts `_esm`/`_css` from the instance's class and bidirectionally syncs traitlets state with the Bokeh model.
- **File location**: `panel/pane/anywidget.py` (separate from ipywidget.py since it avoids ipywidgets_bokeh).
- **Priority**: Higher than `IPyWidget` (which is 0.6) so `pn.panel()` routes anywidget instances to this pane by default.
- **Dependency strategy**: Open question for research phase - whether anywidget should be an optional import with duck-typing fallback, or pure duck-typing (check for `_esm`/`_css` attributes).
- **Environments**: Must work in regular Python server (`panel serve`), Jupyter notebooks, and Pyodide.

## Future Ideas

### AnyWidget subclass pattern

Add a helper function to convert an anywidget class into a `panel.custom.AnyWidgetComponent` subclass with proper `param.Parameter` definitions mapped from traitlets. This would let users do e.g. `MyPanelWidget = pn.pane.anywidget.to_component(SomeAnyWidget)` and get a first-class Panel component with typed params instead of a pane wrapper.

Also support a subclass pattern where users specify `_anywidget_class` as a class attribute:

```python
class MyMap(pn.pane.AnyWidget):
    _anywidget_class = lonboard.Map

map_widget = MyMap(center=[40.7, -74.0], zoom=10)
map_widget.param.watch(callback, ['zoom'])
```

### Pydantic Parameterized wrapper (general architecture)

Similar to the AnyWidget pane wrapping traitlets-based objects, create a `PydanticParameterized` class that wraps a Pydantic `BaseModel` instance and exposes its fields as `param.Parameter` attributes. This would let param/Panel users interact with Pydantic models using familiar methods (`param.bind`, `@param.depends`, `.rx`, etc.).

Like the AnyWidget subclass pattern, support specifying the model class as a class attribute:

```python
class MyConfig(pn.PydanticParameterized):
    _model_class = SomePydanticModel

config = MyConfig(name="example", threshold=0.5)
config.param.watch(callback, ['threshold'])
pn.bind(some_func, config.param.threshold)
```

**Shared architecture**: Both AnyWidget (traitlets → param) and Pydantic (pydantic fields → param) follow the same pattern: take a foreign type system's fields, map them to `param.Parameter` types, dynamically create a Parameterized class, and set up bidirectional sync. If possible, extract a general `ForeignModelAdapter` architecture that both can reuse:

1. **Field enumeration**: enumerate source fields (traitlets via `class_traits(sync=True)`, pydantic via `model_fields`)
2. **Type mapping**: map source field types to `param.Parameter` types
3. **Dynamic class creation**: create a Parameterized subclass with the mapped params
4. **Bidirectional sync**: keep the source object and param object in sync with loop guards
5. **Subclass pattern**: `_model_class` / `_anywidget_class` as class attributes for declarative usage

## Iterations

- [x] Refine feature request
- [x] Deep research the problem. Write research reports to `research/anywidget/`. Summarize findings in `research/anywidget/summary.md`.
    - 8 research tracks completed: traitlet mapping, detection, architecture, sync, pane design, ESM handling, UX reactivity, external issues
    - Key decision: dynamic `AnyWidgetComponent` subclass approach, priority=0.8, duck-typing detection
    - Shadow DOM default off, `w_` prefix for name collisions, `.component` for param reactivity
- [x] **Develop simple POC** that can be manually tested to demonstrate feasibility.
    - Created `panel/pane/anywidget.py` with core pane implementation
    - Registered in `panel/pane/__init__.py` (import + `__all__`)
    - Created `examples/reference/panes/AnyWidget.ipynb` with manual test examples
    - Created `research/anywidget/examples/anywidget_poc_test.py` smoke test (panel serve)
    - Added `AnyWidget` to `SKIP_PANES` in `panel/tests/pane/test_base.py`
    - Verified: inline ESM anywidget renders in browser (screenshot + console logs via MCP)
    - Verified: bidirectional sync works (traitlet <-> component param)
    - Verified: `pn.panel()` auto-detection works (priority 0.8 > IPyWidget 0.6)
    - Verified: `pane.component` exposes param reactivity
    - Verified: all 199 existing pane base tests pass (0 regressions)
    - Key bug fixed: `anywidget.AnyWidget.__init__` calls `add_traits()` which converts
      `_esm` from a string to a traitlet descriptor on a dynamic subclass. Fixed by reading
      ESM/CSS from the **instance** (not class) and caching by the original user-defined class.
- [x] **Add proper test suite** (`panel/tests/pane/test_anywidget.py`)
    - 18 unit tests passing: applies/auto-detection (5), model creation (2), initial values (1),
      bidirectional sync (5 — includes observe callback test), CSS extraction (1),
      name collision (1), cache reuse (1), object replacement (1), cleanup (1)
    - All tests use real `anywidget.AnyWidget` subclasses with inline ESM (no mocks)
    - Run with: `pixi run -e test-312 -- pytest panel/tests/pane/test_anywidget.py -x -v -p no:playwright`
    - UI tests (Playwright) deferred to later iteration
- [x] **Add examples to `research/anywidget/examples/`**
    - 10 standalone `panel serve`-able examples created, each with explaining text,
      clear labels distinguishing anywidget vs Panel components, and run instructions.
    - **Inline ESM examples** (no extra deps, always runnable):
        1. `counter.py` — basic Int traitlet + button click + IntSlider bidirectional sync
        2. `slider.py` — HTML range input + Panel IntSlider + Markdown display, bidirectional sync
        3. `styled_card.py` — CSS styling via `_css` + Unicode traitlets + TextInput sync
        4. `multi_trait.py` — all common traitlet types (Int, Unicode, Bool, List, Dict) with Panel controls
        5. `todo_list.py` — List traitlet with add/remove from both browser and Python side
        6. `canvas_draw.py` — canvas drawing with List traitlet for strokes, Clear button from Python
        7. `toggle_theme.py` — Bool traitlet toggling light/dark CSS themes + Panel Checkbox
        8. `leaflet_map.py` — Leaflet.js map loaded from CDN, click/zoom/center bidirectional sync
    - **Third-party anywidget examples** (require `pip install`, graceful ImportError handling):
        9. `drawdata_example.py` — `drawdata.ScatterWidget()` — documents `circle_brush` init error (drawdata bug)
        10. `ipymario_example.py` — `ipymario.Widget()` — documents Bytes traitlet limitation + fix difficulty
        11. `wigglystuff_example.py` — `wigglystuff.TangleSlider()` — documents one-way sync limitation (no `model.on("change:amount")`)
        12. `anymap_ts_example.py` — `anymap_ts.MapLibreMap()` — documents large ESM bundle limitation (~17MB), not rendered
    - **GitHub issue draft**: `issue_anymap_ts.md` — suggests ESM bundle size reduction to anymap-ts maintainer
    - **Screenshots taken** for all examples via `panel_inspect_app`, saved to `research/anywidget/screenshots/`
    - **Feedback round 2 fixes:**
        - `canvas_draw.py`: Fixed ESM to use immutable array updates (`[...strokes, newStroke]`) so change detection works for Clear
        - `slider.py`: Added Panel IntSlider for bidirectional sync test (same pattern as working counter)
        - `wigglystuff_example.py`: Documented one-way sync limitation (library ESM has no `model.on("change:amount")`), centered TangleSlider
        - `drawdata_example.py`: Documented `circle_brush` initialization error as drawdata library bug
        - `ipymario_example.py`: Added fix difficulty analysis (medium, ~50-100 lines, base64 encode/decode)
        - `anymap_ts_example.py`: Replaced with documentation page (no render attempt), added `leaflet_map.py` alternative
    - **Known limitations documented:**
        - `ipymario`: Binary `traitlets.Bytes` trait (`_box`) not serializable as JSON — renders blank. Fix: medium difficulty (base64 encode/decode)
        - `anymap_ts`: ~17MB ESM bundle causes WebSocket disconnection — not rendered. Fix: library must reduce bundle size
        - `wigglystuff`: TangleSlider ESM has no `model.on("change:amount")` handler — one-way sync only (library limitation)
        - `drawdata`: `circle_brush` initialization error in ESM — breaks bidirectional sync (library bug)
- [x] **Eager component creation + param API**
    - Made `pane.component` available immediately after construction (no render needed)
    - Enables `param.watch`, `pn.bind`, and `.rx` patterns on `pane.component`
    - Updated all 10 examples to use `pane.component.param.watch()` and `pn.bind(func, component.param.x)` instead of `widget.observe()`
    - Added 2 new tests: `test_anywidget_component_eager_creation`, `test_anywidget_sync_before_render`
    - All 20 tests passing
- [x] **Third-party issue drafts** (for filing upstream)
    - `issue_drawdata.md` — `circle_brush` ReferenceError breaks widget init, prevents bidirectional sync
    - `issue_wigglystuff.md` — missing `model.on("change:amount")` handler, external changes don't update display, includes suggested fix
    - `issue_anymap_ts.md` — 17MB ESM bundle causes WebSocket disconnection, suggests CDN loading
- [x] Create Panel AnyWidget Pane feature request with working POC example.
- [ ] Edge cases & hardening: file-based `_esm` paths, `FileContents`/`VirtualFileContents`,
      unmapped traitlet types (`Enum`, `Instance`, `Union`, `Set`), display-only widgets,
      error handling for failed traitlet conversion.
- [ ] Third-party anywidget smoke tests: `ipymario`, `drawdata`, `anywidget-maplibre`, `lonboard`.
- [ ] Add an example to research/anywidget/examples for each anywidget in https://anywidget.dev/en/community/#widgets-gallery. We will use that for manual testing and edge cases.
- [ ] Document AnyWidget pane (how-to guide, pane gallery entry).

After each iteration let me review and let us refine the iteration together before moving to the next.
Update this document, research documents, etc. after each iteration.
Clean up core dump files

## Maybe Later

DON'T DO THIS. LET A HUMAN DO THIS!

- [ ] Jupyter Notebook Testing of all examples in https://anywidget.dev/en/community/#widgets-gallery
- [ ] VS Code Notebook Testing
- [ ] Clean up (`research/`,).

## Acceptance Criteria

- Folder of example code that works:
    - Each example from https://anywidget.dev/en/community/#widgets-gallery included
- Works in regular Python server - apps can be served without issues, verified via screenshot and browser console inspection (pytest UI tests)
- Works in Jupyter notebooks
- Works in Pyodide - example created for manual testing
- Works with panel-live - examples folder and HTML document created for manual testing
- Higher `pn.panel()` priority than `IPyWidget` so anywidget objects route here by default
- Bidirectional traitlet sync: Python-side traitlet changes reflect in browser, browser-side changes reflect in Python traitlets

## Key Files to Understand

| File | Role |
|------|------|
| `panel/custom.py` | `AnyWidgetComponent` - existing component for *authoring* in anywidget style |
| `panel/models/anywidget_component.ts` | TypeScript Bokeh model implementing the anywidget model adapter shim |
| `panel/models/esm.py` | Python-side Bokeh model for `AnyWidgetComponent` |
| `panel/pane/ipywidget.py` | Existing `IPyWidget` pane using `ipywidgets_bokeh` |
| `panel/pane/base.py` | `PaneBase` / `Pane` base classes |
| `panel/reactive.py` | `Syncable` / `Reactive` base - bidirectional Bokeh model sync |
| `panel/viewable.py` | `Viewable` - `servable()`, `show()`, notebook rendering |
| `panel/tests/ui/test_custom.py` | Existing UI tests for `AnyWidgetComponent` variants |

## Resources

- https://github.com/manzt/anywidget - anywidget source
- https://anywidget.dev/ - anywidget docs and widget gallery
    - https://github.com/altair-viz/altair
    - https://github.com/uwdata/mosaic
    - https://github.com/opengeos/anymap-ts
    - https://github.com/developmentseed/lonboard
- https://anywidget.dev/en/community/#widgets-gallery - community widgets to test against
- https://pypi.org/project/ipywidgets-bokeh/ - current Panel ipywidgets bridge (reliability issues, not actively maintained)
- https://github.com/marimo-team/marimo - reactive notebook with strong anywidget support (reference for integration patterns)

## 3rd party issues

- https://github.com/opengeos/anymap-ts/issues/92
- https://github.com/koaning/drawdata/issues/34
- https://github.com/koaning/wigglystuff/issues/135
