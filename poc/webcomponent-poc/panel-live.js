/**
 * panel-live.js — Web Component POC for Panel Live
 *
 * Defines <panel-live>, <panel-file>, and <panel-requirements> custom elements.
 *
 * Usage:
 *   <script src="panel-live.js"></script>
 *   <panel-live>
 *     import panel as pn
 *     pn.panel("Hello").servable()
 *   </panel-live>
 *
 *   <panel-live mode="editor" theme="light">
 *     import panel as pn
 *     pn.widgets.FloatSlider(name="X").servable()
 *   </panel-live>
 *
 *   <panel-live mode="playground" layout="horizontal">
 *     ...
 *   </panel-live>
 */

// ============================================================
// Cleanup stale service workers (JupyterLite/JupyterHub can
// register workers that intercept fetches and cause crashes)
// ============================================================
if (navigator.serviceWorker && navigator.serviceWorker.controller) {
  navigator.serviceWorker.getRegistrations().then(regs => {
    const had = regs.length > 0;
    regs.forEach(r => r.unregister());
    if (had) location.reload();
  });
}

// ============================================================
// Configuration
// ============================================================

const PANEL_LIVE_CONFIG = {
  pyodideVersion: 'v0.28.2',
  panelVersion: '1.8.7',
  bokehVersion: '3.8.2',
};

function cdnUrls() {
  const { pyodideVersion, panelVersion, bokehVersion } = PANEL_LIVE_CONFIG;
  return {
    pyodide: `https://cdn.jsdelivr.net/pyodide/${pyodideVersion}/full/pyodide.js`,
    bokehJs: [
      `https://cdn.bokeh.org/bokeh/release/bokeh-${bokehVersion}.js`,
      `https://cdn.bokeh.org/bokeh/release/bokeh-widgets-${bokehVersion}.min.js`,
      `https://cdn.bokeh.org/bokeh/release/bokeh-tables-${bokehVersion}.min.js`,
    ],
    panelJs: `https://cdn.jsdelivr.net/npm/@holoviz/panel@${panelVersion}/dist/panel.min.js`,
    bokehWhl: `https://cdn.holoviz.org/panel/${panelVersion}/dist/wheels/bokeh-${bokehVersion}-py3-none-any.whl`,
    panelWhl: `https://cdn.holoviz.org/panel/${panelVersion}/dist/wheels/panel-${panelVersion}-py3-none-any.whl`,
  };
}

// ============================================================
// Shared Pyodide Runtime (singleton)
// ============================================================

let _pyodide = null;
let _initPromise = null;
const _installedPackages = new Set(['panel', 'bokeh', 'pyodide-http']);
const _loadedExtResources = new Set();
let _jsResourcesLoaded = false;

function loadScript(url) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${url}"]`)) { resolve(); return; }
    const s = document.createElement('script');
    s.src = url;
    s.crossOrigin = 'anonymous';
    s.onload = resolve;
    s.onerror = () => reject(new Error('Failed to load ' + url));
    document.head.appendChild(s);
  });
}

function loadCSS(url) {
  if (document.querySelector(`link[href="${url}"]`)) return;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = url;
  link.crossOrigin = 'anonymous';
  document.head.appendChild(link);
}

async function loadJSResources() {
  if (_jsResourcesLoaded) return;
  const urls = cdnUrls();
  for (const url of urls.bokehJs) await loadScript(url);
  await loadScript(urls.panelJs);
  _jsResourcesLoaded = true;
}

async function initPyodide(statusCallback) {
  if (_initPromise) return _initPromise;
  _initPromise = (async () => {
    statusCallback('Loading Bokeh & Panel JS...');
    await loadJSResources();

    statusCallback('Loading Pyodide...');
    await loadScript(cdnUrls().pyodide);

    statusCallback('Initializing Pyodide...');
    console.log('[panel-live] Initializing Pyodide...');
    const pyodide = await window.loadPyodide();

    statusCallback('Loading micropip...');
    console.log('[panel-live] Loading micropip...');
    await pyodide.loadPackage('micropip');

    const urls = cdnUrls();

    statusCallback('Installing Bokeh + Panel wheels...');
    console.log('[panel-live] Installing wheels:', urls.bokehWhl, urls.panelWhl);
    const micropip = pyodide.pyimport('micropip');
    await micropip.install([urls.bokehWhl, urls.panelWhl]);

    statusCallback('Initializing Panel...');
    console.log('[panel-live] Initializing Panel...');
    await pyodide.runPythonAsync(
      'import panel as pn\n' +
      'print("Panel", pn.__version__, "ready")\n'
    );

    _pyodide = pyodide;
    return pyodide;
  })();
  return _initPromise;
}

