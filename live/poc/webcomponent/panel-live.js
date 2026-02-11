/**
 * panel-live.js — Web Component for Panel Live
 *
 * Defines <panel-live>, <panel-file>, <panel-requirements>, and <panel-example>
 * custom elements plus the PanelLive imperative JS API.
 *
 * See docs/api-design.md for the full API specification.
 *
 * Usage:
 *   <script src="panel-live.js"></script>
 *   <panel-live>
 *     import panel as pn
 *     pn.panel("Hello").servable()
 *   </panel-live>
 *
 *   <panel-live mode="editor" theme="dark">
 *     import panel as pn
 *     pn.widgets.FloatSlider(name="X").servable()
 *   </panel-live>
 *
 *   <panel-live mode="playground" layout="horizontal" theme="auto">
 *     ...
 *   </panel-live>
 */

console.log('[panel-live] panel-live.js loaded');

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
// Configuration (merged: built-in defaults < window global < configure())
// ============================================================

const _defaults = {
  pyodideVersion: 'v0.28.2',
  panelVersion: '1.8.7',
  bokehVersion: '3.8.2',
  pyodideCdn: 'https://cdn.jsdelivr.net/pyodide/',
  panelCdn: 'https://cdn.holoviz.org/panel/',
  bokehCdn: 'https://cdn.bokeh.org/bokeh/release/',
};

const _config = Object.assign(
  {},
  _defaults,
  typeof window !== 'undefined' && window.PANEL_LIVE_CONFIG ? window.PANEL_LIVE_CONFIG : {}
);

