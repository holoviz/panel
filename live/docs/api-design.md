# Panel Live — API Design Specification

**Status:** Approved
**Version:** 1.0.0-draft
**Date:** 2026-02-10

This document is the canonical reference for the `panel-live` public API. It covers the HTML declarative API, JavaScript imperative API, CSS theming system, version management, and future web worker architecture.

---

## Design Decisions

1. **`<panel-live>` custom element** — 3 of 4 competitors use custom elements; attributes are the natural way to configure HTML; child elements compose naturally; the POC validates this approach.
2. **Light DOM** (no Shadow DOM) — Bokeh's `embed_items()` uses `document.getElementById()` which can't reach into Shadow DOM.
3. **Single element, mode as attribute** — `mode="app|editor|playground"` is simpler than 3 separate tag types.
4. **Dual API** — declarative HTML for simple cases, imperative JS (`PanelLive.mount()`) for framework integration.
5. **`theme="auto"` default** — respects `prefers-color-scheme` media query; overridable with `"dark"` or `"light"`.

---

## A. HTML Declarative API

### `<panel-live>` Element — Attributes

| Attribute | Default | Values | Description |
|-----------|---------|--------|-------------|
| `mode` | `"app"` | `app`, `editor`, `playground` | Display mode |
| `theme` | `"auto"` | `auto`, `light`, `dark` | Color scheme (`auto` = prefers-color-scheme) |
| `layout` | mode-aware | `horizontal`, `vertical` | Editor/preview split direction. Defaults to `"vertical"` for editor mode, `"horizontal"` for playground. |
| `src` | — | URL | External Python file URL |
| `fullscreen` | — | boolean attr | Toggle fullscreen (playground) |
| `height` | — | CSS length | Explicit height (e.g. `"500px"`) |
| `auto-run` | `true` | boolean attr | Execute code on load |
| `label` | `"Python"` | string | Language pill text in header |
| `examples-src` | — | URL | JSON file defining examples |
| `code-visibility` | `"visible"` | `visible`, `hidden`, `collapsed` | Editor pane state (editor mode) |
| `code-position` | `"first"` | `first`, `last` | Whether code appears before or after output (editor/playground) |

**Reserved for future:** `worker` (`true`/`false`/`"shared"`), `loading` (`eager`/`lazy`), `env` (named shared environment), `auto-detect` (requirements auto-detection toggle).

### Code Provision (priority order)

```html
<!-- 1. External source -->
<panel-live src="https://example.com/app.py"></panel-live>

<!-- 2. Inline text (simplest) -->
<panel-live>
import panel as pn
pn.panel("Hello World").servable()
</panel-live>

<!-- 3. Multi-file with child elements -->
<panel-live mode="editor">
  <panel-file name="app.py" entrypoint>
import panel as pn
from utils import greet
pn.panel(greet("World")).servable()
  </panel-file>
  <panel-file name="utils.py">
def greet(name):
    return f"Hello, {name}!"
  </panel-file>
  <panel-requirements>
pandas
hvplot
  </panel-requirements>
</panel-live>
```

### Child Elements

#### `<panel-file>` — declares a Python source file

| Attribute | Default | Description |
|-----------|---------|-------------|
| `name` | `"app.py"` | Filename in Pyodide virtual FS |
| `entrypoint` | — | Boolean; marks file to execute (first file if none marked) |
| `src` | — | URL to fetch content from (alternative to inline text) |

#### `<panel-requirements>` — newline-separated pip specifiers

Comments and blank lines are stripped.

```html
<panel-requirements>
pandas>=2.0
hvplot
# comment lines are stripped
</panel-requirements>
```

#### `<panel-example>` — code example for playground dropdown

| Attribute | Default | Description |
|-----------|---------|-------------|
| `name` | `"Example"` | Display name in dropdown |
| `src` | — | URL to fetch example code from |

### Complete Usage Examples

