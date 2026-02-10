# Web Worker Architecture & Browser Crash Investigation

Research findings for panel-live: web worker implementation patterns, browser crash causes, and zero-install deployment analysis.

---

## 1. Executive Summary

### Key Recommendations

1. **Use a Dedicated Web Worker per app** as the default architecture. This is what every competitor does and is the simplest, most reliable approach. Panel already has working worker code (`pyodide_worker.js` + `pyodide_handler.js`) that can be adapted.

2. **Use raw `postMessage` / `MessageChannel`** for worker communication, not `coincident` or `comlink`. The existing Panel worker code already uses `postMessage`. The Bokeh document patch protocol is domain-specific and doesn't benefit from generic RPC abstractions. Keep it simple.

3. **Adopt `coi-serviceworker`** for zero-install deployment on static hosts (GitHub Pages, etc.). This is a proven, tiny library that adds COOP/COEP headers via a service worker, enabling SharedArrayBuffer without server configuration. JupyterLite uses the same approach.

4. **SharedWorker is a future optimization**, not a launch requirement. The complexity and browser compatibility issues (no Chrome Android support) don't justify it for MVP. Revisit when multiple-apps-per-page is a confirmed use case.

5. **Browser crashes are caused by a combination of factors**: main-thread Pyodide execution (memory pressure), missing COOP/COEP headers (doubles memory), and a known Pyodide scheduler bug with JSPI in Chrome 137+. Moving to a web worker addresses the first two; the JSPI issue is upstream.

---

## 2. Web Worker Implementation Comparison

### 2.1 How Competitors Use Workers

| Project | Worker Type | Communication | SharedWorker | Key Design Choices |
|---------|-------------|---------------|--------------|-------------------|
| **stlite** | Dedicated Worker (default), SharedWorker (opt-in) | `postMessage` | Yes, via `shared-worker` attribute | Falls back to Dedicated Worker on unsupported browsers (Chrome Android). SharedWorker shares Python env + filesystem across apps. |
| **shinylive** | Dedicated Worker | `postMessage` with custom message protocol | No | Runs Pyodide in a dedicated worker. Custom protocol for Shiny session messages (input/output/error). MessageChannel for bidirectional comm. |
| **PyScript** | Dedicated Worker | `coincident` library (Atomics-based Proxy) | No | Workers get synchronous access to main-thread DOM via Atomics.wait proxy. Requires COOP/COEP headers for sync mode. Falls back to async without. |
| **gradio-lite** | Dedicated Worker (one per app) | `postMessage` | No | Each `<gradio-lite>` app gets its own worker for isolation. Simple message passing for Python execution results. |

### 2.2 Detailed Analysis

#### stlite (SharedWorker Pioneer)

stlite is the only competitor offering SharedWorker mode. Key details:

- **Default**: Each `stlite.mount()` or `<streamlit-app>` runs in its own Dedicated Worker
- **SharedWorker mode**: Enabled via `shared-worker` attribute on `<streamlit-app>` or `sharedWorker: true` option
- **Fallback**: Automatically falls back to Dedicated Workers when SharedWorker is unsupported (Chrome Android, some WebKit builds)
- **Shared state**: Python environment and filesystem are shared. Each app gets a separate home directory (`/home/pyodide/<id>`) but files are accessible across apps
- **Trade-off**: Memory savings (~300-500MB per additional app avoided) vs. reduced isolation (one crash takes down all apps)

#### shinylive (Custom Protocol)

- Uses a Dedicated Worker with a custom message protocol that mirrors Shiny's server-side session architecture
- The worker runs Pyodide and the entire Shiny framework inside it
- Communication follows Shiny's existing message protocol (JSON messages for inputs/outputs)
- No SharedWorker support -- each Shinylive app is fully isolated

#### PyScript (coincident Library)

- Uses the `coincident` library by WebReflection for worker communication
- `coincident` provides an Atomics-based Proxy that gives workers synchronous access to the main thread's `window` object
- **Requires COOP/COEP headers** for synchronous mode (Atomics.wait)
- Falls back to async-only mode without headers
- Performance tiers:
  - With SharedArrayBuffer: ~50,000 roundtrips/second
  - With ServiceWorker polyfill: ~1,000 roundtrips/second
  - Without SAB: fully async only

