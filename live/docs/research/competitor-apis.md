# Competitor API Research: Browser-Embedded Python Apps

Research into **shinylive**, **stlite**, **gradio-lite**, and **PyScript** -- the four leading products for embedding Python apps in the browser. Conducted for the panel-live project to inform API design decisions.

---

## 1. Executive Summary

### Key Takeaways

1. **Every competitor uses web workers.** This is table stakes. Shinylive, stlite, gradio-lite, and PyScript all run Pyodide in a web worker to keep the main thread responsive. Panel-live's current main-thread execution is a critical gap.

2. **The custom HTML element pattern dominates.** Three of four competitors use custom HTML elements (`<gradio-lite>`, `<streamlit-app>`, `<py-script>`/`<script type="py">`) rather than `<script type="...">` tags. The custom element approach provides cleaner semantics, better browser tooling support, and natural attribute-based configuration.

3. **All support multi-file apps through child elements.** Every competitor uses child elements within the main container to declare additional files: `<gradio-file>`, `<app-file>`, `## file:` markers (shinylive), and PyScript's `files` config. This is a proven pattern.

4. **Requirements are declared as child elements or config attributes.** `<gradio-requirements>`, `<app-requirements>`, PyScript's `packages` config, and shinylive's `requirements.txt`. All also support auto-detection as a fallback.

5. **SharedWorker support reduces memory for multi-app pages.** Both stlite and gradio-lite offer SharedWorker mode (single Pyodide instance shared across apps on the same page), reducing memory from ~300-500MB per app to ~300-500MB total. This is critical for documentation pages with multiple embedded apps.

6. **CDN-first distribution via jsdelivr or custom CDN.** All use CDN URLs as the primary distribution method. npm packages exist for framework integrations.

7. **Playground/editor modes are built-in features.** Gradio-lite has `playground` and `layout` attributes. Shinylive has editor/viewer components. PyScript has `py-editor`. Stlite relies on Streamlit's own UI. Panel-live's three separate script types (`panel`, `panel-editor`, `panel-playground`) are unique but more verbose than competitors' attribute-based approach.

8. **Zero-install sharing works on any static host.** All products can be deployed to GitHub Pages, Netlify, or any static file server. The main requirement is proper CORS headers, and for advanced features (SharedArrayBuffer), COOP/COEP headers.

### Pattern Summary

| Pattern | Adopted By | Panel-Live Status |
|---------|-----------|-------------------|
| Web workers | All 4 | Missing (P0) |
| Custom HTML element | 3 of 4 | Uses `<script type>` instead |
| Child elements for files | All 4 | Not supported |
| Child elements for requirements | 3 of 4 | Not supported |
| SharedWorker option | 2 of 4 | Not supported |
| CDN distribution | All 4 | Not distributed |
| Playground/editor as attribute | 2 of 4 | Separate script types |
| Theme attribute | 3 of 4 | Not supported |
| Layout attribute | 2 of 4 | Not supported |

---

## 2. Per-Competitor Deep Dive

---

### 2.1 Gradio-Lite

**Repository:** https://github.com/gradio-app/gradio (monorepo, `lite/` directory)
**npm:** `@gradio/lite`
**CDN:** `https://cdn.jsdelivr.net/npm/@gradio/lite/dist/lite.js`

#### HTML API Surface

Gradio-lite uses a **single custom HTML element** (`<gradio-lite>`) with child elements for configuration:

```html
<!-- Load the library -->
<script type="module" crossorigin
  src="https://cdn.jsdelivr.net/npm/@gradio/lite/dist/lite.js"></script>
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@gradio/lite/dist/lite.css" />

<!-- Simplest possible app -->
<gradio-lite>
import gradio as gr

def greet(name):
    return "Hello, " + name + "!"

gr.Interface(greet, "textbox", "textbox").launch()
</gradio-lite>
```

**Attributes on `<gradio-lite>`:**

| Attribute | Values | Description |
|-----------|--------|-------------|
| `theme` | `"dark"`, `"light"` | Override system theme preference |
| `playground` | (boolean attribute) | Show code editor alongside demo |
| `layout` | `"horizontal"`, `"vertical"` | Playground layout direction (responsive by default) |
| `shared-worker` | (boolean attribute) | Share Pyodide runtime across apps on page |

