(function() {
  const BUNDLE_ID   = {{ BUNDLE_ID|json }};
  const docs_json   = {{ docs_json }};
  const render_items = {{ render_items }};

  if (!docs_json || !render_items || !render_items.length) return;

  // --- only wait for importShim; do NOT inject it ---
  async function waitForImportShim(maxTries=200, intervalMs=25) {
    let tries = 0;
    while (!globalThis.importShim) {
      if (document.readyState === "complete" && tries++ >= maxTries) {
        throw new Error("[Panel ESM] importShim not available");
      }
      await new Promise(r => setTimeout(r, intervalMs));
    }
  }

  // --- resolve the env spec for a bundle id (handles suffixed variants) ---
  function resolve_env_spec(bundleId) {
    // Prefer registry populated by the loader
    const reg = globalThis._pn_env_registry;
    if (reg && typeof reg.get === "function") {
      const spec = reg.get(bundleId);
      if (spec) return spec;
    }
    // Fallback: scan the current import map snapshot we’ve been appending to
    const imports = (globalThis._pn_imports && globalThis._pn_imports.imports) || {};
    const base = `@pn/env/${bundleId}`;
    if (imports[base]) return base;

    // Pick the highest numeric suffix if multiple exist
    const candidates = Object.keys(imports).filter(k => k === base || k.startsWith(base + "/"));
    if (!candidates.length) throw new Error(`[Panel ESM] No env module registered for bundleId ${bundleId}`);
    const best = candidates
      .map(k => [k, Number(k.slice(base.length + 1)) || 1])
      .sort((a, b) => b[1] - a[1])[0][0];
    return best;
  }

  // --- import Env and return Env ---
  async function load_env(bundleId) {
    await waitForImportShim();
    const spec = resolve_env_spec(bundleId);
    const Env  = await importShim(spec);
    await Env.Panel;
    if (!Env.Bokeh) throw new Error("[Panel ESM] Env.Bokeh missing");
    return Env;
  }

  // --- post-embed tweaks (same as your original) ---
  function postprocess_roots() {
    for (const render_item of render_items) {
      for (const root_id of render_item.root_ids || []) {
        const id_el = document.getElementById(root_id);
        if (id_el && id_el.children.length && id_el.children[0].hasAttribute('data-root-id')) {
          const root_el = id_el.children[0];
          root_el.id = root_el.id + '-rendered';
          for (const child of root_el.children) {
            // Ensure JupyterLab does not capture keyboard shortcuts
            // https://jupyterlab.readthedocs.io/en/4.1.x/extension/notebook.html#keyboard-interaction-model
            child.setAttribute('data-lm-suppress-shortcuts', 'true');
          }
        }
      }
    }
  }

  async function embed_document() {
    const { Bokeh } = await load_env(BUNDLE_ID);  // Panel is awaited inside load_env
    if (!Bokeh.embed?.embed_items_notebook)
      throw new Error("[Panel ESM] Bokeh.embed.embed_items_notebook not available");
    await Bokeh.embed.embed_items_notebook(docs_json, render_items);
    postprocess_roots();
  }

  (async () => {
    try {
      await embed_document();
    } catch (err) {
      let tries = 0;
      const timer = setInterval(async () => {
        try {
          await embed_document();
          clearInterval(timer);
        } catch (e) {
          if (document.readyState === "complete" && ++tries > 200) {
            clearInterval(timer);
            console.warn("Panel: ERROR: Unable to render after waiting for importShim/env", e);
          }
        }
      }, 25);
    }
  })();
})();