#### gradio-lite (Simple Isolation)

- Each `<gradio-lite>` block gets its own Dedicated Worker
- Simple `postMessage` communication for sending Python code and receiving results
- No SharedWorker -- isolation is prioritized over memory efficiency
- Worker handles Pyodide initialization, package installation, and code execution independently

### 2.3 Summary

Every competitor uses Web Workers. Dedicated Workers are the universal choice. Only stlite offers SharedWorker as an optimization. PyScript is the only one using a fancy communication library (coincident); everyone else uses raw `postMessage`.

---

## 3. Communication Patterns Comparison

### 3.1 Raw `postMessage` / `MessageChannel`

**How it works**: Worker and main thread exchange JSON-serializable messages via `postMessage`. `MessageChannel` provides a dedicated communication channel.

**Pros**:
- Zero dependencies
- Well-understood, well-documented
- Full control over message format
- Supports `Transferable` objects (ArrayBuffer zero-copy transfer)
- Works everywhere

**Cons**:
- Verbose for complex protocols
- No automatic type safety
- Manual serialization/deserialization
- No built-in RPC pattern

**Used by**: Panel (existing), stlite, shinylive, gradio-lite

### 3.2 coincident (WebReflection)

**How it works**: Uses SharedArrayBuffer + Atomics to create a synchronous Proxy between worker and main thread. Workers can directly access `window`, DOM, localStorage, etc. as if they were on the main thread.

**Pros**:
- Workers can synchronously access main-thread objects
- No need to design a message protocol
- Clean API for DOM manipulation from workers
- Transparent proxy -- code reads like main-thread code

**Cons**:
- **Requires COOP/COEP headers** for synchronous mode (the main selling point)
- Falls back to async without headers (losing the primary advantage)
- Adds a dependency (~12KB)
- Debugging is harder (proxy magic obscures control flow)
- Not needed for Panel's use case (Bokeh document sync has its own protocol)
- Performance overhead for simple message passing vs. raw `postMessage`

**Used by**: PyScript

### 3.3 Comlink (Google Chrome Labs)

**How it works**: RPC library that makes workers look like regular async JS objects. Uses `postMessage` under the hood with ES6 Proxy for ergonomic API.

**Pros**:
- Tiny (~1.1KB)
- TypeScript support with `Comlink.Remote<T>` type inference
- Clean async API: `const result = await worker.doSomething()`
- No SharedArrayBuffer requirement
- Works everywhere `postMessage` works

**Cons**:
- All calls are async (no synchronous access to main thread)
- Requires `expose()` / `wrap()` boilerplate
- Delegates more work to the main thread (main thread handles lazy awaiting)
- Overkill for simple message-based protocols
- Not needed when you already have a domain-specific protocol (Bokeh patches)

**Used by**: Various projects, not specifically Pyodide-based apps

### 3.4 Recommendation for Panel-Live

**Use raw `postMessage`**. Rationale:

1. Panel's existing `pyodide_worker.js` already uses `postMessage` and works
2. The Bokeh document sync protocol (JSON patches + binary buffers) is domain-specific and doesn't benefit from generic RPC
3. `coincident`'s killer feature (sync DOM access from workers) is unnecessary because Panel renders through Bokeh's JS runtime on the main thread
4. No additional dependencies to maintain
5. `MessageChannel` can be used if a dedicated channel is needed (e.g., separate channels for patches, status messages, and errors)

---

## 4. SharedWorker vs. Dedicated Worker

### 4.1 When SharedWorker is Beneficial

- **Multiple apps on one page**: Documentation pages with 3-5 embedded Panel apps would use ~1.5GB with Dedicated Workers vs. ~500MB with a SharedWorker
- **Shared package installation**: Install packages once, share across all apps
- **Shared data**: Apps that need to share a dataset don't need to load it multiple times

### 4.2 Browser Support

| Browser | Dedicated Worker | SharedWorker |
|---------|-----------------|--------------|
| Chrome Desktop | Yes | Yes |
| Firefox Desktop | Yes | Yes |
| Safari Desktop | Yes | Yes |
| Edge Desktop | Yes | Yes |
| Chrome Android | Yes | **No** |
| Safari iOS | Yes | Yes (16.4+) |
| Firefox Android | Yes | **No** |