**Child elements:**

| Element | Attributes | Description |
|---------|-----------|-------------|
| `<gradio-file>` | `name` (filename), `entrypoint` (boolean) | Define a file in the virtual filesystem |
| `<gradio-requirements>` | none | Newline-separated list of pip packages |

#### Multi-File App Example

```html
<gradio-lite>
  <gradio-file name="app.py" entrypoint>
import gradio as gr
from utils import add

demo = gr.Interface(fn=add, inputs=["number", "number"], outputs="number")
demo.launch()
  </gradio-file>

  <gradio-file name="utils.py">
def add(a, b):
    return a + b
  </gradio-file>

  <gradio-requirements>
transformers_js_py
  </gradio-requirements>
</gradio-lite>
```

#### Playground Mode Example

```html
<gradio-lite playground layout="horizontal">
import gradio as gr
gr.Interface(fn=lambda x: x, inputs=gr.Textbox(), outputs=gr.Textbox()).launch()
</gradio-lite>
```

#### Architecture

- **Execution:** Pyodide runs in a dedicated Web Worker (default) or SharedWorker (optional)
- **Package loading:** Uses `micropip.install()` within the Pyodide environment
- **Error display:** Errors go to browser console; no built-in error panel in the embedded app
- **Loading:** Shows loading spinner during Pyodide initialization (5-15 seconds)

#### Distribution

- **CDN:** `cdn.jsdelivr.net/npm/@gradio/lite/dist/lite.js` + `lite.css`
- **npm:** `@gradio/lite` package
- **No separate JS/CSS files** -- just two files to include
- **Module type:** ES module (`type="module"`)

#### Zero-Install Sharing

- Works on any static file host (GitHub Pages, Netlify, S3, etc.)
- No special server headers required for basic functionality
- SharedWorker mode works without COOP/COEP headers
- Can embed directly in any HTML page with just 2 `<script>`/`<link>` tags

#### Key Strengths for Panel-Live to Learn From

1. **Simplest possible API** -- single tag with code inside, attributes for everything
2. **Playground mode via attribute** -- no separate element needed
3. **SharedWorker via attribute** -- simple opt-in for multi-app pages
4. **Child elements for files and requirements** -- natural, declarative pattern
5. **Layout attribute** -- responsive by default, overridable

---

### 2.2 Stlite (Streamlit in Browser)

**Repository:** https://github.com/whitphx/stlite
**npm:** `@stlite/browser` (formerly `@stlite/mountable`)
**CDN:** `https://cdn.jsdelivr.net/npm/@stlite/browser@0.85.1/build/stlite.js`

#### HTML API Surface

Stlite offers **two APIs**: a custom HTML element (`<streamlit-app>`) and a JavaScript `mount()` function.

**Custom Element API (Simple):**

```html
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@stlite/browser@0.85.1/build/stlite.css" />
<script type="module"
  src="https://cdn.jsdelivr.net/npm/@stlite/browser@0.85.1/build/stlite.js"></script>

<streamlit-app>
import streamlit as st
name = st.text_input('Your name')
st.write("Hello,", name or "world")
</streamlit-app>
```

**Child elements for advanced configuration:**

| Element | Attributes | Description |
|---------|-----------|-------------|
| `<app-file>` | `name` (filename), `entrypoint` (boolean) | Define a file in the virtual filesystem |
| `<app-requirements>` | none | Newline-separated list of pip packages |

**JavaScript Mount API (Programmatic):**

```javascript
import { mount } from "https://cdn.jsdelivr.net/npm/@stlite/browser@0.85.1/build/stlite.js";

const controller = mount(
  {
    entrypoint: "streamlit_app.py",
    files: {
      "streamlit_app.py": `
        import streamlit as st
        st.write("Hello, world!")
      `,
      "utils.py": `
        def helper():
            return 42
      `,
      "data.csv": { url: "https://example.com/data.csv" }
    },
    requirements: ["faker", "pandas"],
    streamlitConfig: {
      "theme.base": "dark",
      "client.toolbarMode": "viewer"
    },
    sharedWorker: true,
    idbfsMountpoints: ["/home"]
  },
  document.getElementById("root")
);

// Controller methods:
// controller.unmount()
// controller.install(requirements)
// controller.writeFile(path, data)
// controller.readFile(path)
// controller.unlink(path)
// controller.renameFile(old, new)
```

