# Current POC Analysis: panel-embed.js

**Analyst:** Software Architect, panel-live-cat1 team
**Date:** 2026-02-10
**Scope:** Full analysis of `/home/jovyan/repos/private/panel/live/` codebase

---

## 1. Architecture Map

### Code Structure

The POC is a **single-file IIFE** (Immediately Invoked Function Expression) at `live/src/panel-embed.js` (1479 lines). It exposes a single global `window.PanelEmbed` object. There is no module system, no build step, and no imports. All dependencies (Pyodide, Bokeh, Panel, CodeMirror) are loaded dynamically from CDNs at runtime.

### Main Components

```text
panel-embed.js (IIFE, 1479 lines)
|
+-- Config System          (lines 30-52)    -- Version defaults, CDN URL builder
+-- Script Loader          (lines 54-82)    -- loadScript(), loadCSS(), loadJSResources()
+-- Status Bar             (lines 84-191)   -- injectStyles(), ensureStatusBar(), setStatus()
+-- CSS Injection          (lines 87-171)   -- ~80 CSS rules as JS string array
+-- Pyodide Runtime        (lines 194-244)  -- Singleton init, _doInit() pipeline
+-- Package Manager        (lines 246-299)  -- detectAndInstallRequirements(), loadExtensionResources()
+-- DOM Cleanup            (lines 301-320)  -- cleanupContainer() for Bokeh views
+-- Inline Executor        (lines 322-449)  -- runApp() - 3-branch execution
+-- Runner Executor        (lines 451-568)  -- runRunnerApp() - 3-branch execution (iframe variant)
+-- CodeMirror Manager     (lines 570-628)  -- CM5 lazy loader + factory
+-- Iframe Manager         (lines 630-681)  -- Sequential iframe loading, postMessage relay
+-- Sharing (URL Hash)     (lines 683-701)  -- gzip compress/decompress for URL sharing
+-- Utilities              (lines 703-714)  -- uid(), fetchCode()
+-- Editor DOM Builder     (lines 716-832)  -- buildEditorDOM(), createToolbar()
+-- App Mode               (lines 834-895)  -- appMode() - inline or iframe app
+-- Editor Mode            (lines 897-982)  -- editorMode() - code editor + preview
+-- Playground Mode        (lines 984-1222) -- playgroundMode() - side-by-side editor+preview
+-- Auto-Discover          (lines 1224-1448)-- DOMContentLoaded scanner for <script type="panel">
+-- Public API             (lines 1458-1479)-- window.PanelEmbed = { configure, init, app, editor, playground }
```

### Component Interaction Diagram

```text
                              +---------------------+
                              |   HTML Page (host)   |
                              +---------------------+
                                        |
                    +-------------------+-------------------+
                    |                   |                   |
             Declarative API      Imperative API      Auto-Discover
          <script type="panel">   PanelEmbed.app()   DOMContentLoaded
          <script type="panel-    PanelEmbed.editor()    scan for
           editor">               PanelEmbed.playground() script tags
                    |                   |                   |
                    +-------------------+-------------------+
                                        |
                              +---------+---------+
                              |                   |
                         Inline Mode         Iframe Mode
                              |                   |
                    +---------+          +--------+--------+
                    |                    |                  |
              initPyodide()      panel-runner.html    postMessage
                    |           (loads panel-embed.js   relay
                    |            in iframe context)
                    |                    |
              +-----+-----+       initPyodide()
              |           |             |
          runApp()    loadCodeMirror()  runRunnerApp()
              |                         |
        3-branch exec            3-branch exec
        (servable /              (servable /
         servable+target /        servable+target /
         expression)              expression)
              |                         |
        Bokeh embed_items        Bokeh embed_items
        + _link_docs             + write_doc
```

### Supporting Files

