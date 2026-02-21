# External Issues Research: marimo and ipywidgets_bokeh

This report catalogs anywidget-related issues from the marimo and ipywidgets_bokeh projects, evaluates their relevance to Panel's proposed native AnyWidget pane, and identifies risks or mitigations needed.

---

## 1. marimo AnyWidget Issues

marimo implements anywidget support via `mo.ui.anywidget()`, using its own comm-like protocol rather than ipywidgets infrastructure. The issues found reveal integration pain points that any non-Jupyter host (including Panel) must address.

### 1.1 Binary Data / Buffer Handling (marimo#2506)

**Source**: https://github.com/marimo-team/marimo/issues/2506

**Problem**: Binary data from `traitlets.Bytes` traits was not correctly transmitted to the frontend. Specifically, bytes read from image files arrived as incorrect types on the JavaScript side (`DataView` check returned `false`), while bytes from `numpy.tobytes()` worked correctly. The root cause was a JSON encoding bug in marimo's serialization layer that mishandled certain byte sequences. A follow-up bug also surfaced: updating a `Bytes` trait alongside other traits caused a `TraitError` because the bytes value was deserialized as an empty dict during multi-trait updates.

**Resolution**: Two PRs were needed -- one fixing JSON encoding of PNG binary data (marimo#2517) and another fixing bytes handling during concurrent trait updates (marimo#2557).

**Relevance to Panel**: HIGH. Panel's AnyWidget pane maps `traitlets.Bytes` to `param.Bytes`, which maps to `bp.Nullable(bp.Bytes)` in the Bokeh model. Bokeh transmits `bp.Bytes` as binary websocket frames (not JSON), which avoids the JSON encoding pitfall that affected marimo. On the frontend, Panel's `AnyWidgetAdapter.get()` method in `anywidget_component.ts` converts `ArrayBuffer` to `DataView` before returning values to widget code, matching the anywidget convention. **Panel's architecture addresses this issue natively** because Bokeh's binary protocol avoids the JSON serialization path that caused marimo's bug.

**Mitigation needed**: Ensure the `AnyWidgetAdapter.get()` DataView conversion handles edge cases (zero-length buffers, null values). Add a test for binary round-trip with image file bytes.

---

### 1.2 Callback Signature Incompatibility (marimo#7989)

**Source**: https://github.com/marimo-team/marimo/issues/7989

**Problem**: The `model.on("change:prop", callback)` API has inconsistent callback signatures across hosts. Jupyter (via Backbone.js) passes three arguments: `(model, newValue, options)`. marimo passes one argument: `(newValue)`. The anywidget author clarified the intended signature is `() => void` -- a no-argument function where values are retrieved via `model.get()`. However, existing widgets like Altair's vegawidget rely on the three-argument Backbone convention, causing breakage on non-Jupyter hosts.

**Resolution**: Open issue. The anywidget project recommends `() => void` callbacks that use `model.get()` internally.

**Relevance to Panel**: MEDIUM. Panel's `AnyWidgetAdapter.on()` in `anywidget_component.ts:59-92` fires the callback with zero arguments for `"change:*"` events. This matches the recommended anywidget AFM specification. Widgets that depend on the three-argument Backbone signature will fail on Panel the same way they fail on marimo. This is considered acceptable behavior per the anywidget spec.

**Mitigation needed**: Document this known incompatibility. Consider adding a compatibility shim that passes `(undefined, model.get(prop), {})` as arguments if a widget is known to use the Backbone convention, but this should NOT be the default.

---

### 1.3 ESM Hot Reload Failures (marimo#3018)

**Source**: https://github.com/marimo-team/marimo/issues/3018

**Problem**: If an anywidget's `_esm` code has a syntax error on first evaluation, fixing the code and re-running the cell did not update the rendered widget. The stale (broken) ESM was cached, and marimo did not invalidate it on definition change.

**Resolution**: Fixed in marimo#3022 by allowing re-rendering when `_esm` changes.

**Relevance to Panel**: LOW for the pane (which wraps existing anywidget instances, not develops them), but MEDIUM for `AnyWidgetComponent` users who develop widgets directly. Panel's frontend module cache (`MODULE_CACHE` in `reactive_esm.ts`) keys modules by `class_name-esm_length` or bundle hash. If the ESM string changes, the cache key changes, and the module is recompiled. For the AnyWidget pane specifically, the ESM is extracted once when the component class is created, so it would not automatically pick up changes to the anywidget's `_esm` trait. However, Panel's `_watch_esm()` mechanism supports HMR for file-based ESM.

**Mitigation needed**: For `AnyWidgetComponent` users developing widgets: no action needed (Panel already handles ESM changes). For the AnyWidget pane wrapping `FileContents`-based widgets: consider connecting to the `FileContents.changed` signal to trigger ESM updates (deferred to future HMR support).

---

### 1.4 Shadow DOM Styling Isolation (marimo#6026)

**Source**: https://github.com/marimo-team/marimo/issues/6026

**Problem**: marimo uses Shadow DOM to isolate widget styling from the host page. This caused PrimeVue component styles to be stripped -- buttons and icons appeared unstyled. The workaround required manually injecting stylesheets into the ShadowDOM's `adoptedStyleSheets` rather than appending `<link>` or `<style>` elements as children.

**Resolution**: Closed with documented workarounds (use web components, or manually inject stylesheets into the shadow root).

**Relevance to Panel**: MEDIUM. Panel's `AnyWidgetComponent` uses Shadow DOM by default (`use_shadow_dom = True`). Anywidgets that inject global CSS via `document.head.appendChild()` or rely on CSS inheritance from the host page will be affected. However, Panel provides two mitigations:
1. The `_css` attribute from anywidgets is injected into the component's stylesheets pipeline, which Panel applies correctly within the shadow root.
2. Users can set `use_shadow_dom = False` on the dynamic component class if shadow DOM isolation causes problems.

**Mitigation needed**: When creating the dynamic component class, if the anywidget defines `_css`, ensure it is injected via `_stylesheets` which Panel applies within the shadow root. Document that `use_shadow_dom` can be overridden for widgets with complex styling needs. Consider defaulting to `use_shadow_dom = False` for the AnyWidget pane since anywidgets designed for Jupyter do not expect shadow DOM isolation.

---

### 1.5 Shadow DOM API Incompatibility (marimo#2196)

**Source**: https://github.com/marimo-team/marimo/issues/2196

**Problem**: The `document.getSelection()` browser API does not work within Shadow DOM in Chromium browsers. A text annotation widget that relied on `getSelection()` worked in Jupyter (no shadow DOM) but failed in marimo (shadow DOM). The behavior is inconsistent across browsers: Chromium requires `ShadowRoot.getSelection()` (non-standard), Firefox's `document.getSelection()` pierces shadow DOM, and Safari supports `Selection.getComposedRanges()` in v17+.

**Resolution**: Closed as NOT_PLANNED (browser API limitation).

**Relevance to Panel**: MEDIUM. Same issue applies if Panel uses Shadow DOM. Any anywidget that uses `document.getSelection()`, `document.activeElement`, `document.elementFromPoint()`, or other APIs that don't pierce Shadow DOM will have issues.

**Mitigation needed**: Same as 1.4 -- consider defaulting `use_shadow_dom = False` for the AnyWidget pane. If Shadow DOM is used, document the known browser API limitations.

---

### 1.6 Static Asset Serving (marimo#3279)

**Source**: https://github.com/marimo-team/marimo/issues/3279

**Problem**: Anywidgets that use web workers, WASM binaries, or other static assets (loaded via `new URL("./file.js", import.meta.url)`) cannot resolve these paths correctly. The bundled ESM tries to load workers from relative paths, but `import.meta.url` resolves to a blob URL or a marimo-specific route, making relative resolution fail.

**Resolution**: Open issue, labeled "upstream". Partially dependent on anywidget ecosystem standardization.

**Relevance to Panel**: MEDIUM. Panel serves ESM via blob URLs (when inline) or server-relative URLs (when file-based). For blob URLs, `import.meta.url` resolves to `blob:...`, and relative paths from that base will fail. For server-served bundles, `import.meta.url` resolves to the server URL, and relative paths should work if the assets are co-located. This is a fundamental challenge for any host that loads ESM from non-file URLs.

**Mitigation needed**: For anywidgets that ship bundled JS (the common case for published packages), assets are typically inlined in the bundle and this is not an issue. For widgets that use separate worker/WASM files, Panel should:
1. Support serving the widget's directory as static files (similar to `_bundle_path` serving).
2. Document that widgets relying on `import.meta.url`-relative asset loading may need their ESM served as a file rather than inline.

---

### 1.7 Fine-Grained Trait Observation (marimo#2976)

**Source**: https://github.com/marimo-team/marimo/issues/2976

**Problem**: Users wanted to observe specific traitlet changes without triggering on all trait changes. In marimo's cell execution model, any change to a tracked widget re-runs the cell.

**Resolution**: Closed as not planned; workaround using `mo.state()` with targeted `widget.observe()` calls.

**Relevance to Panel**: NOT APPLICABLE. Panel's param system natively supports watching specific parameters via `component.param.watch(cb, ['specific_param'])`. The UX design (Track 7) exposes `pane.component` which provides full param.watch/pn.bind/rx support on individual parameters. This is a non-issue for Panel.

---

### 1.8 Widget API Discoverability (marimo#2916)

**Source**: https://github.com/marimo-team/marimo/issues/2916

**Problem**: `mo.ui.anywidget` does not expose the wrapped widget's API (traitlet names, types, docs) in IDE autocompletion.

**Resolution**: Closed as not planned.

**Relevance to Panel**: LOW. Panel's `pane.component` exposes param Parameters, which have metadata (type, default, doc). However, dynamic class creation means IDE autocompletion will not know the specific params. The subclass pattern (Option E from Track 7) provides better discoverability for library authors who define typed wrappers.

**Mitigation needed**: None required for initial implementation. The subclass pattern (`class MyMap(pn.pane.AnyWidget): _anywidget_class = lonboard.Map`) provides static typing for those who need it.

---

## 2. ipywidgets_bokeh Issues

ipywidgets_bokeh is the current mechanism for embedding ipywidgets (including anywidgets) in Panel/Bokeh. It implements a full ipywidgets comm/kernel shim in the browser. The issues found strongly motivate building a native Panel solution.

### 2.1 anywidget Not Working (ipywidgets_bokeh#89)

**Source**: https://github.com/bokeh/ipywidgets_bokeh/issues/89

**Problem**: Basic anywidget examples failed with the error `"Class null not found in module @jupyter-widgets/base@2.0.0"` when served via `panel serve`. The issue was that the widget's initial state was not fully embedded on first render, causing the frontend to fail when looking up the widget class.

**Resolution**: Fixed in PR#97 ("Embed full state on initial render"), June 2023.

**Relevance to Panel**: HIGH (motivation). This issue illustrates the fragility of the ipywidgets comm protocol approach. The fix required deep changes to state serialization timing. Panel's native AnyWidget pane bypasses this entirely -- it does not use the ipywidgets comm protocol or widget manager. ESM code and state are transmitted through Panel's own Bokeh model sync, which is well-tested and reliable.

---

### 2.2 ArrayBuffer Serialization Failure (ipywidgets_bokeh#46)

**Source**: https://github.com/bokeh/ipywidgets_bokeh/issues/46

**Problem**: VegaFusionWidget (which uses WASM and generates `ArrayBuffer` objects) failed with `"[object ArrayBuffer] is not serializable"`. Bokeh's `to_serializable()` function could not handle binary `ArrayBuffer` data passed through the ipywidgets_bokeh bridge.

**Resolution**: OPEN (since January 2022).

**Relevance to Panel**: HIGH (motivation). This demonstrates a fundamental limitation of the ipywidgets_bokeh approach: it serializes widget state through Bokeh's JSON serialization pipeline, which cannot handle binary data types like `ArrayBuffer`. Panel's native AnyWidget pane avoids this because:
1. Binary data (`param.Bytes` / `bp.Bytes`) is transmitted as binary websocket frames by Bokeh, not JSON.
2. The `AnyWidgetAdapter.get()` method converts `ArrayBuffer` to `DataView` on the frontend, matching the anywidget convention.
3. There is no intermediate ipywidgets serialization layer that could choke on binary data.

---

### 2.3 Lost Widget Interactions / jslink Broken (ipywidgets_bokeh#39)

**Source**: https://github.com/bokeh/ipywidgets_bokeh/issues/39

**Problem**: When two ipywidgets are linked via `jslink` and each is wrapped in a separate `IPyWidget` Bokeh model, the frontend link breaks. The `Link` widget that mediates the jslink connection gets serialized but loses its reference to the source/target widgets because they live in separate Bokeh model trees.

**Resolution**: OPEN (since October 2021). Philipp Rudiger acknowledged it is "quite difficult" to fix.

**Relevance to Panel**: LOW (not directly applicable). The AnyWidget pane wraps a single anywidget instance as a self-contained Panel component. If users need to link two anywidgets, they should use Panel's native linking mechanisms (`pn.bind`, `param.watch`, `.link()`) rather than ipywidgets' `jslink`. The pane's `component` attribute provides full param reactivity for this purpose.

---

### 2.4 Add Support for anywidget (ipywidgets_bokeh#110)

**Source**: https://github.com/bokeh/ipywidgets_bokeh/issues/110

**Problem**: Feature request to add direct anywidget support to ipywidgets_bokeh or core Bokeh. Currently open with no implementation plan. 3 thumbs-up reactions indicate community interest.

**Resolution**: OPEN (since February 2025).

**Relevance to Panel**: HIGH (motivation). This open request confirms community demand for anywidget support outside Jupyter. Panel's native AnyWidget pane directly addresses this need without waiting for ipywidgets_bokeh to implement it.

---

### 2.5 Wrong Widget Protocol Version (ipywidgets_bokeh#100)

**Source**: https://github.com/bokeh/ipywidgets_bokeh/issues/100

**Problem**: Creating ipywidgets inside a callback function triggered by a Panel widget produces the error `"Wrong widget protocol version: received protocol version '', but was expecting major version '2'"`. The protocol version header is missing when widgets are dynamically created in callback contexts rather than at module initialization time.

**Resolution**: OPEN (since July 2023).

**Relevance to Panel**: HIGH (motivation). This is another example of the fragility of the comm protocol bridge. Panel's native AnyWidget pane does not use the ipywidgets widget protocol at all -- it uses Bokeh's document sync protocol, which has no version negotiation issues.

---

### 2.6 Panel Leafmap Errors (ipywidgets_bokeh#106)

**Source**: https://github.com/bokeh/ipywidgets_bokeh/issues/106

**Problem**: Clicking tool icons in a leafmap widget served through Panel triggers `"Error: Could not process update msg for model id..."` JavaScript errors. The widget mostly works but specific interactions silently fail.

**Resolution**: OPEN (since June 2024).

**Relevance to Panel**: MEDIUM (motivation). Complex widgets with many interacting sub-components are the most likely to hit edge cases in the ipywidgets_bokeh comm bridge. While anywidgets tend to be simpler (single self-contained ESM module), this illustrates the general reliability problems with the bridge approach.

---

### 2.7 Get Rid of requireJS (ipywidgets_bokeh#126)

**Source**: https://github.com/bokeh/ipywidgets_bokeh/issues/126

**Problem**: ipywidgets_bokeh depends on requireJS for module loading, which conflicts with modern JavaScript frameworks and ES module patterns. The issue references Panel#8220 as a related concern.

**Resolution**: OPEN (February 2026).

**Relevance to Panel**: HIGH (motivation). Panel's native AnyWidget pane uses `es-module-shims` for ESM loading, which is a modern, standards-based polyfill. There is no requireJS dependency. This is a fundamental architectural advantage of the native approach over ipywidgets_bokeh.

---

### 2.8 Bokeh >= 3.0 Support (ipywidgets_bokeh#67)

**Source**: https://github.com/bokeh/ipywidgets_bokeh/issues/67

**Problem**: ipywidgets_bokeh broke when Bokeh 3.0 removed the `HTMLBox` class from `bokeh.models.layouts`. The library needed updates to use the new Bokeh model API.

**Resolution**: Partially addressed but issue remains open. Development branch started but not fully resolved.

**Relevance to Panel**: MEDIUM (maintenance concern). ipywidgets_bokeh has to track Bokeh's model API, which changes across major versions. Panel's native AnyWidget pane uses Panel's own `AnyWidgetComponent` Bokeh model, which is maintained as part of Panel itself and always compatible with the Bokeh version Panel supports.

---

### 2.9 Maintenance Status

**Sources**: https://snyk.io/advisor/python/ipywidgets-bokeh, https://pypi.org/project/ipywidgets-bokeh/

The ipywidgets_bokeh project shows signs of low maintenance:
- No new PyPI releases in the past 12 months
- 25 open issues, many dating back 2+ years
- Sporadic commit activity
- Core issues (requireJS, protocol version, jslink) remain unresolved

This maintenance status is a strong motivator for Panel to build a native solution that does not depend on ipywidgets_bokeh for anywidget support.

---

## 3. Cross-Reference: Panel Architecture vs External Issues

| # | Issue | Source | Panel Architecture Addresses It? | Mitigation Needed |
|---|-------|--------|----------------------------------|-------------------|
| 1 | Binary data serialization | marimo#2506 | YES -- Bokeh binary frames avoid JSON encoding | Test binary round-trip with image files |
| 2 | Callback signature mismatch | marimo#7989 | YES -- `AnyWidgetAdapter.on()` uses zero-arg callbacks per AFM spec | Document known incompatibility with Backbone-style widgets |
| 3 | ESM hot reload | marimo#3018 | PARTIAL -- module cache invalidates on ESM change, but pane doesn't watch FileContents | Deferred to HMR feature |
| 4 | Shadow DOM styling | marimo#6026 | PARTIAL -- `_css` injected via stylesheets, but global CSS inheritance breaks | Consider `use_shadow_dom=False` default; document workaround |
| 5 | Shadow DOM API limits | marimo#2196 | PARTIAL -- Same issue if Shadow DOM enabled | Consider `use_shadow_dom=False` default |
| 6 | Static asset serving | marimo#3279 | PARTIAL -- bundle serving works; blob URL relative paths don't | Document limitation; support file-based ESM serving |
| 7 | Fine-grained observation | marimo#2976 | YES -- `component.param.watch(cb, ['name'])` | None |
| 8 | Widget API discovery | marimo#2916 | PARTIAL -- dynamic classes lack IDE completion | Subclass pattern for library authors |
| 9 | anywidget class loading | iwb#89 | YES -- No ipywidgets class registry; direct ESM loading | None |
| 10 | ArrayBuffer serialization | iwb#46 | YES -- Bokeh binary protocol; `AnyWidgetAdapter` handles DataView | None |
| 11 | jslink broken | iwb#39 | N/A -- Panel uses its own linking mechanisms | Document Panel linking as alternative |
| 12 | anywidget support request | iwb#110 | YES -- This is exactly what the pane provides | None |
| 13 | Protocol version errors | iwb#100 | YES -- No ipywidgets protocol; Bokeh document sync only | None |
| 14 | Complex widget errors | iwb#106 | PARTIAL -- Simpler architecture avoids many issues, but complex widgets may have own bugs | Integration testing with real-world widgets |
| 15 | requireJS conflicts | iwb#126 | YES -- Uses es-module-shims (ESM standard) | None |
| 16 | Bokeh version tracking | iwb#67 | YES -- AnyWidgetComponent model maintained in Panel | None |
| 17 | Low maintenance | ipywidgets_bokeh | YES -- Native solution eliminates external dependency | None |

---

## 4. Risk Assessment

### 4.1 Shadow DOM: Highest New Risk Identified

The marimo issues (#6026, #2196) reveal that Shadow DOM isolation is the single most impactful compatibility risk for hosting anywidgets. Anywidgets designed for Jupyter assume they render in the main document, with full access to `document.getSelection()`, `document.activeElement`, global CSS inheritance, and other APIs that do not pierce Shadow DOM.

**Recommendation**: Default `use_shadow_dom = False` for the AnyWidget pane's dynamic component class. This matches the environment anywidgets expect (no shadow DOM in Jupyter) and avoids the class of issues marimo encountered. Users who need style isolation can opt in.

### 4.2 Binary Data: Low Risk

Panel's architecture is well-positioned for binary data. Bokeh's binary websocket frames and the `AnyWidgetAdapter.get()` DataView conversion handle the standard path correctly. The main risk is edge cases (zero-length buffers, null bytes, concurrent multi-trait updates with bytes). These should be covered by explicit tests.

### 4.3 ESM Compatibility: Low Risk for Published Widgets

Published anywidgets typically ship self-contained bundled ESM. Bare import specifiers, dynamic `import.meta.url` asset loading, and web workers are mainly concerns for development-time or specialized widgets. The common path works well.

### 4.4 Callback Signature: Low Risk

The anywidget AFM specification defines a zero-argument callback, which is what Panel implements. Widgets relying on the Backbone three-argument convention are considered non-conformant. This is an ecosystem-level issue, not a Panel-specific one.

### 4.5 ipywidgets_bokeh Dependency Elimination: Strong Positive

By building a native AnyWidget pane, Panel eliminates its dependency on ipywidgets_bokeh for anywidget support. This removes an entire class of issues: protocol version mismatches, requireJS conflicts, binary serialization failures, state embedding timing bugs, and Bokeh version tracking. The maintenance burden shifts from an externally-maintained bridge to Panel's own well-tested ESM pipeline.

### 4.6 Overall Assessment

**Risk Level: LOW to MEDIUM**

The proposed architecture addresses the majority of issues found in both marimo and ipywidgets_bokeh. The primary remaining risk is Shadow DOM compatibility, which has a straightforward mitigation (default to `use_shadow_dom=False`). No architectural changes are needed based on this external issues review -- only minor adjustments to defaults and additional test coverage.