#### Mount Options Reference

| Option | Type | Description |
|--------|------|-------------|
| `entrypoint` | `string` | Main script path (default: `"streamlit_app.py"`) |
| `files` | `Record<string, string\|Uint8Array\|{url}>` | Virtual filesystem files |
| `requirements` | `string[]` | Python packages to install |
| `streamlitConfig` | `Record<string, any>` | Streamlit configuration |
| `archives` | `ArchiveObject[]` | ZIP files to download and unpack |
| `pyodideUrl` | `string` | Custom Pyodide URL |
| `sharedWorker` | `boolean` | Enable SharedWorker mode |
| `idbfsMountpoints` | `string[]` | Persistent filesystem paths (IndexedDB) |

#### Architecture

- **Execution:** Pyodide runs in a dedicated Web Worker (default) or SharedWorker (optional)
- **Package loading:** `micropip.install()` with advanced options (keep_going, deps, credentials, pre, index_urls, constraints, reinstall)
- **Error display:** Uses Streamlit's built-in error display (red exception boxes)
- **Loading:** Streamlit-style loading spinner
- **Filesystem:** Emscripten virtual FS with IndexedDB persistence support
- **Multipage apps:** Standard Streamlit `pages/` directory convention

#### Distribution

- **CDN:** `cdn.jsdelivr.net/npm/@stlite/browser@VERSION/build/stlite.js` + `stlite.css`
- **npm packages:** `@stlite/browser`, `@stlite/react`, `@stlite/desktop`
- **React wrapper:** `@stlite/react` for embedding in React apps
- **Desktop:** `@stlite/desktop` for Electron-based desktop apps

#### Zero-Install Sharing

- Works on any static file host
- No special server headers required for basic functionality
- SharedWorker falls back to regular Worker on incompatible platforms (e.g., Chrome for Android)
- Files can be loaded from URLs (`{ url: "..." }`)

#### Key Strengths for Panel-Live to Learn From

1. **Dual API approach** -- simple custom element for basic use, programmatic `mount()` for advanced use
2. **Controller object** -- returned from `mount()` for runtime interaction (file management, install packages)
3. **Rich file specification** -- strings, binary data, or URL references
4. **IndexedDB persistence** -- files survive page reloads
5. **React wrapper** -- first-class React integration via `@stlite/react`
6. **Desktop version** -- Electron wrapper for offline apps
7. **Archive support** -- load ZIP files and unpack into virtual filesystem

---

### 2.3 Shinylive

**Repository:** https://github.com/posit-dev/py-shinylive (Python package), https://github.com/posit-dev/shinylive (JS/assets)
**Website:** https://shinylive.io
**Quarto extension:** https://github.com/quarto-ext/shinylive

#### HTML API Surface

Shinylive is **unique** among competitors in that it does NOT provide a simple HTML embed API. Instead, it works through:

1. **A CLI tool** (`shinylive export`) that generates a complete static site from Shiny app files
2. **A Quarto extension** that embeds apps in Quarto documents
3. **A web editor** at shinylive.io that encodes apps in URL hash fragments

There is **no `<shinylive>` HTML tag** or equivalent. You cannot simply include a `<script>` tag and write Python inline.

**Quarto Integration (primary embed method):**

````markdown
---
filters:
  - shinylive
---

```{shinylive-python}
#| standalone: true
#| viewerHeight: 420
#| components: [editor, viewer]
#| layout: vertical

from shiny import App, ui, render

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 0, 100, 40),
    ui.output_text_verbatim("txt"),
)

def server(input, output, session):
    @render.text
    def txt():
        return f"n*2 is {input.n() * 2}"

app = App(app_ui, server)
```
````

**Quarto Chunk Attributes:**

| Attribute | Values | Description |
|-----------|--------|-------------|
| `#\| standalone: true` | boolean | Required; marks a complete Shiny app |
| `#\| viewerHeight: N` | pixels | Height of the viewer panel |
| `#\| components: [editor, viewer]` | array | Which UI components to show |
| `#\| layout: vertical` | `"vertical"` | Stack editor above viewer |

**Multi-file support via `## file:` markers:**