```text
panel-runner.html    -- Minimal HTML that loads panel-embed.js and initializes Pyodide
                        in an iframe. Receives code via postMessage, runs via
                        PanelEmbed._runRunnerApp(). Self-test when opened directly.

playground.html      -- Full-page playground using PanelEmbed.playground() imperative API.
                        Defines examples inline as JS object literals.

embed-iframe.html    -- Demo page: iframe-mode apps and editors using declarative API.
embed-inline.html    -- Demo page: inline-mode (single Pyodide) using declarative API.

serve.py             -- 27-line dev server: SimpleHTTPRequestHandler + COOP/COEP headers.

examples/hello.py    -- 9-line Panel app (external file for src= attribute demo).
examples/slider.py   -- 11-line Panel app (external file for src= attribute demo).
```

---

## 2. API Surface Inventory

### 2.1 Script Types (Declarative API)

#### `<script type="panel">`
Renders a Panel app with no editor UI.

| Attribute | Values | Default | Description |
|-----------|--------|---------|-------------|
| `src` | URL string | (none) | Load code from external .py file |
| `data-target` | element ID | auto-generated | Target container ID |
| `data-iframe` | (presence) | absent | Use iframe isolation |
| `data-height` | CSS value | (none) | Min-height for output |

**Example (inline code):**
```html
<script type="panel">
import panel as pn
pn.Column("# Hello", "World").servable()
</script>
```

**Example (external file, iframe):**
```html
<script type="panel" src="examples/hello.py" data-iframe></script>
```

#### `<script type="panel-editor">`
Renders a code editor above/below a live preview.

| Attribute | Values | Default | Description |
|-----------|--------|---------|-------------|
| `src` | URL string | (none) | Load code from external .py file |
| `data-title` | string | "Panel App" | Header title text |
| `data-iframe` | (presence) | absent | Use iframe isolation |
| `data-height` | CSS value | (none) | Min-height for output |
| `data-layout` | "code-above" / "code-below" | "code-above" | Editor position relative to preview |
| `data-code` | "visible" / "hidden" | "visible" | Initial code visibility (hidden = collapsible) |

**Example (collapsible code, code-below layout):**
```html
<script type="panel-editor" data-code="hidden" data-layout="code-below" data-title="Demo">
import panel as pn
pn.Column("# Hello").servable()
</script>
```

### 2.2 Imperative JavaScript API

#### `PanelEmbed.configure(overrides)`
Sets global configuration. Merges into defaults.

```js
PanelEmbed.configure({
  pyodideVersion: 'v0.28.2',  // Pyodide WASM version
  panelVersion: '1.8.7',      // Panel Python+JS version
  bokehVersion: '3.8.2',      // Bokeh Python+JS version
});
```

Only these three options are supported. No theme, no CDN override, no debug flags.

#### `PanelEmbed.init()`
Eagerly initializes Pyodide. Returns a Promise.
```js
await PanelEmbed.init();
```

#### `PanelEmbed.app(target, code, opts)`
Renders an app into a container.
```js
PanelEmbed.app('my-container', 'import panel as pn\n...', {
  iframe: true,      // use iframe isolation
  src: 'app.py',     // load from URL (overrides code param)
  height: '400px',   // min-height
});
```

#### `PanelEmbed.editor(target, code, opts)`
Renders editor + preview into a container.
```js
PanelEmbed.editor('my-container', 'import panel as pn\n...', {
  iframe: true,
  src: 'app.py',
  title: 'My App',
  layout: 'code-below',
  codeVisibility: 'hidden',
  height: '400px',
});
```

#### `PanelEmbed.playground(target, opts)`
Renders full playground (side-by-side editor + iframe preview).
```js
PanelEmbed.playground('main', {
  code: 'import panel as pn\n...',
  sharing: true,
  resizable: true,
  title: 'Panel Playground',
  examples: {
    "Hello": 'import panel as pn\n...',
    "External": 'examples/hello.py',  // URLs auto-fetched
  },
});
```