async function detectAndInstallRequirements(code, statusCallback) {
  _pyodide.globals.set('__user_code__', code);
  const newPkgs = await _pyodide.runPythonAsync(
    'from panel.io.mime_render import find_requirements\n' +
    'reqs = find_requirements(__user_code__)\n' +
    'import json\n' +
    'json.dumps(reqs)\n'
  );
  const requirements = JSON.parse(newPkgs);
  const toInstall = requirements.filter(pkg => !_installedPackages.has(pkg));
  if (toInstall.length > 0) {
    statusCallback('Installing: ' + toInstall.join(', ') + '...');
    const micropip = _pyodide.pyimport('micropip');
    await micropip.install(toInstall);
    toInstall.forEach(pkg => _installedPackages.add(pkg));
  }
}

async function installExplicitRequirements(requirementsText, statusCallback) {
  const pkgs = requirementsText.split('\n')
    .map(l => l.trim())
    .filter(l => l && !l.startsWith('#'));
  if (pkgs.length === 0) return;
  statusCallback('Installing: ' + pkgs.join(', ') + '...');
  const micropip = _pyodide.pyimport('micropip');
  await micropip.install(pkgs);
  pkgs.forEach(pkg => _installedPackages.add(pkg.split(/[=<>!]/)[0]));
}

async function loadExtensionResources() {
  const resourcesJson = await _pyodide.runPythonAsync(
    'import json\n' +
    'from bokeh.model import Model\n' +
    'js_urls = []\n' +
    'css_urls = []\n' +
    'for _cls in Model.model_class_reverse_map.values():\n' +
    "    for url in getattr(_cls, '__javascript__', []) or []:\n" +
    '        if url not in js_urls:\n' +
    '            js_urls.append(url)\n' +
    "    for url in getattr(_cls, '__css__', []) or []:\n" +
    '        if url not in css_urls:\n' +
    '            css_urls.append(url)\n' +
    'json.dumps({"js": js_urls, "css": css_urls})\n'
  );
  const resources = JSON.parse(resourcesJson);
  for (const url of resources.css) {
    if (!_loadedExtResources.has(url)) { _loadedExtResources.add(url); loadCSS(url); }
  }
  for (const url of resources.js) {
    if (!_loadedExtResources.has(url)) { _loadedExtResources.add(url); await loadScript(url); }
  }
}

function cleanupContainer(el) {
  if (window.Bokeh && window.Bokeh.index && window.Bokeh.index.roots) {
    try {
      for (const root of Array.from(window.Bokeh.index.roots)) {
        try { if (root.el && el.contains(root.el)) root.remove(); } catch (e) {}
      }
    } catch (e) {}
  }
  el.innerHTML = '';
}

// ============================================================
// Execution queue (Pyodide is single-threaded, shared state
// like state.curdoc means we must serialize app execution)
// ============================================================

let _execQueue = Promise.resolve();

function enqueueExecution(fn) {
  _execQueue = _execQueue.then(fn, fn);
  return _execQueue;
}

// ============================================================
// 3-branch Panel execution (from panel-embed.js, proven logic)
// ============================================================