function cdnUrls() {
  const { pyodideVersion, panelVersion, bokehVersion, pyodideCdn, panelCdn, bokehCdn } = _config;
  return {
    pyodide: `${pyodideCdn}${pyodideVersion}/full/pyodide.js`,
    bokehJs: [
      `${bokehCdn}bokeh-${bokehVersion}.js`,
      `${bokehCdn}bokeh-widgets-${bokehVersion}.min.js`,
      `${bokehCdn}bokeh-tables-${bokehVersion}.min.js`,
    ],
    panelJs: `https://cdn.jsdelivr.net/npm/@holoviz/panel@${panelVersion}/dist/panel.min.js`,
    bokehWhl: `${panelCdn}${panelVersion}/dist/wheels/bokeh-${bokehVersion}-py3-none-any.whl`,
    panelWhl: `${panelCdn}${panelVersion}/dist/wheels/panel-${panelVersion}-py3-none-any.whl`,
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

// ============================================================
// CodeMirror (line numbers + Python syntax highlighting)
// ============================================================

let _cmLoaded = false;
let _cmLoadPromise = null;
const CM_VERSION = '5.65.18';
const CM_CDN = `https://cdnjs.cloudflare.com/ajax/libs/codemirror/${CM_VERSION}`;

function loadCodeMirror() {
  if (_cmLoadPromise) return _cmLoadPromise;
  _cmLoadPromise = (async () => {
    if (_cmLoaded) return;
    loadCSS(CM_CDN + '/codemirror.min.css');
    loadCSS(CM_CDN + '/theme/dracula.min.css');
    await loadScript(CM_CDN + '/codemirror.min.js');
    await loadScript(CM_CDN + '/mode/python/python.min.js');
    await loadScript(CM_CDN + '/addon/edit/matchbrackets.min.js');
    await loadScript(CM_CDN + '/addon/edit/closebrackets.min.js');
    await loadScript(CM_CDN + '/addon/selection/active-line.min.js');
    await loadScript(CM_CDN + '/addon/comment/comment.min.js');
    _cmLoaded = true;
    console.log('[panel-live] CodeMirror loaded');
  })();
  return _cmLoadPromise;
}

function createCMEditor(textarea, resolvedTheme, onRun) {
  const cmTheme = resolvedTheme === 'light' ? 'default' : 'dracula';
  const cm = CodeMirror.fromTextArea(textarea, {
    mode: 'python',
    theme: cmTheme,
    lineNumbers: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    styleActiveLine: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    lineWrapping: false,
    extraKeys: {
      'Ctrl-Enter': () => { if (onRun) onRun(); },
      'Cmd-Enter': () => { if (onRun) onRun(); },
      'Ctrl-/': 'toggleComment',
      'Cmd-/': 'toggleComment',
      'Tab': (cm) => {
        if (cm.somethingSelected()) {
          cm.indentSelection('add');
        } else {
          cm.replaceSelection('    ', 'end');
        }
      },
      'Shift-Tab': (cm) => { cm.indentSelection('subtract'); },
    }
  });
  setTimeout(() => cm.refresh(), 50);
  return cm;
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
    const branch = hasServable && !hasServableTarget ? 'servable' : hasServableTarget ? 'servable(target=)' : 'expression';
    console.log('[panel-live] Executing code via %s branch (target=%s)', branch, targetId);

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
    console.error('[panel-live] runPanelCode error:', error);
    targetEl.innerHTML = '<pre style="color:var(--pl-error-color,#b71c1c);background:var(--pl-error-bg,#ffebee);padding:16px;border-radius:4px;white-space:pre-wrap;font-size:13px;margin:0;">' +
      (error.message || String(error)).replace(/</g, '&lt;') + '</pre>';
    throw error; // re-throw so callers can handle
  }
}

// ============================================================
// Utility: unique IDs
// ============================================================

let _idCounter = 0;
function uid() { return 'pl-' + (++_idCounter); }

// ============================================================
// Theme resolution
// ============================================================

const _darkMQ = window.matchMedia('(prefers-color-scheme: dark)');

function resolveTheme(themeAttr) {
  if (themeAttr === 'light' || themeAttr === 'dark') return themeAttr;
  // "auto" or missing — detect from system
  return _darkMQ.matches ? 'dark' : 'light';
}

// ============================================================
// <panel-file>, <panel-requirements>, <panel-example>
// ============================================================

class PanelFile extends HTMLElement {
  get name() { return this.getAttribute('name') || 'app.py'; }
  get entrypoint() { return this.hasAttribute('entrypoint'); }
  get src() { return this.getAttribute('src') || null; }
  get code() { return this.textContent; }

  /** Fetch content from src if set, otherwise return inline text */
  async resolveCode() {
    if (this.src) {
      const resp = await fetch(this.src);
      if (!resp.ok) throw new Error(`Failed to fetch ${this.src}: ${resp.status}`);
      return await resp.text();
    }
    return this.textContent;
  }
}

class PanelRequirements extends HTMLElement {
  get packages() { return this.textContent; }
}

class PanelExample extends HTMLElement {
  get label() { return this.getAttribute('name') || 'Example'; }
  get src() { return this.getAttribute('src') || null; }
  get code() { return this.textContent; }

  /** Fetch content from src if set, otherwise return inline text */
  async resolveCode() {
    if (this.src) {
      const resp = await fetch(this.src);
      if (!resp.ok) throw new Error(`Failed to fetch ${this.src}: ${resp.status}`);
      return await resp.text();
    }
    return this.textContent.trim();
  }
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

class PanelLive extends HTMLElement {

  static get observedAttributes() {
    return ['mode', 'theme', 'layout', 'src', 'height', 'auto-run', 'label', 'code-visibility', 'code-position'];
  }

  constructor() {
    super();
    // NOTE: We intentionally do NOT use Shadow DOM because Bokeh's
    // embed_items() and document.getElementById() search the main DOM tree.
    // Shadow DOM would hide the output containers from Bokeh's renderer.
    this._rendered = false;
    this._running = false;
    this._status = 'idle';
    this._cm = null;
    this._textarea = null;
    this._outputEl = null;
    this._statusEl = null;
    this._resolvedTheme = null;
    this._themeListener = null;
  }

  connectedCallback() {
    if (!this._rendered) {
      console.log('[panel-live] <panel-live> connected, mode=%s theme=%s', this.mode, this.theme);
      // Resolve theme immediately and set data attribute for CSS
      this._setupTheme();
      // Defer render: connectedCallback fires when the opening tag is parsed,
      // BEFORE the browser has parsed children. We need children to
      // exist so _extractCode() can read the text content.
      requestAnimationFrame(async () => {
        await this._extractCode();
        this._hideSourceNodes();
        this._render();
        this._rendered = true;
      });
    }
  }

  disconnectedCallback() {
    // Remove theme media query listener
    if (this._themeListener) {
      _darkMQ.removeEventListener('change', this._themeListener);
      this._themeListener = null;
    }
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (oldVal === newVal || !this._rendered) return;
    if (name === 'theme') {
      this._setupTheme();
    }
    this._render();
  }

  // --- Properties (matching API spec attributes) ---

  get mode() { return this.getAttribute('mode') || 'app'; }
  set mode(v) { this.setAttribute('mode', v); }

  get theme() { return this.getAttribute('theme') || 'auto'; }
  set theme(v) { this.setAttribute('theme', v); }

  get layout() {
    const v = this.getAttribute('layout');
    if (v) return v;
    return this.mode === 'editor' ? 'vertical' : 'horizontal';
  }
  set layout(v) { this.setAttribute('layout', v); }

  get label() { return this.getAttribute('label') || 'Python'; }
  set label(v) { this.setAttribute('label', v); }

  get codeVisibility() { return this.getAttribute('code-visibility') || 'visible'; }
  set codeVisibility(v) { this.setAttribute('code-visibility', v); }

  get codePosition() { return this.getAttribute('code-position') || 'first'; }
  set codePosition(v) { this.setAttribute('code-position', v); }

  get autoRun() { return !this.hasAttribute('auto-run') || this.getAttribute('auto-run') !== 'false'; }
  set autoRun(v) { this.setAttribute('auto-run', v ? 'true' : 'false'); }

  get status() { return this._status; }

  // --- Theme resolution ---

  _setupTheme() {
    // Remove old listener
    if (this._themeListener) {
      _darkMQ.removeEventListener('change', this._themeListener);
      this._themeListener = null;
    }
    this._resolvedTheme = resolveTheme(this.theme);
    this.setAttribute('data-resolved-theme', this._resolvedTheme);

    // If auto, listen for system theme changes
    if (this.theme === 'auto') {
      this._themeListener = (e) => {
        this._resolvedTheme = e.matches ? 'dark' : 'light';
        this.setAttribute('data-resolved-theme', this._resolvedTheme);
      };
      _darkMQ.addEventListener('change', this._themeListener);
    }
  }

  // --- Event helpers ---

  _emit(name, detail) {
    this.dispatchEvent(new CustomEvent(name, { detail, bubbles: true, composed: true }));
  }

  _setStatus(status, message) {
    this._status = status;
    this._emit('pl-status', { status, message });
  }

  // --- Hide source text nodes (after extraction) ---

  _hideSourceNodes() {
    // Clear raw text nodes so they don't render visibly in Light DOM.
    // Child custom elements (<panel-example> etc.) are hidden via CSS.
    for (const node of Array.from(this.childNodes)) {
      if (node.nodeType === Node.TEXT_NODE) {
        node.textContent = '';
      }
    }
  }

  // --- Code extraction ---

  async _extractCode() {
    // Check for <panel-file> children
    const files = this.querySelectorAll('panel-file');
    if (files.length > 0) {
      this._files = {};
      let entrypoint = null;
      for (const f of files) {
        this._files[f.name] = await f.resolveCode();
        if (f.entrypoint || !entrypoint) entrypoint = f.name;
      }
      this._entrypoint = entrypoint;
      this._code = this._files[this._entrypoint];
    } else {
      // Direct text content (ignoring child elements)
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
        this._examples.push({ label: ex.label, code: await ex.resolveCode() });
      }
      // If no direct text content, use first example as default
      if (!this._code) {
        this._code = this._examples[0].code;
      }
    } else {
      this._examples = null;
    }

    // Check for examples-src attribute (JSON URL)
    const examplesSrc = this.getAttribute('examples-src');
    if (examplesSrc && !this._examples) {
      try {
        const resp = await fetch(examplesSrc);
        if (resp.ok) {
          const data = await resp.json();
          this._examples = Array.isArray(data) ? data : [];
          if (!this._code && this._examples.length > 0) {
            this._code = this._examples[0].code || '';
          }
        }
      } catch (e) {
        console.warn('[panel-live] Failed to load examples from', examplesSrc, e);
      }
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

    console.log('[panel-live] Code extracted (%d chars), files=%s, src=%s',
      (this._code || '').length,
      this._files ? Object.keys(this._files).join(', ') : 'none',
      this._srcUrl || 'none');
  }


  // --- Rendering ---

  _render() {
    const mode = this.mode;
    const layout = this.layout;
    const rt = this._resolvedTheme || resolveTheme(this.theme);

    // Clear previous render (light DOM children that we added)
    // Preserve original source children by checking for our container
    const container = this.querySelector('.pl-container');
    if (container) container.remove();

    if (mode === 'app') {
      this._renderAppMode(rt);
    } else if (mode === 'editor') {
      this._renderEditorMode(rt, layout);
    } else if (mode === 'playground') {
      this._renderPlaygroundMode(rt, layout);
    }
  }

  _renderAppMode(rt) {
    const container = document.createElement('div');
    container.className = 'pl-container';
    const h = this.getAttribute('height');
    if (h) container.style.height = h;

    container.innerHTML = `
      <div class="pl-status"><span class="pl-spinner"></span> Initializing...</div>
      <div class="pl-output" id="${uid()}"></div>
    `;
    this.appendChild(container);

    const statusEl = container.querySelector('.pl-status');
    const outputEl = container.querySelector('.pl-output');
    this._outputEl = outputEl;
    this._statusEl = statusEl;

    if (this.autoRun) {
      this._initAndRun(outputEl, this._code, msg => { statusEl.textContent = msg; }, statusEl);
    } else {
      statusEl.textContent = 'Ready (auto-run disabled)';
    }
  }

  _renderEditorMode(rt, layout) {
    if (layout === 'horizontal') {
      return this._renderEditorHorizontal(rt);
    }
    const outputId = uid();
    const pillLabel = this.label;
    const codeVis = this.codeVisibility;
    const container = document.createElement('div');
    container.className = 'pl-container pl-editor-stacked' + (this.codePosition === 'last' ? ' code-last' : '');
    const h = this.getAttribute('height');
    if (h) container.style.height = h;

    // Build code section (header + textarea)
    let codeHtml = `
      <div class="pl-editor-header">
        <span class="pl-lang">${this._escapeHtml(pillLabel)}</span>
        <span class="pl-title"></span>
        <span class="pl-shortcut">Ctrl+Enter to run</span>
        <button class="pl-btn run-btn">Run</button>
      </div>
      <textarea class="pl-editor-area" spellcheck="false">${this._escapeHtml(this._code)}</textarea>
    `;

    if (codeVis === 'hidden') {
      // No editor, no toggle — output only (but textarea is kept for getCode/setCode)
      container.innerHTML = `
        <textarea class="pl-editor-area" style="display:none" spellcheck="false">${this._escapeHtml(this._code)}</textarea>
        <div class="pl-status"><span class="pl-spinner"></span> Initializing...</div>
        <div class="pl-output" id="${outputId}"></div>
      `;
    } else if (codeVis === 'collapsed') {
      container.innerHTML = `
        <div class="pl-code-section pl-collapsed">
          ${codeHtml}
        </div>
        <div class="pl-code-toggle"><button>&lt;&gt; Code</button></div>
        <div class="pl-status"><span class="pl-spinner"></span> Initializing...</div>
        <div class="pl-output" id="${outputId}"></div>
      `;
    } else {
      container.innerHTML = `
        ${codeHtml}
        <div class="pl-status"><span class="pl-spinner"></span> Initializing...</div>
        <div class="pl-output" id="${outputId}"></div>
      `;
    }

    this.appendChild(container);

    const textarea = container.querySelector('.pl-editor-area');
    const runBtn = container.querySelector('.run-btn');
    const statusEl = container.querySelector('.pl-status');
    const outputEl = container.querySelector('.pl-output');
    this._textarea = textarea;
    this._outputEl = outputEl;
    this._statusEl = statusEl;

    // Wire code toggle
    const toggleBtn = container.querySelector('.pl-code-toggle button');
    if (toggleBtn) {
      const codeSection = container.querySelector('.pl-code-section');
      toggleBtn.addEventListener('click', () => {
        const isCollapsed = codeSection.classList.contains('pl-collapsed');
        if (isCollapsed) {
          codeSection.classList.remove('pl-collapsed');
          codeSection.classList.add('pl-expanded');
          if (this._cm) setTimeout(() => this._cm.refresh(), 50);
        } else {
          codeSection.classList.remove('pl-expanded');
          codeSection.classList.add('pl-collapsed');
        }
      });
    }

    // Replace textarea with CodeMirror (skip for hidden — no visible editor)
    if (codeVis !== 'hidden') {
      loadCodeMirror().then(() => {
        this._cm = createCMEditor(textarea, rt, () => {
          this._runFromEditor(textarea, outputEl, statusEl);
        });
        textarea.classList.add('pl-cm-active');
      });
    }

    if (runBtn) {
      runBtn.addEventListener('click', () => {
        this._runFromEditor(textarea, outputEl, statusEl);
      });
    }

    // Auto-run on load
    if (this.autoRun) {
      this._initAndRun(outputEl, this._code, msg => { statusEl.textContent = msg; }, statusEl);
    } else {
      statusEl.textContent = 'Ready (auto-run disabled)';
    }
  }

  _renderEditorHorizontal(rt) {
    const outputId = uid();
    const pillLabel = this.label;
    const codeVis = this.codeVisibility;
    const codePosClass = this.codePosition === 'last' ? ' code-last' : '';
    const container = document.createElement('div');
    container.className = 'pl-container pl-resizable';
    const h = this.getAttribute('height');
    if (h) { container.style.height = h; container.style.minHeight = h; }

    if (codeVis === 'hidden') {
      // No editor, just output
      container.innerHTML = `
        <textarea class="pl-editor-area" style="display:none">${this._escapeHtml(this._code)}</textarea>
        <div class="pl-status"><span class="pl-spinner"></span> Initializing...</div>
        <div class="pl-output" id="${outputId}"></div>
      `;
      this.appendChild(container);

      const statusEl = container.querySelector('.pl-status');
      const outputEl = container.querySelector('.pl-output');
      this._textarea = container.querySelector('.pl-editor-area');
      this._outputEl = outputEl;
      this._statusEl = statusEl;

      if (this.autoRun) {
        this._initAndRun(outputEl, this._code, msg => { statusEl.textContent = msg; }, statusEl);
      } else {
        statusEl.textContent = 'Ready (auto-run disabled)';
      }
      return;
    }

    // Build editor pane content based on code-visibility
    let editorContent;
    if (codeVis === 'collapsed') {
      editorContent = `
        <div class="pl-code-section pl-collapsed">
          <div class="pl-editor-header">
            <span class="pl-lang">${this._escapeHtml(pillLabel)}</span>
            <span class="pl-title"></span>
            <span class="pl-shortcut">Ctrl+Enter to run</span>
            <button class="pl-btn run-btn">Run</button>
          </div>
          <textarea class="pl-editor-area" spellcheck="false">${this._escapeHtml(this._code)}</textarea>
        </div>
        <div class="pl-code-toggle"><button>&lt;&gt; Code</button></div>
      `;
    } else {
      editorContent = `
        <div class="pl-editor-header">
          <span class="pl-lang">${this._escapeHtml(pillLabel)}</span>
          <span class="pl-title"></span>
          <span class="pl-shortcut">Ctrl+Enter to run</span>
          <button class="pl-btn run-btn">Run</button>
        </div>
        <textarea class="pl-editor-area" spellcheck="false">${this._escapeHtml(this._code)}</textarea>
      `;
    }

    container.innerHTML = `
      <div class="pl-playground${codePosClass}">
        <div class="pl-editor-pane${codeVis === 'collapsed' ? ' pl-pane-collapsed' : ''}">
          ${editorContent}
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
    const statusEl = container.querySelector('.pl-status');
    const outputEl = container.querySelector('.pl-output');
    const dragHandle = container.querySelector('.pl-drag-handle');
    const editorPane = container.querySelector('.pl-editor-pane');
    const previewPane = container.querySelector('.pl-preview-pane');
    this._textarea = textarea;
    this._outputEl = outputEl;
    this._statusEl = statusEl;

    // Wire code toggle
    const toggleBtn = container.querySelector('.pl-code-toggle button');
    if (toggleBtn) {
      const codeSection = container.querySelector('.pl-code-section');
      toggleBtn.addEventListener('click', () => {
        const isCollapsed = codeSection.classList.contains('pl-collapsed');
        if (isCollapsed) {
          codeSection.classList.remove('pl-collapsed');
          codeSection.classList.add('pl-expanded');
          editorPane.classList.remove('pl-pane-collapsed');
          if (this._cm) setTimeout(() => this._cm.refresh(), 50);
        } else {
          codeSection.classList.remove('pl-expanded');
          codeSection.classList.add('pl-collapsed');
          editorPane.classList.add('pl-pane-collapsed');
        }
      });
    }

    // Replace textarea with CodeMirror
    loadCodeMirror().then(() => {
      this._cm = createCMEditor(textarea, rt, () => {
        this._runFromEditor(textarea, outputEl, statusEl);
      });
      textarea.classList.add('pl-cm-active');
    });

    if (runBtn) {
      runBtn.addEventListener('click', () => {
        this._runFromEditor(textarea, outputEl, statusEl);
      });
    }

    // Draggable split handle
    this._initDragHandle(dragHandle, editorPane, previewPane, 'horizontal');

    // Auto-run on load
    if (this.autoRun) {
      this._initAndRun(outputEl, this._code, msg => { statusEl.textContent = msg; }, statusEl);
    } else {
      statusEl.textContent = 'Ready (auto-run disabled)';
    }
  }

  _renderPlaygroundMode(rt, layout) {
    const layoutClass = layout === 'vertical' ? 'vertical' : '';
    const codePosClass = this.codePosition === 'last' ? ' code-last' : '';
    const outputId = uid();
    const pillLabel = this.label;
    const container = document.createElement('div');
    container.className = 'pl-container pl-resizable';
    const h = this.getAttribute('height');
    if (h) { container.style.height = h; container.style.minHeight = h; }

    // Build header buttons
    let examplesHtml = '';
    if (this._examples && this._examples.length > 0) {
      const opts = this._examples.map((ex, i) =>
        `<option value="${i}">${this._escapeHtml(ex.label)}</option>`
      ).join('');
      examplesHtml = `<select class="pl-examples-select"><option value="" disabled selected>Examples...</option>${opts}</select>`;
    }

    container.innerHTML = `
      <div class="pl-playground ${layoutClass}${codePosClass}">
        <div class="pl-editor-pane">
          <div class="pl-editor-header">
            <span class="pl-lang">${this._escapeHtml(pillLabel)}</span>
            ${examplesHtml}
            <span class="pl-title"></span>
            <button class="pl-btn secondary share-btn">Share<span class="pl-toast">Link copied!</span></button>
            <button class="pl-btn secondary reset-btn">Reset</button>
            <button class="pl-btn secondary maximize-btn" title="Toggle fullscreen">&#x26F6;</button>
            <button class="pl-btn run-btn">Run</button>
          </div>
          <textarea class="pl-editor-area" spellcheck="false">${this._escapeHtml(this._code)}</textarea>
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
    this._textarea = textarea;
    this._outputEl = outputEl;
    this._statusEl = statusEl;

    // Replace textarea with CodeMirror
    loadCodeMirror().then(() => {
      this._cm = createCMEditor(textarea, rt, () => {
        this._runFromEditor(textarea, outputEl, statusEl);
      });
      textarea.classList.add('pl-cm-active');
    });

    runBtn.addEventListener('click', () => {
      this._runFromEditor(textarea, outputEl, statusEl);
    });

    resetBtn.addEventListener('click', () => {
      if (this._cm) {
        this._cm.setValue(this._code);
      } else {
        textarea.value = this._code;
      }
    });

    // Share button: encode code in URL hash and copy to clipboard
    shareBtn.addEventListener('click', () => {
      const code = this._cm ? this._cm.getValue() : textarea.value;
      setCodeInHash(code);
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
          if (this._cm) {
            this._cm.setValue(example.code);
          } else {
            textarea.value = example.code;
          }
          this._runFromEditor(textarea, outputEl, statusEl);
        }
        examplesSelect.selectedIndex = 0; // reset to "Examples..."
      });
    }

    // Maximize (fullscreen toggle)
    const maximizeBtn = container.querySelector('.maximize-btn');
    maximizeBtn.addEventListener('click', () => {
      if (this.hasAttribute('fullscreen')) {
        this.removeAttribute('fullscreen');
      } else {
        this.setAttribute('fullscreen', '');
      }
      if (this._cm) setTimeout(() => this._cm.refresh(), 50);
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && this.hasAttribute('fullscreen')) {
        this.removeAttribute('fullscreen');
        if (this._cm) setTimeout(() => this._cm.refresh(), 50);
      }
    });

    // Draggable split handle
    this._initDragHandle(dragHandle, editorPane, previewPane, layout);

    // Auto-run on load
    if (this.autoRun) {
      this._initAndRun(outputEl, this._code, msg => { statusEl.textContent = msg; }, statusEl);
    } else {
      statusEl.textContent = 'Ready (auto-run disabled)';
    }
  }

  _initDragHandle(handle, editorPane, previewPane, layout) {
    const isVertical = layout === 'vertical';
    const isReversed = handle.parentElement.classList.contains('code-last');
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
      editorPane.style.flex = 'none';
      previewPane.style.flex = 'none';
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    };

    const onMouseMove = (e) => {
      if (!dragging) return;
      let delta = isVertical ? e.clientY - startPos : e.clientX - startPos;
      if (isReversed) delta = -delta;
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
    return enqueueExecution(async () => {
      try {
        this._setStatus('loading', 'Initializing...');

        // Fetch src if needed
        if (this._srcUrl && !this._code.trim()) {
          console.log('[panel-live] Fetching source from %s', this._srcUrl);
          statusCallback('Fetching source...');
          const resp = await fetch(this._srcUrl);
          if (!resp.ok) throw new Error(`Failed to fetch ${this._srcUrl}: ${resp.status}`);
          code = await resp.text();
          this._code = code;
          if (this._cm) {
            this._cm.setValue(code);
          } else {
            const textarea = this.querySelector('.pl-editor-area');
            if (textarea) textarea.value = code;
          }
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

        console.log('[panel-live] Running app (mode=%s, %d chars)', this.mode, (code || '').length);
        this._setStatus('running', 'Running app...');
        this._emit('pl-run-start');
        statusCallback('Running app...');
        await runPanelCode(outputEl, code, statusCallback);
        console.log('[panel-live] App rendered successfully (mode=%s)', this.mode);
        if (statusEl) statusEl.classList.add('hidden');
        this._setStatus('ready', 'App rendered');
        this._emit('pl-ready');
        this._emit('pl-run-end');
      } catch (error) {
        console.error('[panel-live] Error in _initAndRun:', error);
        outputEl.innerHTML = '<pre style="color:var(--pl-error-color,#b71c1c);background:var(--pl-error-bg,#ffebee);padding:16px;border-radius:4px;white-space:pre-wrap;font-size:13px;margin:0;">' +
          (error.message || String(error)).replace(/</g, '&lt;') + '</pre>';
        if (statusEl) statusEl.classList.add('hidden');
        this._setStatus('error', error.message || String(error));
        this._emit('pl-error', { error: error.message || String(error), traceback: String(error) });
        this._emit('pl-run-end');
      }
    });
  }

  async _runFromEditor(textarea, outputEl, statusEl) {
    if (this._running) return;
    this._running = true;
    statusEl.classList.remove('hidden');
    statusEl.innerHTML = '<span class="pl-spinner"></span> Running...';
    const code = this._cm ? this._cm.getValue() : textarea.value;
    console.log('[panel-live] Run from editor (%d chars)', code.length);
    this._setStatus('running', 'Running...');
    this._emit('pl-run-start');
    try {
      await runPanelCode(outputEl, code, msg => { statusEl.textContent = msg; });
      console.log('[panel-live] Editor run completed');
      statusEl.classList.add('hidden');
      this._setStatus('ready', 'Run completed');
      this._emit('pl-ready');
    } catch (error) {
      console.error('[panel-live] Error in editor run:', error);
      outputEl.innerHTML = '<pre style="color:var(--pl-error-color,#b71c1c);background:var(--pl-error-bg,#ffebee);padding:16px;border-radius:4px;white-space:pre-wrap;font-size:13px;margin:0;">' +
        (error.message || String(error)).replace(/</g, '&lt;') + '</pre>';
      statusEl.classList.add('hidden');
      this._setStatus('error', error.message || String(error));
      this._emit('pl-error', { error: error.message || String(error), traceback: String(error) });
    }
    this._emit('pl-run-end');
    this._running = false;
  }

  // --- Public methods (used by PanelLiveController) ---

  run() {
    if (this._outputEl && this._statusEl) {
      const textarea = this._textarea || this.querySelector('.pl-editor-area');
      if (textarea) {
        this._runFromEditor(textarea, this._outputEl, this._statusEl);
      }
    }
  }

  getCode() {
    if (this._cm) return this._cm.getValue();
    if (this._textarea) return this._textarea.value;
    return this._code || '';
  }

  setCode(code) {
    if (this._cm) {
      this._cm.setValue(code);
    } else if (this._textarea) {
      this._textarea.value = code;
    }
  }

  _escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}

