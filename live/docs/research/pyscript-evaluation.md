# PyScript Evaluation for Panel Live

**Date:** 2025-02-10
**Status:** POC Complete - Evaluation

## Executive Summary

PyScript provides a well-designed plugin system and convenient `<py-editor>` component, but it is **not a good fit** as the foundation for Panel's browser embedding story. The core issue is that Panel's rendering pipeline requires main-thread DOM access and careful Bokeh document lifecycle management, which conflicts with PyScript's worker-oriented architecture. We would still need to write all the hard parts ourselves, while taking on a significant external dependency.

**Recommendation: Stay independent.** Continue building on panel-embed.js. Selectively borrow ideas from PyScript (plugin architecture, config format) but do not depend on it.

---

## What Was Tested

Three POC files were created in `/home/jovyan/repos/private/panel/live/poc/pyscript/`:

| File | What it tests |
|------|--------------|
| `basic-app.html` | Panel app via `<script type="py">` with inline init code |
| `editor-app.html` | Three approaches: py-editor (worker), main-thread script, custom textarea |
| `panel-pyscript-plugin.js` | PyScript plugin using hooks API for Panel initialization |

---

## Detailed Findings

### 1. Can PyScript's plugin system handle Panel's initialization?

**Partially, but with significant caveats.**

PyScript's plugin lifecycle hooks (`onReady`, `codeBeforeRun`, `onAfterRun`) map reasonably well to Panel's initialization steps:

| Panel Init Step | PyScript Hook | Works? |
|----------------|---------------|--------|
| Load Bokeh JS + Panel JS | `onReady` | Yes, but we can also just use `<script>` tags in `<head>` |
| Install Python wheels | `onReady` or `packages` config | Yes - PyScript's `packages` config handles this natively |
| Set up Bokeh Document | `codeBeforeRun` | Yes - can inject setup code |
| Render .servable() objects | `onAfterRun` | **Problematic** - requires complex DOM manipulation that depends on user code output |
| Load extension resources | `onAfterRun` | Yes, but timing is tricky |

**Key issue:** The `onAfterRun` hook receives `(wrap, element)` but the rendering logic needs to know:
- Whether the user called `.servable()` vs `.servable(target=...)` vs just returned an expression
- Which DOM element to render into
- How to clean up previous renders on re-run

These are application-level concerns that PyScript's generic plugin system cannot anticipate. We end up writing the same `runApp()` logic from panel-embed.js inside the plugin hooks.

### 2. Does py-editor work for Panel code with .servable()?

**No.** This is the biggest blocker.

`<py-editor>` runs code in a **web worker**, which is isolated from the main thread. Panel's rendering pipeline requires:

1. **Main-thread Bokeh document** - `Document()`, `set_curdoc()`, `state.curdoc` all operate on the main thread
2. **DOM access for rendering** - `Bokeh.embed.embed_items()` must run on the main thread to create DOM elements
3. **Bidirectional document linking** - `_link_docs()` connects the Python Bokeh doc to the JS Bokeh doc for reactive updates

Workers can access `pyscript.window` and `pyscript.document` via coincident/Atomics, but this is a **synchronous proxy** that cannot support the asynchronous, callback-heavy rendering Bokeh needs. Specifically:
- `Bokeh.embed.embed_items()` returns Promises and creates complex DOM structures
- Panel's `_link_docs()` sets up event listeners between Python and JS documents
- Widget callbacks need to synchronously update the DOM

**Result:** py-editor can import Panel objects and print/inspect them, but cannot render interactive widgets. For an editable Panel experience, we must build our own editor component that executes on the main thread - exactly what panel-embed.js already does with CodeMirror.

### 3. How does PyScript handle Bokeh JS model loading?

**It does not.** PyScript has no awareness of Bokeh's model system. We must:

1. Load Bokeh JS files (`bokeh.min.js`, `bokeh-widgets.min.js`, `bokeh-tables.min.js`) manually via `<script>` tags or our plugin's `onReady`
2. Load Panel JS (`panel.min.js`) manually
3. After user code runs, scan `Model.model_class_reverse_map` for extension `__javascript__` and `__css__` URLs
4. Dynamically load those resources

This is exactly what `loadJSResources()` and `loadExtensionResources()` do in panel-embed.js. PyScript adds no value here.

### 4. What about Panel extensions (panel-material-ui, etc.)?

Extensions register custom Bokeh models with `__javascript__` and `__css__` class attributes. After user code imports and uses an extension, we must:

1. Detect the new model classes
2. Load their JS/CSS resources
3. Do this **before** calling `Bokeh.embed.embed_items()`

PyScript's `packages` config can install the Python package, but has no mechanism for the JS/CSS resource loading that follows. Our `loadExtensionResources()` function is still required.

### 5. How much control do we lose over the loading UX?

**Significant loss of control.**

| Aspect | panel-embed.js | PyScript |
|--------|---------------|----------|
| Status messages | Full control (`setStatus()`) | PyScript shows its own loading indicators |
| Error display | Custom error rendering in target div | PyScript's error output format |
| Loading order | Sequential, controlled | PyScript decides when to start |
| Multiple apps | Sequential with shared Pyodide | Each `<script type="py">` may get separate interpreter |
| Re-execution | Full cleanup + re-render cycle | No built-in re-execution support |

PyScript's loading UX is designed for generic Python-in-browser use cases. Panel needs domain-specific UX (e.g., "Loading Bokeh JS...", "Installing packages...", "Rendering app...").

---

## What PyScript Gets Right (Ideas to Borrow)

### Configuration Format
PyScript's JSON config inline attribute is clean:
```html
<script type="py" config='{"packages": ["numpy", "pandas"]}'>
```
We could adopt a similar config pattern for `<script type="panel">`.

### Plugin Architecture
The lifecycle hook pattern (`onReady`, `codeBeforeRun`, `onAfterRun`) is well-designed. panel-embed.js could expose a similar extension point for third-party integrations.

### Worker Isolation via coincident
For compute-heavy tasks (not rendering), PyScript's worker model with coincident is elegant. Panel could potentially use a similar approach for non-UI computation while keeping rendering on the main thread.

### Lazy Loading
py-editor doesn't load the interpreter until the run button is clicked. This is a good UX pattern we could adopt for editor mode.

---

## Performance Observations

### Load Time Comparison (Estimated)

| Step | panel-embed.js (direct) | PyScript layer |
|------|------------------------|----------------|
| PyScript core.js | N/A | ~50-100ms additional |
| Pyodide loading | Same (both use same CDN) | Same |
| Package install | Same wheels | Same wheels, but PyScript's resolver may add overhead |
| Panel init | Direct micropip calls | Same, but routed through PyScript's package manager |
| Total overhead | Baseline | +100-300ms from PyScript scaffolding |

PyScript adds a non-trivial layer of abstraction over Pyodide that provides no performance benefit for our use case. The additional download of `core.js` (~150KB gzipped) and its initialization adds measurable overhead.

---

## API Coupling Risk Assessment

### High Risk Areas

1. **Version pinning**: PyScript releases frequently (monthly). Breaking changes in the plugin API, hook signatures, or core behavior would require Panel to update. We'd need to pin to specific PyScript versions and test against each release.

2. **Worker architecture changes**: PyScript's coincident-based worker model is still evolving. Changes to SharedArrayBuffer handling or worker lifecycle could break our plugin.

3. **Editor component**: `<py-editor>` is explicitly labeled as early-stage ("Work on the Python editor is in its early stages"). The API is likely to change significantly.

4. **Config format**: PyScript's config schema has changed between major versions. Our config would need to track their format.

### Medium Risk Areas

5. **CDN availability**: Depending on pyscript.net CDN for core.js. If it goes down, our apps break. (With direct Pyodide, we only depend on jsdelivr/cdn.pyodide.org, which are more established.)