````markdown
```{shinylive-python}
#| standalone: true
#| components: [editor, viewer]

from utils import helper
from shiny import App, ui

app_ui = ui.page_fluid(ui.output_text("txt"))

def server(input, output, session):
    @render.text
    def txt():
        return helper()

app = App(app_ui, server)

## file: utils.py
def helper():
    return "Hello from utils!"

## file: requirements.txt
isodate
attrs==21.4.0
```
````

**URL-based sharing:**

- Editor: `https://shinylive.io/py/editor/#code=BASE64_ENCODED_APP`
- App only: `https://shinylive.io/py/app/#code=BASE64_ENCODED_APP`
- Gist: `https://shinylive.io/py/editor/#gist=GIST_ID`

The URL hash is never sent to the server, preserving privacy.

**CLI Export:**

```bash
pip install shinylive
shinylive export myapp site
# Produces: site/app.json, site/index.html, site/edit/index.html, site/shinylive-sw.js
python3 -m http.server --directory site 8008
```

#### Architecture

- **Execution:** Pyodide runs in a Web Worker with a service worker for caching
- **Package loading:** Pre-bundled packages (175+) plus dynamic installation via `micropip`
- **Error display:** In the Shiny app's output area and Python console
- **Loading:** Progressive loading with caching (~13MB base, numpy adds 7.5MB, pandas 13MB, matplotlib 11.5MB)
- **Service worker:** `shinylive-sw.js` handles caching of Pyodide and packages
- **Security:** Code runs in browser sandbox; code is visible to users; data cannot be kept secret

#### Distribution

- **Python package:** `pip install shinylive` (CLI tool for exporting)
- **Quarto extension:** `quarto add quarto-ext/shinylive`
- **No standalone JS CDN** -- the JS assets are bundled with the exported site
- **Hosting:** Any static file server (GitHub Pages, Netlify, Posit Connect)

#### Zero-Install Sharing

- Exported sites work on any static host
- Service worker handles caching
- URL hash-based sharing works instantly on shinylive.io
- Multi-app sites can share the `shinylive/pyodide/` directory

#### Key Strengths for Panel-Live to Learn From

1. **Service worker caching** -- reduces subsequent load times dramatically
2. **URL hash sharing** -- private (never sent to server), compact
3. **Quarto integration** -- first-class documentation framework support
4. **Pre-bundled packages** -- 175+ packages shipped, no download needed for common ones
5. **Multi-app export** -- shared Pyodide directory reduces disk usage

#### Key Weaknesses to Avoid

1. **No HTML embed API** -- cannot simply add a `<script>` tag to an HTML page
2. **Requires CLI tool** -- export workflow is heavier than drop-in competitors
3. **Quarto-specific** -- no generic HTML/Markdown integration outside Quarto

---

### 2.4 PyScript

**Repository:** https://github.com/pyscript/pyscript
**Website:** https://pyscript.net
**Docs:** https://docs.pyscript.net/2026.1.1/
**CDN:** `https://pyscript.net/releases/2026.1.1/core.js`

#### HTML API Surface

PyScript uses **`<script>` tags with custom type attributes** rather than custom HTML elements:

```html
<!-- Load PyScript -->
<link rel="stylesheet" href="https://pyscript.net/releases/2026.1.1/core.css" />
<script type="module" src="https://pyscript.net/releases/2026.1.1/core.js"></script>

<!-- Run Python (Pyodide) -->
<script type="py">
from pyscript import display
display("Hello, World!")
</script>

<!-- Run MicroPython -->
<script type="mpy">
from pyscript import display
display("Hello from MicroPython!")
</script>

<!-- Run in a web worker -->
<script type="py" worker>
from pyscript import display
display("Running in a worker!")
</script>

<!-- External file with config -->
<script type="py" src="./main.py" config="./pyscript.json"></script>
```

**Script type attributes:**

| Type | Description |
|------|-------------|
| `type="py"` | Run Python code via Pyodide |
| `type="mpy"` | Run Python code via MicroPython (170KB, instant startup) |
| `type="py-editor"` | Interactive code editor with Pyodide |
| `type="mpy-editor"` | Interactive code editor with MicroPython |

**Attributes on `<script>` tags:**