#### Internal APIs (exposed for panel-runner.html)
```js
PanelEmbed._setStatus(msg, isError)
PanelEmbed._hideStatus()
PanelEmbed._initPyodide()
PanelEmbed._runRunnerApp(code)
PanelEmbed._loadScript(url)
PanelEmbed._cdnUrls()
```

### 2.3 CSS Classes and Styling Hooks

All classes use `pnl-` prefix. No CSS custom properties.

| Class | Purpose |
|-------|---------|
| `#pnl-status` | Fixed top status bar |
| `.pnl-hidden` | Hidden state for status bar |
| `.pnl-error` | Error state (red background) |
| `.pnl-spinner` | CSS loading spinner animation |
| `.pnl-target` | App render container |
| `.pnl-embed` | App-only wrapper (no editor) |
| `.pnl-editor` | Editor wrapper |
| `.pnl-editor-header` | Editor header bar (Dracula-themed) |
| `.pnl-lang` | "PYTHON" language badge |
| `.pnl-title` | Editor title text |
| `.pnl-shortcut` | Keyboard shortcut hint |
| `.pnl-app-status` | Per-app loading text |
| `.pnl-editor-toolbar` | Collapsible code toggle bar |
| `.pnl-editor-code-section` | Collapsible section wrapper |
| `.pnl-collapsed` | Collapsed state |
| `.pnl-active` | Active toggle button state |
| `.pnl-layout-code-below` | Code-below layout modifier |
| `.pnl-fetch-error` | Error display for failed fetches |
| `.pnl-playground` | Playground root container |
| `.pnl-pg-*` | ~20 playground-specific classes |
| `.pnl-toast` | Toast notification for "Link copied" |

### 2.4 URL Hash API (Sharing)

Used only in playground mode.

```
https://example.com/playground.html#code=<gzip-base64url-encoded-python>
```

- Compression: `CompressionStream('gzip')` + base64url encoding
- Decompression: reverse on page load
- Updated via `history.replaceState()`
- Clipboard copy via `navigator.clipboard.writeText()`

### 2.5 Runner Iframe postMessage Protocol

**Parent -> Runner iframe:**
```js
{ type: 'run', code: '<python code string>' }
```

**Runner iframe -> Parent:**
```js
{ type: 'ready' }       // Pyodide initialized, ready to receive code
{ type: 'rendered' }    // App rendered successfully
{ type: 'error', error: '<error message>' }  // Execution failed
```

---

## 3. Execution Flow Trace

### 3.1 Inline Mode (Single Pyodide)

```text
Page load
  |
  v
DOMContentLoaded fires
  |
  v
autoDiscover() scans DOM
  |
  v
Finds <script type="panel"> tags (no data-iframe)
  |
  v
For each: creates wrapper div + target div, inserts after script tag
  |
  v
Promise.all([loadCodeMirror(), initPyodide(), ...srcFetches])
  |
  v
initPyodide() -> _doInit():
  1. loadJSResources(): Load bokeh-3.8.2.min.js, bokeh-widgets, bokeh-tables, panel.min.js (sequential)
  2. loadScript(pyodide.js): Load Pyodide WASM loader
  3. loadPyodide({fullStdLib: false}): Initialize WASM runtime
  4. loadPackage('micropip'): Install micropip
  5. micropip.install(bokeh.whl, panel.whl, pyodide-http): Install Python packages from wheels
  6. import panel; init_doc(): Initialize Panel Python environment
  7. isReady = true, hideStatus()
  |
  v
For each inline app, sequentially:
  runApp(targetId, code):
    1. detectAndInstallRequirements(code): Uses find_requirements() to discover imports
    2. micropip.install(missing packages)
    3. cleanupContainer(targetId): Remove existing Bokeh views
    4. Branch on code analysis:
       a) .servable() detected (no target=):
          - exec code in isolated namespace (__ns__)
          - Create Document, MockSessionContext
          - loadExtensionResources(): discover __javascript__/__css__ on Bokeh Models
          - Create data-root-id divs in target
          - Bokeh.embed.embed_items() with docs_json
          - _link_docs() for bidirectional sync
       b) .servable(target=...) detected:
          - exec code in isolated namespace
          - loadExtensionResources()
          - write_doc() (Panel handles DOM targeting)
       c) Expression (no .servable()):
          - exec_with_return(code)
          - If result: write(targetId, result) (Panel auto-wraps)
          - If null: show "no visual output" message
    5. On error: display formatted error in target div
    6. runningApps.delete(targetId)
```