6. **Bundle size**: PyScript's core.js includes MicroPython support, plugin infrastructure, and other features we don't need. This is dead weight.

---

## Worker Support Quality

PyScript's worker support via coincident is well-engineered but **not suitable for Panel rendering**:

- **DOM proxy works** for simple operations (reading values, setting text)
- **DOM proxy fails** for complex operations (Bokeh embed, event listener setup, Canvas rendering)
- **SharedArrayBuffer requirement** means servers need COOP/COEP headers or the mini-coi.js workaround
- **No way to stop a worker** - if user code has an infinite loop in py-editor, the only recourse is page refresh

For Panel's use case, we need main-thread execution for rendering with optional worker offloading for computation. PyScript forces a choice between main-thread (no editor) and worker (no rendering).

---

## What Panel-Specific Code Is Still Needed Even With PyScript

Even if we adopted PyScript as a foundation, we would still need to write and maintain:

1. **Bokeh JS loading** - sequential script loading with version management
2. **Panel JS loading** - CDN URL construction, version pinning
3. **Document lifecycle** - `Document()` creation, `set_curdoc()`, `MockSessionContext`, `doc.hold()`
4. **Extension resource loading** - scanning `Model.model_class_reverse_map`, loading JS/CSS
5. **Three execution branches** - `.servable()` vs `.servable(target=)` vs expression
6. **Render pipeline** - `_doc_json()`, `embed_items()`, `_link_docs()`, `sync_location()`
7. **Cleanup on re-run** - destroying old Bokeh views, resetting document
8. **Custom editor** - CodeMirror integration (py-editor is unusable for Panel)
9. **Package detection** - `find_requirements()` for auto-installing imports
10. **Status/error UX** - domain-specific loading indicators and error display

This is essentially **all of panel-embed.js**. PyScript would provide only the Pyodide initialization and basic script tag parsing, which is ~50 lines of code.

---

## Recommendation

### Do Not Adopt PyScript as a Foundation

The cost/benefit analysis is clear:

| What PyScript provides | Lines of code saved |
|----------------------|-------------------|
| Pyodide loading + init | ~20 lines |
| Package installation via config | ~15 lines |
| Script tag discovery | ~15 lines |
| **Total** | **~50 lines** |

| What we still need to write | Lines of code |
|---------------------------|--------------|
| Everything in panel-embed.js except Pyodide loading | ~1400 lines |

We would save ~50 lines while adding:
- A major external dependency (~150KB)
- Version coupling risk
- Loss of UX control
- Inability to use py-editor for our primary use case
- Additional complexity from working around PyScript's abstractions

### Recommended Approach: Stay Independent, Borrow Ideas

1. **Keep panel-embed.js** as the foundation
2. **Adopt PyScript's config pattern** - allow `config='{...}'` on `<script type="panel">`
3. **Consider a plugin API** - expose lifecycle hooks similar to PyScript's for extensibility
4. **Implement lazy loading** for editor mode (don't load Pyodide until Run is clicked)
5. **Explore worker offloading** for computation using raw Web Workers + coincident (without PyScript's abstraction layer)

### Possible Hybrid Approach (Not Recommended, But Documented)

If the team strongly wants PyScript integration, a hybrid approach could work:
- Use PyScript for main-thread `<script type="py">` execution (basic apps)
- Use our own editor infrastructure (CodeMirror) for editable Panel apps
- Write a PyScript plugin that handles Panel initialization in the `onReady` hook
- Accept the version coupling and UX limitations

This hybrid saves ~50 lines but adds the full dependency risk. Not recommended.

---

## POC File Inventory

```
/home/jovyan/repos/private/panel/live/poc/pyscript/
  basic-app.html              # Panel app via <script type="py"> (works)
  editor-app.html             # Three approaches: py-editor, main-thread, custom textarea
  panel-pyscript-plugin.js    # PyScript plugin for Panel initialization (reference impl)

/home/jovyan/repos/private/panel/live/docs/research/
  pyscript-evaluation.md      # This document
```