| Attribute | Description |
|-----------|-------------|
| `src` | Path to external Python file |
| `config` | Path to JSON/TOML config file, or inline JSON string |
| `worker` | (boolean) Run in a web worker |
| `target` | DOM element ID for rendering output |
| `name` | Name for the worker (for inter-worker communication) |
| `terminal` | (boolean) Show a terminal-like output area |

**Editor-specific attributes:**

| Attribute | Description |
|-----------|-------------|
| `env` | Share interpreter across editors with same env value |
| `setup` | (boolean) Hidden bootstrap script for the environment |
| `target` | DOM element ID for output rendering |

**Configuration (pyscript.json or pyscript.toml):**

```json
{
  "packages": ["arrr", "pandas>=2.0"],
  "files": {
    "https://example.com/data.csv": "./data.csv",
    "./utils.py": "./lib/utils.py"
  },
  "js_modules": {
    "main": {
      "https://cdn.jsdelivr.net/npm/leaflet@1.x/dist/leaflet-src.esm.js": "leaflet"
    },
    "worker": {
      "https://cdn.jsdelivr.net/npm/ml-lib/dist/index.js": "ml"
    }
  },
  "plugins": ["!error"],
  "sync_main_only": false,
  "interpreter": "0.27.4"
}
```

**Configuration options reference:**

| Option | Type | Description |
|--------|------|-------------|
| `packages` | `string[]` | Python packages to install |
| `files` | `Record<string, string>` | URL-to-path file mappings |
| `js_modules.main` | `Record<string, string>` | JS modules for main thread |
| `js_modules.worker` | `Record<string, string>` | JS modules for workers |
| `plugins` | `string[]` | Enable/disable plugins (`!` prefix to disable) |
| `sync_main_only` | `boolean` | Restrict worker communication |
| `interpreter` | `string` | Pin Pyodide/MicroPython version |
| `experimental_create_proxy` | `"auto"` | Auto-handle FFI proxies |

#### Editor (py-editor) Deep Dive

```html
<!-- Basic editor -->
<script type="py-editor">
import this
</script>

<!-- Editor with shared environment -->
<script type="py-editor" env="shared">
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3]})
</script>

<!-- Second editor sharing the same environment -->
<script type="py-editor" env="shared">
print(df.head())
</script>

<!-- Hidden setup script for an environment -->
<script type="py-editor" env="data-env" setup>
import pandas as pd
data = pd.read_csv("data.csv")
</script>

<!-- User-facing editor that can use pre-loaded data -->
<script type="py-editor" env="data-env">
# 'data' is already available from setup
print(data.describe())
</script>
```

**Editor keyboard shortcuts:**
- `Ctrl+Enter` / `Cmd+Enter`: Execute all code
- `Shift+Enter`: Execute code
- `Esc` then `Tab`: Move focus outside editor (accessibility)
- `Tab`: Indent code

**Programmatic code access (after PyScript loads):**
```javascript
const editor = document.querySelector('script[type="py-editor"]');
editor.code;                    // Read current code
editor.code = "new code";      // Write new code
editor.process(editor.code);   // Execute code
```

#### Architecture

- **Core:** PolyScript -- a small, efficient core that handles code execution
- **Plugin system:** Most functionality is implemented as plugins with lifecycle hooks
- **Workers:** Uses the `coincident` library for worker communication (leverages Atomics API)
- **MicroPython support:** 170KB runtime for instant startup (vs ~13MB for Pyodide)
- **Interpreter isolation:** Each `<script>` tag can have its own interpreter, or share via `env` attribute

**Worker requirements for DOM access from workers:**
- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Embedder-Policy: require-corp`
- `Cross-Origin-Resource-Policy: cross-origin`
- Alternative: `mini-coi.js` service worker or `service-worker="./sw.js"` attribute

**Worker creation methods:**
```html
<!-- Via HTML attribute -->
<script type="py" src="./worker.py" worker name="my-worker"></script>