### 3.2 Iframe Mode

```text
Page load
  |
  v
autoDiscover() scans DOM
  |
  v
Finds <script type="panel" data-iframe> tags
  |
  v
For each: creates wrapper div + iframe element, inserts after script tag
  |
  v
initIframeListeners(): registers window 'message' listener
  |
  v
Sequential iframe loading (to avoid memory spikes):
  First iframe: set src="panel-runner.html", store code in pendingIframeCode
  Remaining: push to iframeLoadQueue
  |
  v
panel-runner.html loads in iframe:
  1. Loads panel-embed.js (full IIFE again, inside iframe)
  2. Calls PanelEmbed.init() -> initPyodide() (inside iframe context)
  3. On ready: postMessage({type: 'ready'}) to parent
  |
  v
Parent receives 'ready':
  1. Finds which iframe sent it (iterates all iframes, compares contentWindow)
  2. Sends pendingIframeCode via postMessage({type: 'run', code: '...'})
  3. Calls loadNextIframe() to start next iframe
  |
  v
Runner iframe receives 'run':
  runRunnerApp(code):
    1. detectAndInstallRequirements(code)
    2. Cleanup: remove existing Bokeh views, clear #output div, init_doc()
    3. Same 3-branch execution as runApp() but:
       - No namespace isolation (uses global exec())
       - Target is always 'output' (hardcoded)
       - Uses runCount to handle race conditions (stale run detection)
    4. On success: postMessage({type: 'rendered'})
    5. On error: postMessage({type: 'error', error: msg})
```

### 3.3 Playground Mode

```text
PanelEmbed.playground('main', opts) called
  |
  v
playgroundMode() builds full DOM:
  - Header with title, examples dropdown, Run button, Share button, status dot
  - Editor pane: raw <textarea> (NOT CodeMirror)
  - Resize handle
  - Preview pane: iframe with src="panel-runner.html"
  |
  v
Load from URL hash (#code=...) if present:
  decompressCode() -> set textarea value
  |
  v
Examples dropdown: onchange fetches .py URLs or sets inline code
  |
  v
iframe sends 'ready' -> doRun() sends current textarea value to iframe
  |
  v
Run button / Ctrl+Enter -> doRun() sends textarea value via postMessage
  |
  v
Share button -> compressCode() -> update URL hash + clipboard
```

**Key difference from editor mode:** Playground uses a raw `<textarea>` with manual Tab handling, NOT CodeMirror. This is an inconsistency.

---

## 4. Panel Initialization Requirements

### 4.1 Pyodide Loading and Configuration

```text
Required CDN resources (loaded sequentially):
  1. Bokeh JS (3 files, sequential): bokeh-3.8.2.min.js, bokeh-widgets, bokeh-tables
  2. Panel JS (1 file): panel.min.js
  3. Pyodide JS (1 file): pyodide.js
  4. Pyodide WASM: loaded by loadPyodide() (downloaded automatically)
  5. micropip Python package: loaded via pyodide.loadPackage()
  6. bokeh.whl: from cdn.holoviz.org/panel/wheels/
  7. panel.whl: from cdn.holoviz.org/panel/<version>/dist/wheels/
  8. pyodide-http: from PyPI via micropip
```

### 4.2 Bokeh JS Model Registration

