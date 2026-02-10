# Panel Playground - Analysis & Solution

## Problem Statement

**Make it trivially easy to display, edit, share, and embed live Panel apps in the browser using Pyodide -- with no server required.**

The core primitive is: given Panel Python code, render a working interactive app in the browser, and update it dynamically when the code changes -- **without reloading Pyodide**.

### Current Pain Points

| Problem | Detail |
|---------|--------|
| **Slow reload** | The Panel Sharing editor reloads Pyodide on every re-run (~10-20s). This makes iterative development painful. |
| **Boilerplate overhead** | Embedding Panel via PyScript requires HTML templates, script tags, package configs, cross-origin headers. Too much non-Python code. |
| **No playground** | Unlike Streamlit (stlite), Gradio (gradio-lite), Shiny (shinylive), Panel has no official interactive playground. |
| **Sphinx limitation** | The nbsite pyodide directive supports only one Panel instance per page and no templates. Users can interact with the output but not edit the code. |
| **Server cost** | Sharing Panel apps via servers is expensive. WASM-based sharing eliminates infrastructure costs entirely. |

### Success Criteria

1. **Initial load**: < 15s on broadband (Pyodide + Panel bootstrap), with visible loading progress
2. **Dynamic reload**: < 2s to re-render after code change (no Pyodide reload)
3. **Minimal boilerplate**: Embed a Panel app with ~5 lines of HTML
4. **Sharing**: URL-based code sharing (no server needed)
5. **Template support**: Works with Panel templates (FastListTemplate, etc.)
6. **Auto-detect dependencies**: Automatically installs required packages

---

## Market Analysis

### How Others Solve This

