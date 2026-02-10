/**
 * panel-embed.js — Shared Library for Panel Embedding
 *
 * Single IIFE file exposing window.PanelEmbed with:
 *   Declarative: <script type="panel"> / <script type="panel-editor">
 *   Imperative:  PanelEmbed.configure(), .init(), .app(), .editor(), .playground()
 *
 * No build step required. Auto-injects CSS on first use.
 */
(function () {
  'use strict';

  // ===== Cleanup stale service workers =====
  // JupyterLite (and other tools) may register service workers (e.g.
  // PyodideServiceWorker.js) on the same origin. A stale worker intercepts
  // every fetch and throws on 404s (missing favicon, etc.). Unregistering
  // alone is not enough — the worker keeps controlling the page until all
  // clients close. So we unregister and force one reload to escape it.
  if (navigator.serviceWorker && navigator.serviceWorker.controller) {
    navigator.serviceWorker.getRegistrations().then(function (regs) {
      var hadWorker = regs.length > 0;
      regs.forEach(function (r) { r.unregister(); });
      if (hadWorker) {
        location.reload();
      }
    });
    return; // Stop IIFE — page will reload momentarily
  }

  // ===== Script base URL (for resolving sibling resources like panel-runner.html) =====
  var _scriptBaseUrl = (function () {
    var src = (document.currentScript || {}).src || '';
    return src ? src.substring(0, src.lastIndexOf('/') + 1) : '';
  })();

  // ===== Config =====
  const defaults = {
    pyodideVersion: 'v0.28.2',
    panelVersion: '1.8.7',
    bokehVersion: '3.8.2',
  };

  let config = { ...defaults };

  function cdnUrls() {
    const { pyodideVersion, panelVersion, bokehVersion } = config;
    return {
      pyodide: `https://cdn.jsdelivr.net/pyodide/${pyodideVersion}/full/pyodide.js`,
      bokehJs: [
        `https://cdn.bokeh.org/bokeh/release/bokeh-${bokehVersion}.min.js`,
        `https://cdn.bokeh.org/bokeh/release/bokeh-widgets-${bokehVersion}.min.js`,
        `https://cdn.bokeh.org/bokeh/release/bokeh-tables-${bokehVersion}.min.js`,
      ],
      panelJs: `https://cdn.jsdelivr.net/npm/@holoviz/panel@${panelVersion}/dist/panel.min.js`,
      bokehWhl: `https://cdn.holoviz.org/panel/wheels/bokeh-${bokehVersion}-py3-none-any.whl`,
      panelWhl: `https://cdn.holoviz.org/panel/${panelVersion}/dist/wheels/panel-${panelVersion}-py3-none-any.whl`,
    };
  }

  // ===== Loader =====
  function loadScript(url) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = url;
      s.crossOrigin = 'anonymous';
      s.onload = resolve;
      s.onerror = function () { reject(new Error('Failed to load ' + url)); };
      document.head.appendChild(s);
    });
  }

  function loadCSS(url) {
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = url;
    link.crossOrigin = 'anonymous';
    document.head.appendChild(link);
  }

  async function loadJSResources() {
    var urls = cdnUrls();
    setStatus('Loading Bokeh JS...');
    for (var i = 0; i < urls.bokehJs.length; i++) {
      await loadScript(urls.bokehJs[i]);
    }
    setStatus('Loading Panel JS...');
    await loadScript(urls.panelJs);
  }

  // ===== StatusBar =====
  var statusEl = null;

  function injectStyles() {
    if (document.getElementById('panel-embed-styles')) return;
    var style = document.createElement('style');
    style.id = 'panel-embed-styles';
    style.textContent = [
      // Status bar
      '#pnl-status{position:fixed;top:0;left:0;right:0;background:#1b5e20;color:white;padding:8px 16px;font-size:14px;z-index:9999;transition:opacity .3s;font-family:system-ui,-apple-system,sans-serif}',
      '#pnl-status.pnl-hidden{opacity:0;pointer-events:none}',
      '#pnl-status.pnl-error{background:#b71c1c}',
      '.pnl-spinner{display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.3);border-radius:50%;border-top-color:white;animation:pnl-spin .8s linear infinite;margin-right:8px;vertical-align:middle}',
      '@keyframes pnl-spin{to{transform:rotate(360deg)}}',

      // Panel target container
      '.pnl-target{width:100%;min-height:100px;border:1px solid #eee;border-radius:0 0 8px 8px;padding:8px;box-sizing:border-box}',

      // Panel embed container (no-editor)
      '.pnl-embed{border:1px solid #ddd;border-radius:8px;overflow:hidden;margin:16px 0}',
      '.pnl-embed .pnl-target{border:none;border-radius:0}',

      // Editor chrome
      '.pnl-editor{border:1px solid #ddd;border-radius:8px;overflow:hidden;margin:16px 0;box-shadow:0 2px 8px rgba(0,0,0,.08)}',
      '.pnl-editor-header{background:#282a36;color:#f8f8f2;padding:8px 14px;display:flex;align-items:center;gap:10px;font-size:13px;font-weight:500;border-bottom:1px solid #44475a;font-family:system-ui,-apple-system,sans-serif}',
      '.pnl-editor-header .pnl-lang{background:#3b82f6;color:white;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;letter-spacing:.5px;text-transform:uppercase}',
      '.pnl-editor-header .pnl-title{flex:1}',
      '.pnl-editor-header button{background:#50fa7b;color:#282a36;border:none;padding:5px 16px;border-radius:4px;cursor:pointer;font-size:12px;font-weight:700;transition:background .15s}',
      '.pnl-editor-header button:hover{background:#69ff94}',
      '.pnl-editor-header button:disabled{background:#6272a4;color:#44475a;cursor:not-allowed}',
      '.pnl-editor-header .pnl-shortcut{font-size:11px;color:#6272a4;margin-left:-4px}',

      // CodeMirror overrides inside editor
      '.pnl-editor .CodeMirror{height:auto;min-height:120px;max-height:400px;font-family:"JetBrains Mono","Fira Code","Cascadia Code","Consolas",monospace;font-size:13.5px;line-height:1.55;border-bottom:1px solid #44475a}',
      '.pnl-editor .CodeMirror-scroll{min-height:120px}',

      // Per-app status overlay
      '.pnl-app-status{padding:12px 16px;color:#666;font-size:13px;font-family:system-ui,-apple-system,sans-serif}',
      '.pnl-app-status.pnl-error{color:#b71c1c}',

      // Iframe inside editor
      '.pnl-editor iframe{width:100%;border:none;min-height:250px}',
      '.pnl-embed iframe{width:100%;border:none;min-height:300px}',

      // Toolbar (for collapsible code)
      '.pnl-editor-toolbar{display:flex;align-items:center;justify-content:flex-end;padding:4px 8px;background:#f5f5f5;border-top:1px solid #ddd;border-bottom:1px solid #ddd;gap:4px}',
      '.pnl-editor-toolbar button{background:none;border:1px solid #ccc;border-radius:4px;padding:4px 8px;cursor:pointer;font-size:13px;color:#555;display:flex;align-items:center;gap:4px;transition:background .15s,color .15s;font-family:system-ui,-apple-system,sans-serif}',
      '.pnl-editor-toolbar button:hover{background:#e0e0e0;color:#333}',
      '.pnl-editor-toolbar button.pnl-active{background:#282a36;color:#f8f8f2;border-color:#282a36}',

      // Collapsible code section
      '.pnl-editor-code-section{overflow:hidden;transition:max-height .3s ease,opacity .3s ease;max-height:2000px;opacity:1}',
      '.pnl-editor-code-section.pnl-collapsed{max-height:0;opacity:0}',

      // Layout: code-below — preview gets top border radius, no bottom border on target
      '.pnl-layout-code-below .pnl-target{border-radius:8px 8px 0 0;border-bottom:none}',
      '.pnl-layout-code-below .pnl-editor-header{border-bottom:none;border-top:1px solid #44475a}',

      // Fetch error
      '.pnl-fetch-error{color:#b71c1c;padding:16px;font-size:13px;font-family:monospace;white-space:pre-wrap;background:#fff5f5;border:1px solid #ffcdd2;border-radius:4px;margin:8px}',

      // Playground styles
      '.pnl-playground{display:flex;flex-direction:column;height:100%}',
      '.pnl-pg-header{display:flex;align-items:center;gap:12px;padding:8px 16px;background:#1a1a2e;color:white;border-bottom:2px solid #16213e;font-family:system-ui,-apple-system,sans-serif}',
      '.pnl-pg-header h1{font-size:16px;font-weight:600;margin:0;background:linear-gradient(135deg,#00d2ff,#3a7bd5);-webkit-background-clip:text;-webkit-text-fill-color:transparent}',
      '.pnl-pg-header select,.pnl-pg-header button{padding:6px 12px;border-radius:6px;border:none;font-size:13px;cursor:pointer}',
      '.pnl-pg-header select{background:#16213e;color:#ddd}',
      '.pnl-pg-btn-run{background:#00b894!important;color:white!important;font-weight:600}',
      '.pnl-pg-btn-run:hover{background:#00a381!important}',
      '.pnl-pg-btn-share{background:#16213e!important;color:#ddd!important}',
      '.pnl-pg-btn-share:hover{background:#1a1a4e!important}',
      '.pnl-pg-shortcut{font-size:11px;opacity:.7;margin-left:4px}',
      '.pnl-pg-status-dot{width:8px;height:8px;border-radius:50%;background:#e74c3c;margin-left:auto;transition:background .3s}',
      '.pnl-pg-status-dot.pnl-ready{background:#00b894}',
      '.pnl-pg-status-text{font-size:12px;color:#aaa}',
      '.pnl-pg-main{flex:1;display:flex;overflow:hidden}',
      '.pnl-pg-editor-pane{flex:1;display:flex;flex-direction:column;min-width:300px;border-right:2px solid #ddd}',
      '.pnl-pg-editor-container{flex:1;overflow:auto;display:flex}',
      '.pnl-pg-textarea{flex:1;width:100%;border:none;resize:none;font-family:"JetBrains Mono","Fira Code","Cascadia Code","Consolas",monospace;font-size:14px;line-height:1.5;padding:12px 16px;background:#fafafa;color:#1a1a2e;tab-size:4;outline:none}',
      '.pnl-pg-preview-pane{flex:1;display:flex;flex-direction:column;min-width:300px;background:white}',
      '.pnl-pg-preview-pane iframe{flex:1;border:none;width:100%}',
      '.pnl-pg-resize{width:4px;cursor:col-resize;background:#ddd;transition:background .2s}',
      '.pnl-pg-resize:hover{background:#3a7bd5}',
      '.pnl-toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#1a1a2e;color:white;padding:10px 20px;border-radius:8px;font-size:13px;opacity:0;transition:opacity .3s;pointer-events:none;z-index:9999;font-family:system-ui,-apple-system,sans-serif}',
      '.pnl-toast.pnl-show{opacity:1}',
    ].join('\n');
    document.head.appendChild(style);
  }

  function ensureStatusBar() {
    if (statusEl) return;
    injectStyles();
    statusEl = document.createElement('div');
    statusEl.id = 'pnl-status';
    statusEl.className = 'pnl-hidden';
    document.body.insertBefore(statusEl, document.body.firstChild);
  }

  function setStatus(msg, isError) {
    ensureStatusBar();
    statusEl.innerHTML = isError
      ? '<span style="margin-right:8px">&#x26A0;</span>' + msg
      : '<span class="pnl-spinner"></span>' + msg;
    statusEl.className = isError ? 'pnl-error' : '';
  }

  function hideStatus() {
    if (statusEl) statusEl.className = 'pnl-hidden';
  }

  // ===== Runtime (singleton Pyodide) =====
  var pyodide = null;
  var initPromise = null;
  var installedPackages = new Set(['panel', 'bokeh', 'pyodide-http']);
  var isReady = false;
  var runningApps = new Set();

  async function initPyodide() {
    if (initPromise) return initPromise;
    initPromise = _doInit();
    return initPromise;
  }

  async function _doInit() {
    ensureStatusBar();

    // Step 1: Bokeh + Panel JS
    await loadJSResources();

    // Step 2: Pyodide runtime
    setStatus('Loading Pyodide runtime...');
    await loadScript(cdnUrls().pyodide);

    setStatus('Initializing Pyodide...');
    pyodide = await window.loadPyodide({ fullStdLib: false });

    // Step 3: Python packages
    setStatus('Installing packages...');
    var urls = cdnUrls();
    await pyodide.loadPackage('micropip');
    pyodide.globals.set('__bokeh_whl__', urls.bokehWhl);
    pyodide.globals.set('__panel_whl__', urls.panelWhl);
    await pyodide.runPythonAsync(
      'import micropip\n' +
      'await micropip.install(__bokeh_whl__)\n' +
      'await micropip.install(__panel_whl__, reinstall=True, keep_going=True)\n' +
      "await micropip.install('pyodide-http')\n"
    );

    // Step 4: Initialize Panel
    setStatus('Initializing Panel...');
    await pyodide.runPythonAsync(
      'import panel as pn\n' +
      'from panel.io.pyodide import init_doc\n' +
      'print("Panel", pn.__version__, "ready")\n'
    );

    isReady = true;
    hideStatus();
    return pyodide;
  }

  // ===== Packages =====
  async function detectAndInstallRequirements(code) {
    pyodide.globals.set('__user_code__', code);
    var newPkgs = await pyodide.runPythonAsync(
      'from panel.io.mime_render import find_requirements\n' +
      'reqs = find_requirements(__user_code__)\n' +
      'import json\n' +
      'json.dumps(reqs)\n'
    );
    var requirements = JSON.parse(newPkgs);
    var toInstall = requirements.filter(function (pkg) { return !installedPackages.has(pkg); });

    if (toInstall.length > 0) {
      setStatus('Installing: ' + toInstall.join(', ') + '...');
      var micropip = pyodide.pyimport('micropip');
      await micropip.install(toInstall);
      toInstall.forEach(function (pkg) { installedPackages.add(pkg); });
      hideStatus();
    }
  }

  var loadedExtResources = new Set();

  async function loadExtensionResources() {
    var resourcesJson = await pyodide.runPythonAsync(
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
    var resources = JSON.parse(resourcesJson);

    for (var i = 0; i < resources.css.length; i++) {
      var url = resources.css[i];
      if (loadedExtResources.has(url)) continue;
      loadedExtResources.add(url);
      loadCSS(url);
    }

    for (var j = 0; j < resources.js.length; j++) {
      var jsUrl = resources.js[j];
      if (loadedExtResources.has(jsUrl)) continue;
      loadedExtResources.add(jsUrl);
      await loadScript(jsUrl);
    }
  }

  // ===== Cleanup =====
  function cleanupContainer(targetId) {
    var targetEl = document.getElementById(targetId);
    if (!targetEl) return;

    if (window.Bokeh && window.Bokeh.index && window.Bokeh.index.roots) {
      try {
        var roots = Array.from(window.Bokeh.index.roots);
        for (var i = 0; i < roots.length; i++) {
          try {
            if (roots[i].el && targetEl.contains(roots[i].el)) {
              roots[i].remove();
            }
          } catch (e) { /* ignore */ }
        }
      } catch (e) { /* ignore */ }
    }

    targetEl.innerHTML = '';
  }

  // ===== Executor =====
  // 3-branch execution: servable, servable+target, expression
  // Uses namespace isolation and scoped DOM queries.
  async function runApp(targetId, code) {
    if (!isReady) throw new Error('Pyodide not ready yet.');

    if (runningApps.has(targetId)) return;
    runningApps.add(targetId);

    var targetEl = document.getElementById(targetId);
    targetEl.innerHTML = '<div class="pnl-app-status"><span class="pnl-spinner"></span>Running...</div>';

    try {
      await detectAndInstallRequirements(code);

      cleanupContainer(targetId);

      var hasServable = code.includes('.servable(');
      var hasServableTarget = /\.servable\s*\(\s*target\s*=/.test(code);

      pyodide.globals.set('__panel_user_code__', code);
      pyodide.globals.set('__panel_target_id__', targetId);

      if (hasServable && !hasServableTarget) {
        // .servable() flow
        await pyodide.runPythonAsync(
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

        await pyodide.runPythonAsync(
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
        await pyodide.runPythonAsync(
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

        await pyodide.runPythonAsync(
          'from panel.io.pyodide import write_doc\n' +
          'await write_doc()\n'
        );

      } else {
        // Expression flow (no .servable())
        await pyodide.runPythonAsync(
          'import panel as pn\n' +
          'from panel.io.mime_render import exec_with_return\n' +
          '__ns__ = {"__builtins__": __builtins__}\n' +
          '__exec_result__ = exec_with_return(__panel_user_code__, __ns__)\n'
        );

        await loadExtensionResources();

        await pyodide.runPythonAsync(
          'import js\n' +
          'from panel.io.pyodide import write\n' +
          'if __exec_result__ is not None:\n' +
          '    await write(__panel_target_id__, __exec_result__)\n' +
          'else:\n' +
          '    target_el = js.document.getElementById(__panel_target_id__)\n' +
          '    target_el.innerHTML = \'<p style="color: #666; padding: 16px;">Code executed (no visual output)</p>\'\n'
        );
      }
    } catch (error) {
      var errorMsg = error.message || String(error);
      var el = document.getElementById(targetId);
      el.innerHTML = '<pre style="color:#b71c1c;padding:16px;white-space:pre-wrap;font-size:13px;">' +
        errorMsg.replace(/</g, '&lt;') + '</pre>';
    } finally {
      runningApps.delete(targetId);
    }
  }

  // ===== Runner Executor (for panel-runner.html — no namespace isolation) =====
  var runCount = 0;

  async function runRunnerApp(code) {
    if (!isReady) throw new Error('Pyodide not ready yet.');

    runCount++;
    var currentRun = runCount;
    setStatus('Running code...');

    try {
      await detectAndInstallRequirements(code);
      if (currentRun !== runCount) return;

      setStatus('Preparing...');
      await pyodide.runPythonAsync(
        'import js\n' +
        'import json\n' +
        'from bokeh.io import curdoc\n' +
        'from bokeh.settings import settings as bk_settings\n' +
        'from panel.io.pyodide import init_doc\n' +
        'from panel.io.state import state\n' +
        "if hasattr(js.window, 'Bokeh') and hasattr(js.window.Bokeh, 'index'):\n" +
        '    try:\n' +
        '        roots = list(js.window.Bokeh.index.roots)\n' +
        '        for view in roots:\n' +
        '            try:\n' +
        '                view.remove()\n' +
        '            except Exception:\n' +
        '                pass\n' +
        '    except Exception:\n' +
        '        pass\n' +
        "output_el = js.document.getElementById('output')\n" +
        "output_el.innerHTML = ''\n" +
        'init_doc()\n'
      );
      if (currentRun !== runCount) return;

      var hasServable = code.includes('.servable(');
      var hasServableTarget = /\.servable\s*\(\s*target\s*=/.test(code);

      setStatus('Executing...');
      pyodide.globals.set('__panel_user_code__', code);

      if (hasServable && !hasServableTarget) {
        await pyodide.runPythonAsync(
          'import js\n' +
          'import panel as pn\n' +
          'from panel.io.state import state\n' +
          'exec(__panel_user_code__)\n'
        );
        if (currentRun !== runCount) return;
        await loadExtensionResources();
        if (currentRun !== runCount) return;
        await pyodide.runPythonAsync(
          'import js\n' +
          'from panel.io.pyodide import write_doc\n' +
          'from panel.io.state import state\n' +
          'doc = state.curdoc\n' +
          "target = js.document.getElementById('output')\n" +
          'for root in doc.roots:\n' +
          "    el = js.document.createElement('div')\n" +
          "    el.setAttribute('data-root-id', str(root.id))\n" +
          "    el.id = f'el-{root.id}'\n" +
          '    target.appendChild(el)\n' +
          'await write_doc()\n'
        );
      } else if (hasServableTarget) {
        await pyodide.runPythonAsync(
          'import panel as pn\n' +
          'from panel.io.state import state\n' +
          'exec(__panel_user_code__)\n'
        );
        if (currentRun !== runCount) return;
        await loadExtensionResources();
        if (currentRun !== runCount) return;
        await pyodide.runPythonAsync(
          'from panel.io.pyodide import write_doc\n' +
          'await write_doc()\n'
        );
      } else {
        await pyodide.runPythonAsync(
          'import panel as pn\n' +
          'from panel.io.mime_render import exec_with_return\n' +
          '__exec_result__ = exec_with_return(__panel_user_code__)\n'
        );
        if (currentRun !== runCount) return;
        await loadExtensionResources();
        if (currentRun !== runCount) return;
        await pyodide.runPythonAsync(
          'import js\n' +
          'from panel.io.pyodide import write\n' +
          'if __exec_result__ is not None:\n' +
          "    await write('output', __exec_result__)\n" +
          'else:\n' +
          "    js.document.getElementById('output').innerHTML = '<p style=\"color: #666; padding: 16px;\">Code executed (no visual output)</p>'\n"
        );
      }

      if (currentRun === runCount) {
        hideStatus();
        if (window.parent !== window) {
          window.parent.postMessage({ type: 'rendered' }, '*');
        }
      }
    } catch (error) {
      if (currentRun === runCount) {
        var errorMsg = error.message || String(error);
        setStatus('Error: ' + errorMsg, true);
        var output = document.getElementById('output');
        output.innerHTML = '<pre style="color:#b71c1c;padding:16px;white-space:pre-wrap;font-size:13px;">' +
          errorMsg.replace(/</g, '&lt;') + '</pre>';
        if (window.parent !== window) {
          window.parent.postMessage({ type: 'error', error: errorMsg }, '*');
        }
      }
    }
  }

  // ===== CodeMirrorMgr =====
  var cmLoaded = false;
  var cmLoadPromise = null;
  var CM_VERSION = '5.65.18';
  var CM_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/' + CM_VERSION;

  function loadCodeMirror() {
    if (cmLoadPromise) return cmLoadPromise;
    cmLoadPromise = _doLoadCM();
    return cmLoadPromise;
  }

  async function _doLoadCM() {
    if (cmLoaded) return;
    // CSS
    loadCSS(CM_CDN + '/codemirror.min.css');
    loadCSS(CM_CDN + '/theme/dracula.min.css');
    // JS — sequential (mode depends on core, addons depend on core)
    await loadScript(CM_CDN + '/codemirror.min.js');
    await loadScript(CM_CDN + '/mode/python/python.min.js');
    await loadScript(CM_CDN + '/addon/edit/matchbrackets.min.js');
    await loadScript(CM_CDN + '/addon/edit/closebrackets.min.js');
    await loadScript(CM_CDN + '/addon/selection/active-line.min.js');
    await loadScript(CM_CDN + '/addon/comment/comment.min.js');
    cmLoaded = true;
  }

  function createCMEditor(textarea, onRun) {
    var cm = CodeMirror.fromTextArea(textarea, {
      mode: 'python',
      theme: 'dracula',
      lineNumbers: true,
      matchBrackets: true,
      autoCloseBrackets: true,
      styleActiveLine: true,
      indentUnit: 4,
      tabSize: 4,
      indentWithTabs: false,
      lineWrapping: false,
      extraKeys: {
        'Ctrl-Enter': function () { if (onRun) onRun(); },
        'Cmd-Enter': function () { if (onRun) onRun(); },
        'Ctrl-/': 'toggleComment',
        'Cmd-/': 'toggleComment',
        'Tab': function (cm) {
          if (cm.somethingSelected()) {
            cm.indentSelection('add');
          } else {
            cm.replaceSelection('    ', 'end');
          }
        },
        'Shift-Tab': function (cm) {
          cm.indentSelection('subtract');
        },
      }
    });
    setTimeout(function () { cm.refresh(); }, 50);
    return cm;
  }

  // ===== IframeMode =====
  var readyIframes = new Set();
  var pendingIframeCode = new Map();
  var iframeLoadQueue = [];
  var iframeLoading = false;

  function initIframeListeners() {
    window.addEventListener('message', function (event) {
      var msg = event.data;
      if (!msg || !msg.type) return;
      if (msg.type === 'ready') {
        // Find which iframe sent this
        var iframes = document.querySelectorAll('iframe');
        for (var i = 0; i < iframes.length; i++) {
          if (iframes[i].contentWindow === event.source) {
            var id = iframes[i].id;
            readyIframes.add(id);
            if (pendingIframeCode.has(id)) {
              iframes[i].contentWindow.postMessage(
                { type: 'run', code: pendingIframeCode.get(id) }, '*'
              );
              pendingIframeCode.delete(id);
            }
            loadNextIframe();
            break;
          }
        }
      }
    });
  }

  function loadNextIframe() {
    if (iframeLoading || iframeLoadQueue.length === 0) return;
    iframeLoading = true;
    var id = iframeLoadQueue.shift();
    var iframe = document.getElementById(id);
    if (iframe && !iframe.src.includes('panel-runner.html')) {
      iframe.src = _scriptBaseUrl + 'panel-runner.html';
    }
    // Will be called again when this iframe sends 'ready'
    iframeLoading = false;
  }

  function sendToIframe(iframeId, code) {
    if (readyIframes.has(iframeId)) {
      document.getElementById(iframeId).contentWindow.postMessage(
        { type: 'run', code: code }, '*'
      );
    } else {
      pendingIframeCode.set(iframeId, code);
    }
  }

  // ===== Sharing =====
  async function compressCode(code) {
    var stream = new Blob([code]).stream().pipeThrough(new CompressionStream('gzip'));
    var compressed = await new Response(stream).arrayBuffer();
    var bytes = new Uint8Array(compressed);
    var binary = '';
    bytes.forEach(function (b) { binary += String.fromCharCode(b); });
    return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  async function decompressCode(encoded) {
    var binary = encoded.replace(/-/g, '+').replace(/_/g, '/');
    while (binary.length % 4) binary += '=';
    var raw = atob(binary);
    var bytes = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
    var stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    return await new Response(stream).text();
  }

  // ===== Unique ID generator =====
  var idCounter = 0;
  function uid(prefix) {
    return (prefix || 'pnl') + '-' + (++idCounter);
  }

  // ===== Fetch Code =====
  async function fetchCode(src) {
    var resp = await fetch(src);
    if (!resp.ok) throw new Error('Failed to fetch ' + src + ': ' + resp.status + ' ' + resp.statusText);
    return await resp.text();
  }

  // ===== Build Editor DOM =====
  // Shared DOM construction for editor mode.
  // Returns { editorDiv, textarea, previewEl, codeSection, toolbar, header }
  function buildEditorDOM(opts) {
    var editorId = opts.editorId;
    var previewId = opts.previewId;
    var title = opts.title || 'Panel App';
    var layout = opts.layout || 'code-above';
    var codeVisibility = opts.codeVisibility || 'visible';
    var code = opts.code || '';
    var isIframe = opts.iframe;
    var height = opts.height;

    var editorDiv = document.createElement('div');
    editorDiv.className = 'pnl-editor' + (layout === 'code-below' ? ' pnl-layout-code-below' : '');
    editorDiv.id = editorId;

    // Header
    var header = document.createElement('div');
    header.className = 'pnl-editor-header';
    header.innerHTML =
      '<span class="pnl-lang">Python</span>' +
      '<span class="pnl-title">' + title + '</span>' +
      '<button id="' + editorId + '-run-btn">Run</button>' +
      '<span class="pnl-shortcut">Ctrl+Enter</span>';

    // Textarea (will become CodeMirror)
    var textarea = document.createElement('textarea');
    textarea.id = editorId + '-code';
    textarea.style.display = 'none';
    textarea.value = code;

    // Preview element (iframe or div)
    var previewEl;
    if (isIframe) {
      previewEl = document.createElement('iframe');
      previewEl.id = previewId;
      if (height) previewEl.style.minHeight = height;
    } else {
      previewEl = document.createElement('div');
      previewEl.id = previewId;
      previewEl.className = 'pnl-target';
      if (height) previewEl.style.minHeight = height;
      previewEl.innerHTML = '<div class="pnl-app-status">Waiting for Pyodide...</div>';
    }

    var codeSection = null;
    var toolbar = null;
    var isCollapsible = codeVisibility === 'hidden';

    if (isCollapsible) {
      // Wrap header + textarea in a code section
      codeSection = document.createElement('div');
      codeSection.className = 'pnl-editor-code-section pnl-collapsed';
      codeSection.appendChild(header);
      codeSection.appendChild(textarea);

      toolbar = createToolbar(codeSection);

      if (layout === 'code-below') {
        // preview, toolbar, code-section
        editorDiv.appendChild(previewEl);
        editorDiv.appendChild(toolbar);
        editorDiv.appendChild(codeSection);
      } else {
        // code-section, toolbar, preview
        editorDiv.appendChild(codeSection);
        editorDiv.appendChild(toolbar);
        editorDiv.appendChild(previewEl);
      }
    } else {
      // Non-collapsible: just header + textarea + preview (or reversed)
      if (layout === 'code-below') {
        editorDiv.appendChild(previewEl);
        editorDiv.appendChild(header);
        editorDiv.appendChild(textarea);
      } else {
        editorDiv.appendChild(header);
        editorDiv.appendChild(textarea);
        editorDiv.appendChild(previewEl);
      }
    }

    return {
      editorDiv: editorDiv,
      textarea: textarea,
      previewEl: previewEl,
      codeSection: codeSection,
      toolbar: toolbar,
      header: header,
    };
  }

  // ===== Create Toolbar =====
  // Creates a toolbar with a <> toggle button for collapsible code sections.
  function createToolbar(codeSection) {
    var toolbar = document.createElement('div');
    toolbar.className = 'pnl-editor-toolbar';
    var btn = document.createElement('button');
    btn.innerHTML = '&lt;&gt; Code';
    btn.onclick = function () {
      var isCollapsed = codeSection.classList.contains('pnl-collapsed');
      if (isCollapsed) {
        codeSection.classList.remove('pnl-collapsed');
        btn.classList.add('pnl-active');
        var cmEl = codeSection.querySelector('.CodeMirror');
        if (cmEl && cmEl.CodeMirror) {
          setTimeout(function () { cmEl.CodeMirror.refresh(); }, 50);
        }
      } else {
        codeSection.classList.add('pnl-collapsed');
        btn.classList.remove('pnl-active');
      }
    };
    toolbar.appendChild(btn);
    return toolbar;
  }

  // ===== Modes =====

  // --- PanelEmbed.app(target, code, opts) ---
  function appMode(target, code, opts) {
    opts = opts || {};
    injectStyles();
    var container = typeof target === 'string' ? document.getElementById(target) : target;
    var targetId = uid('app');
    var src = opts.src || null;

    if (opts.iframe) {
      // Iframe mode
      var wrapper = document.createElement('div');
      wrapper.className = 'pnl-embed';
      var iframe = document.createElement('iframe');
      iframe.id = targetId;
      if (opts.height) iframe.style.minHeight = opts.height;
      wrapper.appendChild(iframe);
      container.appendChild(wrapper);

      initIframeListeners();

      if (src && !code) {
        fetchCode(src).then(function (fetched) {
          pendingIframeCode.set(targetId, fetched);
          iframeLoadQueue.push(targetId);
          loadNextIframe();
        }).catch(function (err) {
          iframe.srcdoc = '<div style="color:#b71c1c;padding:16px;font-family:monospace">' + err.message + '</div>';
        });
      } else {
        pendingIframeCode.set(targetId, code);
        iframeLoadQueue.push(targetId);
        loadNextIframe();
      }
    } else {
      // Inline mode
      var wrapper = document.createElement('div');
      wrapper.className = 'pnl-embed';
      var targetDiv = document.createElement('div');
      targetDiv.id = targetId;
      targetDiv.className = 'pnl-target';
      if (opts.height) targetDiv.style.minHeight = opts.height;
      targetDiv.innerHTML = '<div class="pnl-app-status">Waiting for Pyodide...</div>';
      wrapper.appendChild(targetDiv);
      container.appendChild(wrapper);

      var srcPromise = (src && !code) ? fetchCode(src) : Promise.resolve(null);

      Promise.all([initPyodide(), srcPromise]).then(function (results) {
        var fetched = results[1];
        var finalCode = fetched !== null ? fetched : code;
        return runApp(targetId, finalCode);
      }).catch(function (err) {
        if (src && err.message && err.message.indexOf('Failed to fetch') === 0) {
          targetDiv.innerHTML = '<div class="pnl-fetch-error">' + err.message + '</div>';
        } else {
          setStatus('Fatal: ' + (err.message || err), true);
        }
      });
    }
  }

  // --- PanelEmbed.editor(target, code, opts) ---
  function editorMode(target, code, opts) {
    opts = opts || {};
    injectStyles();
    var container = typeof target === 'string' ? document.getElementById(target) : target;
    var editorId = uid('editor');
    var previewId = editorId + '-preview';
    var src = opts.src || null;
    var layout = opts.layout || 'code-above';
    var codeVisibility = opts.codeVisibility || 'visible';

    var dom = buildEditorDOM({
      editorId: editorId,
      previewId: previewId,
      title: opts.title,
      layout: layout,
      codeVisibility: codeVisibility,
      code: code || '',
      iframe: opts.iframe,
      height: opts.height,
    });

    container.appendChild(dom.editorDiv);

    var cmInstance = null;

    function getCode() {
      return cmInstance ? cmInstance.getValue() : dom.textarea.value;
    }

    function doRun() {
      if (opts.iframe) {
        sendToIframe(previewId, getCode());
      } else {
        runApp(previewId, getCode());
      }
    }

    function setupCM() {
      dom.textarea.style.display = '';
      cmInstance = createCMEditor(dom.textarea, doRun);
      dom.header.querySelector('button').onclick = doRun;
    }

    if (opts.iframe) {
      initIframeListeners();

      loadCodeMirror().then(function () {
        setupCM();

        if (src) {
          fetchCode(src).then(function (fetched) {
            dom.textarea.value = fetched;
            cmInstance.setValue(fetched);
            pendingIframeCode.set(previewId, fetched);
            iframeLoadQueue.push(previewId);
            loadNextIframe();
          }).catch(function (err) {
            dom.previewEl.srcdoc = '<div style="color:#b71c1c;padding:16px;font-family:monospace">' + err.message + '</div>';
          });
        } else {
          pendingIframeCode.set(previewId, code);
          iframeLoadQueue.push(previewId);
          loadNextIframe();
        }
      });
    } else {
      var srcPromise = src ? fetchCode(src) : Promise.resolve(null);

      Promise.all([loadCodeMirror(), initPyodide(), srcPromise]).then(function (results) {
        var fetched = results[2];
        if (fetched !== null) {
          dom.textarea.value = fetched;
          code = fetched;
        }
        setupCM();
        return runApp(previewId, getCode());
      }).catch(function (err) {
        if (src && err.message && err.message.indexOf('Failed to fetch') === 0) {
          dom.previewEl.innerHTML = '<div class="pnl-fetch-error">' + err.message + '</div>';
        } else {
          setStatus('Fatal: ' + (err.message || err), true);
        }
      });
    }
  }

  // --- PanelEmbed.playground(target, opts) ---
  function playgroundMode(target, opts) {
    opts = opts || {};
    injectStyles();
    var container = typeof target === 'string' ? document.getElementById(target) : target;
    var examples = opts.examples || {};
    var defaultCode = opts.code || '';
    var sharing = opts.sharing !== false;
    var resizable = opts.resizable !== false;

    // Build DOM
    container.innerHTML = '';
    var pg = document.createElement('div');
    pg.className = 'pnl-playground';
    pg.style.height = '100%';

    // Header
    var header = document.createElement('div');
    header.className = 'pnl-pg-header';
    var h1 = document.createElement('h1');
    h1.textContent = opts.title || 'Panel Playground';
    header.appendChild(h1);

    // Examples dropdown
    var exampleKeys = Object.keys(examples);
    var select = null;
    if (exampleKeys.length > 0) {
      select = document.createElement('select');
      var defaultOpt = document.createElement('option');
      defaultOpt.value = '';
      defaultOpt.textContent = '-- Examples --';
      select.appendChild(defaultOpt);
      exampleKeys.forEach(function (name) {
        var opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        select.appendChild(opt);
      });
      header.appendChild(select);
    }

    // Run button
    var runBtn = document.createElement('button');
    runBtn.className = 'pnl-pg-btn-run';
    runBtn.innerHTML = 'Run <span class="pnl-pg-shortcut">Ctrl+Enter</span>';
    header.appendChild(runBtn);

    // Share button
    var shareBtn = null;
    if (sharing) {
      shareBtn = document.createElement('button');
      shareBtn.className = 'pnl-pg-btn-share';
      shareBtn.textContent = 'Share';
      header.appendChild(shareBtn);
    }

    // Status
    var statusText = document.createElement('span');
    statusText.className = 'pnl-pg-status-text';
    statusText.textContent = 'Loading...';
    header.appendChild(statusText);

    var statusDot = document.createElement('span');
    statusDot.className = 'pnl-pg-status-dot';
    header.appendChild(statusDot);

    pg.appendChild(header);

    // Main area
    var main = document.createElement('div');
    main.className = 'pnl-pg-main';

    var editorPane = document.createElement('div');
    editorPane.className = 'pnl-pg-editor-pane';
    var editorContainer = document.createElement('div');
    editorContainer.className = 'pnl-pg-editor-container';
    var codeTextarea = document.createElement('textarea');
    codeTextarea.className = 'pnl-pg-textarea';
    codeTextarea.spellcheck = false;
    codeTextarea.value = defaultCode;
    editorContainer.appendChild(codeTextarea);
    editorPane.appendChild(editorContainer);

    var resizeHandle = null;
    if (resizable) {
      resizeHandle = document.createElement('div');
      resizeHandle.className = 'pnl-pg-resize';
    }

    var previewPane = document.createElement('div');
    previewPane.className = 'pnl-pg-preview-pane';
    var previewIframe = document.createElement('iframe');
    previewIframe.id = uid('pg-preview');
    previewIframe.src = _scriptBaseUrl + 'panel-runner.html';
    previewPane.appendChild(previewIframe);

    main.appendChild(editorPane);
    if (resizeHandle) main.appendChild(resizeHandle);
    main.appendChild(previewPane);
    pg.appendChild(main);

    // Toast
    var toast = document.createElement('div');
    toast.className = 'pnl-toast';
    toast.textContent = 'Link copied to clipboard!';
    pg.appendChild(toast);

    container.appendChild(pg);

    // Wire up
    function getCode() {
      return codeTextarea.value;
    }

    function setCode(code) {
      codeTextarea.value = code;
    }

    function doRun() {
      previewIframe.contentWindow.postMessage({ type: 'run', code: getCode() }, '*');
    }

    runBtn.onclick = doRun;

    // Keyboard shortcut
    codeTextarea.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        doRun();
      }
      if (e.key === 'Tab') {
        e.preventDefault();
        var start = e.target.selectionStart;
        var end = e.target.selectionEnd;
        e.target.value = e.target.value.substring(0, start) + '    ' + e.target.value.substring(end);
        e.target.selectionStart = e.target.selectionEnd = start + 4;
      }
    });

    // Examples
    if (select) {
      select.onchange = function () {
        var name = select.value;
        if (name && examples[name]) {
          var val = examples[name];
          // If value is a URL (ends in .py or .json), fetch it
          if (typeof val === 'string' && (val.endsWith('.py') || val.startsWith('http'))) {
            fetch(val).then(function (r) { return r.text(); }).then(function (code) {
              setCode(code);
            }).catch(function (err) {
              console.warn('Failed to load example:', err);
            });
          } else {
            setCode(val);
          }
        }
      };
      // Select first example if code not provided
      if (!defaultCode && exampleKeys.length > 0) {
        select.value = exampleKeys[0];
        var firstVal = examples[exampleKeys[0]];
        if (typeof firstVal === 'string' && !firstVal.endsWith('.py') && !firstVal.startsWith('http')) {
          setCode(firstVal);
        }
      }
    }

    // Sharing
    if (shareBtn) {
      shareBtn.onclick = async function () {
        var code = getCode();
        var compressed = await compressCode(code);
        var url = location.origin + location.pathname + '#code=' + compressed;
        await navigator.clipboard.writeText(url);
        toast.classList.add('pnl-show');
        setTimeout(function () { toast.classList.remove('pnl-show'); }, 2000);
        history.replaceState(null, '', '#code=' + compressed);
      };
    }

    // Load from hash
    (async function () {
      var hash = location.hash;
      if (hash.startsWith('#code=')) {
        try {
          var encoded = hash.slice(6);
          var code = await decompressCode(encoded);
          setCode(code);
          if (select) select.value = '';
        } catch (e) {
          console.warn('Failed to decode URL hash:', e);
        }
      }
    })();

    // Resize handle
    if (resizeHandle) {
      var isResizing = false;
      resizeHandle.addEventListener('mousedown', function () {
        isResizing = true;
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        previewIframe.style.pointerEvents = 'none';
      });
      document.addEventListener('mousemove', function (e) {
        if (!isResizing) return;
        var rect = main.getBoundingClientRect();
        var fraction = (e.clientX - rect.left) / rect.width;
        var clamped = Math.max(0.2, Math.min(0.8, fraction));
        editorPane.style.flex = '' + clamped;
        previewPane.style.flex = '' + (1 - clamped);
      });
      document.addEventListener('mouseup', function () {
        if (isResizing) {
          isResizing = false;
          document.body.style.cursor = '';
          document.body.style.userSelect = '';
          previewIframe.style.pointerEvents = '';
        }
      });
    }

    // Listen for messages from iframe
    window.addEventListener('message', function (event) {
      var msg = event.data;
      if (!msg || !msg.type) return;
      if (event.source !== previewIframe.contentWindow) return;
      if (msg.type === 'ready') {
        statusDot.classList.add('pnl-ready');
        statusText.textContent = 'Ready';
        doRun();
      } else if (msg.type === 'rendered') {
        statusText.textContent = 'Ready';
      } else if (msg.type === 'error') {
        statusText.textContent = 'Error';
        statusDot.classList.remove('pnl-ready');
      }
    });
  }

  // ===== AutoDiscover =====
  // On DOMContentLoaded, scan for <script type="panel"> and <script type="panel-editor">
  function autoDiscover() {
    // Process <script type="panel">
    var appScripts = document.querySelectorAll('script[type="panel"]');
    // Collect all inline apps to run sequentially after init
    var inlineApps = [];
    var iframeApps = [];

    for (var i = 0; i < appScripts.length; i++) {
      var s = appScripts[i];
      var code = s.textContent.trim();
      var src = s.getAttribute('src') || null;
      var targetId = s.getAttribute('data-target');
      var isIframe = s.hasAttribute('data-iframe');
      var height = s.getAttribute('data-height');

      // Create container after the script tag
      var wrapper = document.createElement('div');
      if (isIframe) {
        wrapper.className = 'pnl-embed';
        var iframe = document.createElement('iframe');
        var iid = targetId || uid('app');
        iframe.id = iid;
        if (height) iframe.style.minHeight = height;
        wrapper.appendChild(iframe);
        s.parentNode.insertBefore(wrapper, s.nextSibling);

        iframeApps.push({ id: iid, code: code, src: src });
      } else {
        wrapper.className = 'pnl-embed';
        var div = document.createElement('div');
        var did = targetId || uid('app');
        div.id = did;
        div.className = 'pnl-target';
        if (height) div.style.minHeight = height;
        div.innerHTML = '<div class="pnl-app-status">Waiting for Pyodide...</div>';
        wrapper.appendChild(div);
        s.parentNode.insertBefore(wrapper, s.nextSibling);

        inlineApps.push({ id: did, code: code, src: src });
      }
    }

    // Process <script type="panel-editor">
    var editorScripts = document.querySelectorAll('script[type="panel-editor"]');
    var inlineEditors = [];
    var iframeEditors = [];

    for (var j = 0; j < editorScripts.length; j++) {
      var es = editorScripts[j];
      var eCode = es.textContent.trim();
      var eTitle = es.getAttribute('data-title') || 'Panel App';
      var eIsIframe = es.hasAttribute('data-iframe');
      var eHeight = es.getAttribute('data-height');
      var eLayout = es.getAttribute('data-layout') || 'code-above';
      var eCodeVis = es.getAttribute('data-code') || 'visible';
      var eSrc = es.getAttribute('src') || null;

      var editorId = uid('editor');
      var previewId = editorId + '-preview';

      var dom = buildEditorDOM({
        editorId: editorId,
        previewId: previewId,
        title: eTitle,
        layout: eLayout,
        codeVisibility: eCodeVis,
        code: eCode,
        iframe: eIsIframe,
        height: eHeight,
      });

      es.parentNode.insertBefore(dom.editorDiv, es.nextSibling);

      var item = {
        editorId: editorId,
        previewId: previewId,
        code: eCode,
        src: eSrc,
        textarea: dom.textarea,
        header: dom.header,
        previewEl: dom.previewEl,
      };

      if (eIsIframe) {
        iframeEditors.push(item);
      } else {
        inlineEditors.push(item);
      }
    }

    // No apps/editors found — nothing to do
    if (inlineApps.length === 0 && iframeApps.length === 0 &&
        inlineEditors.length === 0 && iframeEditors.length === 0) {
      return;
    }

    injectStyles();

    // Iframe mode: set up listeners and sequential loading
    if (iframeApps.length > 0 || iframeEditors.length > 0) {
      initIframeListeners();

      // Collect all src fetch promises for iframe items
      var iframeSrcPromises = [];
      var allIframeItems = iframeApps.concat(
        iframeEditors.map(function (item) { return { id: item.previewId, code: item.code, src: item.src }; })
      );

      allIframeItems.forEach(function (item) {
        if (item.src) {
          var p = fetchCode(item.src).then(function (fetched) {
            item.code = fetched;
          }).catch(function (err) {
            item.fetchError = err.message;
          });
          iframeSrcPromises.push(p);
        }
      });

      // Set up CodeMirror for iframe editors (parallel with fetches)
      var iframeCMPromise = iframeEditors.length > 0 ? loadCodeMirror() : Promise.resolve();

      Promise.all([iframeCMPromise].concat(iframeSrcPromises)).then(function () {
        // Set fetched code into editor textareas/CM instances
        iframeEditors.forEach(function (item) {
          item.textarea.style.display = '';
          // Update textarea if src was fetched
          if (item.src) {
            // Find matching iframe item to get resolved code
            var matchItem = allIframeItems.filter(function (ai) { return ai.id === item.previewId; })[0];
            if (matchItem && !matchItem.fetchError) {
              item.textarea.value = matchItem.code;
              item.code = matchItem.code;
            }
          }
          var cm = createCMEditor(item.textarea, function () {
            sendToIframe(item.previewId, cm.getValue());
          });
          item.header.querySelector('button').onclick = function () {
            sendToIframe(item.previewId, cm.getValue());
          };
        });

        // Load iframes sequentially
        if (allIframeItems.length > 0) {
          var first = allIframeItems[0];
          if (first.fetchError) {
            var el = document.getElementById(first.id);
            if (el) el.srcdoc = '<div class="pnl-fetch-error">' + first.fetchError + '</div>';
          } else {
            pendingIframeCode.set(first.id, first.code);
            var firstIframe = document.getElementById(first.id);
            if (firstIframe) firstIframe.src = _scriptBaseUrl + 'panel-runner.html';
          }

          for (var k = 1; k < allIframeItems.length; k++) {
            if (allIframeItems[k].fetchError) continue;
            pendingIframeCode.set(allIframeItems[k].id, allIframeItems[k].code);
            iframeLoadQueue.push(allIframeItems[k].id);
          }
        }
      });
    }

    // Inline mode: init Pyodide + CodeMirror + fetch src, run sequentially
    if (inlineApps.length > 0 || inlineEditors.length > 0) {
      var cmPromise = inlineEditors.length > 0 ? loadCodeMirror() : Promise.resolve();
      var inlineCMs = {};

      // Build src fetch promises for all inline items
      var inlineSrcPromises = [];
      var allInlineItems = inlineApps.concat(inlineEditors);
      allInlineItems.forEach(function (item) {
        if (item.src) {
          var p = fetchCode(item.src).then(function (fetched) {
            item.code = fetched;
          }).catch(function (err) {
            item.fetchError = err.message;
          });
          inlineSrcPromises.push(p);
        }
      });

      Promise.all([cmPromise, initPyodide()].concat(inlineSrcPromises)).then(async function () {
        // Set up CodeMirror editors with resolved code
        inlineEditors.forEach(function (item) {
          item.textarea.value = item.code;
          item.textarea.style.display = '';
          var cm = createCMEditor(item.textarea, function () {
            runApp(item.previewId, cm.getValue());
          });
          inlineCMs[item.editorId] = cm;
          item.header.querySelector('button').onclick = function () {
            runApp(item.previewId, cm.getValue());
          };
        });

        // Run all inline apps sequentially
        for (var a = 0; a < inlineApps.length; a++) {
          if (inlineApps[a].fetchError) {
            var el = document.getElementById(inlineApps[a].id);
            if (el) el.innerHTML = '<div class="pnl-fetch-error">' + inlineApps[a].fetchError + '</div>';
            continue;
          }
          await runApp(inlineApps[a].id, inlineApps[a].code);
        }

        // Run all inline editor previews sequentially
        for (var e = 0; e < inlineEditors.length; e++) {
          var item = inlineEditors[e];
          if (item.fetchError) {
            item.previewEl.innerHTML = '<div class="pnl-fetch-error">' + item.fetchError + '</div>';
            continue;
          }
          var cm = inlineCMs[item.editorId];
          var code = cm ? cm.getValue() : item.code;
          await runApp(item.previewId, code);
        }
      }).catch(function (err) {
        setStatus('Fatal: ' + (err.message || err), true);
      });
    }
  }

  // Auto-discover on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoDiscover);
  } else {
    // DOM already loaded (script loaded with defer or dynamically)
    setTimeout(autoDiscover, 0);
  }

  // ===== Public API =====
  window.PanelEmbed = {
    configure: function (overrides) {
      Object.assign(config, overrides);
    },
    init: function () {
      return initPyodide();
    },
    app: appMode,
    editor: editorMode,
    playground: playgroundMode,

    // Internal — exposed for panel-runner.html
    _setStatus: setStatus,
    _hideStatus: hideStatus,
    _initPyodide: initPyodide,
    _runRunnerApp: runRunnerApp,
    _loadScript: loadScript,
    _cdnUrls: cdnUrls,
  };

})();