Bokeh JS must be loaded BEFORE Panel JS. The load order matters:
1. `bokeh-3.8.2.min.js` - Core
2. `bokeh-widgets-3.8.2.min.js` - Widget models
3. `bokeh-tables-3.8.2.min.js` - Table models
4. `panel.min.js` - Panel's custom Bokeh models

After user code runs, `loadExtensionResources()` discovers additional JS/CSS by scanning `Model.model_class_reverse_map` for `__javascript__` and `__css__` class attributes. This handles extensions like Tabulator, Plotly, etc.

### 4.3 Panel Extension Resource Loading

`loadExtensionResources()` (lines 269-299):
- Runs Python to iterate all registered Bokeh Model classes
- Collects `__javascript__` and `__css__` URLs
- Loads each CSS via `<link>` tags
- Loads each JS via `<script>` tags (sequential)
- Tracks already-loaded URLs to avoid duplicates

### 4.4 The `.servable()` Rendering Pipeline

Three distinct rendering paths based on code analysis:

**Path A: `.servable()` (no target parameter)**
```python
# Setup
doc = Document()
set_curdoc(doc)
doc.hold()
doc._session_context = lambda: MockSessionContext(document=doc)
state.curdoc = doc

# Execute user code (calls .servable() which adds roots to doc)
exec(user_code, namespace)

# Render
docs_json, render_items, root_ids = _doc_json(doc, root_els)
views = Bokeh.embed.embed_items(docs_json, render_items)
jsdoc = list(views[0].roots)[0].model.document
_link_docs(doc, jsdoc)  # bidirectional Python<->JS sync
sync_location()
```

**Path B: `.servable(target=...)` (explicit target)**
```python
# Same setup as Path A
exec(user_code, namespace)
# User code handles its own DOM targeting
await write_doc()  # Panel's built-in write_doc handles everything
```

**Path C: Expression (no `.servable()`)**
```python
result = exec_with_return(user_code, namespace)
if result is not None:
    await write(target_id, result)  # Panel auto-wraps with pn.panel()
```

### 4.5 How `find_requirements()` Works

`panel.io.mime_render.find_requirements()` (called at line 249-255):
- Parses Python code AST
- Extracts `import` and `from X import` statements
- Returns list of package names
- Maps some import names to pip names (e.g., `PIL` -> `Pillow`)
- Does NOT handle: dynamic imports, `__import__()`, conditional imports, packages whose pip name differs from import name

---

## 5. Reusability Assessment

### Config System (lines 30-52) -- REFACTOR
The CDN URL builder pattern is solid and reusable. However:
- Hardcoded to 3 options (pyodide/panel/bokeh versions)
- No CDN base URL override
- No way to point to local wheels or alternate CDNs
- Refactor to support more options (worker mode, debug, theme) and custom CDN URLs