SharedWorker is missing from Chrome Android and Firefox Android -- significant gaps for mobile.

### 4.3 Complexity Trade-offs

| Aspect | Dedicated Worker | SharedWorker |
|--------|-----------------|--------------|
| Implementation complexity | Low | Medium-High |
| Debugging | Straightforward | Harder (shared state) |
| Error isolation | Per-app | All apps affected by one crash |
| Memory per app | ~300-500MB each | ~300-500MB total (shared) |
| Lifecycle management | Simple (worker per app) | Complex (reference counting, cleanup) |
| Fallback needed | No | Yes (to Dedicated Worker) |

### 4.4 Recommendation

**Start with Dedicated Worker. SharedWorker is a Phase 2 optimization.**

- MVP: One Dedicated Worker per app. Simple, reliable, good isolation.
- Phase 2: Add SharedWorker as opt-in for multi-app pages (like stlite's `shared-worker` attribute)
- Fallback: Auto-detect SharedWorker support, fall back to Dedicated Worker

---

## 5. Panel's Existing Worker Code Analysis

### 5.1 What Exists

Panel already has a complete web worker implementation for its `panel convert --to pyodide-worker` output:

**`panel/_templates/pyodide_worker.js`** (Worker-side):
- Loads Pyodide via `importScripts`
- Unpacks data archives from zip files
- Installs packages via micropip
- Executes user code and sends rendered document JSON back to main thread
- Handles bidirectional Bokeh document patching via `postMessage`
- Message types: `patch`, `rendered`, `location`, `status`, `render`, `idle`
- Uses `_link_docs_worker()` from `panel.io.pyodide` for Python-side document sync

**`panel/_templates/pyodide_handler.js`** (Main-thread handler):
- Creates a `new Worker("./app.js")` Dedicated Worker
- Manages a message queue for event batching (coalesces rapid model changes)
- Handles Bokeh document embedding from worker-provided JSON
- Patches Bokeh documents bidirectionally between worker and main thread
- Manages loading UI (spinner, status messages)

**`panel/_templates/serviceWorker.js`** (Service Worker for PWA caching):
- Standard service worker for caching static assets
- Used by `panel convert` for PWA support
- NOT for COOP/COEP header injection

**`panel/io/pyodide.py`** (Python-side Pyodide support):
- `_link_docs_worker()`: Links Python Document to a dispatch function for worker sync
- `_link_docs()`: Links Python and JS documents in main-thread Pyodide
- `_process_document_events()`: Serializes Bokeh document events for cross-thread transfer
- `_convert_json_patch()`: Converts JS JSON patches to Python-compatible format
- `write_doc()`: Renders Document contents, works in both main thread and worker
- Handles `_IN_WORKER` detection and PyScript worker compatibility

**`panel/io/convert.py`** (Conversion pipeline):
- `script_to_html()`: Converts Panel scripts to standalone HTML with worker support
- Supports 4 runtimes: `pyodide`, `pyscript`, `pyodide-worker`, `pyscript-worker`
- Generates worker JS from templates
- Handles COOP/COEP `crossorigin` attributes for `pyscript-worker` mode

### 5.2 Can It Be Reused for Panel-Live?

**Yes, substantially.** The existing code provides:

1. A working Pyodide-in-worker pattern with proven message protocol
2. Bidirectional Bokeh document sync (the hardest part)
3. Package installation and data archive unpacking
4. Loading status communication
5. Python-side worker support (`_link_docs_worker`)

**What needs to change for panel-live**:

1. **Dynamic code execution**: Current worker executes code baked in at conversion time. Panel-live needs to send code dynamically from the editor.
2. **Re-execution**: Current worker has no "reset and re-run" capability. Need to clear state between runs (or terminate and recreate worker).
3. **Multiple apps on one page**: Current handler assumes one worker per page. Panel-live needs to manage multiple worker instances.
4. **Error communication**: Current error handling sends raw tracebacks. Panel-live needs structured error messages for the editor UI.
5. **Progress granularity**: Current status messages are coarse. Panel-live needs finer-grained loading progress.

**Reuse strategy**: Extract the message protocol and Bokeh sync logic from the templates into reusable modules. Add dynamic execution, re-run, and multi-instance management on top.

---

## 6. Browser Crash Investigation

### 6.1 COOP/COEP Headers and SharedArrayBuffer

#### What's Required

For SharedArrayBuffer to be available in browser contexts:

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp  (or credentialless)
```

These headers make the page "cross-origin isolated," which:
- Enables `SharedArrayBuffer` (required for Pyodide's efficient memory model)
- Enables `Atomics.wait` (required for `coincident` sync mode)
- Restricts cross-origin resource loading (all resources must explicitly opt in via CORS or `crossorigin` attributes)

#### What Happens Without Them

- **`SharedArrayBuffer` is unavailable**: Pyodide falls back to regular `ArrayBuffer`
- **Memory impact**: Without SAB, Pyodide's WebAssembly memory cannot be shared between threads, and memory growth requires copying the entire buffer. The `live-analysis.md` documents that this roughly doubles memory usage.
- **Functionality impact**: Pyodide still works, but uses more memory and cannot support interrupt/cancellation of running code
- **`credentialless` vs `require-corp`**: `credentialless` is less restrictive -- it allows loading cross-origin resources that don't require credentials. The Panel `serve.py` already uses `credentialless`, which is the better choice for embedding scenarios.

### 6.2 Pyodide Memory Footprint

| Scenario | Approximate Memory |
|----------|-------------------|
| Bare Pyodide (with SAB) | ~150-200MB |
| Pyodide + Panel + Bokeh | ~300-400MB |
| Pyodide + Panel + large packages (numpy, pandas) | ~400-600MB |
| Without SAB (add ~50-100% overhead) | ~450-900MB |
| Multiple instances (iframe mode) | N x above |

**Key memory facts**:
- Pyodide itself is ~6.4MB to download but expands to ~150MB+ in WASM memory
- WASM memory can grow but **never shrinks** during a session
- Each `loadPyodide()` call creates a new WASM instance with its own memory
- Worker termination is the **only reliable way** to free WASM memory
- In iframe mode, each iframe loads its own Pyodide instance

### 6.3 Known Pyodide Crash Issues

#### STATUS_STACK_BUFFER_OVERRUN (Issue #5705)

**Root cause**: Two separate problems:

1. **JSPI (JavaScript Promise Integration)**: Chrome 137+ enabled JSPI by default. This causes crashes in tight asyncio loops. Error: `RangeError: WebAssembly.Table.get(): invalid address`. Pyodide versions 0.26.3+ are affected.

2. **Scheduler memory leak**: The MessageChannel-based scheduler in Pyodide accumulates memory in rapid async loops. Memory grows to 500MB-2GB within minutes. Present even with JSPI disabled. Versions 0.26.2 and earlier show the memory leak without the crash.

**Symptoms in panel-live context**:
- Tab crashes after 6+ seconds of Panel app execution (especially apps with periodic callbacks or streaming)
- Memory usage spikes rapidly
- More likely in Chrome than Firefox
- Crash happens at "Loaded pyodide-http" stage when memory is already high from package loading

#### Memory Access Out of Bounds (Issues #1384, #1473)

- WASM runtime errors from memory corruption
- Often triggered by NumPy operations or large data manipulations
- More common in Chrome than Firefox
- Can be triggered by memory pressure (multiple tabs, other heavy pages)

### 6.4 Why Panel-Live Crashes

Based on the evidence, panel-live crashes are caused by a combination of:

1. **Main-thread execution**: Pyodide on the main thread competes with rendering, GC, and other browser tasks for memory
2. **Missing COOP/COEP behind proxies**: When served through Jupyter server proxy or other reverse proxies that strip custom headers, SAB is unavailable, doubling memory usage
3. **Multiple instances in iframe mode**: Each iframe loads its own Pyodide (~300-500MB), quickly exhausting browser memory on 8GB machines
4. **JSPI interaction**: Chrome 137+ JSPI causes crashes in Pyodide's async scheduler

### 6.5 Mitigation Strategies

| Strategy | Impact | Effort |
|----------|--------|--------|
| **Move Pyodide to Web Worker** | Eliminates main-thread memory pressure. Worker crash doesn't take down the page. | Medium (existing code to adapt) |
| **Ensure COOP/COEP headers** | Enables SAB, reduces memory ~50% | Low (serve.py already does this; add coi-serviceworker for static hosting) |
| **Limit concurrent Pyodide instances** | Prevents OOM on multi-app pages | Low (load apps lazily, cap at 2-3 concurrent) |
| **Worker termination for re-runs** | Reclaims all WASM memory between runs | Low (terminate worker, create new one) |
| **Detect and warn about low memory** | User awareness before crash | Medium (performance.memory API where available) |
| **Lazy app loading** | Only load Pyodide when app is visible (IntersectionObserver) | Low |
| **Pin Pyodide version carefully** | Avoid JSPI-related crashes | Low (avoid 0.26.3-0.27.x for Chrome JSPI issue) |
| **SharedWorker for multi-app pages** | Share one Pyodide across apps | High (Phase 2) |

---

## 7. Zero-Install Deployment Analysis

### 7.1 GitHub Pages

**Can panel-live work on GitHub Pages?**

GitHub Pages **does not support custom HTTP headers**. There is no `_headers` file support (that's Netlify/Cloudflare). This means:

- No COOP/COEP headers natively
- No SharedArrayBuffer natively
- **BUT**: `coi-serviceworker` can inject these headers via a service worker

**coi-serviceworker approach**:
1. Include `coi-serviceworker.js` in the repo (must be same-origin, cannot be from CDN)
2. Add `<script src="coi-serviceworker.js"></script>` to the HTML
3. On first load, page reloads once to activate the service worker
4. Service worker intercepts all requests and adds COOP/COEP headers
5. SharedArrayBuffer becomes available

**Limitations**:
- Page requires HTTPS (GitHub Pages provides this)
- First-visit reload is slightly jarring (but only once per origin)
- Service worker file must be at the root path or same directory
- Cannot be bundled -- must be a separate file

**Verdict**: GitHub Pages works with coi-serviceworker. JupyterLite uses this exact approach.

### 7.2 GitHub Raw URLs

**Can you load from `raw.githubusercontent.com`?**

No, this is problematic:
- `raw.githubusercontent.com` serves files with `Content-Type: text/plain`
- HTML files are not rendered as HTML
- No service worker support (wrong content type)
- CORS restrictions prevent loading as iframe source

**Alternative**: Use GitHub Pages (free, automatic HTTPS, custom domain support).

### 7.3 Static Hosting Providers with Custom Header Support

| Provider | Custom Headers | COOP/COEP | Free Tier | Setup Effort |
|----------|---------------|-----------|-----------|--------------|
| **Netlify** | Yes (`_headers` file or `netlify.toml`) | Native | Yes | Very Low |
| **Vercel** | Yes (`vercel.json`) | Native | Yes | Very Low |
| **Cloudflare Pages** | Yes (`_headers` file) | Native | Yes | Very Low |
| **GitHub Pages** | No (use coi-serviceworker) | Via SW | Yes | Low |
| **Surge.sh** | No | Via SW | Yes | Low |
| **Firebase Hosting** | Yes (`firebase.json`) | Native | Yes | Low |
| **AWS S3 + CloudFront** | Yes (CloudFront response headers) | Native | Paid | Medium |

**Recommendation**: For the official panel-live deployment, use **Netlify or Cloudflare Pages** for native header support. For user-deployed apps, include `coi-serviceworker` as a fallback.

### 7.4 How Competitors Handle Zero-Install

| Project | Hosted Service | Static Hosting | Sharing Pattern |
|---------|---------------|----------------|-----------------|
| **shinylive** | shinylive.io (official) | Yes, with `shinylive` Python package generating static files | Export to static site, deploy anywhere |
| **stlite** | stlite.net (examples) | Works from any static host | Embed via `<script>` tag from CDN |
| **gradio-lite** | Gradio spaces (Hugging Face) | Works from any static host | Embed via `<gradio-lite>` web component |
| **PyScript** | pyscript.com (editor) | Works from any static host (with caveats for workers) | Embed via `<script type="py">` |
| **py.cafe** | py.cafe (hosted service) | No static option | URL-based sharing on hosted platform |

### 7.5 The Sharing Use Case

**Goal**: A developer writes a Panel app and shares it with colleagues via a link.

**Simplest path with panel-live**:

1. **Option A: Hosted playground** (like py.cafe or shinylive.io)
   - Host `panel-live.holoviz.org` on Netlify/Cloudflare with COOP/COEP headers
   - Support `?code=<compressed>` URL parameter (already partially implemented in POC)
   - Developer writes code, clicks "Share", sends URL
   - No setup required for recipients

2. **Option B: Self-hosted static file**
   - Developer runs `panel convert app.py --to panel-live` (future CLI)
   - Output: single HTML file + optional worker JS + coi-serviceworker.js
   - Upload to any static host (GitHub Pages, Netlify, etc.)
   - Share the URL

3. **Option C: Embedded in documentation**
   - Use Sphinx/MkDocs extension to embed `<script type="panel">` blocks
   - Documentation site deployed with correct headers
   - Readers interact with live examples directly

**Recommendation**: Prioritize Option A (hosted playground) for MVP. It has the lowest friction and matches what py.cafe and shinylive.io provide. Option B comes naturally from Panel's existing `convert` infrastructure.

### 7.6 Graceful Degradation Without COOP/COEP

Panel-live should work without COOP/COEP headers, just with reduced performance:

| Feature | With COOP/COEP | Without COOP/COEP |
|---------|---------------|-------------------|
| SharedArrayBuffer | Available | Unavailable |
| Pyodide memory efficiency | Normal (~300-400MB) | Higher (~450-700MB) |
| Code interruption | Possible (via SAB) | Not possible |
| Worker support | Full | Full (workers don't need COOP/COEP) |
| coincident sync mode | Available | Async fallback only |
| Basic functionality | Full | Full |

**Key insight**: Dedicated Workers work fine without COOP/COEP. SharedArrayBuffer is a nice-to-have for memory efficiency and code interruption, but not a hard requirement. Panel-live should detect SAB availability and adjust behavior accordingly.

---

## 8. Recommended Web Worker Architecture for Panel-Live

### 8.1 Architecture Overview

```
Main Thread (UI)                    Worker Thread (Python)
+---------------------------+       +---------------------------+
| panel-live.js             |       | panel-live-worker.js      |
|                           |       |                           |
| - CodeMirror editor       |  msg  | - Pyodide runtime         |
| - Loading UI              | <---> | - Panel + Bokeh packages  |
| - Bokeh rendering         |       | - User code execution     |
| - Error display           |       | - Document sync           |
| - App container           |       |                           |
+---------------------------+       +---------------------------+
         |                                     |
         | Bokeh document patches              | Python Document events
         | (JSON + binary buffers)             | (serialized patches)
         v                                     v
+---------------------------+       +---------------------------+
| Bokeh JS Document         |       | Bokeh Python Document     |
| (rendered in DOM)         |       | (in Pyodide)              |
+---------------------------+       +---------------------------+
```

### 8.2 Message Protocol

Extend the existing Panel worker protocol:

```typescript
// Main -> Worker messages
type MainToWorker =
  | { type: 'init', config: { pyodideUrl: string, packages: string[] } }
  | { type: 'execute', code: string, runId: string }
  | { type: 'patch', patch: object }
  | { type: 'location', location: string }
  | { type: 'interrupt' }  // requires SAB
  | { type: 'terminate' }

// Worker -> Main messages
type WorkerToMain =
  | { type: 'status', stage: string, detail?: string }
  | { type: 'progress', percent: number }
  | { type: 'render', docsJson: string, renderItems: string, rootIds: string }
  | { type: 'patch', patch: object, buffers?: ArrayBuffer[] }
  | { type: 'error', error: { message: string, traceback: string, type: string } }
  | { type: 'idle' }
  | { type: 'ready' }
```

### 8.3 Lifecycle

1. **Create worker**: `new Worker('panel-live-worker.js')`
2. **Send init**: Configuration, Pyodide URL, base packages
3. **Worker loads Pyodide**: Sends `status` messages for progress
4. **Worker installs packages**: Sends `progress` messages
5. **Worker sends `ready`**: Main thread enables UI
6. **User clicks Run**: Main sends `execute` with code
7. **Worker executes code**: Sends `render` when done, `error` if failed
8. **Bidirectional sync**: `patch` messages keep documents in sync
9. **Re-run**: Either (a) send new `execute` (reuses existing state) or (b) terminate worker and create new one (clean slate)

### 8.4 Re-execution Strategy

For re-running user code (the editor/playground use case):

**Option A: Soft reset** -- Clear Python namespace, re-execute
- Fast (no Pyodide reload)
- Risk of state leaks between runs
- Good for iterative development

**Option B: Hard reset** -- Terminate worker, create new one
- Clean slate, no state leaks
- Slow (re-loads Pyodide, ~5-15s)
- Good for final testing

**Recommendation**: Default to soft reset. Provide a "Hard Reset" button for cases where state is corrupted. Implement soft reset by:
1. Clearing the Python namespace (except standard library imports)
2. Destroying existing Bokeh document and roots
3. Re-executing user code

### 8.5 Multi-App Page Support

For documentation pages with multiple Panel apps:

1. Each `<script type="panel">` creates its own Dedicated Worker
2. Workers load lazily (IntersectionObserver -- only when visible)
3. Maximum concurrent workers: 3 (configurable)
4. Workers beyond the limit queue and load when earlier ones complete
5. Future: SharedWorker opt-in for high-density pages

### 8.6 Error Handling

1. **Worker crash** (`error` event): Show "Python environment crashed. Click to reload." with a restart button
2. **Python exception**: Show formatted traceback in error panel below editor
3. **Package install failure**: Show which package failed, suggest alternatives
4. **Timeout**: If execution takes >30s, show warning (not automatic kill)
5. **Out of memory**: Detect via `performance.memory` if available, warn before crash

---

## 9. Implementation Roadmap

### Phase 1: Basic Worker Support (Week 1-2)

1. Adapt `pyodide_worker.js` template into a panel-live worker module
2. Add `execute` message type for dynamic code execution
3. Add structured error reporting
4. Implement worker creation/termination lifecycle
5. Integrate with existing panel-live UI

### Phase 2: Polish (Week 3-4)

1. Add fine-grained loading progress
2. Implement soft reset for re-execution
3. Add lazy loading (IntersectionObserver) for multi-app pages
4. Integrate coi-serviceworker for static hosting
5. Test SAB detection and graceful degradation

### Phase 3: Optimization (Future)

1. SharedWorker for multi-app pages (opt-in)
2. Pyodide package caching across page loads
3. Code interruption via SharedArrayBuffer
4. Memory monitoring and warnings

---

## 10. References

- [Pyodide Web Worker Documentation](https://pyodide.org/en/stable/usage/webworker.html)
- [stlite GitHub](https://github.com/whitphx/stlite) -- SharedWorker implementation
- [shinylive GitHub](https://github.com/posit-dev/shinylive) -- Worker architecture
- [coincident GitHub](https://github.com/WebReflection/coincident) -- Atomics-based worker proxy
- [Comlink GitHub](https://github.com/GoogleChromeLabs/comlink) -- Worker RPC library
- [coi-serviceworker GitHub](https://github.com/gzuidhof/coi-serviceworker) -- COOP/COEP via service worker
- [Pyodide Issue #5705](https://github.com/pyodide/pyodide/issues/5705) -- STATUS_STACK_BUFFER_OVERRUN crash
- [Pyodide Issue #5702](https://github.com/pyodide/pyodide/issues/5702) -- JSPI memory leak crash
- [Pyodide Issue #1384](https://github.com/pyodide/pyodide/issues/1384) -- Memory access out of bounds
- [MDN Cross-Origin-Embedder-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy)
- [web.dev: Making your website cross-origin isolated](https://web.dev/articles/coop-coep)
- [GitHub Pages COOP/COEP Discussion](https://github.com/orgs/community/discussions/13309)
- [Setting COOP/COEP on Static Hosting](https://blog.tomayac.com/2025/03/08/setting-coop-coep-headers-on-static-hosting-like-github-pages/)
- [JupyterLite SharedArrayBuffer Discussion](https://github.com/jupyterlite/jupyterlite/issues/1409)
- [PyScript Web Workers Guide](https://docs.pyscript.net/2024.5.1/user-guide/workers/)
- [Pyodide Memory Discussion #4338](https://github.com/pyodide/pyodide/discussions/4338)
- [Pyodide Memory Discussion #5140](https://github.com/pyodide/pyodide/discussions/5140)
