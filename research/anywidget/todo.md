# Todo: Add AnyWidget Pane

Add a new `AnyWidget` pane (`panel/pane/anywidget.py`) that renders instantiated anywidget objects natively through Panel's ESM/ReactiveESM infrastructure, **bypassing `ipywidgets_bokeh` entirely**.

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
- [ ] **Develop simple POC** that can be manually tested to demonstrate feasibility.
    - Create `panel/pane/anywidget.py` with core pane implementation
    - Register in `panel/pane/__init__.py`
    - Create `examples/reference/panes/AnyWidget.ipynb` with manual test examples
    - Verify: inline ESM anywidget renders, bidirectional sync works, `pn.panel()` auto-detection works
    - Verify: `pane.component` exposes param reactivity (`.param.watch`, `pn.bind`)
    - Test with simple counter widget (no external deps required)
    - Scope: working code, not production-quality. Skip edge cases, advanced features, full test suite.
- [ ] Create Panel AnyWidget Pane feature request with working POC example.
- [ ] Implement in full. Add sufficient tests.
- [ ] Document AnyWidget pane.
- [ ] Clean up.

After each iteration let me review and let us refine the iteration together before moving to the next.
Update this document, research documents, etc. after each iteration.

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
