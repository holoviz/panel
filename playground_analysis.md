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

```
┌─────────────────────────────────────────────┐
│  Host Page (playground.html)                │
│  ┌──────────────┐  ┌─────────────────────┐  │
│  │ Code Editor  │  │ Preview iframe      │  │
│  │ (CodeMirror) │  │ (panel_runner.html) │  │
│  │              │──│                     │  │
│  │ [Run button] │  │ ┌─────────────────┐ │  │
│  │              │  │ │ Pyodide (ONCE)  │ │  │
│  │              │  │ │ Panel/Bokeh     │ │  │
│  │              │  │ │ (installed ONCE)│ │  │
│  │              │  │ ├─────────────────┤ │  │
│  │              │  │ │ runPanelCode()  │ │  │
│  │              │  │ │ 1. Reset state  │ │  │
│  │              │  │ │ 2. Exec code    │ │  │
│  │              │  │ │ 3. Render app   │ │  │
│  └──────────────┘  │ └─────────────────┘ │  │
│                    └─────────────────────┘  │
│  Communication: window.postMessage()        │
└─────────────────────────────────────────────┘
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

## POC Implementations

### POC 1: `poc/panel_runner.html` - The Core Primitive

**What it is:** A single HTML file that loads Pyodide + Panel once and provides a `runPanelCode(code)` JavaScript function for dynamic execution.

**Key features:**
- Loads Pyodide, Bokeh JS, and Panel JS in parallel for fastest initial load
- `runPanelCode(code)` handles cleanup, code execution, and rendering
- Auto-detects and installs new package requirements
- Supports `.servable()`, `.servable(target=...)`, and auto-display (last expression)
- Loading status indicator with progress messages
- iframe `postMessage` API for embedding: `iframe.contentWindow.postMessage({type: 'run', code: '...'})`
- Standalone mode with self-test demo when opened directly

**Testing:**
```bash
cd poc
python -m http.server 8080
# Open http://localhost:8080/panel_runner.html
```

When opened directly, it runs a self-test demo. When embedded as an iframe, it waits for `postMessage` commands.

### POC 2: `poc/playground.html` - Editor + Live Preview

**What it is:** A side-by-side code editor + live preview, like shinylive or stlite.

**Key features:**
- CodeMirror 6 editor with Python syntax highlighting
- Side-by-side layout with draggable resize handle
- Run button + Ctrl/Cmd+Enter keyboard shortcut
- 6 built-in examples (Hello, Slider, Matplotlib, DataFrame/Tabulator, Template, Chat)
- URL-based sharing: gzip + base64url in URL hash fragment
- Ready indicator (red dot = loading, green = ready)
- Auto-runs initial example when iframe is ready

**Testing:**
```bash
cd poc
python -m http.server 8080
# Open http://localhost:8080/playground.html
```

**Sharing test:**
1. Edit code in the editor
2. Click "Share" button
3. URL is copied to clipboard with `#code=...` hash
4. Open the URL in a new tab - same code appears and runs

### POC 3: `poc/embed.html` - Embeddable Snippets

**What it is:** Demonstrates embedding Panel apps in any HTML page with minimal boilerplate.

**Key features:**
- Simple embed: just an iframe + `panelEmbed('id', code)` call
- Inline editor: textarea + preview iframe with Run button
- Auto-servable: code without `.servable()` auto-displays the last expression
- Shows the path toward `<panel-app>` custom elements and Claude.ai artifacts

**Testing:**
```bash
cd poc
python -m http.server 8080
# Open http://localhost:8080/embed.html
```

**Claude.ai / Artifact embed pattern:**
```html
<iframe src="https://your-cdn.com/panel_runner.html"
        style="width:100%;height:400px;border:none"></iframe>
<script>
const iframe = document.querySelector('iframe');
iframe.onload = () => {
  iframe.contentWindow.postMessage({
    type: 'run',
    code: 'import panel as pn\npn.Column("Hello!").servable()'
  }, '*');
};
</script>
```

---

## Known Limitations & Future Work

### Current POC Limitations

1. **Memory leaks**: Pyodide proxy functions (`_proxies` list in `pyodide.py`) accumulate across runs. For long editing sessions, this could grow. Fix: add explicit cleanup of old proxies.

2. **Template JS extensions**: Some Panel extensions (Tabulator, Plotly, Perspective) require additional JS loaded in the page. The current POC loads base Bokeh/Panel JS. Dynamic extension loading needs work.

3. **Cross-origin**: The iframe approach requires same-origin or proper CORS headers. For CDN hosting, this needs `Access-Control-Allow-Origin` headers.