customElements.define('panel-live', PanelLive);
console.log('[panel-live] <panel-live> custom element registered');

// ============================================================
// PanelLiveController (returned by PanelLive.mount())
// ============================================================

class PanelLiveController {
  constructor(element) {
    this._element = element;
  }

  /** The underlying <panel-live> DOM element */
  get element() { return this._element; }

  /** Execute current code (editor/playground) */
  run() { this._element.run(); }

  /** Get current code string */
  getCode() { return this._element.getCode(); }

  /** Set code (updates editor) */
  setCode(code) { this._element.setCode(code); }

  /** Current status: 'idle' | 'loading' | 'running' | 'ready' | 'error' */
  get status() { return this._element.status; }

  /** Remove element and cleanup */
  destroy() {
    this._element.remove();
    this._element = null;
  }
}

// ============================================================
// Public API: window.PanelLive
// ============================================================

window.PanelLive = {
  /**
   * Set global configuration defaults. Must be called before first
   * init()/mount() or <panel-live> connectedCallback.
   */
  configure(overrides) {
    Object.assign(_config, overrides);
  },

  /**
   * Pre-warm Pyodide singleton. Idempotent (returns same promise on repeat calls).
   * @param {Object} [options]
   * @param {Function} [options.onStatus] - Status callback
   * @returns {Promise<void>}
   */
  async init(options) {
    const onStatus = (options && options.onStatus) || (msg => console.log('[PanelLive]', msg));
    await initPyodide(onStatus);
  },

  /**
   * Programmatic creation. Returns a controller for runtime interaction.
   * @param {Object} options
   * @param {string|HTMLElement} target - CSS selector or DOM element
   * @returns {Promise<PanelLiveController>}
   */
  async mount(options, target) {
    const el = document.createElement('panel-live');
    if (options.mode) el.setAttribute('mode', options.mode);
    if (options.theme) el.setAttribute('theme', options.theme);
    if (options.layout) el.setAttribute('layout', options.layout);
    if (options.height) el.setAttribute('height', options.height);
    if (options.label) el.setAttribute('label', options.label);
    if (options.codeVisibility) el.setAttribute('code-visibility', options.codeVisibility);
    if (options.fullscreen) el.setAttribute('fullscreen', '');
    if (options.autoRun === false) el.setAttribute('auto-run', 'false');

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
      reqEl.textContent = Array.isArray(options.requirements)
        ? options.requirements.join('\n')
        : options.requirements;
      el.appendChild(reqEl);
    }

    if (options.examples) {
      for (const ex of options.examples) {
        const exEl = document.createElement('panel-example');
        exEl.setAttribute('name', ex.name || 'Example');
        if (ex.src) {
          exEl.setAttribute('src', ex.src);
        } else if (ex.code) {
          exEl.textContent = ex.code;
        }
        el.appendChild(exEl);
      }
    }

    // Resolve target
    if (typeof target === 'string') {
      target = document.querySelector(target);
    }
    if (!target) throw new Error('PanelLive.mount(): target not found');
    target.appendChild(el);

    return new PanelLiveController(el);
  },
};
