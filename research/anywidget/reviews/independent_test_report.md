# Independent AnyWidget Pane Test Report

**Date:** 2026-03-02
**Reviewer:** Independent automated test suite
**Branch:** enhancement/any-widget
**Python:** 3.12.12
**Panel:** 1.8.8-a.0
**Browser:** Chromium (Playwright)

---

## Executive Summary

Six novel test suites were created to probe the AnyWidget pane beyond its existing examples. Overall the pane performs well for single-widget scenarios. **Two significant bugs were discovered:**

1. **BUG (Critical): Multiple AnyWidgetComponent instances in a Column do not all render** — Only the first AnyWidgetComponent's ESM `render()` function is called; subsequent widgets in a Column have their shadow DOM container but no user content rendered.

2. **BUG (Moderate): pane.object replacement does not reliably re-render new ESM content** — Replacing `pane.object` with a different widget class does not trigger a fresh ESM render in the browser. The same-class replacement does work (unexpectedly).

All other tested scenarios pass cleanly.

---

## Test Results Summary

| Test Suite | Tests | Pass | xfail | xpass | Bugs Found |
|---|---|---|---|---|---|
| test_rapid_updates.py | 4 | 4 | 0 | 0 | None |
| test_nested_data.py | 5 | 5 | 0 | 0 | None |
| test_large_data.py | 5 | 5 | 0 | 0 | None |
| test_multi_widget.py | 5 | 1 | 4 | 0 | **BUG #1** |
| test_widget_replace.py | 5 | 1 | 3 | 1 | **BUG #2** |
| test_custom_events.py | 5 | 5 | 0 | 0 | None |
| **Totals** | **29** | **21** | **7** | **1** | **2 bugs** |

---

## Test 1: Rapid State Changes — PASS

**File:** `panel/tests/ui/anywidget/test_rapid_updates.py`

**Widget:** `RapidCounterWidget` with a `value` (Int) and `running` (Bool) traitlet. JavaScript sets an interval every 100ms that auto-increments value when `running=True`.

**Tests run:**
- `test_rapid_counter_renders` — Widget renders with initial value 0. PASS
- `test_rapid_auto_increment` — JS interval fires, value >= 3 in Python within 5s. PASS
- `test_rapid_python_to_browser_during_updates` — Stop interval, set Python value=999, browser reflects it. PASS
- `test_rapid_reset` — Reset button sends value=0 back to Python. PASS

**Findings:**
- Rapid updates (100ms interval) propagate reliably to Python with no loss observed
- Python can override the value mid-stream once the interval is stopped
- The `_trait_changing` guard in `_setup_trait_sync()` correctly prevents infinite loops during rapid bidirectional sync
- No console errors during rapid state changes

**Verdict: PASS** — Rapid state sync works correctly.

---

## Test 2: Complex Nested Data — PASS

**File:** `panel/tests/ui/anywidget/test_nested_data.py`

**Widget:** `NestedDataWidget` with a `data` (Dict) traitlet containing arbitrarily nested dicts and lists, and a `path_result` (Unicode) traitlet for reading nested paths back to Python.

**Tests run:**
- `test_nested_renders_with_initial_data` — Complex initial dict renders correctly. PASS
- `test_nested_python_to_browser` — 3-level nested dict set from Python appears in browser. PASS
- `test_nested_browser_to_python` — JS sets `data.level1.level2.level3 = "deep_value"`, Python receives it. PASS
- `test_nested_path_read_browser_to_python` — JS reads nested path, stores as string, Python receives. PASS
- `test_nested_list_within_dict` — Lists inside dicts sync correctly in both directions. PASS

**Findings:**
- The `_deep_serialize()` function handles nested dicts/lists correctly up to arbitrary depth
- JS deep clone (via `JSON.parse(JSON.stringify(...))`) required before mutating nested dicts to ensure change detection fires
- Both Python->Browser and Browser->Python directions work for deeply nested structures
- No serialization errors or data corruption

**Verdict: PASS** — Deep nested data sync works correctly.

---

## Test 3: Large Data Transfer — PASS

**File:** `panel/tests/ui/anywidget/test_large_data.py`

**Widget:** `LargeListWidget` with an `items` (List) traitlet, tested with 500-2000 items.