async function runPanelCode(targetEl, code, statusCallback) {
  const targetId = targetEl.id || ('panel-target-' + Math.random().toString(36).slice(2, 8));
  targetEl.id = targetId;

  try {
    await detectAndInstallRequirements(code, statusCallback);
    cleanupContainer(targetEl);

    const hasServable = code.includes('.servable(');
    const hasServableTarget = /\.servable\s*\(\s*target\s*=/.test(code);

    _pyodide.globals.set('__panel_user_code__', code);
    _pyodide.globals.set('__panel_target_id__', targetId);

    if (hasServable && !hasServableTarget) {
      // .servable() flow
      await _pyodide.runPythonAsync(
        'import js\n' +
        'import panel as pn\n' +
        'from bokeh.io.doc import set_curdoc\n' +
        'from bokeh.document import Document\n' +
        'from bokeh.settings import settings as bk_settings\n' +
        'from panel.io.document import MockSessionContext\n' +
        'from panel.io.state import state\n' +
        '__ns__ = {"__builtins__": __builtins__}\n' +
        'exec("import panel as pn", __ns__)\n' +
        'bk_settings.simple_ids.set_value(False)\n' +
        'doc = Document()\n' +
        'set_curdoc(doc)\n' +
        'doc.hold()\n' +
        'doc._session_context = lambda: MockSessionContext(document=doc)\n' +
        'state.curdoc = doc\n' +
        'exec(__panel_user_code__, __ns__)\n'
      );
      await loadExtensionResources();
      await _pyodide.runPythonAsync(
        'import js\n' +
        'from panel.io.pyodide import _doc_json, _link_docs, sync_location\n' +
        'from panel.io.state import state\n' +
        'doc = state.curdoc\n' +
        'target_el = js.document.getElementById(__panel_target_id__)\n' +
        "target_el.innerHTML = ''\n" +
        'for root in doc.roots:\n' +
        "    el = js.document.createElement('div')\n" +
        "    el.setAttribute('data-root-id', str(root.id))\n" +
        "    el.id = f'el-{root.id}'\n" +
        '    target_el.appendChild(el)\n' +
        "root_els = target_el.querySelectorAll('[data-root-id]')\n" +
        'for el in root_els:\n' +
        "    el.innerHTML = ''\n" +
        'docs_json, render_items, root_ids = _doc_json(doc, root_els)\n' +
        'doc._session_context = None\n' +
        'views = await js.window.Bokeh.embed.embed_items(\n' +
        '    js.JSON.parse(docs_json), js.JSON.parse(render_items)\n' +
        ')\n' +
        'jsdoc = list(views[0].roots)[0].model.document\n' +
        '_link_docs(doc, jsdoc)\n' +
        'sync_location()\n'
      );
    } else if (hasServableTarget) {
      // .servable(target=...) flow
      await _pyodide.runPythonAsync(
        'import panel as pn\n' +
        'from bokeh.io.doc import set_curdoc\n' +
        'from bokeh.document import Document\n' +
        'from bokeh.settings import settings as bk_settings\n' +
        'from panel.io.document import MockSessionContext\n' +
        'from panel.io.state import state\n' +
        '__ns__ = {"__builtins__": __builtins__}\n' +
        'exec("import panel as pn", __ns__)\n' +
        'bk_settings.simple_ids.set_value(False)\n' +
        'doc = Document()\n' +
        'set_curdoc(doc)\n' +
        'doc.hold()\n' +
        'doc._session_context = lambda: MockSessionContext(document=doc)\n' +
        'state.curdoc = doc\n' +
        'exec(__panel_user_code__, __ns__)\n'
      );
      await loadExtensionResources();
      await _pyodide.runPythonAsync(
        'from panel.io.pyodide import write_doc\n' +
        'await write_doc()\n'
      );
    } else {
      // Expression flow (no .servable())
      await _pyodide.runPythonAsync(
        'import panel as pn\n' +
        'from panel.io.mime_render import exec_with_return\n' +
        '__ns__ = {"__builtins__": __builtins__}\n' +
        '__exec_result__ = exec_with_return(__panel_user_code__, __ns__)\n'
      );
      await loadExtensionResources();
      await _pyodide.runPythonAsync(
        'import js\n' +
        'from panel.io.pyodide import write\n' +
        'if __exec_result__ is not None:\n' +
        '    await write(__panel_target_id__, __exec_result__)\n' +
        'else:\n' +
        '    el = js.document.getElementById(__panel_target_id__)\n' +
        '    el.innerHTML = \'<p style="color:#666;padding:16px;">Code executed (no visual output)</p>\'\n'
      );
    }
  } catch (error) {
    targetEl.innerHTML = '<pre style="color:#b71c1c;background:#ffebee;padding:16px;border-radius:4px;white-space:pre-wrap;font-size:13px;margin:0;">' +
      (error.message || String(error)).replace(/</g, '&lt;') + '</pre>';
  }
}

// ============================================================
// Utility: unique IDs
// ============================================================

let _idCounter = 0;
function uid() { return 'pl-' + (++_idCounter); }

// ============================================================
// <panel-file> and <panel-requirements> (data-only elements)
// ============================================================

class PanelFile extends HTMLElement {
  get name() { return this.getAttribute('name') || 'app.py'; }
  get entrypoint() { return this.hasAttribute('entrypoint'); }
  get code() { return this.textContent; }
}

class PanelRequirements extends HTMLElement {
  get packages() { return this.textContent; }
}

class PanelExample extends HTMLElement {
  get label() { return this.getAttribute('name') || 'Example'; }
  get code() { return this.textContent; }
}

customElements.define('panel-file', PanelFile);
customElements.define('panel-requirements', PanelRequirements);
customElements.define('panel-example', PanelExample);

// ============================================================
// URL sharing: encode/decode code in URL hash
// ============================================================

function encodeCode(code) {
  return btoa(String.fromCharCode(...new TextEncoder().encode(code)));
}

function decodeCode(encoded) {
  return new TextDecoder().decode(Uint8Array.from(atob(encoded), c => c.charCodeAt(0)));
}

function getCodeFromHash() {
  const hash = location.hash.slice(1);
  const params = new URLSearchParams(hash);
  const encoded = params.get('code');
  if (encoded) {
    try { return decodeCode(encoded); } catch (e) { return null; }
  }
  return null;
}

function setCodeInHash(code) {
  const encoded = encodeCode(code);
  const params = new URLSearchParams(location.hash.slice(1));
  params.set('code', encoded);
  history.replaceState(null, '', '#' + params.toString());
}

// ============================================================
// <panel-live> — Main Custom Element
// ============================================================

let _stylesInjected = false;

const PANEL_LIVE_STYLES = `
  panel-live {
    display: block;
    font-family: system-ui, -apple-system, sans-serif;
  }
  panel-live:not(:defined) { display: none; }

  .pl-container {
    border: 1px solid var(--pl-border, #e0e0e0);
    border-radius: var(--pl-radius, 6px);
    overflow: hidden;
    background: var(--pl-bg, #fff);
  }

  /* Status bar */
  .pl-status {
    padding: 12px 16px;
    font-size: 14px;
    color: var(--pl-status-color, #555);
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .pl-status.hidden { display: none; }
  .pl-status.error { color: #b71c1c; background: #ffebee; }
  .pl-spinner {
    width: 16px; height: 16px;
    border: 2px solid #ddd;
    border-top-color: #1976d2;
    border-radius: 50%;
    animation: pl-spin 0.7s linear infinite;
  }
  @keyframes pl-spin { to { transform: rotate(360deg); } }

  /* Output area */
  .pl-output {
    min-height: 100px;
    padding: 0;
  }

  /* Editor header */
  .pl-editor-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: var(--pl-header-bg, #1e1e2e);
    color: var(--pl-header-color, #cdd6f4);
    font-size: 13px;
  }
  .pl-editor-header.light {
    background: var(--pl-header-bg, #f5f5f5);
    color: var(--pl-header-color, #333);
  }
  .pl-lang {
    background: #3b82f6;
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
  }
  .pl-title { flex: 1; font-weight: 500; }
  .pl-shortcut { opacity: 0.5; font-size: 11px; }
  .pl-btn {
    background: var(--pl-btn-bg, #a6e3a1);
    color: var(--pl-btn-color, #1e1e2e);
    border: none;
    padding: 4px 14px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 700;
    font-size: 13px;
  }
  .pl-btn:hover { filter: brightness(1.1); }
  .pl-btn.secondary {
    background: transparent;
    color: var(--pl-header-color, #cdd6f4);
    border: 1px solid currentColor;
    font-weight: 400;
    opacity: 0.7;
  }
  .pl-btn.secondary:hover { opacity: 1; }

  /* Editor textarea */
  .pl-editor-area {
    width: 100%;
    min-height: 180px;
    max-height: 500px;
    border: none;
    resize: vertical;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 14px;
    line-height: 1.6;
    padding: 12px 16px;
    tab-size: 4;
    outline: none;
    box-sizing: border-box;
  }
  .pl-editor-area.dark {
    background: var(--pl-editor-bg, #1e1e2e);
    color: var(--pl-editor-color, #cdd6f4);
  }
  .pl-editor-area.light {
    background: var(--pl-editor-bg, #fafafa);
    color: var(--pl-editor-color, #1a1a2e);
  }

  /* Playground layout */
  .pl-playground {
    display: flex;
  }
  .pl-playground.vertical {
    flex-direction: column;
  }
  .pl-playground > .pl-editor-pane {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .pl-playground > .pl-preview-pane {
    flex: 1;
    min-width: 0;
    border-left: 1px solid var(--pl-border, #e0e0e0);
  }
  .pl-playground.vertical > .pl-preview-pane {
    border-left: none;
    border-top: 1px solid var(--pl-border, #e0e0e0);
  }
  .pl-playground > .pl-editor-pane .pl-editor-area {
    flex: 1;
    resize: none;
    min-height: 300px;
  }

  /* Editor mode (stacked) */
  .pl-editor-stacked .pl-output {
    border-top: 1px solid var(--pl-border, #e0e0e0);
  }

  /* Fullscreen playground */
  panel-live[fullscreen] {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: 10000;
    margin: 0;
    border-radius: 0;
  }
  panel-live[fullscreen] .pl-container {
    height: 100vh;
    border: none;
    border-radius: 0;
    display: flex;
    flex-direction: column;
  }
  panel-live[fullscreen] .pl-playground {
    flex: 1;
    min-height: 0;
  }
  panel-live[fullscreen] .pl-playground > .pl-editor-pane {
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  panel-live[fullscreen] .pl-playground > .pl-editor-pane .pl-editor-header {
    flex-shrink: 0;
  }
  panel-live[fullscreen] .pl-playground > .pl-editor-pane .pl-editor-area {
    min-height: 0;
    flex: 1;
  }
  panel-live[fullscreen] .pl-playground > .pl-preview-pane {
    overflow: auto;
  }

  /* Examples dropdown */
  .pl-examples-select {
    background: transparent;
    color: inherit;
    border: 1px solid currentColor;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    opacity: 0.7;
    max-width: 180px;
    outline: none;
  }
  .pl-examples-select:hover { opacity: 1; }
  .pl-examples-select option { color: #1a1a2e; background: #fff; }

  /* Share button feedback */
  .pl-btn.share-btn { position: relative; }
  .pl-toast {
    position: absolute;
    bottom: calc(100% + 6px);
    left: 50%;
    transform: translateX(-50%);
    background: #333;
    color: #fff;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 400;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s;
  }
  .pl-toast.show { opacity: 1; }

  /* Draggable split handle */
  .pl-drag-handle {
    width: 6px;
    cursor: col-resize;
    background: var(--pl-border, #e0e0e0);
    flex-shrink: 0;
    transition: background 0.15s;
  }
  .pl-drag-handle:hover, .pl-drag-handle.dragging {
    background: #3b82f6;
  }
  .pl-playground.vertical > .pl-drag-handle {
    width: auto;
    height: 6px;
    cursor: row-resize;
  }
`;

class PanelLive extends HTMLElement {

  static get observedAttributes() {
    return ['mode', 'theme', 'layout', 'src'];
  }

  constructor() {
    super();
    // NOTE: We intentionally do NOT use Shadow DOM because Bokeh's
    // embed_items() and document.getElementById() search the main DOM tree.
    // Shadow DOM would hide the output containers from Bokeh's renderer.
    this._rendered = false;
    this._running = false;
  }

  connectedCallback() {
    if (!this._rendered) {
      // Defer: connectedCallback fires when the opening tag is parsed,
      // BEFORE the browser has parsed children. We need children to
      // exist so _extractCode() can read the text content.
      requestAnimationFrame(() => {
        this._extractCode();
        this._injectStyles();
        this._render();
        this._rendered = true;
      });
    }
  }

  disconnectedCallback() {
    // Future: terminate worker, cleanup Bokeh docs
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (oldVal === newVal || !this._rendered) return;
    this._render();
  }

  // --- Properties ---

  get mode() { return this.getAttribute('mode') || 'app'; }
  set mode(v) { this.setAttribute('mode', v); }

  get theme() { return this.getAttribute('theme') || 'dark'; }
  set theme(v) { this.setAttribute('theme', v); }

  get layout() { return this.getAttribute('layout') || 'horizontal'; }
  set layout(v) { this.setAttribute('layout', v); }

  // --- Code extraction ---

  _extractCode() {
    // Check for <panel-file> children
    const files = this.querySelectorAll('panel-file');
    if (files.length > 0) {
      this._files = {};
      let entrypoint = null;
      for (const f of files) {
        this._files[f.name] = f.code;
        if (f.entrypoint || !entrypoint) entrypoint = f.name;
      }
      this._entrypoint = entrypoint;
      this._code = this._files[this._entrypoint];
    } else {
      // Direct text content (ignoring child elements)
      // We need to get text that's not inside child elements
      let code = '';
      for (const node of this.childNodes) {
        if (node.nodeType === Node.TEXT_NODE) {
          code += node.textContent;
        }
      }
      this._code = code.trim();
      this._files = null;
    }

    // Check for <panel-example> children
    const examples = this.querySelectorAll('panel-example');
    if (examples.length > 0) {
      this._examples = [];
      for (const ex of examples) {
        this._examples.push({ label: ex.label, code: ex.code.trim() });
      }
      // If no direct text content, use first example as default
      if (!this._code) {
        this._code = this._examples[0].code;
      }
    } else {
      this._examples = null;
    }

    // Check for <panel-requirements>
    const reqEl = this.querySelector('panel-requirements');
    this._requirements = reqEl ? reqEl.packages : null;

    // Check for src attribute
    if (this.hasAttribute('src')) {
      this._srcUrl = this.getAttribute('src');
    }

    // Check URL hash for shared code (overrides inline code in playground mode)
    const hashCode = getCodeFromHash();
    if (hashCode && this.mode === 'playground') {
      this._code = hashCode;
    }
  }

  // --- Styles (injected once into document head) ---

  _injectStyles() {
    if (_stylesInjected) return;
    const style = document.createElement('style');
    style.textContent = PANEL_LIVE_STYLES;
    document.head.appendChild(style);
    _stylesInjected = true;
  }

  // --- Rendering ---

  _render() {
    const mode = this.mode;
    const theme = this.theme;
    const layout = this.layout;

    // Clear previous render (light DOM children that we added)
    while (this.firstChild) this.removeChild(this.firstChild);

    if (mode === 'app') {
      this._renderAppMode(theme);
    } else if (mode === 'editor') {
      this._renderEditorMode(theme);
    } else if (mode === 'playground') {
      this._renderPlaygroundMode(theme, layout);
    }
  }

  _renderAppMode(theme) {
    const container = document.createElement('div');
    container.className = 'pl-container';
    container.innerHTML = `
      <div class="pl-status"><span class="pl-spinner"></span> Initializing...</div>
      <div class="pl-output" id="${uid()}"></div>
    `;
    this.appendChild(container);

    const statusEl = container.querySelector('.pl-status');
    const outputEl = container.querySelector('.pl-output');

    this._initAndRun(outputEl, this._code, msg => { statusEl.textContent = msg; }, statusEl);
  }

  _renderEditorMode(theme) {
    const themeClass = theme === 'light' ? 'light' : 'dark';
    const outputId = uid();
    const container = document.createElement('div');
    container.className = 'pl-container pl-editor-stacked';
    container.innerHTML = `
      <div class="pl-editor-header ${themeClass}">
        <span class="pl-lang">Panel</span>
        <span class="pl-title">Panel Live</span>
        <span class="pl-shortcut">Ctrl+Enter to run</span>
        <button class="pl-btn run-btn">Run</button>
      </div>
      <textarea class="pl-editor-area ${themeClass}" spellcheck="false">${this._escapeHtml(this._code)}</textarea>
      <div class="pl-status"><span class="pl-spinner"></span> Initializing...</div>
      <div class="pl-output" id="${outputId}"></div>
    `;
    this.appendChild(container);

    const textarea = container.querySelector('.pl-editor-area');
    const runBtn = container.querySelector('.run-btn');
    const statusEl = container.querySelector('.pl-status');
    const outputEl = container.querySelector('.pl-output');

    // Tab key support
    textarea.addEventListener('keydown', e => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = textarea.selectionStart;
        textarea.value = textarea.value.substring(0, start) + '    ' + textarea.value.substring(textarea.selectionEnd);
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        this._runFromEditor(textarea, outputEl, statusEl);
      }
    });

    runBtn.addEventListener('click', () => {
      this._runFromEditor(textarea, outputEl, statusEl);
    });

    // Auto-run on load
    this._initAndRun(outputEl, this._code, msg => { statusEl.textContent = msg; }, statusEl);
  }

  _renderPlaygroundMode(theme, layout) {
    const themeClass = theme === 'light' ? 'light' : 'dark';
    const layoutClass = layout === 'vertical' ? 'vertical' : '';
    const outputId = uid();
    const container = document.createElement('div');
    container.className = 'pl-container';

    // Build header buttons
    let examplesHtml = '';
    if (this._examples && this._examples.length > 0) {
      const opts = this._examples.map((ex, i) =>
        `<option value="${i}">${this._escapeHtml(ex.label)}</option>`
      ).join('');
      examplesHtml = `<select class="pl-examples-select"><option value="" disabled selected>Examples...</option>${opts}</select>`;
    }

    container.innerHTML = `
      <div class="pl-playground ${layoutClass}">
        <div class="pl-editor-pane">
          <div class="pl-editor-header ${themeClass}">
            <span class="pl-lang">Panel</span>
            ${examplesHtml}
            <span class="pl-title"></span>
            <button class="pl-btn secondary share-btn">Share<span class="pl-toast">Link copied!</span></button>
            <button class="pl-btn secondary reset-btn">Reset</button>
            <button class="pl-btn run-btn">Run</button>
          </div>
          <textarea class="pl-editor-area ${themeClass}" spellcheck="false">${this._escapeHtml(this._code)}</textarea>
        </div>
        <div class="pl-drag-handle"></div>
        <div class="pl-preview-pane">
          <div class="pl-status"><span class="pl-spinner"></span> Initializing...</div>
          <div class="pl-output" id="${outputId}"></div>
        </div>
      </div>
    `;
    this.appendChild(container);

    const textarea = container.querySelector('.pl-editor-area');
    const runBtn = container.querySelector('.run-btn');
    const resetBtn = container.querySelector('.reset-btn');
    const shareBtn = container.querySelector('.share-btn');
    const examplesSelect = container.querySelector('.pl-examples-select');
    const statusEl = container.querySelector('.pl-status');
    const outputEl = container.querySelector('.pl-output');
    const dragHandle = container.querySelector('.pl-drag-handle');
    const editorPane = container.querySelector('.pl-editor-pane');
    const previewPane = container.querySelector('.pl-preview-pane');

    // Tab key + Ctrl+Enter
    textarea.addEventListener('keydown', e => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = textarea.selectionStart;
        textarea.value = textarea.value.substring(0, start) + '    ' + textarea.value.substring(textarea.selectionEnd);
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        this._runFromEditor(textarea, outputEl, statusEl);
      }
    });

    runBtn.addEventListener('click', () => {
      this._runFromEditor(textarea, outputEl, statusEl);
    });

    resetBtn.addEventListener('click', () => {
      textarea.value = this._code;
    });

    // Share button: encode code in URL hash and copy to clipboard
    shareBtn.addEventListener('click', () => {
      setCodeInHash(textarea.value);
      const url = location.href;
      navigator.clipboard.writeText(url).then(() => {
        const toast = shareBtn.querySelector('.pl-toast');
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 1500);
      });
    });

    // Examples dropdown
    if (examplesSelect) {
      examplesSelect.addEventListener('change', () => {
        const idx = parseInt(examplesSelect.value, 10);
        const example = this._examples[idx];
        if (example) {
          textarea.value = example.code;
          this._runFromEditor(textarea, outputEl, statusEl);
        }
        examplesSelect.selectedIndex = 0; // reset to "Examples..."
      });
    }

    // Draggable split handle
    this._initDragHandle(dragHandle, editorPane, previewPane, layout);

    // Auto-run on load
    this._initAndRun(outputEl, this._code, msg => { statusEl.textContent = msg; }, statusEl);
  }

  _initDragHandle(handle, editorPane, previewPane, layout) {
    const isVertical = layout === 'vertical';
    let dragging = false;
    let startPos = 0;
    let startEditorSize = 0;
    let totalSize = 0;

    const onMouseDown = (e) => {
      e.preventDefault();
      dragging = true;
      handle.classList.add('dragging');
      const playground = handle.parentElement;
      if (isVertical) {
        startPos = e.clientY;
        startEditorSize = editorPane.offsetHeight;
        totalSize = playground.offsetHeight;
      } else {
        startPos = e.clientX;
        startEditorSize = editorPane.offsetWidth;
        totalSize = playground.offsetWidth;
      }
      // Remove flex:1 and set explicit sizes
      editorPane.style.flex = 'none';
      previewPane.style.flex = 'none';
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    };

    const onMouseMove = (e) => {
      if (!dragging) return;
      const delta = isVertical ? e.clientY - startPos : e.clientX - startPos;
      const handleSize = isVertical ? handle.offsetHeight : handle.offsetWidth;
      const newEditorSize = Math.max(100, Math.min(totalSize - handleSize - 100, startEditorSize + delta));
      const newPreviewSize = totalSize - handleSize - newEditorSize;
      if (isVertical) {
        editorPane.style.height = newEditorSize + 'px';
        previewPane.style.height = newPreviewSize + 'px';
      } else {
        editorPane.style.width = newEditorSize + 'px';
        previewPane.style.width = newPreviewSize + 'px';
      }
    };

    const onMouseUp = () => {
      dragging = false;
      handle.classList.remove('dragging');
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    handle.addEventListener('mousedown', onMouseDown);
  }

  // --- Execution ---

  async _initAndRun(outputEl, code, statusCallback, statusEl) {
    // Enqueue to serialize: Pyodide global state (state.curdoc) can't handle concurrent runs
    return enqueueExecution(async () => {
      try {
        // Fetch src if needed
        if (this._srcUrl && !this._code.trim()) {
          statusCallback('Fetching source...');
          const resp = await fetch(this._srcUrl);
          if (!resp.ok) throw new Error(`Failed to fetch ${this._srcUrl}: ${resp.status}`);
          code = await resp.text();
          this._code = code;
          // Update textarea if in editor/playground mode
          const textarea = this.querySelector('.pl-editor-area');
          if (textarea) textarea.value = code;
        }

        await initPyodide(statusCallback);

        // Install explicit requirements if any
        if (this._requirements) {
          await installExplicitRequirements(this._requirements, statusCallback);
        }

        // Write multi-file support
        if (this._files) {
          for (const [name, content] of Object.entries(this._files)) {
            if (name !== this._entrypoint) {
              _pyodide.globals.set('__file_name__', name);
              _pyodide.globals.set('__file_content__', content);
              await _pyodide.runPythonAsync(
                'import pathlib\n' +
                'pathlib.Path(__file_name__).write_text(__file_content__)\n'
              );
            }
          }
        }

        statusCallback('Running app...');
        await runPanelCode(outputEl, code, statusCallback);
        if (statusEl) statusEl.classList.add('hidden');
      } catch (error) {
        outputEl.innerHTML = '<pre style="color:#b71c1c;background:#ffebee;padding:16px;border-radius:4px;white-space:pre-wrap;font-size:13px;margin:0;">' +
          (error.message || String(error)).replace(/</g, '&lt;') + '</pre>';
        if (statusEl) statusEl.classList.add('hidden');
      }
    });
  }

  async _runFromEditor(textarea, outputEl, statusEl) {
    if (this._running) return;
    this._running = true;
    statusEl.classList.remove('hidden');
    statusEl.innerHTML = '<span class="pl-spinner"></span> Running...';
    const code = textarea.value;
    try {
      await runPanelCode(outputEl, code, msg => { statusEl.textContent = msg; });
      statusEl.classList.add('hidden');
    } catch (error) {
      outputEl.innerHTML = '<pre style="color:#b71c1c;background:#ffebee;padding:16px;border-radius:4px;white-space:pre-wrap;font-size:13px;margin:0;">' +
        (error.message || String(error)).replace(/</g, '&lt;') + '</pre>';
      statusEl.classList.add('hidden');
    }
    this._running = false;
  }

  _escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}