```html
<!-- App mode: output only, minimal -->
<panel-live>
import panel as pn
pn.panel("# Hello World").servable()
</panel-live>

<!-- Editor mode: code + output stacked, dark theme -->
<panel-live mode="editor" theme="dark">
import panel as pn
pn.widgets.FloatSlider(name="Amplitude", start=0, end=10).servable()
</panel-live>

<!-- Playground mode: side-by-side, fullscreen, with examples -->
<panel-live mode="playground" layout="horizontal" theme="dark" fullscreen>
  <panel-example name="Slider">
import panel as pn
slider = pn.widgets.FloatSlider(name="Value", start=0, end=10, value=5)
pn.Row(slider, pn.bind(lambda v: f"Value: {v:.1f}", slider)).servable()
  </panel-example>
  <panel-example name="DataFrame">
import panel as pn
import pandas as pd
df = pd.DataFrame({"x": [1,2,3], "y": [4,5,6]})
pn.panel(df).servable()
  </panel-example>
</panel-live>

<!-- Editor mode: external src, collapsed code, custom label -->
<panel-live mode="editor" src="examples/slider.py" code-visibility="collapsed" label="Panel">
</panel-live>

<!-- Multi-file app with explicit requirements -->
<panel-live mode="editor">
  <panel-file name="app.py" entrypoint>
import panel as pn
from utils import greet
pn.panel(greet("World")).servable()
  </panel-file>
  <panel-file name="utils.py">
def greet(name):
    return f"Hello, {name}!"
  </panel-file>
  <panel-requirements>
pandas
hvplot
  </panel-requirements>
</panel-live>

<!-- Examples loaded from external sources -->
<panel-live mode="playground">
  <panel-example name="Hello" src="examples/hello.py"></panel-example>
  <panel-example name="Slider" src="examples/slider.py"></panel-example>
</panel-live>
```

---

## B. JavaScript Imperative API

### `PanelLive.configure(options)`

Global defaults. Must be called before first `init()`/`mount()` or `<panel-live>` connectedCallback.

```javascript
PanelLive.configure({
  pyodideVersion: 'v0.28.2',
  panelVersion: '1.8.7',
  bokehVersion: '3.8.2',
  // Advanced: custom CDN base URLs for airgapped deployments
  pyodideCdn: 'https://cdn.jsdelivr.net/pyodide/',
  panelCdn: 'https://cdn.holoviz.org/panel/',
  bokehCdn: 'https://cdn.bokeh.org/bokeh/release/',
  // Future
  worker: false,
  sharedWorker: false,
});
```

Also supports `window.PANEL_LIVE_CONFIG` set before script load for static HTML pages:

```html
<script>window.PANEL_LIVE_CONFIG = { panelVersion: '1.9.0', bokehVersion: '3.9.0' };</script>
<script src="panel-live.min.js"></script>
```

### `PanelLive.init(options?) -> Promise<void>`

Pre-warm Pyodide singleton. Idempotent (returns same promise on repeat calls).

```javascript
PanelLive.init({ onStatus: msg => console.log(msg) });
```

### `PanelLive.mount(options, target) -> Promise<PanelLiveController>`

Programmatic creation. Returns a controller for runtime interaction.

```javascript
const ctrl = await PanelLive.mount({
  mode: 'playground',
  theme: 'dark',
  layout: 'horizontal',
  files: {
    'app.py': 'import panel as pn\npn.panel("Hello").servable()',
    'utils.py': 'def greet(name): return f"Hi {name}"',
  },
  entrypoint: 'app.py',
  requirements: ['pandas', 'hvplot'],
  examples: [
    { name: 'Hello', code: 'import panel as pn\npn.panel("Hello").servable()' },
    { name: 'Advanced', src: 'https://example.com/advanced.py' },
  ],
}, '#my-container');
```

### `PanelLiveController` (returned by `mount()`)

```javascript
ctrl.element        // The underlying <panel-live> DOM element
ctrl.run()          // Execute current code (editor/playground)
ctrl.getCode()      // Get current code string
ctrl.setCode(code)  // Set code (updates editor)
ctrl.status         // 'idle' | 'loading' | 'running' | 'ready' | 'error'
ctrl.destroy()      // Remove and cleanup
```

### Events (dispatched on `<panel-live>` element)

| Event | `detail` | Description |
|-------|----------|-------------|
| `pl-status` | `{status, message}` | Status change during lifecycle |
| `pl-ready` | — | App fully rendered |
| `pl-error` | `{error, traceback}` | Execution error |
| `pl-run-start` | — | Code execution started (re-run) |
| `pl-run-end` | — | Code execution finished |

---

## C. CSS Custom Properties

All visual aspects customizable via `--pl-*` variables on the `panel-live` element:

```css
panel-live {
  /* Container */
  --pl-border: #e0e0e0;       --pl-radius: 6px;
  --pl-bg: #ffffff;            --pl-font-mono: 'JetBrains Mono', monospace;
  /* Header */
  --pl-header-bg: #1e1e2e;    --pl-header-color: #cdd6f4;
  /* Language pill */
  --pl-pill-bg: #3b82f6;      --pl-pill-color: #ffffff;
  /* Editor */
  --pl-editor-bg: #1e1e2e;    --pl-editor-color: #cdd6f4;
  --pl-editor-font-size: 14px; --pl-editor-line-height: 1.6;
  /* Buttons */
  --pl-btn-bg: #a6e3a1;       --pl-btn-color: #1e1e2e;
  /* Output */
  --pl-output-bg: #ffffff;     --pl-output-min-height: 100px;
  /* Status */
  --pl-status-color: #555;     --pl-status-spinner: #1976d2;
  /* Error */
  --pl-error-color: #b71c1c;   --pl-error-bg: #ffebee;
  /* Drag handle */
  --pl-handle-bg: #e0e0e0;     --pl-handle-hover-bg: #3b82f6;
}
```

The `theme` attribute sets preset values for all variables. `theme="auto"` uses `@media (prefers-color-scheme)`. Users can override any variable on specific instances or via CSS classes.

### Theme Presets

**Light theme** (default when system preference is light):

```css
panel-live[theme="light"], panel-live[data-resolved-theme="light"] {
  --pl-border: #e0e0e0;       --pl-bg: #ffffff;
  --pl-header-bg: #f5f5f5;    --pl-header-color: #333333;
  --pl-editor-bg: #fafafa;    --pl-editor-color: #1a1a2e;
  --pl-btn-bg: #4caf50;       --pl-btn-color: #ffffff;
  --pl-output-bg: #ffffff;
  --pl-status-color: #555;     --pl-status-spinner: #1976d2;
  --pl-error-color: #b71c1c;   --pl-error-bg: #ffebee;
  --pl-handle-bg: #e0e0e0;     --pl-handle-hover-bg: #3b82f6;
}
```

**Dark theme** (default when system preference is dark):

```css
panel-live[theme="dark"], panel-live[data-resolved-theme="dark"] {
  --pl-border: #44475a;       --pl-bg: #1e1e2e;
  --pl-header-bg: #1e1e2e;    --pl-header-color: #cdd6f4;
  --pl-editor-bg: #1e1e2e;    --pl-editor-color: #cdd6f4;
  --pl-btn-bg: #a6e3a1;       --pl-btn-color: #1e1e2e;
  --pl-output-bg: #282a36;
  --pl-status-color: #a0a0a0;  --pl-status-spinner: #64b5f6;
  --pl-error-color: #ef9a9a;   --pl-error-bg: #3e1e1e;
  --pl-handle-bg: #44475a;     --pl-handle-hover-bg: #3b82f6;
}
```

---

## D. Version Management

### CDN Distribution

```
cdn.holoviz.org/panel-live/{version}/panel-live.min.js
cdn.holoviz.org/panel-live/{version}/panel-live.esm.js
cdn.holoviz.org/panel-live/latest/panel-live.min.js
```

Each release of `panel-live.js` embeds matching defaults for Panel/Bokeh/Pyodide versions. Users pin via `PanelLive.configure()` or `window.PANEL_LIVE_CONFIG`.

### Version Coupling (critical)

Bokeh JS version **MUST** match Bokeh Python wheel version. Panel JS version **MUST** match Panel Python wheel version. This is why they're managed in a single config object.

### Resolution Order

1. `PanelLive.configure()` call (highest priority)
2. `window.PANEL_LIVE_CONFIG` global object
3. Built-in defaults embedded in the release

---

## E. Future: Web Worker Support

### Architecture

The API is designed so worker support is **transparent** — same `<panel-live>` markup works regardless of execution backend. Implementation uses an adapter pattern:

```
MainThreadBackend  — current: direct Pyodide calls
WorkerBackend      — future: adapts pyodide_worker.js message protocol
SharedWorkerBackend — future: multiplexed execution across <panel-live> instances
```

### Panel's Existing Worker Protocol (to adapt)

From `panel/_templates/pyodide_worker.js` and `pyodide_handler.js`:

