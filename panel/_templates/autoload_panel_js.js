{#
ESM-only autoload for Panel notebooks with safe Panel IIFE handling.
- Waits for es-module-shim before using importShim.
- No legacy globals remain after load (we temporarily patch window.Bokeh only to capture Panel).
- Each pn.extension(esm=True) defines a unique @pn/env/<bundle_id> module and imports it inline.
#}

(function(root) {
  const BK_RE = /^https:\/\/cdn\.bokeh\.org\/bokeh\/release\/bokeh-/;
  const PN_RE = /^https:\/\/cdn\.holoviz\.org\/panel\/[^/]+\/dist\/panel/i;
  const reloading = {{ reloading|default(False)|json }};

  root._pn_env_registry  = root._pn_env_registry  || new Map(); // bundleId -> envSpec
  root._pn_spec_catalog  = root._pn_spec_catalog  || new Set(); // all spec keys we've registered

  // ------------------------------------------------------------
  // Helpers
  // ------------------------------------------------------------
  const BUNDLE_ID = {{ BUNDLE_ID|json }};

  // Shared registries
  root._pn_imports = root._pn_imports || { imports: {} };
  const IMPORTS = root._pn_imports.imports;

  function installImportMapDelta(delta) {
    if (!delta || !Object.keys(delta).length) return;
    const tag = document.createElement('script');
    tag.type = 'importmap-shim';
    tag.textContent = JSON.stringify({ imports: delta });
    document.head.appendChild(tag);
  }

  function blobURL(content, type) {
    const blob = new Blob([content], { type });
    return URL.createObjectURL(blob);
  }

  function injectCSS(urls) {
    const existing = new Set(Array.from(document.getElementsByTagName('link')).map(l => l.href));
    for (const url of urls || []) {
      const enc = encodeURI(url);
      if (existing.has(enc)) continue;
      const el = document.createElement("link");
      el.rel = "stylesheet";
      el.type = "text/css";
      el.href = url;
      document.head.appendChild(el);
    }
  }

  function injectRawCSS(cssList) {
    for (const css of cssList || []) {
      const el = document.createElement("style");
      el.appendChild(document.createTextNode(css));
      document.head.appendChild(el);
    }
  }

  // ------------------------------------------------------------
  // Ensure es-module-shim is loaded (so importShim exists)
  // ------------------------------------------------------------
  async function ensureEsModuleShim() {
    if (root.importShim) return; // already present
    // Reuse a shared ready-promise so concurrent cells don't duplicate work
    if (!root._pn_esms_ready) {
      root._pn_esms_ready = new Promise((resolve, reject) => {
        const existing = Array.from(document.scripts).find(s => /es-module-shim/.test(s.src));
        if (existing) {
          // If the tag is already there, wait for its load event or next tick if already complete
          if (existing.dataset._pn_loaded === "1" || root.importShim) {
            resolve();
          } else {
            existing.addEventListener('load', () => {
              existing.dataset._pn_loaded = "1";
              resolve();
            }, { once: true });
            existing.addEventListener('error', () => reject(new Error("[Panel ESM] Failed to load es-module-shim")), { once: true });
          }
          return;
        }
        const s = document.createElement('script');
        s.async = true;
        s.src = "https://unpkg.com/es-module-shims@1/dist/es-module-shims.js";
        s.addEventListener('load', () => {
          s.dataset._pn_loaded = "1";
          resolve();
        }, { once: true });
        s.addEventListener('error', () => reject(new Error("[Panel ESM] Failed to load es-module-shim")), { once: true });
        document.head.appendChild(s);
      });
    }
    await root._pn_esms_ready;
    if (!root.importShim) throw new Error("[Panel ESM] importShim unavailable after es-module-shim load");
  }

  // ------------------------------------------------------------
  // Bootstrap this bundle
  // ------------------------------------------------------------
  (async function bootstrap() {
    // CSS first
    injectCSS({{ bundle.css_urls|default([])|json }});
    injectRawCSS({{ bundle.css_raw|default([])|json }});

    const JS_URLS     = {{ bundle.js_urls|default([])|json }};
    const JS_MODULES  = {{ bundle.js_modules|default([])|json }};
    const JS_EXPORTS  = {{ bundle.js_module_exports|default({})|json }};

    const BOKEH_ESM_URLS = (JS_URLS || []).filter(u => BK_RE.test(u));
    const PANEL_IIFE_URL = (JS_URLS || []).find(u => PN_RE.test(u)) || null;

    // Build the env module source
    let envSrc = "";

    // Bokeh
    if (BOKEH_ESM_URLS)
      envSrc += `import * as _bokeh_mod from ${JSON.stringify(BOKEH_ESM_URLS[0])};\n const Bokeh = _bokeh_mod.default ?? _bokeh_mod;\n Bokeh[Bokeh.version] = Bokeh;`;
    else
      envSrc += `import const Bokeh = undefined;\n`;

    // Named ESM exports
    for (const [name, url] of Object.entries(JS_EXPORTS || {}))
      envSrc += `import ${name} from ${JSON.stringify(url)};\nexport { ${name} };\n`;

    // Self-contained Panel IIFE capture (uses globalThis for caches)
    envSrc += `
// Assumes Bokeh is already resolved in the env module (from Bokeh ESM default export).
// Same signature as before, but bokehPluginUrls are IIFE URLs (e.g. GL, tables, widgets...).
async function __pnEnsurePanelIIFE(panelUrl, bokehPluginUrls) {
  if (!panelUrl) throw new Error("[Panel ESM] No Panel IIFE URL provided");

  const locks  = (globalThis._pn_iife_locks  ||= new Map()); // key -> Promise
  const panels = (globalThis._pn_panel_cache ||= new Map()); // key -> Panel API
  const loaded = (globalThis._pn_iife_loaded ||= new Set()); // URL set for plugin/panel scripts

  const plugins = Array.isArray(bokehPluginUrls) ? bokehPluginUrls : (bokehPluginUrls ? [bokehPluginUrls] : []);
  const key = panelUrl + "||" + plugins.join(",");

  if (panels.has(key)) return panels.get(key);
  if (locks.has(key))  return locks.get(key);

  const task = (async () => {
    // Ensure we have a real Bokeh namespace with register_plugin
    if (!Bokeh || typeof Bokeh.register_plugin !== "function") {
      throw new Error("[Panel ESM] Bokeh namespace missing or lacks register_plugin; ensure core Bokeh ESM loaded first");
    }

    // Temporarily expose Bokeh on globalThis so plugin IIFEs can register
    const hadOwnBokeh = Object.prototype.hasOwnProperty.call(globalThis, "Bokeh");
    const prevBokeh = hadOwnBokeh ? globalThis.Bokeh : undefined;
    Object.defineProperty(globalThis, "Bokeh", {
      configurable: true,
      enumerable: true,
      writable: true,
      value: Bokeh,
    });

    try {
      // 1) Load Bokeh plugin IIFEs (GL, etc.) sequentially (deterministic)
      for (const url of plugins) {
        if (!url) continue;
        if (loaded.has(url)) continue;
        // If a <script> with same src already exists, wait a tick; otherwise append and await
        const existing = Array.from(document.scripts).some(s => s.src === url);
        if (!existing) {
          await new Promise((resolve, reject) => {
            const s = document.createElement("script");
            s.async = false; // preserve registration order
            s.src = url;
            s.onload = resolve;
            s.onerror = () => reject(new Error("[Panel ESM] Failed to load Bokeh plugin IIFE "+url));
            document.head.appendChild(s);
          });
        } else {
          await Promise.resolve();
        }
        loaded.add(url);
      }

      // 2) Load Panel IIFE (registers onto Bokeh)
      if (!loaded.has(panelUrl)) {
        const existingPanel = Array.from(document.scripts).some(s => s.src === panelUrl);
        if (!existingPanel) {
          await new Promise((resolve, reject) => {
            const s = document.createElement("script");
            s.async = false;
            s.src = panelUrl;
            s.onload = resolve;
            s.onerror = () => reject(new Error("[Panel ESM] Failed to load Panel IIFE "+panelUrl));
            document.head.appendChild(s);
          });
        } else {
          await Promise.resolve();
        }
        loaded.add(panelUrl);
      }

      // 3) Capture and freeze Panel API from the real Bokeh namespace
      const panelApi = Bokeh && Bokeh.Panel;
      if (!panelApi) throw new Error("[Panel ESM] Panel API not found after IIFE execution");
      const frozen = Object.freeze(panelApi);
      panels.set(key, frozen);
      return frozen;
    } finally {
      // Restore whatever Bokeh was there before
      if (hadOwnBokeh) globalThis.Bokeh = prevBokeh;
      else { try { delete globalThis.Bokeh; } catch {} }
    }
  })();

  locks.set(key, task);
  try { return await task; }
  finally { if (locks.get(key) === task) locks.delete(key); }
}

const Panel = (async () => {
  const api = await __pnEnsurePanelIIFE(
    ${JSON.stringify(PANEL_IIFE_URL)},
    ${JSON.stringify(BOKEH_ESM_URLS.slice(1))}
  );
  return api;
})();

export { Bokeh, Panel };
`;

    const envURL = blobURL(envSrc, "text/javascript");
    const baseSpec = `@pn/env/${BUNDLE_ID}`;

    // If we already chose a spec for this bundle, just reuse it (no map changes)
    let envSpec = root._pn_env_registry.get(BUNDLE_ID);
    const delta = {};

    if (!envSpec) {
      // Prefer the base spec if it's unused; else auto-suffix
      if (!IMPORTS[baseSpec]) {
	envSpec = baseSpec;
      } else {
	// If baseSpec exists, only reuse it if it maps to the *same* URL.
	if (IMPORTS[baseSpec] === envURL) {
	  envSpec = baseSpec; // identical; no delta
	} else {
	  // Find a free suffixed spec without overriding the map
	  let i = 2;
	  let candidate;
	  do { candidate = `${baseSpec}/${i++}`; } while (IMPORTS[candidate]);
	  envSpec = candidate;
	}
      }

      // Register the chosen spec if it's new
      if (!IMPORTS[envSpec]) {
	IMPORTS[envSpec] = envURL;
	delta[envSpec] = envURL;
	root._pn_spec_catalog.add(envSpec);
      }
      root._pn_env_registry.set(BUNDLE_ID, envSpec);
    }

    // 1) Ensure the shim is ready
    await ensureEsModuleShim();

    installImportMapDelta(delta);

    // 3) Now it's safe to use importShim
    try {
      const Env = await root.importShim(envSpec);
      const Bokeh = Env.Bokeh;           // namespace object exported from the Bokeh ESM
      const Panel = await Env.Panel;     // unwrap the async Panel capture
      const inlineFns = [
        {% for js in (bundle.js_raw if bundle else js_raw) %}
        (Env) => { {{ js|indent(8) }} },
        {% endfor %}
        (Env) => {}
      ];
      for (const fn of inlineFns) {
        try { fn(Env); } catch (e) { if (!reloading) throw e; }
      }
    } catch (err) {
      console.error("[Panel ESM] Failed to initialize bundle", err);
      if (!reloading) throw err;
    }
  })();
})(window);
