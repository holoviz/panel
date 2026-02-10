/**
 * panel-pyscript-plugin.js
 *
 * PyScript plugin that handles Panel-specific initialization:
 *   - Loads Bokeh JS + Panel JS before the Python interpreter runs
 *   - Installs Panel/Bokeh wheels via micropip (faster than PyPI)
 *   - Wires up the .servable() rendering pipeline
 *   - Loads extension resources (custom CSS/JS from Bokeh models)
 *
 * Usage:
 *   <script type="module" src="panel-pyscript-plugin.js"></script>
 *   <!-- must appear BEFORE the PyScript core.js import -->
 */

// --- Configuration ---
const PANEL_VERSION = "1.8.7";
const BOKEH_VERSION = "3.8.2";

const BOKEH_JS_URLS = [
  `https://cdn.bokeh.org/bokeh/release/bokeh-${BOKEH_VERSION}.min.js`,
  `https://cdn.bokeh.org/bokeh/release/bokeh-widgets-${BOKEH_VERSION}.min.js`,
  `https://cdn.bokeh.org/bokeh/release/bokeh-tables-${BOKEH_VERSION}.min.js`,
];
const PANEL_JS_URL = `https://cdn.jsdelivr.net/npm/@holoviz/panel@${PANEL_VERSION}/dist/panel.min.js`;
const BOKEH_WHL = `https://cdn.holoviz.org/panel/wheels/bokeh-${BOKEH_VERSION}-py3-none-any.whl`;
const PANEL_WHL = `https://cdn.holoviz.org/panel/${PANEL_VERSION}/dist/wheels/panel-${PANEL_VERSION}-py3-none-any.whl`;

// --- Helpers ---

function loadScript(url) {
  return new Promise((resolve, reject) => {
    // Skip if already loaded (idempotent)
    if (document.querySelector(`script[src="${url}"]`)) {
      resolve();
      return;
    }
    const s = document.createElement("script");
    s.src = url;
    s.crossOrigin = "anonymous";
    s.onload = resolve;
    s.onerror = () => reject(new Error("Failed to load " + url));
    document.head.appendChild(s);
  });
}

let jsLoaded = false;
let jsLoadPromise = null;

async function ensureBokehPanelJS() {
  if (jsLoaded) return;
  if (jsLoadPromise) return jsLoadPromise;
  jsLoadPromise = (async () => {
    for (const url of BOKEH_JS_URLS) {
      await loadScript(url);
    }
    await loadScript(PANEL_JS_URL);
    jsLoaded = true;
  })();
  return jsLoadPromise;
}

// --- Status indicator ---
let statusEl = null;

function setStatus(msg) {
  if (!statusEl) {
    statusEl = document.createElement("div");
    statusEl.id = "panel-status";
    statusEl.style.cssText =
      "position:fixed;top:0;left:0;right:0;background:#1b5e20;color:white;" +
      "padding:8px 16px;font-size:14px;z-index:9999;font-family:system-ui,sans-serif;" +
      "transition:opacity .3s";
    document.body.prepend(statusEl);
  }
  statusEl.style.opacity = "1";
  statusEl.textContent = msg;
}

function hideStatus() {
  if (statusEl) statusEl.style.opacity = "0";
}

// --- Track loaded extension resources ---
const loadedExtResources = new Set();

async function loadExtensionResources(pyodide) {
  const resourcesJson = await pyodide.runPythonAsync(`
import json
from bokeh.model import Model
js_urls = []
css_urls = []
for _cls in Model.model_class_reverse_map.values():
    for url in getattr(_cls, '__javascript__', []) or []:
        if url not in js_urls:
            js_urls.append(url)
    for url in getattr(_cls, '__css__', []) or []:
        if url not in css_urls:
            css_urls.append(url)
json.dumps({"js": js_urls, "css": css_urls})
`);
  const resources = JSON.parse(resourcesJson);

  for (const url of resources.css) {
    if (loadedExtResources.has(url)) continue;
    loadedExtResources.add(url);
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = url;
    link.crossOrigin = "anonymous";
    document.head.appendChild(link);
  }

  for (const url of resources.js) {
    if (loadedExtResources.has(url)) continue;
    loadedExtResources.add(url);
    await loadScript(url);
  }
}

// --- PyScript Plugin Registration ---
//
// We import hooks from PyScript's core.js and register our Panel
// initialization logic into the lifecycle.