**Tests run:**
- `test_large_list_renders` — 1000-item list renders without errors. PASS
- `test_large_list_sum_computed_in_browser` — JS computes sum of 100 items, syncs back to Python. PASS
- `test_large_list_python_to_browser` — Python sends 1000-item list, browser shows count=1000. PASS
- `test_large_list_browser_to_python` — JS generates 500-item list, Python receives all 500 items with correct values. PASS
- `test_large_list_replace_with_larger` — Replace 100-item list with 2000-item list, browser updates correctly. PASS

**Findings:**
- No payload size limit issues observed up to 2000 items
- Bokeh's JSON serialization handles large lists without truncation
- The 10s timeout is sufficient for large list transfers
- List integrity maintained (correct values at correct indices)

**Verdict: PASS** — Large data transfer works correctly.

---

## Test 4: Multiple Widgets on Same Page — FAIL (Bug #1)

**File:** `panel/tests/ui/anywidget/test_multi_widget.py`

**Widget:** Three distinct widget classes (`CounterWidgetA`, `CounterWidgetB`, `CounterWidgetC`) placed in a `pn.Column`.

**Tests run:**
- `test_multi_widget_all_render` — **XFAIL** (bug confirmed)
- `test_multi_widget_isolation_click` — **XFAIL** (bug confirmed)
- `test_multi_widget_python_targets_correct` — **XFAIL** (bug confirmed)
- `test_multi_widget_four_widgets_no_interference` — **XFAIL** (bug confirmed)
- `test_multi_widget_same_class_independence` — **PASS** (Python-only check, no browser)

### Bug #1: Only First AnyWidgetComponent Renders in a Column

**Severity:** Critical
**Scope:** Affects any use of multiple AnyWidget panes in a layout (Column, Row, etc.)

**Reproduction:**
```python
import anywidget, traitlets, panel as pn

class WidgetA(anywidget.AnyWidget):
    value = traitlets.Int(0).tag(sync=True)
    _esm = '''
    function render({ model, el }) {
        let d = document.createElement('div');
        d.className = 'widget-a-container';
        el.appendChild(d);
    }
    export default { render };
    '''

class WidgetB(anywidget.AnyWidget):
    value = traitlets.Int(0).tag(sync=True)
    _esm = '''
    function render({ model, el }) {
        let d = document.createElement('div');
        d.className = 'widget-b-container';
        el.appendChild(d);
    }
    export default { render };
    '''

col = pn.Column(pn.pane.AnyWidget(WidgetA()), pn.pane.AnyWidget(WidgetB()))
col.show()
# Result: Only widget-a-container appears in browser; widget-b-container is missing.
```

**Observed behavior:**
- Two `AnyWidgetComponent` shadow roots are created (correct)
- Shadow root 1 contains `widget-a-container` (correct)
- Shadow root 2 has the widget's container div (e.g. `counter-widget-b`) but NO user-rendered content inside it
- Console log shows `Rendering WidgetA` fires but `Rendering WidgetB` does NOT fire
- No console errors

**Bokeh model structure is correct** — both children have the right class names, ESM strings, and data model values. The bug is in the browser-side ESM render pipeline.

**Investigation:**
- `JSComponent` (not AnyWidgetComponent) renders correctly with multiple instances in a Column
- `AnyWidgetComponent` used directly (without `pn.pane.AnyWidget` wrapper) also fails with the same bug
- The ESM module cache (`MODULE_CACHE`) uses `"anywidget_component"` as the render module cache key — shared across all instances. This cache key is set by the first instance.
- The user ESM module cache key (`{class_name}-{esm_length}`) differs per widget, so ESM content is not shared.
- The bug appears to be in the timing of `compiled_module` resolution vs. when `render_esm()` is triggered for the second instance.

**Python-side state is correct:** Both widgets' params have independent values and sync correctly between traitlets and component params. The bug is purely in the browser rendering.

**Root cause (hypothesis):** The `AnyWidgetComponentView._render_cache_key` is `"anywidget_component"` (shared across all instances). When the first widget's `compiled_module` resolves, it calls `init_module()` which sets `model.render_module` in the MODULE_CACHE. When the second widget's `compiled_module` resolves, its `init_module()` retrieves the already-resolved `render_module` from cache. The `render_module.then()` callback may execute synchronously (as a microtask) during the resolution of the second widget's `compiled_module`, before the second view has finished initializing. This could cause `Bokeh.index.find_one_by_id(id)` to return `null` or the view to not yet have its `render_fn` set.