4. **No `pn.extension()` args**: Extensions like `pn.extension("tabulator")` need the corresponding JS to be pre-loaded in the page. The POC would need dynamic JS loading.

5. **Version coupling**: The Bokeh JS version must exactly match the Bokeh Python wheel version. The POC parameterizes this but it's fragile.

### Roadmap

| Phase | Feature | Description |
|-------|---------|-------------|
| **1** | Core runner | `panel_runner.html` - persistent Pyodide + clean state reset (this POC) |
| **2** | Editor playground | Side-by-side editor + preview with sharing (this POC) |
| **3** | Dynamic JS loading | Auto-load extension JS (tabulator, plotly, etc.) based on `pn.extension()` call |
| **4** | Web component | `<panel-playground>` custom element for trivial embedding |
| **5** | Sphinx directive | Enhanced nbsite directive with editor + preview mode |
| **6** | CDN hosting | Host `panel_runner.html` on `cdn.holoviz.org` for zero-setup embedding |
| **7** | Claude/Canvas | Package as a React/JS artifact for AI canvas tools |

### Solving the Extension JS Loading Problem

The biggest remaining challenge is dynamically loading JS for Panel extensions. Approach:

```javascript
// After running user code, check what extensions were requested
const extensions = await pyodide.runPythonAsync(`
  import json
  from panel.config import config
  json.dumps(list(config._extensions_loaded))
`);
// Dynamically load the required JS files
for (const ext of JSON.parse(extensions)) {
  await loadScript(`https://cdn.holoviz.org/panel/${PANEL_VERSION}/dist/bundled/${ext}/...`);
}
```

### Web Component Vision

The ultimate API goal:

```html
<!-- Just drop this in any HTML page -->
<script src="https://cdn.holoviz.org/panel/playground.js"></script>

<!-- Renders as an app -->
<panel-app>
import panel as pn
pn.Column("# Hello!", "Panel in the browser!").servable()
</panel-app>

<!-- Renders as editor + app -->
<panel-playground height="500px">
import panel as pn
slider = pn.widgets.FloatSlider(name="Value", start=0, end=10)
pn.Column(slider, pn.bind(lambda v: f"Value: {v}", slider)).servable()
</panel-playground>
```

This would be implemented as a Web Component that creates the iframe + editor + runner infrastructure automatically.

---

## Comparison: POC vs Previous PR #5812

| Aspect | PR #5812 | This POC |
|--------|----------|----------|
| **Pyodide persistence** | Destroyed on each run (`document.write`) | Persistent (never reloaded) |
| **Reload speed** | ~15-20s (full Pyodide reload) | ~1-2s (state reset only) |
| **State cleanup** | Incomplete (caused idempotency bugs) | Complete: JS views + DOM + Python Document |
| **DOM management** | Pre-rendered by `script_to_html()` | Dynamic `data-root-id` creation at runtime |
| **Template support** | Failed (needed Python process for pre-render) | Works (`write_doc()` handles templates natively) |
| **Package management** | Manual `installIfMissing()` per package | Auto-detect via `find_requirements()` |
| **Code editor** | Basic textarea | CodeMirror 6 with syntax highlighting |
| **Sharing** | None | gzip + base64url in URL hash |
| **Architecture** | Monolithic (conversion + rendering interleaved) | Layered (runner as iframe, editor as host) |

---

## Running the POCs

```bash
# From the panel repo root
cd poc
python -m http.server 8080

# Then open in browser:
# POC 1 (core runner):     http://localhost:8080/panel_runner.html
# POC 2 (playground):      http://localhost:8080/playground.html
# POC 3 (embedding demo):  http://localhost:8080/embed.html
```

**Important**: The POC uses Panel 1.8.7 and Bokeh 3.8.1 from CDN. Adjust the version constants at the top of `panel_runner.html` if needed.

**CDN URL patterns** (important - Bokeh and Panel wheels use different base paths):
```javascript
// Bokeh wheel: at CDN root (no Panel version in path)
const BOKEH_WHL = `https://cdn.holoviz.org/panel/wheels/bokeh-${BOKEH_VERSION}-py3-none-any.whl`;
// Panel wheel: under Panel version path
const PANEL_WHL = `https://cdn.holoviz.org/panel/${PANEL_VERSION}/dist/wheels/panel-${PANEL_VERSION}-py3-none-any.whl`;
```

**Version configuration** (in `panel_runner.html`):
```javascript
const PYODIDE_VERSION = 'v0.28.2';
const PANEL_VERSION = '1.8.7';
const BOKEH_VERSION = '3.8.1';
```