let hooksRegistered = false;

export async function registerPanelPlugin(pyscriptCoreUrl) {
  if (hooksRegistered) return;
  hooksRegistered = true;

  // Dynamic import of PyScript hooks
  const coreUrl =
    pyscriptCoreUrl || "https://pyscript.net/releases/2024.11.1/core.js";
  const { hooks } = await import(coreUrl);

  // --- onReady: load Bokeh/Panel JS + install Python packages ---
  hooks.main.onReady.add(async (wrap, element) => {
    setStatus("Loading Bokeh & Panel JS...");
    await ensureBokehPanelJS();

    setStatus("Installing Panel packages...");
    // wrap.interpreter is the Pyodide instance
    const pyodide = wrap.interpreter;

    await pyodide.loadPackage("micropip");
    await pyodide.runPythonAsync(`
import micropip
await micropip.install("${BOKEH_WHL}")
await micropip.install("${PANEL_WHL}", reinstall=True, keep_going=True)
await micropip.install("pyodide-http")
`);

    setStatus("Initializing Panel...");
    await pyodide.runPythonAsync(`
import panel as pn
from panel.io.pyodide import init_doc
print("Panel", pn.__version__, "ready (via PyScript plugin)")
`);

    hideStatus();
  });

  // --- codeBeforeRun: set up document context for .servable() ---
  hooks.main.codeBeforeRun.add(() => {
    return `
import panel as pn
from bokeh.io.doc import set_curdoc
from bokeh.document import Document
from bokeh.settings import settings as bk_settings
from panel.io.document import MockSessionContext
from panel.io.state import state

bk_settings.simple_ids.set_value(False)
doc = Document()
set_curdoc(doc)
doc.hold()
doc._session_context = lambda: MockSessionContext(document=doc)
state.curdoc = doc
`;
  });

  // --- onAfterRun: render servable objects into the DOM ---
  hooks.main.onAfterRun.add(async (wrap, element) => {
    const pyodide = wrap.interpreter;

    // Load any extension resources (custom JS/CSS from Bokeh models)
    setStatus("Loading extension resources...");
    await loadExtensionResources(pyodide);

    // Find or create a target container
    let targetId = element?.getAttribute("data-target");
    let targetEl;
    if (targetId) {
      targetEl = document.getElementById(targetId);
    }
    if (!targetEl) {
      // Create a target div after the script element
      targetEl = document.createElement("div");
      targetEl.id = "panel-target-" + Date.now();
      targetId = targetEl.id;
      if (element && element.parentNode) {
        // Insert after the PyScript-generated output div
        const outputDiv = element.nextElementSibling;
        if (outputDiv) {
          outputDiv.after(targetEl);
        } else {
          element.parentNode.appendChild(targetEl);
        }
      } else {
        document.body.appendChild(targetEl);
      }
    }

    setStatus("Rendering Panel app...");

    // Check if user code used .servable()
    const hasServable = await pyodide.runPythonAsync(`
from panel.io.state import state
len(state.curdoc.roots) > 0
`);

    if (hasServable) {
      pyodide.globals.set("__panel_target_id__", targetId);
      await pyodide.runPythonAsync(`
import js
from panel.io.pyodide import _doc_json, _link_docs, sync_location
from panel.io.state import state

doc = state.curdoc
target_el = js.document.getElementById(__panel_target_id__)
target_el.innerHTML = ''

for root in doc.roots:
    el = js.document.createElement('div')
    el.setAttribute('data-root-id', str(root.id))
    el.id = f'el-{root.id}'
    target_el.appendChild(el)

root_els = target_el.querySelectorAll('[data-root-id]')
for el in root_els:
    el.innerHTML = ''

docs_json, render_items, root_ids = _doc_json(doc, root_els)
doc._session_context = None

views = await js.window.Bokeh.embed.embed_items(
    js.JSON.parse(docs_json), js.JSON.parse(render_items)
)
jsdoc = list(views[0].roots)[0].model.document
_link_docs(doc, jsdoc)
sync_location()
`);
    }

    hideStatus();
  });
}

// --- Auto-register if script is loaded as a module ---
// Look for a data attribute on the script tag to get the PyScript core URL
const currentScript = document.querySelector(
  'script[src*="panel-pyscript-plugin"]'
);
const coreUrl = currentScript?.getAttribute("data-pyscript-core");
registerPanelPlugin(coreUrl);