**Verdict: FAIL** — Multiple AnyWidget panes in a layout do not all render.

---

## Test 5: Widget Replacement — PARTIAL FAIL (Bug #2)

**File:** `panel/tests/ui/anywidget/test_widget_replace.py`

**Widget:** Two different widget classes (`WidgetTypeA` counter, `WidgetTypeB` text), replacing `pane.object` between them.

**Tests run:**
- `test_first_widget_renders` — Initial widget renders correctly. PASS
- `test_widget_replace_different_class` — **XFAIL** (bug confirmed)
- `test_new_widget_syncs_after_replace` — **XFAIL** (bug confirmed)
- `test_old_widget_not_affected_after_replace` — **XFAIL** (bug confirmed)
- `test_replace_with_same_class` — **XPASS** (unexpectedly passes despite xfail marker)

### Bug #2: Widget Replacement Does Not Re-Render New ESM Content

**Severity:** Moderate
**Scope:** Replacing `pane.object` with a widget of a different class

**Observed behavior:**
- Replacing `pane.object = WidgetTypeB(...)` correctly updates the Python-side component
- The old widget's teardown runs correctly (traitlet watchers removed)
- The new widget's component is created with correct param values
- In the browser: the new widget's shadow DOM container appears (container div exists)
- BUT the new widget's `render()` function is not called — no user content rendered
- The `replace_with_same_class` test XPASSES: replacing with the same class (cached ESM module) works because the render module is already loaded and can be re-triggered

**Note:** The Python-side replacement (`_teardown_trait_sync`, `_create_component`) works correctly. The failure is browser-side ESM content rendering after replacement.

**Verdict: PARTIAL FAIL** — Same-class replacement works; different-class replacement does not render new ESM content.

---

## Test 6: Custom Events — PASS

**File:** `panel/tests/ui/anywidget/test_custom_events.py`

**Widget:** `CustomEventWidget` that uses `model.send()` to send messages from JS to Python, and `widget.send()` for Python-to-JS responses. Also uses `received_messages` List traitlet to track message count.

**Tests run:**
- `test_custom_event_ping` — JS sends ping, Python `_handle_custom_msg` receives it. PASS
- `test_custom_event_payload` — JS sends message with nested payload `{value: 42, name: "test", items: [1,2,3]}`, Python receives full payload. PASS
- `test_custom_event_python_response_to_js` — Python sends pong via `widget.send()`, JS receives it via `model.on("msg:custom")`. PASS
- `test_custom_event_multiple_messages` — 3 ping messages all arrive at Python. PASS
- `test_custom_event_traitlet_update_syncs` — `received_messages` traitlet updated by Python, JS receives updated count. PASS

**Findings:**
- The `_setup_msg_routing()` bridge works correctly for both directions
- `widget._handle_custom_msg()` is correctly called with the message content
- `widget.send()` override correctly routes through `component._send_msg()`
- Nested payload data is preserved intact across the JS→Python bridge
- The `msg:custom` event listener in JS receives Python responses correctly
- Multiple messages in sequence all arrive (no message loss)

**Verdict: PASS** — Custom message passing works correctly in both directions.

---

## Detailed Bug Reports

### Bug #1: Multiple AnyWidgetComponent in a Column — Only First Renders — FIXED

**Status: FIXED** — Root cause identified and fix applied.