<!-- Via Python -->
from pyscript import PyWorker
worker = PyWorker("worker.py", type="pyodide")
```

#### Built-in APIs

| API | Description |
|-----|-------------|
| `pyscript.display()` | Rich output rendering (text, HTML, images, JSON) |
| `pyscript.when()` | Event decorator: `@when("click", "#btn")` |
| `pyscript.web` | Pythonic DOM API: `web.page["id"].value` |
| `pyscript.document` | DOM proxy (works in main + worker) |
| `pyscript.window` | Window proxy (works in main + worker) |
| `pyscript.fetch()` | HTTP requests (browser Fetch API wrapper) |
| `pyscript.storage` | IndexedDB storage (sync dict-like API) |
| `pyscript.HTML()` | Unescaped HTML rendering |
| `pyscript.WebSocket` | WebSocket connections |
| `pyscript.PyWorker()` | Create workers from Python |
| `pyscript.workers` | Access named workers |
| `pyscript.sync` | Worker-to-main thread data passing |
| `pyscript.config` | Read-only config access |
| `pyscript.RUNNING_IN_WORKER` | Boolean: True in workers |
| `pyscript.js_import()` | Dynamic JS module import |

#### Distribution

- **CDN:** `https://pyscript.net/releases/VERSION/core.js` + `core.css`
- **Offline:** `offline.zip` file with each release (PyScript + Pyodide + MicroPython)
- **No npm package** -- CDN-only distribution
- **Versioned URLs:** `https://pyscript.net/releases/2026.1.1/core.js`

#### Zero-Install Sharing

- Works on any static file host
- Basic functionality works without special headers
- DOM access from workers requires COOP/COEP headers (or mini-coi.js polyfill)
- Offline ZIP available for restricted environments

#### Key Strengths for Panel-Live to Learn From

1. **Plugin system** -- extensible architecture with lifecycle hooks
2. **MicroPython option** -- 170KB instant startup for lightweight use cases
3. **py-editor** -- full-featured code editor with shared environments, setup scripts, keyboard shortcuts
4. **coincident library** -- elegant worker communication using Atomics API
5. **Configuration flexibility** -- JSON, TOML, inline, or file-based config
6. **Files configuration** -- URL-to-path mapping with ZIP auto-extraction
7. **JS module imports** -- bridge JavaScript modules into Python namespace
8. **Offline support** -- offline.zip for restricted environments

#### Key Weaknesses to Avoid

1. **History of API instability** -- tags have changed multiple times (`<py-script>` -> `<script type="py">`)
2. **No built-in playground mode** -- py-editor is an editor, not a side-by-side playground
3. **Complex header requirements** -- COOP/COEP needed for full worker features
4. **No SharedWorker** -- each script gets its own worker (no memory sharing between apps)

---

## 3. Comparison Tables

### 3.1 HTML API Approach

| Product | Primary HTML Element | Secondary API | Pattern |
|---------|---------------------|--------------|---------|
| **gradio-lite** | `<gradio-lite>` custom element | None | Custom element + child elements |
| **stlite** | `<streamlit-app>` custom element | `mount()` JS function | Custom element + JS API |
| **shinylive** | None (Quarto code block) | CLI export | Quarto integration + CLI |
| **PyScript** | `<script type="py">` | `<script type="py-editor">` | Script type + config files |
| **panel-live (current)** | `<script type="panel">` | `PanelLive.configure()` | Script type variants |

### 3.2 Mode/Display Configuration

| Product | App-Only | Editor | Playground | How Configured |
|---------|----------|--------|------------|----------------|
| **gradio-lite** | Default | N/A | `playground` attribute | Attribute on same element |
| **stlite** | Default | N/A | N/A | Streamlit handles UI |
| **shinylive** | `components: [viewer]` | `components: [editor, viewer]` | Same as editor | Quarto chunk attribute |
| **PyScript** | `<script type="py">` | `<script type="py-editor">` | N/A | Different script types |
| **panel-live** | `<script type="panel">` | `<script type="panel-editor">` | `<script type="panel-playground">` | Different script types |

### 3.3 Multi-File Support

| Product | Syntax | Example |
|---------|--------|---------|
| **gradio-lite** | `<gradio-file name="x.py" entrypoint>` child elements | Natural HTML nesting |
| **stlite** | `<app-file name="x.py" entrypoint>` child elements OR `files` JS object | Both declarative and programmatic |
| **shinylive** | `## file: x.py` markers in code block | Text-based markers |
| **PyScript** | `"files"` config mapping URLs to paths | Config-file based |
| **panel-live** | Not supported | -- |

### 3.4 Requirements Specification

