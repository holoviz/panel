# AnyWidget Implementation — Consolidated Recommendations

**Date:** 2026-03-02
**Sources:** anywidget protocol comparison, marimo comparison, UX review, COOP/COEP investigation

## Implemented (This Session)

### Critical Fixes
1. **`send()` signature mismatch** — Fixed to accept both native 3-positional args and options-style calling conventions
2. **`experimental.invoke()` RPC** — Full implementation with AbortSignal support, passed to both `initialize()` and `render()`
3. **Bokeh reserved name collision** — Added `_BOKEH_RESERVED` frozenset (69 names) to collision detection
4. **Arrow binary transfer** — Both directions (ESM→Python and Python→ESM) now work via base64 encoding

### Protocol Improvements
5. **`off()` protocol compliance** — Accepts 0 or 1 args for bulk cleanup
6. **Generic `"change"` event** — `model.on("change", cb)` fires on any property change
7. **`widget_manager` stub** — Returns rejected Promise with clear error message

### UX Improvements
8. **`pane.trait_name_map`** — Property for discovering renamed traits
9. **`logger.info` on rename** — Logs when traits are renamed to help debugging

### Documentation
10. **Reference guide** — Updated with trait collision docs, third-party examples, troubleshooting, COOP/COEP headers
11. **IPyWidget cross-reference** — Added note directing anywidget users to the AnyWidget pane

## Future Recommendations

### For Panel Core Team to Consider

1. **`response_headers` parameter for `pn.serve()`** — Currently COOP/COEP headers require a Tornado `OutputTransform`. A simpler `response_headers={"Cross-Origin-Opener-Policy": "same-origin"}` would improve DX.

2. **`__getattr__` fallback on AnyWidget pane** — The UX review noted that `pane.value` (the intuitive access) doesn't work; users must use `pane.component.value`. A `__getattr__` fallback could proxy attribute access to the component, though this has namespace collision risks.

3. **Dirty-field tracking in `save_changes()`** — Marimo tracks which fields were `set()` since last `save_changes()` and only sends the changed subset. Panel currently sends all accumulated changes. This is a minor optimization for network efficiency.

4. **Content-hash ESM deduplication** — Marimo caches ESM imports by content hash, enabling deduplication across widget instances. Panel caches by widget class. Content-hash would help when multiple instances of different classes share the same ESM bundle.

5. **`change:` callback argument protocol** — Panel intentionally passes `cb(value)` as 1 arg (value first), while the official protocol is `cb(context, value)` as 2 args (value second). This matches real-world widget usage but deviates from the spec. No change recommended — document the decision clearly.

### Upstream Issues to Track

1. **tldraw v3 ESM incompatibility** — Uses `_asyncOptionalChain` which causes SyntaxError in es-module-shims. Track upstream fix.

2. **drawdata `circle_brush` initialization** — Bug in drawdata library, not Panel.

3. **jupyter-scatter WebGL rendering** — 951KB ESM bundle times out in headless Chromium. Likely WebGL/es-module-shims limitation with large bundles.

4. **wigglystuff Matrix DeprecationWarning** — Upstream traitlets compatibility issue.

## Test Coverage Summary

| Category | Count | Status |
|----------|-------|--------|
| Unit tests (test_anywidget.py) | 76 | All passing |
| Pane base tests | 199 | All passing |
| UI tests (counter, slider, etc.) | ~89+ | Passing |
| Tier 1 examples | 16 | Most working, some with known limitations |
| Tier 2 examples | 4 | Working with documented quirks |
| Tier 3 examples | 6 | Limitations documented |

## Research Reports

- **Anywidget protocol comparison:** `reviews/anywidget_protocol_comparison.md`
- **Marimo implementation comparison:** `reviews/marimo_comparison.md`
- **UX review:** `reviews/ux_review.md`
- **COOP/COEP investigation:** Documented in `todo.md` Log section and AnyWidget reference guide