```
Worker -> Main: {type: 'render', docs_json, render_items, root_ids}
Worker -> Main: {type: 'patch', patch, buffers}
Worker -> Main: {type: 'idle'}
Worker -> Main: {type: 'status', msg}
Main -> Worker: {type: 'rendered'}
Main -> Worker: {type: 'patch', patch}
```

**Adaptation needed:** Accept code dynamically via `{type: 'run', code, requirements}` instead of build-time template variables. Support re-running. Target arbitrary containers instead of full-page selectors.

### Phased Rollout

1. **v1.0:** Main thread only (current approach)
2. **v1.x:** `worker` attribute for opt-in dedicated worker
3. **v2.0:** Worker as default, `worker="false"` for opt-out, `worker="shared"` for SharedWorker

---

## F. Competitor Comparison

| Feature | panel-live | gradio-lite | stlite | PyScript | shinylive |
|---------|-----------|-------------|--------|----------|-----------|
| **HTML Element** | `<panel-live>` | `<gradio-lite>` | `<streamlit-app>` | `<script type="py">` | N/A (Quarto) |
| **Mode attribute** | `mode="app\|editor\|playground"` | `playground` (boolean) | N/A | `type="py-editor"` | `components: [editor, viewer]` |
| **Theme** | `theme="auto\|light\|dark"` | `theme="dark\|light"` | Via Streamlit config | N/A | N/A |
| **Layout** | `layout="horizontal\|vertical"` | `layout="horizontal\|vertical"` | N/A | N/A | `layout: vertical` |
| **Multi-file** | `<panel-file>` children | `<gradio-file>` children | `<app-file>` children | `files` config | `## file:` markers |
| **Requirements** | `<panel-requirements>` | `<gradio-requirements>` | `<app-requirements>` | `packages` config | `requirements.txt` file |
| **Examples** | `<panel-example>` children | N/A | N/A | N/A | N/A |
| **JS API** | `PanelLive.mount()` | N/A | `mount()` | Programmatic | CLI export |
| **Controller** | `PanelLiveController` | N/A | Controller object | N/A | N/A |
| **CSS variables** | `--pl-*` | N/A | N/A | N/A | N/A |
| **Events** | `pl-status`, `pl-ready`, etc. | N/A | N/A | N/A | N/A |
| **URL sharing** | Hash-encoded | N/A | N/A | N/A | Hash-encoded |
| **Worker** | Future (v1.x) | Dedicated/Shared | Dedicated/Shared | Optional | Dedicated |
| **Fullscreen** | `fullscreen` attr | N/A | N/A | N/A | N/A |
| **External src** | `src` attr + child `src` | N/A | `{url: ...}` files | `src` attr | N/A |

### Competitive Differentiators

1. **Three display modes in one element** — no other competitor offers app, editor, and playground from a single tag with a `mode` attribute.
2. **Full CSS custom property system** — no competitor exposes a comprehensive `--pl-*` theming API.
3. **`<panel-example>` child elements** — built-in example selector for playground mode.
4. **`PanelLiveController`** — richer runtime interaction than any competitor's JS API.
5. **`theme="auto"`** — automatic light/dark detection via `prefers-color-scheme`.
6. **Panel/HoloViz ecosystem** — hvPlot, HoloViews, Param, panel-material-ui provide a richer widget/visualization toolkit than any single competitor.

---

## G. Implementation Notes

### Light DOM Rationale

Bokeh's `embed_items()` calls `document.getElementById()` on the main document. Shadow DOM encapsulates its internal DOM tree, making elements invisible to this lookup. Since Panel's rendering pipeline depends on Bokeh, we must use Light DOM. All styling is scoped via the `panel-live` element selector and `.pl-*` class prefix.

### Execution Queue

Pyodide is single-threaded. The global `state.curdoc` means concurrent app executions would corrupt each other's document state. All executions are serialized through a promise-based queue (`enqueueExecution()`). This is transparent to the user — multiple `<panel-live>` elements on a page will initialize Pyodide once and run sequentially.

### `theme="auto"` Implementation

The `auto` theme resolves at `connectedCallback` time by checking `window.matchMedia('(prefers-color-scheme: dark)')`. A `MediaQueryList` listener updates the resolved theme when the user's system preference changes. The resolved theme is stored as a `data-resolved-theme` attribute for CSS targeting.

### Child Element `src` Fetching

`<panel-file src="...">` and `<panel-example src="...">` fetch their content during `connectedCallback`. Fetch failures are surfaced via `pl-error` events and inline error display.