| Product | Syntax | Example |
|---------|--------|---------|
| **gradio-lite** | `<gradio-requirements>` child element | Newline-separated packages |
| **stlite** | `<app-requirements>` child OR `requirements` JS array | Both declarative and programmatic |
| **shinylive** | `## file: requirements.txt` in code block | Standard requirements.txt format |
| **PyScript** | `"packages"` in config JSON/TOML | Config-file based |
| **panel-live** | Auto-detection only | No explicit specification |

### 3.5 Worker Architecture

| Product | Default Execution | SharedWorker | COOP/COEP Required | Communication |
|---------|------------------|-------------|-------------------|---------------|
| **gradio-lite** | Dedicated Worker | Yes (`shared-worker` attr) | No | postMessage |
| **stlite** | Dedicated Worker | Yes (`sharedWorker` option) | No | postMessage |
| **shinylive** | Web Worker + Service Worker | No | No (service worker handles it) | postMessage |
| **PyScript** | Main thread (default) or Worker (`worker` attr) | No | For DOM access from workers | coincident (Atomics API) |
| **panel-live** | Main thread | No | For SharedArrayBuffer | postMessage (iframes) |

### 3.6 Distribution

| Product | CDN | npm | Offline | Doc Framework Extensions |
|---------|-----|-----|---------|--------------------------|
| **gradio-lite** | jsdelivr | `@gradio/lite` | No | Quarto, Sphinx (via HTML) |
| **stlite** | jsdelivr | `@stlite/browser`, `@stlite/react`, `@stlite/desktop` | Desktop app | No official extensions |
| **shinylive** | Bundled with export | No | Yes (exported site is self-contained) | Quarto (official), Sphinx (community) |
| **PyScript** | pyscript.net | No | Yes (`offline.zip`) | No official extensions |
| **panel-live** | Not distributed | No | No | Not yet |

### 3.7 Feature Comparison

| Feature | gradio-lite | stlite | shinylive | PyScript | panel-live |
|---------|-------------|--------|-----------|----------|------------|
| Web Workers | Yes | Yes | Yes | Yes | No |
| SharedWorker | Yes | Yes | No | No | No |
| Multi-file | Yes | Yes | Yes | Yes | No |
| Requirements | Yes | Yes | Yes | Yes | Auto only |
| Theme control | Yes | Via config | No | No | No |
| Layout options | Yes | No | Yes (Quarto) | No | No |
| Editor mode | Yes (playground) | No | Yes | Yes (py-editor) | Yes |
| URL sharing | No | No | Yes | No | Yes |
| Offline support | No | Desktop | Exported site | Yes (zip) | No |
| React wrapper | No | Yes | No | No | No |
| Service worker | No | No | Yes | Optional | No |
| IndexedDB persistence | No | Yes | No | Yes | No |
| MicroPython | No | No | No | Yes | No |

---

## 4. Recommendations for Panel-Live

### 4.1 API Design: Adopt the Custom Element Pattern

**Recommendation:** Use `<panel-live>` as the primary custom element with attributes for mode configuration, rather than separate `<script type="panel-*">` variants.

**Rationale:**
- 3 of 4 competitors use custom elements
- Custom elements provide better browser tooling (DevTools inspection, CSS targeting)
- A single element with a `mode` attribute is simpler than three separate script types
- Gradio-lite proves this works well: `<gradio-lite playground layout="horizontal">`

**Proposed API:**

```html
<!-- App only (default) -->
<panel-live>
import panel as pn
pn.panel("Hello World").servable()
</panel-live>

<!-- Editor mode -->
<panel-live mode="editor">
import panel as pn
pn.panel("Hello World").servable()
</panel-live>

<!-- Playground mode -->
<panel-live mode="playground" layout="horizontal">
import panel as pn
pn.panel("Hello World").servable()
</panel-live>

<!-- With files and requirements -->
<panel-live mode="editor">
  <panel-file name="app.py" entrypoint>
import panel as pn
from utils import create_plot
pn.panel(create_plot()).servable()
  </panel-file>

  <panel-file name="utils.py">
def create_plot():
    return "Plot here"
  </panel-file>

  <panel-requirements>
pandas
hvplot
  </panel-requirements>
</panel-live>
```

**Alternative:** Keep `<script type="panel">` but add `mode` attribute: `<script type="panel" mode="editor">`. This follows the PyScript pattern and avoids custom element registration complexity. Both approaches are valid.