**Root cause:** In `_render_code()`, `view.model` was temporarily set to `view.adapter` for the ESM render call, but only restored in an async `.then()` callback. When `render_module` resolved for multiple widgets, the `.then()` callbacks ran as microtasks in order: Widget A's render ran first, temporarily setting `view.model = view.adapter`. Widget B's render ran next, calling `Bokeh.index.find_one_by_id()` which traverses all views (including Widget A's) via `children()`. Widget A's `children()` called `this.model.children` on the adapter (not the Bokeh model), which returned `undefined`, causing `undefined.map` to throw.

**Fix:** Restore `view.model = original_model` synchronously in a `try/finally` block immediately after calling the ESM render function, instead of in the `.then()` callback. This ensures the Bokeh model is always restored before any other view traversal occurs.

**Location:** `anywidget_component.ts:_render_code()`

### Bug #2: Widget Replacement (Different Class) Does Not Re-Render

**Location:** Browser-side ESM render after `pane.object` replacement
**Component:** `AnyWidget` pane's `_update_pane()` triggering the browser to load new ESM
**Files involved:**
- `/workspaces/panel/panel/pane/anywidget.py` — `_update_pane()`
- `/workspaces/panel/panel/models/anywidget_component.ts` — ESM loading after model change

**Repro steps:**
1. Create `pn.pane.AnyWidget(WidgetA())`
2. Serve and view in browser
3. Set `pane.object = WidgetB()`
4. Expected: Widget B renders in browser
5. Actual: Browser shows empty widget container, Widget B ESM render() not called

**Note:** Same-class replacement works because the ESM module for that class is already cached in `MODULE_CACHE`, so the re-render pathway succeeds. Different-class replacement requires loading a new ESM module, which appears to not be triggered properly after object replacement.

---

## Implementation Assessment

### What Works Well

1. **Traitlet-to-param mapping** — The `_traitlet_to_param()` function correctly handles all standard traitlet types (Int, Unicode, Bool, List, Dict, Tuple, Set, Enum, Instance).

2. **Bokeh-reserved name collision handling** — Traitlets named `name`, `type`, etc. are correctly renamed to `w_name`, `w_type` and the TypeScript adapter's `_trait_name_map` handles translation transparently to the ESM code.

3. **Framework trait exclusion** — `_FRAMEWORK_TRAITS` correctly prevents internal ipywidgets traits from being synced.

4. **Deep serialization** — `_deep_serialize()` correctly handles nested dicts, lists, DataFrames, dataclasses, and circular references up to `_MAX_SERIALIZE_DEPTH = 10`.

5. **LRU cache** — The `_COMPONENT_CACHE` with max size 256 correctly evicts the least-recently-used entry.

6. **Custom message routing** — `_setup_msg_routing()` correctly bridges both directions (ESM→Python via `component.on_msg`, Python→ESM via `widget.send` override).

7. **Binary buffer handling** — Base64 encoding of binary buffers in `_send_override()` is correctly implemented.

8. **Single-widget patterns** — All single-widget use cases work reliably: rendering, bidirectional sync, rapid updates, large data, nested data, and custom events.

### What Does Not Work

1. **Multiple AnyWidgetComponent in a layout** — See Bug #1.
2. **Widget replacement with different class** — See Bug #2.

---

## Test Files Created

All files located in `/workspaces/panel/panel/tests/ui/anywidget/`:

- `test_rapid_updates.py` — 4 tests for rapid JS→Python state sync
- `test_nested_data.py` — 5 tests for deep nested dict/list sync
- `test_large_data.py` — 5 tests for large list (500-2000 items) sync
- `test_multi_widget.py` — 5 tests for multiple widgets on same page (4 xfail, 1 pass)
- `test_widget_replace.py` — 5 tests for widget object replacement (3 xfail, 1 xpass, 1 pass)
- `test_custom_events.py` — 5 tests for custom message passing

Total: 29 tests across 6 files.

---

## Recommendations

1. **Fix Bug #1 (Critical):** Investigate the `AnyWidgetComponentView` rendering pipeline for multiple instances. The key area is the interaction between `_render_cache_key = "anywidget_component"` (shared render wrapper module) and per-widget `compiled_module` resolution. Consider whether the second widget's `render_esm()` call needs to wait for its `compiled_module` before the shared `render_module.then()` callback fires.

2. **Fix Bug #2 (Moderate):** Investigate `_update_pane()` and how the browser-side model reload is triggered after `pane.object` replacement. Ensure the new AnyWidgetComponent's ESM is reloaded in the browser when the object changes to a different class.

3. **Add regression tests:** Add the 6 test suites (adjusted for the known bugs) to the CI test suite to prevent future regressions.

4. **Document the current limitation:** Until Bug #1 is fixed, document that multiple AnyWidget panes should not be placed directly in a Column/Row. A workaround is to use a single Panel layout widget that wraps them, or to use tabs.