### Pyodide Loader / _doInit() (lines 194-244) -- REFACTOR
The singleton pattern and loading pipeline are reusable in concept:
- (+) Singleton promise prevents double-init
- (+) Sequential loading with status updates
- (-) Runs on main thread (must move to web worker)
- (-) `fullStdLib: false` hardcoded
- (-) No error recovery or retry logic
- (-) Status updates assume main-thread DOM access (won't work from worker)
- Refactor: extract Pyodide init into a worker-compatible module

### Package Manager (lines 246-299) -- REFACTOR
`detectAndInstallRequirements()` and `loadExtensionResources()` are functional:
- (+) Auto-detection via find_requirements() is useful
- (+) Extension resource discovery is essential for Panel
- (-) No explicit requirements API (user can't pin versions)
- (-) `loadedExtResources` uses a flat Set, no per-app scoping
- (-) `installedPackages` is a flat Set, never cleaned up
- Refactor: add explicit requirements support, keep auto-detection as fallback

### Inline Executor / runApp() (lines 322-449) -- REFACTOR
The 3-branch execution logic is the core value of this POC:
- (+) Correctly handles .servable(), .servable(target=), and expression modes
- (+) Namespace isolation via `__ns__`
- (+) Proper Bokeh Document setup (MockSessionContext, doc.hold(), _link_docs)
- (-) Python code as string concatenation (fragile, hard to maintain)
- (-) Servable detection via string matching `.includes('.servable(')` is brittle
- (-) No support for `async def main()` pattern
- (-) No timeout / cancellation
- Refactor: extract Python bootstrap into .py template files, improve detection

### Runner Executor / runRunnerApp() (lines 451-568) -- REPLACE (merge with runApp)
Near-duplicate of runApp() with subtle differences:
- (-) No namespace isolation (`exec()` without namespace dict)
- (-) Hardcoded target='output'
- (-) `runCount` race condition handling is clever but fragile
- (-) Duplicated 3-branch logic
- Replace: merge into unified executor with mode configuration parameter

### CodeMirror Manager (lines 570-628) -- REPLACE
CodeMirror 5 integration:
- (+) Lazy loading pattern is good
- (-) CM5 is maintenance-mode only
- (-) Hardcoded Dracula theme
- (-) CDN (cdnjs.cloudflare.com) blocked by tracking prevention
- (-) Playground mode doesn't even use it (uses raw textarea)
- Replace with CodeMirror 6 (bundled in build)

### Iframe Manager (lines 630-681) -- REFACTOR
Sequential iframe loading:
- (+) Sequential loading prevents memory spikes
- (+) pendingIframeCode + readyIframes handshake works
- (-) No origin validation on postMessage (security hole)
- (-) Identifies iframes by iterating all iframes on page (fragile)
- (-) `loadNextIframe()` has a bug: sets `iframeLoading = false` immediately (line 671), defeating the sequential guard
- Refactor: add origin validation, use MessageChannel, fix sequential loading bug

### Sharing / URL Hash (lines 683-701) -- KEEP AS-IS
Gzip + base64url encoding is solid:
- (+) Standard CompressionStream API
- (+) URL-safe base64 encoding
- (+) Compact output
- Minor improvement: add URL length warning

### CSS / Styling System (lines 87-171) -- REPLACE
80 CSS rules as a JS string array:
- (-) No syntax highlighting in IDE
- (-) No CSS tooling (linting, autoprefixing)
- (-) No CSS custom properties for theming
- (-) Hardcoded colors (Dracula theme colors: #282a36, #f8f8f2, etc.)
- (-) No dark/light mode support
- Replace: extract to separate CSS file with custom properties

### Playground UI (lines 984-1222) -- REFACTOR
The playground mode DOM construction:
- (+) Examples dropdown with URL fetch support
- (+) Resize handle with smooth dragging
- (+) Share button integration
- (-) Uses raw textarea instead of CodeMirror (inconsistent with editor mode)
- (-) ~240 lines of imperative DOM construction (no templating)
- (-) Always uses iframe mode (no inline option)
- Refactor: use CodeMirror, extract DOM construction

### Auto-Discover / DOMContentLoaded (lines 1224-1448) -- REFACTOR
The declarative API scanner:
- (+) Clean scan-and-process pattern
- (+) Separates iframe vs inline apps, processes appropriately
- (+) Handles src fetching, CodeMirror setup, sequential execution
- (-) 224 lines of complex procedural code
- (-) Duplicates setup logic from appMode() and editorMode()
- Refactor: have autoDiscover() simply call appMode()/editorMode() per element

### Error Handling -- REFACTOR
- (+) runApp() catches errors and displays inline
- (-) runRunnerApp() catches errors but only shows in status bar + #output
- (-) No formatted tracebacks
- (-) No stderr capture
- (-) Silent swallowing in Bokeh cleanup (lines 307-317): `catch (e) { /* ignore */ }`

---

## 6. Pain Points & Technical Debt

### 6.1 Hardcoded Values

| Location | Value | Issue |
|----------|-------|-------|
| Line 32 | `pyodideVersion: 'v0.28.2'` | Hardcoded, should be configurable at build time |
| Line 33 | `panelVersion: '1.8.7'` | Hardcoded, out of date (Panel HEAD is building 1.8.8-a.0) |
| Line 34 | `bokehVersion: '3.8.2'` | Hardcoded version coupling |
| Line 218 | `fullStdLib: false` | Hardcoded Pyodide option |
| Line 483 | `'output'` (string) | Hardcoded target ID in runRunnerApp |
| Line 573 | `CM_VERSION = '5.65.18'` | Hardcoded CodeMirror version |
| Line 574 | cdnjs.cloudflare.com | Blocked by tracking prevention |
| Line 667 | `'panel-runner.html'` | Hardcoded runner URL (relative) |
| Line 1077 | `'panel-runner.html'` | Same hardcoded runner URL in playground |

### 6.2 Tight Couplings

1. **panel-runner.html <-> panel-embed.js**: Runner loads the full IIFE and accesses internal `_` prefixed APIs (`_runRunnerApp`, `_initPyodide`, `_setStatus`, etc.). No versioning or compatibility check.

2. **Python string templates <-> Panel internals**: Lines 346-391, 395-418, 422-439, 466-548 contain Python code as JS strings that depend on exact Panel API signatures (`_doc_json`, `_link_docs`, `write_doc`, `write`, `exec_with_return`, `MockSessionContext`, `init_doc`). Any Panel refactor breaks this.

3. **Servable detection <-> string matching**: Lines 339, 393, 489, 490, 518 detect `.servable()` vs `.servable(target=...)` via `code.includes('.servable(')` and regex. A comment containing `.servable(` would trigger the wrong branch.

4. **CDN URL structure <-> version format**: The `cdnUrls()` function (lines 39-52) hardcodes CDN URL patterns. Changes to cdn.holoviz.org or cdn.bokeh.org URL structures break everything.

### 6.3 Duplicated Logic

1. **runApp() vs runRunnerApp()**: Lines 325-449 and 454-568 are ~80% identical 3-branch execution logic. The differences are:
   - runApp uses namespace isolation (`__ns__`), runRunnerApp uses global exec
   - runApp targets arbitrary `targetId`, runRunnerApp hardcodes `'output'`
   - runRunnerApp has `runCount` stale-run detection
   - runApp does `cleanupContainer()` via JS, runRunnerApp does it via Python

2. **Auto-discover vs imperative modes**: `autoDiscover()` (lines 1224-1448) duplicates much of what `appMode()` (837-895) and `editorMode()` (898-982) do, rather than calling them.

3. **Bokeh cleanup**: Two different cleanup approaches - JS-side `cleanupContainer()` (lines 302-320) and Python-side cleanup in runRunnerApp (lines 471-486).

### 6.4 Security Issues

1. **postMessage without origin validation** (lines 637-658, line 37 of panel-runner.html): Any page can send `{type: 'run', code: '...'}` to the runner iframe. The iframe will execute arbitrary Python code. While Pyodide sandboxes most system access, this is still a security concern for pages embedding sensitive data.

2. **No Content Security Policy**: No CSP headers or meta tags. The code dynamically creates script tags from CDN URLs.

3. **eval-equivalent via exec()**: Python `exec()` of user code is expected behavior but should be documented as a security consideration.

### 6.5 Missing Error Handling

| Location | Issue |
|----------|-------|
| Lines 307-317 | Bokeh cleanup silently swallows ALL exceptions |
| Line 218 | `loadPyodide()` failure not caught specifically (falls through to generic catch) |
| Lines 286-298 | `loadExtensionResources()`: if one CSS/JS fails, no error reported |
| Line 463 | `runRunnerApp`: if `currentRun !== runCount`, silently abandoned (no cleanup) |
| Lines 1131-1134 | Example fetch errors only go to `console.warn`, user sees nothing |
| Line 27 | Service worker cleanup: if `location.reload()` fails, page is stuck |

### 6.6 Stale Service Worker Cleanup (lines 13-28)

The IIFE begins by checking for service workers and force-reloading the page. This is a sledgehammer approach:
- Unregisters ALL service workers on the origin (may break other apps)
- Forces a full page reload
- If the reload fails or loops, the IIFE never executes (`return` on line 27)
- Only needed for JupyterLite environments, but affects all deployments

### 6.7 Sequential Loading Bug (lines 661-671)

```js
function loadNextIframe() {
  if (iframeLoading || iframeLoadQueue.length === 0) return;
  iframeLoading = true;         // Set loading flag
  var id = iframeLoadQueue.shift();
  var iframe = document.getElementById(id);
  if (iframe && !iframe.src.includes('panel-runner.html')) {
    iframe.src = 'panel-runner.html';
  }
  iframeLoading = false;        // BUG: immediately unset, defeating the guard
}
```

The `iframeLoading` flag is set to `true` and then immediately set back to `false` on line 671. The intent was to prevent concurrent iframe loading, but the flag is cleared synchronously while the iframe loads asynchronously. The actual sequential behavior comes from `loadNextIframe()` being called from the `ready` message handler (line 653), not from this flag. The `iframeLoading` variable is effectively dead code.

### 6.8 Comparison with Panel's Existing Worker Support

Panel's existing `pyodide_worker.js` and `pyodide_handler.js` templates (in `panel/_templates/`) provide a more mature worker architecture:

| Feature | POC (panel-embed.js) | Panel existing (pyodide_worker/handler) |
|---------|---------------------|----------------------------------------|
| Web Worker | No (main thread) | Yes (dedicated Worker) |
| Bidirectional sync | Yes (_link_docs) | Yes (_link_docs_worker + JSON patches) |
| Event queuing | No | Yes (queue during busy, deduplicate) |
| Patch protocol | N/A (same thread) | Full JSON patch protocol |
| Location sync | sync_location() | Full location update protocol |
| Data archives | No | Yes (unpackArchive for bundled data) |
| Status reporting | DOM-based | postMessage-based |
| Template system | Hardcoded | Jinja2 templated ({{ placeholders }}) |

The existing worker infrastructure could be adapted for panel-live's needs, particularly the patch protocol and event queuing.

---

## Summary Table

| Component | Lines | Verdict | Effort |
|-----------|-------|---------|--------|
| Config system | 30-52 | REFACTOR | Low |
| Script/CSS loader | 54-82 | KEEP | - |
| CSS injection | 87-171 | REPLACE (extract to file) | Medium |
| Status bar | 173-191 | REFACTOR (worker-compatible) | Low |
| Pyodide loader | 194-244 | REFACTOR (move to worker) | High |
| Package manager | 246-299 | REFACTOR (add explicit reqs) | Medium |
| Bokeh cleanup | 301-320 | REFACTOR | Low |
| runApp() executor | 322-449 | REFACTOR (extract Python templates) | Medium |
| runRunnerApp() executor | 451-568 | REPLACE (merge with runApp) | Medium |
| CodeMirror 5 manager | 570-628 | REPLACE (upgrade to CM6) | High |
| Iframe manager | 630-681 | REFACTOR (security + MessageChannel) | Medium |
| URL sharing | 683-701 | KEEP | - |
| Utilities | 703-714 | KEEP | - |
| Editor DOM builder | 716-832 | REFACTOR | Low |
| App mode | 834-895 | REFACTOR | Low |
| Editor mode | 897-982 | REFACTOR | Low |
| Playground mode | 984-1222 | REFACTOR (use CM, reduce DOM construction) | Medium |
| Auto-discover | 1224-1448 | REFACTOR (DRY with imperative API) | Medium |
| Public API | 1458-1479 | REFACTOR (rename to PanelLive) | Low |
