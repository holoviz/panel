# Panel Live - Issues & Roadmap

Outstanding issues for the Panel Live feature. See also `live-dream.md` for vision and `live-analysis.md` for architecture notes.

**Priority levels:**

- **P0 - Blocker**: Must resolve before any public release. Fundamental decisions or critical bugs.
- **P1 - Critical**: Required for a credible MVP / initial release.
- **P2 - Important**: Needed for a polished, competitive product.
- **P3 - Nice-to-have**: Future enhancements and stretch goals.

**Current state:** 28 issues total. 3 resolved, 10 partially addressed, 15 completely open, 1 needs investigation. The POC is a working prototype (`src/panel-embed.js`, 1479 lines) with two execution modes (iframe and inline), a declarative `<script type="panel">` API, CodeMirror editor, and URL-based sharing.

---

## Category 1: Foundation & Architecture Decisions

These issues must be resolved first as they shape everything else.

### P0 - Design Extensible User/Developer-Facing API

**Problem:** The current POC's API (`<script type="panel">`, `<script type="panel-editor">`, `<script type="panel-playground">`) works for single-file, default-config apps. But the API must be designed now to naturally accommodate multi-file support, explicit requirements, layout options, themes, and other configuration without breaking changes later.

**Why it matters:** This is the most important near-term priority. Getting the API right means features like multi-file support, requirements specification, layout options, and theming can be added incrementally without breaking existing users. Getting it wrong means painful migrations or ugly workarounds.

**Design considerations:**