| Framework | Solution | Editor | Sharing | Hot Reload | URL Sharing |
|-----------|----------|--------|---------|------------|-------------|
| **Streamlit** | [stlite](https://edit.share.stlite.net/) | Monaco | URL hash | Yes (re-run script) | gzip+base64 |
| **Gradio** | [gradio-lite](https://gradio.app/playground) | Custom | URL | Yes | Yes |
| **Shiny** | [shinylive](https://shinylive.io/py/editor/) | CodeMirror | URL hash | Yes (iframe) | base64 |
| **Marimo** | [marimo.app](https://marimo.app/) | CodeMirror | URL/Gist | Yes (reactive) | gzip+base64 |
| **PyScript** | `<script type="py-editor">` | CodeMirror | No | Click to run | No |
| **Py.Cafe** | [py.cafe](https://py.cafe/) | Monaco | URL/Project | Yes (uv) | gzip+base64 |
| **Panel** | `panel convert` CLI | None | Static files | No | No |

### Key Insights from Competitors

1. **Gradio minimized boilerplate** -- `<gradio-lite>` custom element with inline Python, no config needed
2. **Shinylive renders in an iframe** -- clean sandboxing, supports templates
3. **Py.Cafe uses `uv`** for fast package installs, has best-in-class reload speed
4. **Stlite keeps Pyodide persistent** -- Streamlit's "re-run entire script" model maps naturally to this
5. **All use gzip + base64url in URL hash** for serverless sharing

---

## Existing Panel Infrastructure

Panel already has 90% of the building blocks:

| Component | Location | Purpose |
|-----------|----------|---------|
| `script_to_html()` | `panel/io/convert.py:311` | Converts Panel script to standalone WASM HTML |
| `init_doc()` | `panel/io/pyodide.py:509` | Creates mock server document for Pyodide |
| `write_doc()` | `panel/io/pyodide.py:580` | Renders document contents into DOM |
| `write()` | `panel/io/pyodide.py:535` | Renders a single object into a DOM target |
| `pyrender()` | `panel/io/pyodide.py:626` | Executes code and returns MIME representation |
| `find_requirements()` | `panel/io/mime_render.py:41` | Auto-detects package requirements from imports |
| `exec_with_return()` | `panel/io/mime_render.py:124` | Executes code and returns last expression |
| `base64url_encode/decode` | `panel/util/__init__.py:237` | URL-safe encoding for sharing |
| `CodeEditor` widget | `panel/widgets/codeeditor.py` | Ace-based code editor |
| Pyodide worker | `panel/_templates/pyodide_worker.js` | WebWorker Pyodide runtime |
| Worker handler | `panel/_templates/pyodide_handler.js` | Main-thread worker communication |

### Previous Attempts (PRs #5769, #5812)

**PR #5769** - Initial POC, replaced by #5812.

**PR #5812** - `panel-lite-editor`: iframe + `script_to_html()` approach.

Key issues encountered:
1. **Idempotency failure**: "I can only run this example once then I can run no other example" -- Bokeh document state was not properly cleaned up between runs
2. **Template rendering**: `script_to_html()` failed with template syntax because it needs a running Python process to pre-render
3. **DOM errors**: "Error rendering Bokeh model: could not find HTML tag" -- stale `data-root-id` elements from previous renders
4. **Pyodide reload**: Using `document.write(html)` destroyed the Pyodide instance, requiring a full reload

The PR was closed because the approach had fundamental issues with re-running code in the same Pyodide instance.

---

## Solution Architecture

### The Core Innovation: Persistent Pyodide with Clean State Reset

The key insight is separating concerns:
- **Pyodide runtime + installed packages**: Persistent (loaded once, never destroyed)
- **Bokeh/Panel document state**: Reset on each run (cheap operation)
- **DOM rendering**: Cleaned up and re-created on each run

### Two Execution Architectures

The implementation supports two distinct execution models, selected per-embed:

**1. Iframe mode** (`data-iframe` attribute or playground) — each app gets its own `panel_runner.html` iframe with a dedicated Pyodide instance. Communication via `postMessage`. Good for sandboxing and template support but uses ~300-500 MB per iframe.

```
┌─────────────────────────────────────────────────┐
│  Host Page (embed.html / playground.html)        │
│  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Code Editor  │  │ iframe (panel_runner.html)│  │
│  │ (CodeMirror) │──│                          │  │
│  │              │  │ ┌──────────────────────┐  │  │
│  │              │  │ │ Pyodide (persistent) │  │  │
│  │              │  │ │ Panel/Bokeh (once)   │  │  │
│  │ [Run button] │  │ ├──────────────────────┤  │  │
│  │              │  │ │ _runRunnerApp(code)  │  │  │
│  │              │  │ │ 1. Reset state       │  │  │
│  │              │  │ │ 2. Exec code         │  │  │
│  │              │  │ │ 3. Render app        │  │  │
│  └──────────────┘  │ └──────────────────────┘  │  │
│                    └──────────────────────────┘  │
│  Communication: window.postMessage()             │
└─────────────────────────────────────────────────┘
```

**2. Inline mode** (no `data-iframe`) — all apps share a single Pyodide instance in the host page. Each app renders into its own `<div>` using namespace isolation (`__ns__ = {"__builtins__": __builtins__}`). Uses ~300-500 MB total regardless of number of apps.

```
┌──────────────────────────────────────────────────────┐
│  Host Page (embed_single.html)                       │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ Shared Pyodide Runtime (singleton)             │  │
│  │ Panel/Bokeh installed once                     │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ App 1        │  │ App 2        │  │ App 3      │ │
│  │ <div> target │  │ <div> target │  │ <div>      │ │
│  │ __ns__ = {}  │  │ __ns__ = {}  │  │ __ns__ = {}│ │
│  │ runApp(id,c) │  │ runApp(id,c) │  │ runApp()   │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                      │
│  Apps run sequentially, each in isolated namespace   │
└──────────────────────────────────────────────────────┘
```

### State Reset Sequence (The Critical Path)

Each time `runPanelCode(code)` is called:

```python
# 1. Remove old Bokeh views from JS index
#    (Cleans up the JavaScript side)
if window.Bokeh and window.Bokeh.index:
    for view in Bokeh.index.roots:
        view.remove()

# 2. Clear the output DOM
output_element.innerHTML = ''

# 3. Create fresh Panel document
#    (Cleans up the Python side)
init_doc()  # Creates new Document, sets as curdoc, holds changes

# 4. Execute user code
#    (.servable() adds roots to the fresh document)
exec(user_code)

# 5. Create data-root-id elements dynamically
#    (This is what script_to_html normally does at build time)
for root in state.curdoc.roots:
    el = document.createElement('div')
    el.setAttribute('data-root-id', root.id)
    output.appendChild(el)

# 6. Render
await write_doc()  # Links Python doc <-> JS doc, renders into DOM
```

**Why this solves the PR #5812 issues:**

| PR #5812 Problem | Solution |
|-------------------|----------|
| Pyodide reloads on every run | Pyodide is persistent in the iframe; only state is reset |
| Bokeh "could not find HTML tag" | `data-root-id` elements are created dynamically AFTER code runs, matching exact root IDs |
| Idempotency failure | Complete state reset: JS views removed, DOM cleared, fresh Document created |
| Template rendering failure | `write_doc()` handles templates natively; no `script_to_html()` needed at runtime |

### Three Rendering Strategies

The runner detects which strategy to use based on code analysis:

| Code Pattern | Strategy | How |
|-------------|----------|-----|
| `.servable()` (no target) | `init_doc()` + exec + dynamic roots + `write_doc()` | Standard Panel app flow |
| `.servable(target='...')` | `init_doc()` + exec + `write_doc()` | User provides target elements |
| No `.servable()` | `exec_with_return()` + `pn.io.pyodide.write()` | Auto-wraps last expression |

### Speed Optimization

**Initial load (~10-15s first visit, ~3-5s cached):**
- Pyodide WASM + Bokeh/Panel JS loaded in **parallel** (not sequentially)
- Specialized Panel CDN wheels (smaller than PyPI packages)
- Browser HTTP cache handles subsequent visits
- Loading progress shown to user at each stage

**Dynamic reload (~1-2s):**
- No Pyodide reload (already loaded)
- No package reinstall (already installed)
- New packages detected via `find_requirements()` and installed incrementally
- State reset is pure JS + lightweight Python (sub-100ms)
- `write_doc()` rendering is fast (Bokeh embed)

---

## `panel-embed.js` — Shared Library

### Purpose

`panel-embed.js` is a single self-contained IIFE (~1460 lines) that provides the entire embedding infrastructure. It requires no build step, no npm dependencies, and auto-injects all necessary CSS on first use. Every POC file (`panel_runner.html`, `playground.html`, `embed.html`, `embed_single.html`) delegates to this library rather than duplicating logic.

### Module Structure

The IIFE is organized into internal modules:

| Module | Lines | Purpose |
|--------|-------|---------|
| **Config** | `defaults`, `config`, `cdnUrls()` | Version constants (Pyodide, Panel, Bokeh) and CDN URL generation |
| **Loaders** | `loadScript()`, `loadCSS()`, `loadJSResources()` | Dynamic `<script>` and `<link>` injection for Bokeh/Panel JS |
| **StatusBar** | `injectStyles()`, `ensureStatusBar()`, `setStatus()`, `hideStatus()` | Global loading indicator with spinner and error states |
| **Pyodide Runtime** | `initPyodide()`, `_doInit()` | Singleton Pyodide initialization: loads JS, initializes Pyodide, installs Panel/Bokeh wheels |
| **Package Detection** | `detectAndInstallRequirements()` | Uses `find_requirements()` to auto-install missing packages via micropip |
| **Extension Resources** | `loadExtensionResources()` | Introspects `Model.model_class_reverse_map` for `__javascript__`/`__css__` URLs and dynamically loads them |
| **Cleanup** | `cleanupContainer()` | Removes Bokeh views scoped to a target container and clears its DOM |
| **App Executor** | `runApp(targetId, code)` | 3-branch execution with namespace isolation for inline mode |
| **Runner Executor** | `runRunnerApp(code)` | Full-page execution for `panel_runner.html` (no namespace isolation, uses `init_doc()`) |
| **CodeMirror Manager** | `loadCodeMirror()`, `createCMEditor()` | Lazy-loads CodeMirror 5 from CDN with Dracula theme, Python mode, and bracket matching |
| **Iframe Mode** | `initIframeListeners()`, `loadNextIframe()`, `sendToIframe()` | Sequential iframe loading with `postMessage` ready/run protocol |
| **Sharing** | `compressCode()`, `decompressCode()` | gzip + base64url encoding/decoding for URL hash sharing |
| **Fetch Code** | `fetchCode(src)` | Fetches external `.py` files; runs in parallel with Pyodide init |
| **Editor DOM Builder** | `buildEditorDOM(opts)` | Constructs the editor chrome: header bar, CodeMirror textarea, preview area, collapsible section |
| **Toolbar Creator** | `createToolbar(codeSection)` | Creates the `<> Code` toggle button for collapsible code sections |
| **Modes** | `appMode()`, `editorMode()`, `playgroundMode()` | Three high-level entry points for different embedding styles |
| **Auto-Discovery** | `autoDiscover()` | On `DOMContentLoaded`, scans for `<script type="panel">` and `<script type="panel-editor">` tags |
| **Public API** | `window.PanelEmbed` | Exposes `configure()`, `init()`, `app()`, `editor()`, `playground()` plus internal helpers |

### Namespace Isolation (Inline Mode)

When multiple apps share a single Pyodide instance (inline mode), each app executes in an isolated namespace to prevent variable collisions:

```python
__ns__ = {"__builtins__": __builtins__}
exec("import panel as pn", __ns__)
exec(user_code, __ns__)
```

This ensures that `slider` defined in App 1 doesn't conflict with `slider` in App 2. The runner executor (`panel_runner.html`) does **not** use namespace isolation since it runs one app at a time in its own iframe.

### Extension Resource Loading

After executing user code, `loadExtensionResources()` introspects all registered Bokeh models to find JS and CSS resources that need loading:

```python
from bokeh.model import Model
for cls in Model.model_class_reverse_map.values():
    for url in getattr(cls, '__javascript__', []) or []:
        js_urls.append(url)
    for url in getattr(cls, '__css__', []) or []:
        css_urls.append(url)
```

This handles extensions like Tabulator, Plotly, and Perspective automatically — when user code imports and uses a Panel widget that requires additional JS/CSS, those resources are detected and loaded before rendering. Resources already loaded are tracked in a `Set` to avoid duplicates.

---

## API Surface

### Declarative API (`<script>` Tags)

The simplest way to embed Panel apps. The browser ignores unknown `type` values, so the Python code is inert until `panel-embed.js` processes it on `DOMContentLoaded`.

#### `<script type="panel">`

Renders a Panel app with no editor. Attributes:

| Attribute | Values | Default | Description |
|-----------|--------|---------|-------------|
| `data-iframe` | (flag) | absent | Use iframe mode (separate Pyodide per app) |
| `data-height` | CSS value | — | Minimum height for the preview area |
| `data-target` | element ID | auto-generated | ID for the render target |
| `src` | URL | — | Load Python code from external file instead of inline |

```html
<!-- Inline code, single Pyodide -->
<script type="panel">
import panel as pn
pn.Column("# Hello!").servable()
</script>

<!-- External file, iframe mode -->
<script type="panel" src="examples/hello.py" data-iframe></script>
```

#### `<script type="panel-editor">`

Renders an editable code block with a live preview. Supports all `<script type="panel">` attributes plus:

| Attribute | Values | Default | Description |
|-----------|--------|---------|-------------|
| `data-title` | string | `"Panel App"` | Title shown in the editor header bar |
| `data-layout` | `code-above`, `code-below` | `code-above` | Whether editor appears above or below the preview |
| `data-code` | `visible`, `hidden` | `visible` | Whether code starts expanded or collapsed behind a `<> Code` toggle |
| `src` | URL | — | Load initial code from external file |

```html
<!-- Editor with code below, collapsible -->
<script type="panel-editor" data-layout="code-below" data-code="hidden" data-title="My Demo">
import panel as pn
pn.Column("# Hello").servable()
</script>

<!-- Editor loading external file -->
<script type="panel-editor" src="examples/slider.py" data-title="Slider"></script>
```

#### Layout × Code Visibility Matrix

The four combinations of `data-layout` and `data-code` produce different DOM structures:

| `data-layout` | `data-code` | DOM Order |
|---------------|-------------|-----------|
| `code-above` | `visible` | Header → CodeMirror → Preview |
| `code-above` | `hidden` | [collapsed: Header → CodeMirror] → Toolbar → Preview |
| `code-below` | `visible` | Preview → Header → CodeMirror |
| `code-below` | `hidden` | Preview → Toolbar → [collapsed: Header → CodeMirror] |

When `data-code="hidden"`, the code section starts collapsed (`max-height: 0; opacity: 0`) and a toolbar with a `<> Code` toggle button is inserted between the code section and the preview. Clicking the button expands the section with a CSS transition and calls `cm.refresh()` with a delay to fix CodeMirror rendering.

### Imperative API (`window.PanelEmbed`)

For programmatic control, `panel-embed.js` exposes `window.PanelEmbed`:

#### `PanelEmbed.configure(overrides)`

Override default version configuration. Must be called before `init()`.

```javascript
PanelEmbed.configure({
  pyodideVersion: 'v0.28.2',
  panelVersion: '1.8.7',
  bokehVersion: '3.8.1',
});
```

#### `PanelEmbed.init()`

Initialize the singleton Pyodide runtime. Returns a `Promise` that resolves when Pyodide + Panel are ready. Called automatically by `app()` and `editor()` in inline mode; call explicitly for iframe mode to pre-warm.

```javascript
await PanelEmbed.init();
```

#### `PanelEmbed.app(target, code, opts?)`

Render a Panel app into a container (no editor).

| Parameter | Type | Description |
|-----------|------|-------------|
| `target` | string \| HTMLElement | Container element or its ID |
| `code` | string | Python code to execute |
| `opts.iframe` | boolean | Use iframe mode |
| `opts.src` | string | URL to fetch code from (overrides `code` if non-empty response) |
| `opts.height` | string | Minimum height for the preview |

```javascript
PanelEmbed.app('my-div', 'import panel as pn\npn.Column("Hello").servable()');
PanelEmbed.app('my-div', '', { src: 'examples/hello.py', iframe: true });
```

#### `PanelEmbed.editor(target, code, opts?)`

Render an editable code block + live preview.

| Parameter | Type | Description |
|-----------|------|-------------|
| `target` | string \| HTMLElement | Container element or its ID |
| `code` | string | Initial Python code |
| `opts.iframe` | boolean | Use iframe mode |
| `opts.src` | string | URL to fetch code from |
| `opts.title` | string | Header title (default: `"Panel App"`) |
| `opts.layout` | `"code-above"` \| `"code-below"` | Editor position relative to preview |
| `opts.codeVisibility` | `"visible"` \| `"hidden"` | Whether code starts expanded or collapsed |
| `opts.height` | string | Minimum height for the preview |

```javascript
PanelEmbed.editor('my-div', code, {
  title: 'Demo',
  layout: 'code-below',
  codeVisibility: 'hidden',
});
```

#### `PanelEmbed.playground(target, opts?)`

Render a full-page playground with side-by-side editor + iframe preview.

| Parameter | Type | Description |
|-----------|------|-------------|
| `target` | string \| HTMLElement | Container element or its ID |
| `opts.code` | string | Initial code |
| `opts.examples` | object | `{ "Name": "code..." }` map for examples dropdown. Values can also be URLs ending in `.py`. |
| `opts.sharing` | boolean | Enable URL hash sharing (default: `true`) |
| `opts.resizable` | boolean | Enable draggable resize handle (default: `true`) |
| `opts.title` | string | Header title (default: `"Panel Playground"`) |

```javascript
PanelEmbed.playground('main', {
  code: 'import panel as pn\npn.Column("Hello").servable()',
  sharing: true,
  examples: { "Hello": '...', "Slider": '...' },
});
```

---

## POC Implementations

### POC 1: `poc/panel_runner.html` — The Core Primitive

**What it is:** A minimal HTML page that loads `panel-embed.js`, initializes Pyodide via `PanelEmbed.init()`, and provides a `runPanelCode()` function (delegating to `PanelEmbed._runRunnerApp()`).

**Key features:**
- Loads Pyodide, Bokeh JS, and Panel JS in parallel for fastest initial load
- `PanelEmbed._runRunnerApp(code)` handles cleanup, code execution, and rendering
- Auto-detects and installs new package requirements
- Supports `.servable()`, `.servable(target=...)`, and auto-display (last expression)
- Loading status indicator with progress messages
- iframe `postMessage` API: receives `{type: 'run', code}`, sends `{type: 'ready'}` and `{type: 'rendered'}`
- Standalone mode with self-test demo when opened directly

**How it works:**
```javascript
// Initialize shared runtime
var readyPromise = PanelEmbed.init().then(function () {
  if (window.parent !== window) {
    window.parent.postMessage({ type: 'ready' }, '*');
  }
});

// Listen for postMessage from parent
window.addEventListener('message', async function (event) {
  if (msg && msg.type === 'run' && msg.code) {
    await PanelEmbed._runRunnerApp(msg.code);
  }
});

// Expose global API and self-test
window.runPanelCode = PanelEmbed._runRunnerApp;
```

### POC 2: `poc/playground.html` — Editor + Live Preview

**What it is:** A full-page side-by-side code editor + live preview, similar to shinylive or stlite. Delegates entirely to `PanelEmbed.playground()`.

**Key features:**
- Textarea-based editor with syntax highlighting (Tab support, Ctrl+Enter)
- Side-by-side layout with draggable resize handle
- Run button + Ctrl/Cmd+Enter keyboard shortcut
- 6 built-in examples (Hello, Slider, Matplotlib, DataFrame/Tabulator, Template, Chat)
- URL-based sharing: gzip + base64url in URL hash fragment
- Ready indicator (red dot = loading, green = ready)
- Auto-runs initial example when iframe is ready

**How it's invoked:**
```javascript
PanelEmbed.playground('main', {
  code: '...',
  sharing: true,
  resizable: true,
  examples: { "Hello Panel": '...', "Slider Callback": '...', ... },
});
```

### POC 3: `poc/embed.html` — Embeddable Snippets (Iframe Mode)

**What it is:** Demonstrates embedding Panel apps in any HTML page using declarative `<script type="panel" data-iframe>` and `<script type="panel-editor" data-iframe>` tags. Each app runs in its own `panel_runner.html` iframe with sequential loading.

**Demos included:**
1. Simple app embed (no editor) — `<script type="panel" data-iframe>`
2. Inline editor + app — `<script type="panel-editor" data-iframe>`
3. Auto-servable (no `.servable()`, auto-displays last expression)
4. Code-below layout — `data-layout="code-below"`
5. Collapsible code — `data-code="hidden"`
6. External source — `src="examples/hello.py"` and `src="examples/slider.py"`
7. Minimal boilerplate reference

**Usage:**
```html
<script src="panel-embed.js"></script>
<script type="panel" data-iframe>
import panel as pn
pn.Column("# Hello!").servable()
</script>
```

### POC 4: `poc/embed_single.html` — Embeddable Snippets (Single Pyodide)

**What it is:** Same demos as `embed.html` but using a **single Pyodide instance** instead of separate iframes. Uses `<script type="panel">` and `<script type="panel-editor">` tags (no `data-iframe` attribute). All apps render into `<div>` targets with namespace isolation.

**Advantages over iframe mode:**
- Memory: ~300-500 MB total vs ~300-500 MB **per iframe**
- Avoids browser crashes from multiple Pyodide instances
- Faster sequential loading (no iframe overhead)

**Additional demos beyond `embed.html`:**
- Collapsible + code-below combined (`data-code="hidden" data-layout="code-below"`)
- All features composed (external source + collapsible + code-below)

**Usage:**
```html
<script src="panel-embed.js"></script>
<script type="panel">
import panel as pn
pn.Column("# Hello!").servable()
</script>
```

Note: The only difference from the iframe version is the absence of the `data-iframe` attribute. The library handles the execution model switch automatically.

### Support Files

| File | Purpose |
|------|---------|
| `poc/serve.py` | HTTP server with `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: credentialless` headers. Required for `SharedArrayBuffer` support which Pyodide needs for efficient WASM memory management. |
| `poc/examples/hello.py` | Simple Panel app for `src` attribute demos (Column with heading, text, and slider) |
| `poc/examples/slider.py` | FloatSlider demo with bound Markdown output for `src` attribute demos |

---

## Known Limitations & Future Work

### Current Limitations

1. **Memory leaks**: Pyodide proxy functions (`_proxies` list in `pyodide.py`) accumulate across runs. For long editing sessions, this could grow. Fix: add explicit cleanup of old proxies.

2. **Template JS extensions**: ~~Some Panel extensions (Tabulator, Plotly, Perspective) require additional JS loaded in the page.~~ **Partially solved**: `loadExtensionResources()` now dynamically loads JS and CSS for Bokeh model extensions after code execution. It introspects `Model.model_class_reverse_map` for classes with `__javascript__` and `__css__` URLs and loads them. This handles most extensions (Tabulator, Plotly, etc.) but extensions that register models lazily or use non-standard loading may still need manual handling.

3. **Cross-origin**: The iframe approach requires same-origin or proper CORS headers. For CDN hosting, this needs `Access-Control-Allow-Origin` headers.

4. **Extension loading via `pn.extension()` args**: ~~Extensions like `pn.extension("tabulator")` need the corresponding JS to be pre-loaded in the page.~~ **Solved**: `loadExtensionResources()` runs after code execution and picks up whatever models were registered by `pn.extension()`. The JS/CSS is loaded dynamically before rendering.

5. **Version coupling**: The Bokeh JS version must exactly match the Bokeh Python wheel version. The library parameterizes this via `PanelEmbed.configure()` but it's fragile.

6. **CodeMirror refresh in collapsed sections**: When expanding a collapsed code section (`data-code="hidden"`), CodeMirror must be refreshed with a `setTimeout` delay for correct rendering. The library handles this in `createToolbar()`, but custom integrations that toggle visibility must call `cm.refresh()` manually.

### Roadmap

| Phase | Feature | Status |
|-------|---------|--------|
| **1** | Core runner — `panel_runner.html` with persistent Pyodide + clean state reset | **Done** |
| **2** | Editor playground — side-by-side editor + preview with sharing | **Done** |
| **3** | Dynamic JS loading — auto-load extension JS (tabulator, plotly, etc.) | **Done** (via `loadExtensionResources()`) |
| **4** | Declarative embedding — minimal-boilerplate `<script type="panel">` tags | **Done** (implemented as `<script type="panel">` / `<script type="panel-editor">` instead of the originally planned `<panel-playground>` custom elements) |
| **5** | Sphinx directive — enhanced nbsite directive with editor + preview mode | Future |
| **6** | CDN hosting — host `panel-embed.js` on `cdn.holoviz.org` for zero-setup embedding | Future |
| **7** | Claude/Canvas — package as a React/JS artifact for AI canvas tools | Future |

---

## Declarative Embedding (Implemented)

The original vision called for Web Component custom elements (`<panel-app>`, `<panel-playground>`). The actual implementation uses standard `<script>` tags with custom `type` attributes, which achieves the same goal with simpler semantics:

```html
<!-- Just drop this in any HTML page -->
<script src="panel-embed.js"></script>

<!-- Renders as an app (no editor) -->
<script type="panel">
import panel as pn
pn.Column("# Hello!", "Panel in the browser!").servable()
</script>

<!-- Renders as editor + app -->
<script type="panel-editor" data-title="My App">
import panel as pn
slider = pn.widgets.FloatSlider(name="Value", start=0, end=10)
pn.Column(slider, pn.bind(lambda v: f"Value: {v}", slider)).servable()
</script>

<!-- Collapsible code below the preview -->
<script type="panel-editor" data-code="hidden" data-layout="code-below">
import panel as pn
pn.Column("# Hello").servable()
</script>

<!-- Load from external file -->
<script type="panel" src="examples/hello.py"></script>
```

**Why `<script type="...">` instead of custom elements:**
- The browser ignores `<script>` tags with unknown `type` values, so the Python code is completely inert until `panel-embed.js` processes it
- No need for Shadow DOM, `connectedCallback()`, or element registration
- Standard HTML — works in any context (CMS, Sphinx, static site generators)
- The `src` attribute has native semantics for loading external resources

**Auto-discovery** runs on `DOMContentLoaded`: `panel-embed.js` scans for all `<script type="panel">` and `<script type="panel-editor">` tags, builds the appropriate DOM structures, and initializes Pyodide. Inline apps are run sequentially (to avoid Pyodide contention); iframe apps load sequentially (to avoid memory spikes).

---

## Comparison: Current Implementation vs Previous PR #5812

| Aspect | PR #5812 | Current Implementation |
|--------|----------|------------------------|
| **Pyodide persistence** | Destroyed on each run (`document.write`) | Persistent (never reloaded) |
| **Reload speed** | ~15-20s (full Pyodide reload) | ~1-2s (state reset only) |
| **State cleanup** | Incomplete (caused idempotency bugs) | Complete: JS views + DOM + Python Document |
| **DOM management** | Pre-rendered by `script_to_html()` | Dynamic `data-root-id` creation at runtime |
| **Template support** | Failed (needed Python process for pre-render) | Works (`write_doc()` handles templates natively) |
| **Package management** | Manual `installIfMissing()` per package | Auto-detect via `find_requirements()` |
| **Code editor** | Basic textarea | CodeMirror 5 with syntax highlighting |
| **Sharing** | None | gzip + base64url in URL hash |
| **Architecture** | Monolithic (conversion + rendering interleaved) | Shared IIFE library (`panel-embed.js`) with declarative + imperative APIs |
| **Execution modes** | Single (iframe only) | Two: inline (single Pyodide) and iframe (per-app Pyodide) |
| **Extension loading** | Manual | Automatic via `loadExtensionResources()` |
| **Embedding boilerplate** | Complex HTML + JS | `<script type="panel">` — one tag |

---

## Running the POCs

```bash
# From the panel repo root
cd poc
python serve.py
# Default: http://localhost:8080 (with COOP/COEP headers)
# Custom port: python serve.py 9000

# Then open in browser:
# POC 1 (core runner):                http://localhost:8080/panel_runner.html
# POC 2 (playground):                 http://localhost:8080/playground.html
# POC 3 (iframe embeds):              http://localhost:8080/embed.html
# POC 4 (single-Pyodide embeds):      http://localhost:8080/embed_single.html
```

**Important**: Use `serve.py` instead of `python -m http.server` — it adds `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: credentialless` headers required for `SharedArrayBuffer`. Without these headers, Pyodide uses a fallback that roughly doubles memory usage and may cause browser crashes.

**External example files** in `poc/examples/`:
- `hello.py` — simple Column app (used by `src` attribute demos)
- `slider.py` — FloatSlider with bound output (used by `src` attribute demos)

**CDN URL patterns** (important — Bokeh and Panel wheels use different base paths):
```javascript
// Bokeh wheel: at CDN root (no Panel version in path)
const BOKEH_WHL = `https://cdn.holoviz.org/panel/wheels/bokeh-${BOKEH_VERSION}-py3-none-any.whl`;
// Panel wheel: under Panel version path
const PANEL_WHL = `https://cdn.holoviz.org/panel/${PANEL_VERSION}/dist/wheels/panel-${PANEL_VERSION}-py3-none-any.whl`;
```

**Version configuration** (via `PanelEmbed.configure()` or defaults in `panel-embed.js`):
```javascript
PanelEmbed.configure({
  pyodideVersion: 'v0.28.2',
  panelVersion: '1.8.7',
  bokehVersion: '3.8.1',
});
```