customElements.define('panel-live', PanelLive);

// ============================================================
// Public API: PanelLive.configure() and PanelLive.mount()
// ============================================================

window.PanelLive = {
  configure(overrides) {
    Object.assign(PANEL_LIVE_CONFIG, overrides);
  },

  async mount(options, target) {
    const el = document.createElement('panel-live');
    if (options.mode) el.setAttribute('mode', options.mode);
    if (options.theme) el.setAttribute('theme', options.theme);
    if (options.layout) el.setAttribute('layout', options.layout);

    if (options.files) {
      for (const [name, content] of Object.entries(options.files)) {
        const fileEl = document.createElement('panel-file');
        fileEl.setAttribute('name', name);
        if (name === (options.entrypoint || Object.keys(options.files)[0])) {
          fileEl.setAttribute('entrypoint', '');
        }
        fileEl.textContent = content;
        el.appendChild(fileEl);
      }
    } else if (options.code) {
      el.textContent = options.code;
    }

    if (options.requirements) {
      const reqEl = document.createElement('panel-requirements');
      reqEl.textContent = options.requirements.join('\n');
      el.appendChild(reqEl);
    }

    if (typeof target === 'string') target = document.getElementById(target);
    target.appendChild(el);
    return el;
  },

  async init() {
    return initPyodide(msg => console.log('[PanelLive]', msg));
  }
};