### 4.2 Web Workers: Mandatory for Credibility

**Recommendation:** Implement dedicated web worker execution as the default, with optional SharedWorker for multi-app pages.

**Rationale:**
- All 4 competitors use workers
- Main-thread execution blocks the page for 5-15 seconds during load
- SharedWorker support (stlite, gradio-lite) is critical for documentation pages

**Priority:** P0 -- this is the single most important architectural gap.

### 4.3 Distribution: CDN + npm

**Recommendation:** Distribute via jsdelivr CDN (like gradio-lite and stlite) with versioned URLs.

**Proposed URLs:**
```
https://cdn.jsdelivr.net/npm/panel-live@1.0.0/dist/panel-live.js
https://cdn.jsdelivr.net/npm/panel-live@1.0.0/dist/panel-live.css
```

Or via holoviz CDN:
```
https://cdn.holoviz.org/panel-live/1.0.0/panel-live.min.js
https://cdn.holoviz.org/panel-live/1.0.0/panel-live.css
```

### 4.4 Multi-File Support: Child Elements

**Recommendation:** Use child elements (`<panel-file>`, `<panel-requirements>`) following the gradio-lite/stlite pattern.

**Rationale:**
- Natural HTML nesting
- Proven pattern across competitors
- Works well with doc framework extensions

### 4.5 Configuration: Dual Approach

**Recommendation:** Support both HTML attributes (simple cases) and a JS API (complex cases), following stlite's dual API pattern.

```javascript
// Programmatic API for complex configurations
PanelLive.mount({
  entrypoint: "app.py",
  files: { "app.py": "...", "utils.py": "..." },
  requirements: ["pandas", "hvplot"],
  theme: "dark",
  layout: "horizontal",
  sharedWorker: true
}, document.getElementById("root"));
```

### 4.6 PyScript Integration: Strategic Assessment

**Recommendation:** Build on PyScript's `coincident` library for worker communication, but do NOT adopt PyScript as a full dependency.

**Rationale:**
- PyScript's `coincident` library solves the hard problem of worker<->main thread communication elegantly
- PyScript's plugin system could provide lifecycle hooks, but adds API coupling risk
- PyScript's `py-editor` could replace CodeMirror, but loses customization control
- Better to use PyScript's proven patterns and libraries selectively

### 4.7 Competitive Differentiators for Panel-Live

Features that would set panel-live apart from all competitors:

1. **URL sharing with compression** -- only shinylive has this, and panel-live already has a basic implementation
2. **Sphinx + MkDocs extensions** -- shinylive only has Quarto; panel-live can target Sphinx and MkDocs directly
3. **Panel ecosystem** -- hvPlot, HoloViews, Param, panel-material-ui provide a richer widget/visualization ecosystem
4. **Theme integration** -- auto-detect and match host page theme (no competitor does this well)
5. **Service worker caching** -- adopt shinylive's approach for dramatically faster subsequent loads

---

## Sources

- [Gradio-Lite Guide](https://www.gradio.app/4.44.1/guides/gradio-lite)
- [Gradio-Lite Blog Post (Hugging Face)](https://huggingface.co/blog/gradio-lite)
- [@gradio/lite npm](https://www.npmjs.com/package/@gradio/lite)
- [Stlite GitHub](https://github.com/whitphx/stlite)
- [@stlite/browser Docs](https://stlite.net/browser/)
- [Shinylive for Python](https://shiny.posit.co/py/get-started/shinylive.html)
- [Shinylive Quarto Extension](https://quarto-ext.github.io/shinylive/)
- [PyScript Docs (2026.1.1)](https://docs.pyscript.net/2026.1.1/)
- [PyScript Editor Guide](https://docs.pyscript.net/2025.2.3/user-guide/editor/)
- [PyScript Workers Guide](https://docs.pyscript.net/2025.2.3/user-guide/workers/)
- [PyScript Configuration Guide](https://docs.pyscript.net/2025.2.3/user-guide/configuration/)
- [PyScript Built-in APIs](https://docs.pyscript.net/2025.2.1/api/)
- [Panel Issue #5766: Make it as easy as Gradio-lite](https://github.com/holoviz/panel/issues/5766)