- How do users specify additional files? (child elements, attributes, config block)
- How do users declare requirements? (attribute, child element, config file)
- How do layout/theme/config options compose? (attributes vs config object vs CSS variables)
- Should there be a JSON/YAML config block approach (like PyScript's `<py-config>`) for complex configuration?
- How does the JS API (`PanelLive.configure()`) relate to the HTML attribute API?
- Should there be a single `<script type="panel">` tag with mode/display configured via attributes (e.g., `mode="editor"`, `mode="playground"`) rather than separate script types? This could simplify the API and make mode-switching more natural. (See also: Interactive API Explorer issue)
- How is the language/pill label configured? (attribute, config, default to 'PYTHON')
- How are example apps provided? (inline child elements, JSON URL via attribute like `examples-src`, or both)
- How are runtime versions (Pyodide, Python, Panel, Bokeh) exposed to users? How does version switching interact with the runtime lifecycle (full restart, hot-swap)?

**Acceptance criteria:** Documented API design that shows how current features work AND how future features (multi-file, requirements, layout, themes) will extend the API without breaking changes. Design reviewed and approved.

**Blocks:** Multi-file Support, Requirements / Package Specification, Playground Layout Options, Customizable Styling.

---

### P0 - Settle on Name [RESOLVED]

**Decision:** The name is **`panel-live`**. This mirrors the "shinylive" naming convention and communicates interactivity.

**Implications:**

- JS library: `PanelLive`
- Script types: `<script type="panel">`, `<script type="panel-editor">`, `<script type="panel-playground">`
- CDN path: `cdn.holoviz.org/panel-live/1.0.0/panel-live.min.js`
- npm package: `panel-live`
- Sphinx extension: `sphinx-panel-live` (directive: `.. panel-live::`)
- MkDocs extension: `mkdocs-panel-live`
- CSS: `panel-live.css`

---

### P0 - Determine Repository [RESOLVED]

**Decision:** The code stays in the **panel repo**. This simplifies version coupling (Bokeh JS version must match Bokeh Python wheel exactly) and keeps everything in one CI pipeline.

**Hosting:** The live site will use a separate GitHub Pages repo following the existing panelite pattern: `holoviz-dev/panel-live` (analogous to `holoviz-dev/panelite`).

---

### P0 - Web Worker Support

**Problem:** Pyodide runs on the main thread, blocking the page during load (~5-15 seconds) and during Python execution. The page becomes completely unresponsive.

**Why it matters:** **Every competitor uses web workers** (stlite, gradio-lite, shinylive, PyScript). This is table stakes for a credible product. Without workers, embedding in documentation or content pages degrades the entire page experience.

**Current state:** No web worker usage in panel-live. However, **Panel already has a complete, production-proven web worker implementation** used by `panel convert --to pyodide-worker` (the default target). This should be adapted rather than built from scratch.

**Existing Panel worker architecture** (2 template files, ~190 lines total):

- `panel/_templates/pyodide_worker.js` — Runs Pyodide in a Web Worker. Loads packages, executes user code, returns serialized Bokeh document JSON via `postMessage`. Never touches the DOM.
- `panel/_templates/pyodide_handler.js` — Main thread handler. Creates the Worker, receives the rendered document, calls `Bokeh.embed.embed_items()` to do all DOM work, then sets up bi-directional sync via Bokeh's JSON patch protocol.

**Message protocol (proven pattern):**

```
Worker → Main:  {type: 'status', msg}         Loading progress
Worker → Main:  {type: 'render', docs_json, render_items, root_ids}   Initial render
Worker → Main:  {type: 'patch', patch, buffers}   Python-side changes
Worker → Main:  {type: 'idle'}                 Ready for next patch
Main → Worker:  {type: 'rendered'}             DOM is ready, link docs
Main → Worker:  {type: 'patch', patch}         User interaction (widget change)
Main → Worker:  {type: 'location', location}   URL/location sync
```

**Key design insight — how Panel solves "Pyodide needs DOM access":**

Pyodide in the worker **never touches the DOM**. Instead:
1. Worker runs Python code → generates Bokeh document JSON (`_doc_json()`)
2. Worker sends serialized JSON to main thread via `postMessage`
3. Main thread calls `Bokeh.embed.embed_items()` for all DOM rendering
4. Bi-directional sync uses `_link_docs_worker(doc, sendPatch)` (Python side) and `jsdoc.on_change(send_change)` (JS side) to relay JSON patches between the worker's Python doc and the main thread's Bokeh JS doc
5. Event queue with busy/idle handshake prevents race conditions

**Adaptation plan for panel-live:**

1. Adapt `pyodide_worker.js` to work dynamically (current version uses build-time template variables `{{ code }}`, `{{ env_spec }}`, etc. — panel-live needs to send code at runtime via `postMessage`)
2. Adapt `pyodide_handler.js` to target arbitrary containers (current version assumes full-page rendering with `document.querySelectorAll('[data-root-id]')`)
3. Support re-running code (current worker is one-shot; panel-live editor/playground needs to re-execute)
4. Consider SharedWorker for multiple apps on one page (reduces memory from ~300-500MB per app to ~300-500MB total)

**Acceptance criteria:** Pyodide loads and runs Python in a web worker. Main thread stays responsive (no jank). Loading spinner/progress animates smoothly during load.

**Blocks:** Keep page responsive during load. Related to: Browser Crash (main thread memory pressure).

---

### P0 - Browser Crash (STATUS_ACCESS_VIOLATION)

**Problem:** The browser keeps crashing with `STATUS_ACCESS_VIOLATION` - both behind Jupyter server proxy and locally on Windows, including when using `serve.py`. Sometimes stops around "Loaded pyodide-http", sometimes crashes immediately.

**Why it matters:** A crashing browser is a showstopper. Users cannot evaluate or trust the product.

**Current state:** `serve.py` adds COOP/COEP headers for SharedArrayBuffer (reduces Pyodide memory ~50%). `live-analysis.md` documents that without these headers, Pyodide doubles memory usage. But crashes still occur.

**Likely causes:**

- Multiple Pyodide instances in iframe mode (each ~300-500MB)
- Main thread memory pressure without web workers
- Missing COOP/COEP headers when served behind proxies that strip them

**Suggested approach:**

1. Reproduce and document exact crash conditions (browser, OS, number of apps, iframe vs inline mode)
2. Add memory monitoring / logging before crash point
3. Web Worker support (P0 above) should significantly reduce main thread memory pressure
4. Limit concurrent Pyodide instances; already sequential for iframes but consider a hard cap
5. Investigate SharedArrayBuffer availability and fallback behavior

**Acceptance criteria:** No browser crashes on reference hardware (8GB RAM machine) with up to 3 concurrent apps. Known limitations documented.

---

### ~~P1 - Evaluate PyScript as Foundation~~ [RESOLVED — REJECTED]

**Decision:** PyScript will **not** be used as a foundation or dependency.

**Reasons:**

1. **Extra dependency risk** — PyScript must be version-compatible with both Pyodide and Panel. Three-way version coupling is fragile and hard to maintain.
2. **Stability concerns** — PyScript has historically been unstable, with breaking API changes across releases.
3. **Not needed** — The web component POC (`poc/webcomponent/panel-live.js`) proves that everything works without PyScript: Pyodide loading, code execution, editor (CodeMirror), extension resource loading, and Panel rendering.
4. **Panel already has worker support** — `panel/_templates/pyodide_worker.js` provides a proven web worker pattern, eliminating PyScript's `coincident` as a motivation.

**POC evaluation completed** — see `docs/research/pyscript-evaluation.md` and `poc/pyscript/` for the full investigation. The POC confirmed that PyScript adds a layer of abstraction with no meaningful value for Panel's use case.

---

### P1 - Folder and File Structure [CONFIRMED]

**Problem:** The monolithic `panel-embed.js` (1479 lines IIFE) is hard to maintain, test, or tree-shake.

**Why it matters:** A proper structure is needed before adding features, tests, or build tooling. Technical debt compounds fast.

**Current structure:**

```text
live/
  serve.py             # dev server
  src/
    panel-embed.js     # 1479-line monolith
    panel-runner.html  # iframe runner
  demos/
    playground.html    # full-page playground
    embed-iframe.html  # iframe demos
    embed-inline.html  # inline demos
  examples/            # 2 example .py files
```

**Confirmed structure:**

```text
panel/live/            # in panel repo, under panel-live name
  src/
    index.js           # entry point
    pyodide-loader.js  # Pyodide initialization
    app-runner.js      # code execution (inline + iframe)
    editor.js          # CodeMirror integration
    playground.js      # side-by-side editor+preview
    styles.css         # extracted CSS
    utils.js           # shared utilities
  templates/
    runner.html        # iframe runner
  examples/
    *.py
  tests/
    *.spec.js          # or playwright tests
  package.json
  build config
```

**Acceptance criteria:** Code split into logical modules. Build step produces a single distributable bundle. No functionality regression.

**Blocked by:** Settle on Name (resolved).

---

### P1 - Separate CSS [CONFIRMED]

**Problem:** ~80 CSS rules are injected inline via `injectStyles()` as a joined string array in JavaScript. Hard to maintain, no syntax highlighting, no CSS tooling support.

**Why it matters:** Both stlite and gradio-lite load separate CSS files. This is standard practice. The current approach prevents CSS linting, autoprefixing, and makes theming harder.

**Confirmed approach:**

1. Extract CSS to a separate `.css` file (`panel-live.css`)
2. Build step bundles or inlines as needed
3. Users load via `<link rel="stylesheet" href="panel-live.css">`
4. Use CSS custom properties (variables) for theming (connects to "Customize Styling" issue)

**Acceptance criteria:** CSS in a separate source file. Build produces both standalone CSS and a JS bundle that can optionally auto-inject it.

---

## Category 2: Bugs & Stability

Issues that affect reliability of the current implementation.

### ~~P0 - Does Not Work with panel-material-ui~~ [RESOLVED]

**Problem:** A "shim" error appeared in the browser console when creating apps that use panel-material-ui.

**Resolution:** Confirmed working in `poc/webcomponent/test-playground.html` — `pmui.Button(label="Click Me")` renders successfully. The original issue may have been related to an older panel-material-ui version or missing extension resource loading. The web component POC's `loadExtensionResources()` correctly loads PMU's JS/CSS dependencies.

**Status:** No longer a blocker. Keep an eye on more complex PMU widgets (e.g., DataGrid, Select) but basic functionality is confirmed.

---

### P1 - Cannot Select Code with Mouse

**Problem:** In the panel-editor mode, it's not possible to use the mouse to select code, making it hard to copy.

**Why it matters:** Basic editor usability. Users expect to be able to select and copy code.

**Likely cause:** CSS `pointer-events`, `user-select`, or CodeMirror configuration issue. Could also be an overlay/z-index problem.

**Suggested approach:**

1. Test in multiple browsers to confirm
2. Inspect CodeMirror container CSS for `user-select: none` or `pointer-events: none`
3. Check for overlapping transparent elements capturing mouse events

**Acceptance criteria:** Users can select code with mouse in all editor modes. Works in Chrome, Firefox, Safari, Edge.

---

### P1 - Handle Python Errors Properly

**Problem:** Python exceptions go to the browser console but aren't communicated well to the user. Tracebacks are raw and unformatted.

**Why it matters:** Users (especially beginners) need clear, visible error messages to debug their code. This is critical for the editor/playground use case.

**Current state:** Partially addressed - `runApp()` catches top-level errors and displays them inline with red styling. But tracebacks are unformatted, and errors in async code or callbacks may still go only to console.

**Suggested approach:**

1. Format Python tracebacks with syntax highlighting (filename, line number, error type)
2. Display errors in a dedicated error panel below the code editor (like PyScript's `py-editor` or Jupyter's error output)
3. Capture `sys.stderr` and `console.error` from the Pyodide context
4. For playground mode: show errors in a collapsible panel that doesn't replace the app output
5. Include a "Copy error" button for bug reporting

**Acceptance criteria:** All Python errors visible to the user in a formatted error panel. Tracebacks show file, line number, and error message clearly.

---

### P2 - Tracking Prevention Blocks CDN Resources

**Problem:** Browser tracking prevention blocks `cdnjs.cloudflare.com` resources (CodeMirror CSS), logged as: `Tracking Prevention blocked access to storage for https://cdnjs.cloudflare.com/...`

**Why it matters:** Users with strict browser settings (common in corporate environments) get a broken editor.

**Suggested approach:**

1. Prefer a non-blocked CDN (e.g., `cdn.jsdelivr.net`) as the primary CDN for CodeMirror assets
2. Upgrading to CodeMirror 6 (separate issue) may resolve this entirely by bundling CM6 into the build
3. Bundling CodeMirror CSS into the panel-live CSS file during build as a longer-term solution

**Acceptance criteria:** Editor works with browser tracking prevention enabled. No third-party CDN dependencies for core functionality.

---

### P2 - CodeMirror 5 is Legacy

**Problem:** The POC uses CodeMirror 5 which is in maintenance mode. CodeMirror 6 is the actively developed version with better accessibility, mobile support, and extensibility.

**Why it matters:** CodeMirror 5 won't receive new features. Competitors use CodeMirror 6 or Monaco. The `playground.html` inconsistently uses a raw `<textarea>` instead of CodeMirror.

**Suggested approach:** Upgrade to CodeMirror 6. This also resolves the Tracking Prevention issue (bundle CM6 in the build) and potentially the mouse selection issue.

**Acceptance criteria:** CodeMirror 6 used consistently across editor and playground modes. Same editing experience in both.

---

### P2 - postMessage Security

**Problem:** `window.addEventListener('message', ...)` in both `panel-runner.html` and `panel-embed.js` does not validate `event.origin`. Any page could send messages to the runner iframe.

**Why it matters:** Security vulnerability. A malicious page could inject arbitrary Python code into the runner iframe if it knows the message format.

**Suggested approach:** Validate `event.origin` against the expected parent origin. Use a nonce or token for message authentication.

**Acceptance criteria:** postMessage handlers validate origin. Documented security model.

---

### P2 - Memory Leak on Re-run (Hypothesis)

**Problem:** `live-analysis.md` documents that Pyodide proxy functions may accumulate across runs. No cleanup mechanism exists. **Note:** This is currently a hypothesis that needs testing, not a confirmed bug.

**Why it matters:** In playground/editor mode, users re-run frequently. If memory does grow with each run, it would eventually degrade performance or crash.

**Suggested approach:**

1. **First, confirm whether memory actually leaks** via browser profiling (DevTools Memory tab) across 20+ re-runs of the same app
2. If confirmed: investigate `pyodide.runPython` cleanup, `destroy()` proxies, or full namespace reset between runs
3. If not confirmed: close this issue

**Acceptance criteria:** Browser profiling results documenting memory behavior across 20+ consecutive re-runs. If leak confirmed: memory usage stays stable. If not: issue closed with evidence.

---

## Category 3: Developer Experience & Features

Features needed for a competitive product.

### P1 - Interactive API Explorer Page

**Problem:** There is no interactive page where users (and developers) can explore the panel-live API hands-on - switching between app/editor/playground display modes, changing themes, toggling layout options, adjusting configuration, etc. in real time.

**Why it matters:** An interactive explorer serves two purposes: (1) it's the best way for users to discover and understand what panel-live can do, and (2) it directly informs API design decisions. For example, if users can interactively switch from app display to editor to playground, this raises the question of whether the API should use a single `<script type="panel">` tag with a `mode` attribute (e.g., `mode="app"`, `mode="editor"`, `mode="playground"`) rather than separate script types. Building this explorer early will pressure-test the API before it's locked in.

**Suggested approach:**

1. Create an interactive page (itself built with panel-live) that lets users:
   - Switch between display modes (app, editor, playground)
   - Change themes (light, dark, custom)
   - Toggle layout (horizontal, vertical)
   - Configure options (requirements, height, etc.)
   - See the corresponding HTML markup update live
2. Use this as a testbed for API design decisions
3. Eventually publish as part of the documentation / examples gallery

**Acceptance criteria:** Interactive page where users can explore all API options and see both the rendered result and the HTML markup needed to reproduce it.

**Related to:** API Design (P0), Documentation (P1).

---

### P2 - Multi-file Support

**Problem:** Only single-file apps are supported. Users cannot import from helper modules or use multi-file project structures.

**Why it matters:** Every competitor supports multi-file apps (stlite via `files` config, gradio-lite via `<gradio-file>`, shinylive via multiple file blocks, PyScript via multiple scripts). Real-world apps often split code across modules.

**Note:** Implementation deferred, but the API design (P0 above) must accommodate this feature.

**Suggested approach:**

- Support declaring additional files (e.g., `<script type="panel-file" name="utils.py">` or a config attribute)
- Write files to the Pyodide virtual filesystem before executing the entrypoint
- One file marked as entrypoint

**Acceptance criteria:** Users can define multiple Python files and import between them. At least one demo shows a multi-file app.

---

### P2 - Requirements / Package Specification

**Problem:** The POC auto-detects packages via `find_requirements()` but provides no way for users to explicitly specify requirements or pin versions.

**Why it matters:** Auto-detection is fragile (misses dynamic imports, conditional imports, packages with different import vs pip names). Every competitor provides explicit requirements support. Users need control over their dependencies.

**Note:** Implementation deferred, but the API design (P0 above) must accommodate this feature.

**Suggested approach:**

- Support a requirements attribute or child element (e.g., `<script type="panel" requirements="pandas==2.0,plotly">` or `<script type="panel-requirements">`)
- Keep auto-detection as a fallback
- Show package installation progress

**Acceptance criteria:** Users can explicitly declare requirements. Installation progress visible. Auto-detection still works as fallback.

---

### P1 - Copy Code Button

**Problem:** No way to easily copy code from the editor or app view. Combined with the mouse selection bug, code is effectively locked.

**Why it matters:** Users want to copy examples to their own projects. This is a primary use case for documentation embeddings.

**Suggested approach:** Add a copy-to-clipboard button (top-right corner of code block, like GitHub code blocks). Show brief "Copied!" confirmation.

**Acceptance criteria:** Copy button visible on hover/focus in both editor and app (visible code) modes. Works across browsers.

---

### P1 - Loading Progress (All Modes)

**Problem:** Loading progress varies between modes. Inline mode shows "Waiting for Pyodide..." text. Iframe mode shows a progress bar. Playground mode has its own approach. No percentage or stage information.

**Why it matters:** Pyodide takes 5-15 seconds to load. Users need to know something is happening and how long to wait.

**Suggested approach:**

1. Consistent loading UI across all modes: spinner + stage text + optional progress bar
2. Stages: "Loading Pyodide..." -> "Installing packages..." -> "Running app..."
3. Animate smoothly (requires web worker so main thread isn't blocked)

**Acceptance criteria:** All three modes show consistent, animated loading progress with stage information.

---

### P2 - Choose and Configure Editor Theme

**Problem:** The editor uses CodeMirror's Dracula theme (dark/neon). No way to change it. May not suit all environments (corporate, light-mode sites).

**Why it matters:** The editor is embedded in third-party pages. A dark neon theme clashing with a light corporate site looks unprofessional.

**Suggested approach:**

1. Default to a neutral theme (e.g., `one-light` for light, `one-dark` for dark)
2. Support `theme` attribute: `<script type="panel-editor" theme="dracula">`
3. Auto-detect light/dark from `prefers-color-scheme` or host page
4. Ship 2-3 built-in themes (light, dark, high-contrast)

**Acceptance criteria:** Default theme looks professional in both light and dark contexts. Users can switch themes via attribute.

---

### P2 - Align Styles Across Modes

**Problem:** Styling is inconsistent between "panel" (app only), "panel-editor" (code + app), and "panel-playground" (side-by-side) modes.

**Why it matters:** Inconsistent styling feels unpolished and makes it harder to switch between modes.

**Current state:** `injectStyles()` provides some shared styling, but it's hardcoded with no systematic design system.

**Acceptance criteria:** Consistent visual language (borders, spacing, colors, fonts) across all three modes. Documented in a style guide.

---

### P2 - Customizable Styling / Branding

**Problem:** No CSS variables, no theming API, no way to brand the embedded components. `PanelLive.configure()` only handles versions, not styling.

**Why it matters:** Organizations embedding Panel apps want them to match their brand. Documentation sites want the editor to match their theme.

**Suggested approach:**

1. CSS custom properties for all configurable values (colors, fonts, spacing, border radius)
2. Sensible defaults that work out of the box
3. Optional `PanelLive.configure({ theme: { primaryColor: '#007bff' } })` for programmatic theming
4. Dark mode support via `prefers-color-scheme` media query
5. The header language pill label (currently says "PANEL") should default to "PYTHON" and be configurable via an attribute (e.g., `label="Panel"`) or CSS custom property

**Acceptance criteria:** Users can customize primary color, background, font, border-radius, and header pill label via CSS variables or attributes. Dark mode supported.

---

### P2 - Playground Layout Options

**Problem:** The playground is always side-by-side (code left, preview right). No horizontal layout (code top, preview bottom) or other options.

**Why it matters:** Gradio-lite supports `layout="horizontal"|"vertical"`. Different contexts call for different layouts (narrow pages need vertical, wide pages need horizontal).

**Suggested approach:** Support `layout` attribute with `horizontal` (side-by-side, current default) and `vertical` (code above, preview below). Auto-detect based on container width as a bonus.

**Acceptance criteria:** Both horizontal and vertical layouts work. Responsive behavior on narrow screens.

---

### P2 - Version Info Display & Version Switching

**Problem:** Users have no way to see which versions of Pyodide, Python, Panel, Bokeh, and other installed packages are running. In playground mode, there is also no way to switch between versions of Pyodide, Panel, or Bokeh and restart the runtime with the new versions.

**Why it matters:** Version visibility is essential for debugging ("does my code fail because of a Panel bug fixed in a newer release?") and for reproducing issues ("which exact versions was this shared snippet running on?"). Version switching in the playground lets users test their code against different releases, verify bug fixes, and explore new features — all without leaving the browser.

**Suggested approach:**

1. **Version info display (all modes):**
   - Show an info panel / popover (e.g., triggered by an ℹ️ icon or "About" link) listing runtime versions: Pyodide, Python, Panel, Bokeh, and any user-installed packages with their versions
   - Query versions at runtime from `pyodide.version`, `panel.__version__`, `bokeh.__version__`, `sys.version`, and `micropip.list()` or equivalent
   - Optionally include this info in the URL-shared state so recipients see the same environment

2. **Version switching (playground mode):**
   - Provide a UI (dropdown, settings panel, or modal) to select versions of Pyodide, Panel, and Bokeh
   - Changing a version triggers a full runtime restart: tear down the current Pyodide instance, load the selected Pyodide version, reinstall packages at the selected versions, and re-run the user's code
   - Show available versions (fetched from CDN/PyPI metadata or a curated list)
   - Warn users that switching versions restarts the runtime and clears any in-memory state

**Acceptance criteria:** All modes display current runtime/package versions on demand. Playground mode allows users to switch Pyodide, Panel, and Bokeh versions and restart the runtime. Version info is accurate and updates after a version switch.

**Related to:** API Design (P0), Loading Progress (P1).

---

### P3 - URL Sharing with Compression

**Problem:** URL sharing exists (gzip + base64url in hash) but could be improved.

**Why it matters:** Sharing is a key use case for playgrounds and documentation. Shorter URLs are easier to share.

**Current state:** Working basic implementation.

**Suggested improvements:**

- Show a "Share" button that copies the URL
- Preview the URL length / warn if too long
- Consider py.cafe's approach with `c=` parameter for gzip-compressed JSON

**Acceptance criteria:** Share button visible in playground/editor modes. Generates compact, shareable URL.

---

### P3 - Dark Theme Support

**Problem:** No dark/light theme toggle for the embedded app output area.

**Why it matters:** Pages using dark mode expect embedded content to match.

**Suggested approach:** Support `theme="dark"|"light"|"auto"` attribute. "auto" detects from `prefers-color-scheme`.

**Acceptance criteria:** Dark and light themes for the app container. Auto-detection works.

---

### P2 - Zero-Install Deployment / Link Sharing

**Problem:** There's no way to share a panel-live app by simply sending a URL. Currently requires a server with specific headers (COOP/COEP for SharedArrayBuffer). Can we make it work by just opening a GitHub raw URL, GitHub Pages link, or similar static host?

**Why it matters:** The killer feature for adoption is "send a link, it just works." Panel core contributors should be able to test apps by clicking a link. Embedding in blog posts, READMEs, and documentation should be trivial - no server setup required.

**Design questions:**

- Can panel-live work from GitHub Pages? (GitHub Pages supports custom headers via `_headers` file on some providers, but not natively)
- Can we fall back gracefully when COOP/COEP headers are missing? (No SharedArrayBuffer, but still functional with slightly higher memory usage)
- Could we provide a hosted service (like `panel-live.holoviz.org/run?url=...`) that proxies content with correct headers?
- How do competitors handle this? (shinylive.io hosts apps, py.cafe provides a hosted service, stlite works from any static host)

**Suggested approach:**

1. Ensure panel-live works without COOP/COEP headers (graceful degradation - no SharedArrayBuffer, higher memory, but functional)
2. Host a reference deployment on GitHub Pages via `holoviz-dev/panel-live`
3. Support URL parameter to load code from external source: `panel-live.holoviz.org/?gist=xxx` or `?url=https://raw.githubusercontent.com/...`
4. Document "share your app" workflow

**Acceptance criteria:** A panel core contributor can click a single link and see a working Panel app in their browser. No server setup, no local installation.

**Related to:** Distribution (P1), URL Sharing (P3).

---

### P3 - Offline Support

**Problem:** All resources loaded from CDN. No service worker for caching. No offline mode.

**Why it matters:** PyScript supports offline usage. Corporate environments may have restricted internet access.

**Acceptance criteria:** After first load, the app works without internet connection (Pyodide and packages cached).

---

## Category 4: Documentation & Ecosystem Integration

### P1 - Documentation

**Problem:** Zero documentation exists for this feature.

**Why it matters:** Without docs, nobody outside the core team can use it. Docs are required for any public release.

**Suggested content:**

1. Getting Started guide (embed an app in 5 minutes)
2. API reference (all script types, attributes, JS API)
3. Configuration guide (versions, themes, packages)
4. Examples gallery
5. Architecture overview (for contributors)
6. Migration guide from pyscript.com / raw Pyodide

**Acceptance criteria:** Complete documentation covering all supported features. Published on panel.holoviz.org.

**Blocked by:** Settle on Name (resolved).

---

### P1 - Examples Gallery

**Problem:** Only 8 examples exist (6 inline in HTML + 2 external .py files). Need a comprehensive, curated collection.

**Why it matters:** Examples are the primary way users discover capabilities. Competitors (shinylive, streamlit playground) have extensive example galleries.

**Suggested examples:**

- Basic: Hello World, Slider, Text Input, Button
- Data: DataFrame display, Tabulator, CSV upload
- Visualization: Matplotlib, hvPlot, Plotly, HoloViews
- Layout: Templates, Columns, Tabs
- Advanced: Chat interface, Streaming, File download
- ML: Transformers.js integration, image classification
- Extensions: panel-material-ui (once working)

**Loading examples from external sources:**

- Examples should be loadable from a JSON URL (e.g., `<panel-live examples-src="examples.json">`) to support external/shared example collections without requiring inline `<panel-example>` children. The JSON format should define example name, description, code, and optional metadata.
- Individual `<panel-example>` elements should support a `src` attribute pointing to an external Python file (e.g., `<panel-example name="Demo" src="examples/demo.py">`), allowing example code to live in separate files rather than inline HTML.

**Default examples when none provided:**

- The playground mode must provide a default curated set of examples when no `<panel-example>` children or `examples-src` attribute are configured. These defaults serve as both a getting-started guide and a demo of capabilities, showing off common patterns (basic widgets, plots, layouts, etc.).

**Acceptance criteria:** 15+ curated examples covering common use cases. Each example works reliably and loads in <15 seconds. Examples can be provided inline, via JSON URL, or via `src` attribute on individual `<panel-example>` elements. Sensible defaults appear when no examples are configured.

---

### P2 - Sphinx Extension

**Problem:** No Sphinx extension exists. The current `nbsite` pyodide directive is limited (one instance per page, no template support, code not editable).

**Why it matters:** Panel's documentation uses Sphinx. Interactive examples in docs are a primary motivator for this entire feature (see `live-dream.md`). Shinylive has excellent Quarto+Sphinx integration.

**Suggested approach:**

1. Sphinx directive: `.. panel-live::` that embeds a panel-editor or panel-playground
2. Support code from directive body or external file reference
3. Support options: `layout`, `theme`, `requirements`, `height`
4. Load panel-live JS/CSS from CDN or bundled with docs

**Acceptance criteria:** Working Sphinx extension that can embed interactive Panel apps in documentation pages. Multiple instances per page.

**Blocked by:** Build, Distribute.

---

### P2 - MkDocs Extension

**Problem:** No MkDocs extension exists. MkDocs is increasingly popular in the Python ecosystem.

**Why it matters:** Some HoloViz projects and many third-party users use MkDocs. py.cafe has `mkdocs-pycafe` as a reference implementation.

**Inspiration:** <https://github.com/py-cafe/mkdocs-pycafe>, <https://mkdocs.py.cafe/en/latest/>

**Acceptance criteria:** Working MkDocs extension with similar capabilities to the Sphinx extension.

**Blocked by:** Build, Distribute.

---

### P2 - Links from Panel Website and README

**Problem:** No links to the playground from the Panel website or GitHub README.

**Why it matters:** Discoverability. Users won't find the feature if it's not linked.

**Acceptance criteria:** Panel website navigation includes playground link. Panel GitHub README mentions the feature with link.

**Blocked by:** Documentation, Distribute.

---

## Category 5: Build, Test & Deploy

### P1 - Build System

**Problem:** No build step. Raw JS file served directly. The monolithic IIFE cannot be tree-shaken, minified, or bundled with dependencies.

**Why it matters:** Production distribution requires minification, source maps, and dependency bundling (e.g., CodeMirror). Panelite has a build system that can serve as a template.

**Suggested approach:**

- Use esbuild, Rollup, or Vite for bundling
- Produce: `panel-live.min.js`, `panel-live.css`, `panel-live.esm.js`
- Source maps for debugging
- Follow panelite patterns where applicable

**Acceptance criteria:** Build produces minified JS + CSS bundles. Source maps available. Build runs in CI.

**Blocked by:** Folder and File Structure.

---

### P1 - Automated Testing

**Problem:** Zero tests for the playground/embed feature.

**Why it matters:** Without tests, every change risks regressions. The feature is complex (Pyodide loading, code execution, editor interaction, multiple modes) and fragile.

**Reference:** `scripts/panelite/test/test_panelite.py` - Playwright-based test suite for Panelite provides a template.

**Suggested approach:**

1. Playwright end-to-end tests: load page, verify app renders, test editor interaction, test re-run
2. Unit tests for JS utilities (code parsing, requirements detection, namespace isolation)
3. Test all three modes (app, editor, playground) in both execution models (iframe, inline)
4. Test error handling scenarios

**Acceptance criteria:** Playwright test suite covering core user flows. Tests run in CI. >80% coverage of critical paths.

**Blocked by:** Build System (need a reliable way to serve the test pages).

---

### P1 - Distribution (CDN / npm)

**Problem:** Not distributed anywhere. No CDN hosting, no npm package.

**Why it matters:** Users need a stable URL to load the library from. `cdn.holoviz.org` is the standard for HoloViz projects.

**Suggested approach:**

- Host on `cdn.holoviz.org` (like panelite)
- Publish to npm for JS ecosystem users
- Version-pinned URLs: `cdn.holoviz.org/panel-live/1.0.0/panel-live.min.js`
- Latest URL: `cdn.holoviz.org/panel-live/latest/panel-live.min.js`

**Acceptance criteria:** Stable, versioned CDN URL. Works via `<script src="...">`. npm package published.

**Blocked by:** Build System, Settle on Name (resolved).

---

### P2 - Pixi Commands

**Problem:** No pixi commands defined for playground development.

**Why it matters:** Panelite uses `pixi run lite-build` and similar. Developers need consistent tooling.

**Suggested commands:** `pixi run panel-live-dev` (serve with hot reload), `pixi run panel-live-build`, `pixi run panel-live-test`.

**Acceptance criteria:** Pixi tasks defined and documented for dev, build, and test workflows.

---

### P2 - GitHub Actions CI/CD

**Problem:** No CI/CD pipeline for the playground.

**Why it matters:** Need automated testing, building, and deployment. Panelite has `.github/workflows/jupyterlite.yaml` as a template.

**Suggested workflows:**

1. **PR checks:** Lint, build, run Playwright tests
2. **Dev build:** Deploy to dev URL on push to main
3. **Release:** Build, test, deploy to `cdn.holoviz.org` on tag
4. **Alpha/Beta/RC:** Pre-release builds similar to panelite

**Acceptance criteria:** CI runs tests on PR. CD deploys on merge to main (dev) and on release tag (prod).

**Blocked by:** Build System, Automated Testing.

---

## Category 6: Technical Debt

### P1 - Python Code as String Concatenation

**Problem:** All Python code executed via Pyodide is built as concatenated strings in JavaScript (`'import js\n' + 'import panel as pn\n' + ...`). Indentation errors are invisible and hard to debug.

**Why it matters:** Fragile and error-prone. Any modification risks subtle Python syntax errors that are extremely hard to trace.

**Suggested approach:** Use template literals with proper indentation. Or better: load Python bootstrap code from separate `.py` files bundled during build.

**Acceptance criteria:** Python bootstrap code maintained in `.py` files, not JS string concatenation.

---

### P1 - Duplicate Execution Logic

**Problem:** `runApp()` (inline mode) and `runRunnerApp()` (iframe/runner mode) have near-identical 3-branch execution logic (servable, servable+target, no-servable) with subtle differences. Code duplication risk.

**Why it matters:** Bug fixes or feature additions must be applied twice and may diverge.

**Suggested approach:** Extract shared execution logic into a common function. Parameterize differences (namespace isolation, cleanup, error handling) rather than duplicating.

**Acceptance criteria:** Single execution code path with mode-specific configuration. No duplicated logic.

---

### P2 - Error Boundaries Between Apps

**Problem:** If one inline app crashes during sequential execution, it may prevent subsequent apps from running.

**Why it matters:** In documentation pages with multiple embedded apps, one broken example shouldn't break the rest.

**Acceptance criteria:** Each app runs in isolation. One app's failure doesn't affect others. Failed apps show error state, remaining apps continue.

---

## Category 7: Future / Nice-to-Have

These are stretch goals for after MVP.

### P3 - React / Framework Wrappers

**Problem:** Stlite provides `@stlite/react`. Modern web apps built with React/Vue/Svelte would benefit from native wrappers.

**Acceptance criteria:** npm package for React (at minimum) that wraps panel-live as a React component.

---

### P3 - Desktop Version (Electron/Tauri)

**Problem:** Stlite has a desktop version. Could be useful for offline tools.

**Acceptance criteria:** Documented approach for wrapping panel-live in Electron or Tauri.

---

### P3 - Filesystem Support

**Problem:** No virtual filesystem access for user code. PyScript supports filesystem access.

**Acceptance criteria:** Users can read/write files in a virtual filesystem. IndexedDB persistence.

---

### P3 - Media Access (Camera, Microphone)

**Problem:** No access to browser media devices from Python code.

**Why it matters:** Enables ML demos (image classification, audio processing) directly in the browser. See `live-dream.md` Pyodide Pane section.

**Acceptance criteria:** Python code can access camera/microphone streams via Pyodide.

---

### P3 - Notebook-like Experience

**Problem:** Only single-cell execution. No multi-cell notebook-like workflow.

**Why it matters:** For learning and exploration, a notebook-style interface (multiple cells, incremental execution) is powerful.

**Acceptance criteria:** Optional multi-cell mode where users can add/remove/reorder cells.

---

## Dependency Graph

```text
API Design ──────────────┬──> Multi-file Support
                         ├──> Requirements / Package Spec
                         ├──> Playground Layout Options
                         └──> Customizable Styling

Folder/File Structure ───┬──> Build System ──┬──> Distribution ──┬──> Sphinx Extension
                         │                   ├──> Automated Testing  ├──> MkDocs Extension
                         │                   └──> Pixi Commands      └──> Links
                         └──> GitHub Actions

Web Worker Support ──────┬──> Keep Page Responsive
                         └──> Browser Crash (partial fix)

Evaluate PyScript ───────┬──> Web Worker Support (if adopting PyScript)
                         └──> Editor features (if using py-editor)

Separate CSS ────────────┬──> Customize Styling
                         └──> Align Styles

CodeMirror 6 Upgrade ────┬──> Tracking Prevention (bundle CM6)
                         ├──> Mouse Selection (likely fixed)
                         └──> Editor Theme Config

Distribution ────────────┬──> Documentation ──> Links
```

## Suggested Execution Order

**Phase 1 - Decisions & Foundations (weeks 1-2):**
API Design, Interactive API Explorer (testbed for API decisions), Evaluate PyScript (separate POC)

**Phase 2 - Core Architecture (weeks 3-6):**
Web Worker Support, Folder/File Structure, Separate CSS, Build System, CodeMirror 6 Upgrade, Fix Browser Crash, Fix panel-material-ui

**Phase 3 - Developer Experience (weeks 7-10):**
Handle Python Errors, Copy Code, Loading Progress, Mouse Selection fix, Editor Theme, Duplicate Execution Logic cleanup, Python string concatenation cleanup

**Phase 4 - Polish & Release (weeks 11-14):**
Automated Testing, Distribution, Documentation, Examples Gallery, Align Styles, Customizable Styling, Pixi Commands, GitHub Actions CI/CD, postMessage Security, Memory Leak investigation, Error Boundaries

**Phase 5 - Ecosystem & Deferred Features (weeks 15+):**
Sphinx Extension, MkDocs Extension, Links, Multi-file Support, Requirements Specification, Layout Options, URL Sharing improvements, Dark Theme, Offline Support

**Phase 6 - Future:**
React wrapper, Desktop version, Filesystem, Media access, Notebook experience
