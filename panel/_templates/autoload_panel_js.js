{#
Renders JavaScript code for "autoloading".

The code automatically and asynchronously loads BokehJS (if necessary) and
then replaces the AUTOLOAD_TAG ``<script>`` tag that
calls it with the rendered model.

:param js_urls: URLs of JS files making up Bokeh library
:type js_urls: list

:param js_modules: (URL, exported global name or null) pairs of JS modules
:type js_modules: list

:param css_urls: CSS urls to inject
:type css_urls: list

#}
(function(root) {
  function now() {
    return new Date();
  }

  const force = {{ force|default(False)|json }};
  const version = '{{ version }}'.replace('rc', '-rc.').replace('.dev', '-dev.');
  const reloading = {{ reloading|default(False)|json }};
  const Bokeh = root.Bokeh;
  const BK_RE = /^https:\/\/cdn\.bokeh\.org\/bokeh\/(release|dev)\/bokeh-/;
  const PN_RE = /^https:\/\/cdn\.holoviz\.org\/panel\/[^/]+\/dist\/panel/i;
  const JUPYTER_ENDPOINT = "/panel-preview/";
  const JUPYTER_EXTENSION_PATH = JUPYTER_ENDPOINT + "static/extensions/panel/";
  const CDN_DIST = {{ cdn_dist|json }};
  // Endpoint paths and the CDN urls serving the same files: Panel's dist,
  // each extension with a CDN and each BokehJS file.
  const CDN_MAP = {{ cdn_map|json }};
  // Executed notebooks retain this bootstrap when published as static pages.
  const live_notebook = root.Jupyter?.notebook != null || document.querySelector('.jp-LabShell') != null;
  root.__panel_live_notebook__ = live_notebook;
  // The lazy-resource registry needs the same export routing and CDN fallback.
  root.__panel_cdn_dist__ = CDN_DIST;
  root.__panel_cdn_map__ = CDN_MAP;

  function cdn_url(url) {
    const index = url.indexOf(JUPYTER_ENDPOINT);
    if (index === -1) {
      return null;
    }
    const path = url.slice(index + JUPYTER_ENDPOINT.length);
    for (const [prefix, cdn] of CDN_MAP) {
      if (path.startsWith(prefix)) {
        return cdn + path.slice(prefix.length);
      }
    }
    return null;
  }

  function resource_url(url) {
    return !live_notebook || root.__panel_endpoint_failed__ === true ? (cdn_url(url) ?? url) : url;
  }

  // Pending until this bootstrap has loaded everything (or given up), so
  // that output rendered meanwhile can wait for Panel's models.
  let bootstrap_resolve;
  const bootstrap = new Promise((resolve) => { bootstrap_resolve = resolve });
  root.__panel_bootstrap__ = bootstrap;
  function bootstrap_done() {
    if (root.__panel_bootstrap__ === bootstrap) {
      root.__panel_bootstrap__ = null;
    }
    bootstrap_resolve();
  }
  setTimeout(bootstrap_done, Math.max({{ timeout|default(0)|json }}, 15000));

  // jupyter_bokeh, which renders Panel output for comms='ipywidgets' and in
  // VS Code, builds a view as soon as its output arrives, so a notebook run
  // top to bottom can render before BokehJS has loaded or before panel.js
  // has registered the models the view needs. Both the classic notebook and
  // VS Code load jupyter_bokeh through RequireJS, so its fetch is held until
  // the bootstrap is done, and should it already be loaded, ipywidgets
  // awaits render(), which is held instead.
  function hold_bokeh_views(module) {
    const View = module?.BokehView;
    if (View == null || View.prototype.__panel_hold__ === true) {
      return;
    }
    const render = View.prototype.render;
    View.prototype.render = function(...args) {
      const pending = root.__panel_bootstrap__;
      return pending == null ? render.apply(this, args) : pending.then(() => render.apply(this, args));
    };
    View.prototype.__panel_hold__ = true;
  }
  if (root.requirejs != null) {
    for (const name of ["@bokeh/jupyter_bokeh", "nbextensions/jupyter_bokeh/index"]) {
      if (root.requirejs.defined(name)) {
        hold_bokeh_views(root.requirejs(name));
      }
    }
    const load = root.requirejs.load;
    if (load?.__panel_hold__ !== true) {
      root.requirejs.load = function(context, name, url) {
        const pending = root.__panel_bootstrap__;
        if (pending != null && name.includes("jupyter_bokeh")) {
          pending.then(() => load.call(this, context, name, url));
          return;
        }
        return load.call(this, context, name, url);
      };
      root.requirejs.load.__panel_hold__ = true;
    }
    const on_resource_load = root.requirejs.onResourceLoad;
    if (on_resource_load?.__panel_hold__ !== true) {
      // Called once a module is defined but before it is handed to the
      // widget manager that asked for it.
      root.requirejs.onResourceLoad = function(context, map, deps) {
        if (map.id.includes("jupyter_bokeh")) {
          hold_bokeh_views(context.defined[map.id]);
        }
        return on_resource_load?.apply(this, arguments);
      };
      root.requirejs.onResourceLoad.__panel_hold__ = true;
    }
  }

  // Set a timeout for this load but only if we are not already initializing
  if (typeof (root._bokeh_timeout) === "undefined" || (force || !root._bokeh_is_initializing)) {
    root._bokeh_timeout = Date.now() + {{ timeout|default(0)|json }};
    root._bokeh_failed_load = false;
  }

  function run_callbacks() {
    try {
      root._bokeh_onload_callbacks.forEach(function(callback) {
        if (callback != null)
          callback();
      });
    } finally {
      delete root._bokeh_onload_callbacks;
    }
    console.debug("Bokeh: all callbacks have finished");
  }

  function show_jupyter_extension_error() {
    if (!live_notebook) {
      return;
    }
    const element = document.getElementById("{{ error_id }}");
    if (element == null || !element.hidden) {
      return;
    }
    element.style.cssText = "color: #b91c1c; font-family: sans-serif; padding: 0.5em;";
    element.textContent = (
      "Panel could not load resources from its Jupyter server extension. " +
      "Install Panel in the environment running the Jupyter server and restart it."
    );
    element.hidden = false;
  }
  root.__panel_jupyter_extension_error__ = show_jupyter_extension_error;

  {% if check_extension %}
  // Proactively checks the extension is actually installed, rather than
  // waiting for some resource's load to fail. A plain HEAD request for the
  // bundle every notebook session needs is enough to tell.
  if (live_notebook) {
    // Whatever is loaded once the check failed goes straight to the CDN.
    const endpoint_failed = () => {
      root.__panel_endpoint_failed__ = true;
      show_jupyter_extension_error();
    };
    fetch(JUPYTER_EXTENSION_PATH + "panel.min.js", {method: "HEAD"}).then((response) => {
      if (!response.ok) {
        endpoint_failed();
      }
    }).catch(endpoint_failed);
  }
  {% endif %}

  function load_libs(css_urls, js_urls, js_modules, Bokeh, callback) {
    if (css_urls == null) css_urls = [];
    if (js_urls == null) js_urls = [];
    if (js_modules == null) js_modules = [];

    root._bokeh_onload_callbacks.push(callback);

    if (root._bokeh_is_loading > 0) {
      // Don't load bokeh if it is still initializing
      console.debug("Bokeh: BokehJS is being loaded, scheduling callback at", now());
      return null;
    } else if (js_urls.length === 0 && js_modules.length === 0) {
      // There is nothing to load
      run_callbacks();
      return null;
    }

    function on_load() {
      root._bokeh_is_loading--;
      if (root._bokeh_is_loading === 0) {
        console.debug("Bokeh: all BokehJS libraries/stylesheets loaded");
        run_callbacks()
      }
    }
    window._bokeh_on_load = on_load

    function on_error(url) {
      console.error("failed to load " + url);
      if (url.includes(JUPYTER_ENDPOINT + "static/")) {
        show_jupyter_extension_error();
      }
    }

    function fallback_to_cdn(element, url, attribute, parent) {
      const fallback = cdn_url(url);
      if (fallback == null || element.dataset.panelCdnFallback != null) {
        return false;
      }
      element.dataset.panelCdnFallback = "";
      element.remove();
      element[attribute] = fallback;
      parent.appendChild(element);
      return true;
    }

    // Mirrors the AMD guard in panel/models/resources.ts: a UMD library that
    // is not loaded by RequireJS must take its browser-global branch, so
    // define.amd reads as undefined while one of these scripts executes. A
    // module script has no currentScript, so it is told apart by the
    // directory its code was loaded from.
    function install_amd_guard() {
      const define = root.define;
      if (typeof define !== "function" || define.amd == null || define.__panel_no_amd__ === true) {
        return;
      }
      const dirs = root.__panel_no_amd_dirs__ = root.__panel_no_amd_dirs__ || [];
      const hidden = () => {
        const script = document.currentScript;
        if (script != null) {
          return script.hasAttribute("data-panel-no-amd");
        }
        const stack = new Error().stack || "";
        return dirs.some((dir) => stack.includes(dir));
      };
      let amd = define.amd;
      try {
        Object.defineProperty(define, "amd", {
          configurable: true,
          enumerable: true,
          get: () => hidden() ? undefined : amd,
          set: (value) => { amd = value },
        });
        Object.defineProperty(define, "__panel_no_amd__", {value: true});
      } catch (e) {
        console.warn(`Panel: could not hide RequireJS from component libraries: ${e}`);
      }
    }

    function hide_amd(element) {
      element.setAttribute("data-panel-no-amd", "");
      install_amd_guard();
    }

    function hide_amd_module(url) {
      const dirs = root.__panel_no_amd_dirs__ = root.__panel_no_amd_dirs__ || [];
      const dir = new URL(url, document.baseURI).href.split("?")[0].replace(/[^/]*$/, "");
      // panel.js itself lives in a dist root, and must never match.
      if (!/\/(dist|static\/extensions\/panel)\/$/.test(dir) && !dirs.includes(dir)) {
        dirs.push(dir);
      }
      install_amd_guard();
    }

    function inject_script_tag(url) {
      const element = document.createElement('script');
      hide_amd(element);
      element.onload = on_load;
      element.onerror = () => {
        if (!fallback_to_cdn(element, url, "src", document.head)) {
          on_error(url);
        }
      };
      element.async = false;
      element.src = resource_url(url);
      console.debug("Bokeh: injecting script tag for BokehJS library: ", url);
      document.head.appendChild(element);
    }

    const skip = [];
    // Held open until every resource below has been queued, then released
    // by on_load() at the end of this function.
    root._bokeh_is_loading = 1;
    if (window.requirejs) {
      const require_config = {{ config|conffilter }};
      // RequireJS tries each path in turn, so a bundled copy the Jupyter
      // extension cannot serve falls back to the CDN, then to the original.
      const require_urls = (url) => {
        url = resource_url(url);
        const fallback = cdn_url(url);
        return fallback == null || fallback === url ? [url] : [url, fallback];
      };
      for (const [name, path] of Object.entries(require_config.paths || {})) {
        require_config.paths[name] = (Array.isArray(path) ? path : [path]).flatMap(require_urls);
      }
      window.requirejs.config(require_config);
      {% if requirements %}
      // Assigns each library's global as its own module resolves, since a
      // library whose factory reads another's global (e.g. deck.gl's carto
      // layers reading window.deck) runs during the batch, not after it.
      {% for r in requirements %}
      {% if r in exports %}
      define("{{ r }}{{ global_suffix }}", ["{{ r }}"], function(module) {
        const name = "{{ exports[r] }}"
        const existing = window[name]
        // A library that never calls define() (plotly.js) resolves to
        // undefined but has assigned its global itself.
        if (module == null) {
          return existing
        }
        // Several packages can contribute to one namespace (deck.gl's core,
        // json and carto bundles all publish `deck`), so merge into a fresh
        // object rather than overwrite.
        if (existing != null && typeof existing === "object" &&
            module != null && typeof module === "object") {
          window[name] = Object.assign({}, existing, module)
        } else {
          window[name] = module
        }
        return window[name]
      })
      {% endif %}
      {% endfor %}
      root._bokeh_is_loading++;
      // Required in stages so a library reading another's global finds it
      // assigned, and so one failing library doesn't stop the rest.
      const require_stages = {{ require_stages|default([])|json }};
      const assign_resolved = () => {
        {% for r in requirements %}
        {% if r in exports %}
        if (window.requirejs.defined("{{ r }}{{ global_suffix }}")) {
          require("{{ r }}{{ global_suffix }}")
        }
        {% endif %}
        {% endfor %}
      };
      const require_stage = (index) => {
        if (index >= require_stages.length) {
          // Only now are the globals the components read actually assigned.
          require_ready_resolve()
          on_load()
          return
        }
        require(require_stages[index], () => require_stage(index + 1), (error) => {
          const modules = error.requireModules ? error.requireModules.join(', ') : 'unknown';
          console.error(`Panel: requirejs failed to load ${modules}: ${error.requireType} ${error.message}`);
          // Publish whatever this stage did resolve, so that one library
          // failing does not blank every component on the page.
          assign_resolved()
          on_error(modules)
          require_stage(index + 1)
        })
      };
      require_stage(0)
      {% endif %}
    }

    const existing_stylesheets = []
    const links = document.getElementsByTagName('link')
    for (let i = 0; i < links.length; i++) {
      const link = links[i]
      if (link.href != null) {
        existing_stylesheets.push(link.href)
      }
    }
    for (let i = 0; i < css_urls.length; i++) {
      const url = css_urls[i];
      const escaped = encodeURI(url)
      if (existing_stylesheets.indexOf(escaped) !== -1) {
        continue;
      }
      const element = document.createElement("link");
      root._bokeh_is_loading++;
      element.onload = on_load;
      element.onerror = () => {
        if (!fallback_to_cdn(element, url, "href", document.body)) {
          on_error(url);
        }
      };
      element.rel = "stylesheet";
      element.type = "text/css";
      element.href = resource_url(url);
      console.debug("Bokeh: injecting link tag for BokehJS stylesheet: ", url);
      document.body.appendChild(element);
    }

    {%- for lib, urls in skip_imports.items() %}
    // The global is already there, so re-fetching what provides it is waste.
    if ((window.{{ lib }} !== undefined) && (!(window.{{ lib }} instanceof HTMLElement))) {
      var urls = {{ urls }};
      for (var i = 0; i < urls.length; i++) {
        skip.push(encodeURI(urls[i]))
      }
    }
    {%- endfor %}
    {%- if require_skip %}
    // RequireJS already has its own path for these, so a script tag would
    // load them a second time and corrupt RequireJS' module resolution.
    if (window.requirejs) {
      var urls = {{ require_skip|json }};
      for (var i = 0; i < urls.length; i++) {
        skip.push(encodeURI(urls[i]))
      }
    }
    {%- endif %}
    var existing_scripts = []
    const scripts = document.getElementsByTagName('script')
    for (let i = 0; i < scripts.length; i++) {
      var script = scripts[i]
      if (script.src != null) {
        existing_scripts.push(script.src)
      }
    }
    for (let i = 0; i < js_urls.length; i++) {
      const url = js_urls[i];
      const escaped = encodeURI(url)
      const shouldSkip = skip.includes(escaped) || existing_scripts.includes(escaped)
      const isBokehOrPanel = BK_RE.test(escaped) || PN_RE.test(escaped)
      const missingOrBroken = Bokeh == null || Bokeh.Panel == null || (Bokeh.version != version && !Bokeh.versions?.has(version)) || Bokeh.versions?.get(version)?.Panel == null;
      if (shouldSkip && !(isBokehOrPanel && missingOrBroken)) {
        continue;
      }
      root._bokeh_is_loading++;
      inject_script_tag(url);
    }
    for (let i = 0; i < js_modules.length; i++) {
      const [url, name] = js_modules[i];
      const escaped = encodeURI(url)
      const loaded = name == null ? existing_scripts.indexOf(escaped) !== -1 : root[name] != null
      if (skip.indexOf(escaped) !== -1 || loaded) {
        continue;
      }
      var element = document.createElement('script');
      hide_amd_module(resource_url(url));
      root._bokeh_is_loading++;
      element.onerror = () => {
        if (!fallback_to_cdn(element, url, "src", document.head)) {
          on_error(url);
        }
      };
      element.async = false;
      element.type = "module";
      if (name == null) {
        element.onload = on_load;
        element.src = resource_url(url);
      } else {
        // Namespace import rather than a default import, matching what the
        // resource registry's module wrapper assigns, so a library that only
        // has named exports resolves to its namespace instead of to undefined.
        // The import loads the module, so it gets no bare tag as well. The url
        // is absolutized because an import specifier resolves through the
        // import map unless it starts with a scheme, / or ./, whereas a src
        // resolves against the document.
        element.textContent = `
        import * as ns from "${new URL(resource_url(url), document.baseURI).href}"
        window.${name} = ns.default ?? ns
        window._bokeh_on_load()
        `
      }
      console.debug("Bokeh: injecting script tag for BokehJS library: ", url);
      document.head.appendChild(element);
    }
    // Releases the reservation taken above, running the callbacks now if
    // nothing else is outstanding.
    on_load()
  };

  function inject_raw_css(css) {
    const element = document.createElement("style");
    element.appendChild(document.createTextNode(css));
    document.body.appendChild(element);
  }

  const js_urls = {{ bundle.js_urls|json }};
  const js_modules = {{ bundle.js_module_tags|json }};
  const css_urls = {{ bundle.css_urls|json }};
  const inline_js = [
    {%- for css in bundle.css_raw %}
    function(Bokeh) {
      inject_raw_css({{ css|json }});
    },
    {%- endfor %}
    {%- for js in (bundle.js_raw if bundle else js_raw) %}
    function(Bokeh, define, module, exports) {
      {# No indent filter: it splits on every character Python's splitlines()
         treats as a line break, which minified libraries (xterm.js) carry
         inside their string literals. #}
{{ js }}
    },
    {% endfor -%}
    function(Bokeh, define, module, exports) {} // ensure no trailing comma for IE
  ];

  // Resolved once RequireJS has loaded its libraries and assigned their
  // globals, so the resource registry can wait for them instead of racing.
  let require_ready_resolve;
  const require_ready = new Promise((resolve) => { require_ready_resolve = resolve });
  {%- if requirements %}
  // A claimed library that is never released would keep its components from
  // ever rendering, so the wait is bounded by the same timeout as the load.
  setTimeout(() => require_ready_resolve(), {{ timeout|default(0)|json }} || 5000);
  {%- else %}
  require_ready_resolve();
  {%- endif %}

  // Module exports are only assigned once their libraries have loaded. A
  // library that fails to load never finishes the load, so the wait is bounded
  // and the registry loads whatever is still missing itself.
  let libs_ready_resolve;
  const libs_ready = new Promise((resolve) => { libs_ready_resolve = resolve });
  setTimeout(() => libs_ready_resolve(), {{ timeout|default(0)|json }} || 5000);

  function declare_resources() {
    // Tells the panel.js resource registry which component libraries this
    // bundle has already satisfied, so nothing is fetched a second time.
    // In inline mode the libraries have no URLs at all, which makes this
    // the only way the registry can know about them.
    const declared = {{ bundle.resource_declarations|default({})|json }};
    if (!declared || !(declared.libs || declared.css)) {
      return;
    }
    // Libraries RequireJS is loading are claimed against require_ready
    // instead of being declared, since they are not ready yet.
    const require_urls = window.requirejs ? {{ require_skip|default([])|json }} : [];
    const satisfied = [], pending = [], exporting = [];
    for (const lib of declared.libs || []) {
      const urls = lib.js || [];
      const by_require = urls.length > 0 && urls.every((url) => require_urls.includes(url));
      const exports = (lib.modules || []).some((module) => module.export != null);
      (by_require ? pending : exports ? exporting : satisfied).push(lib);
    }
    const declarations = [{libs: satisfied, css: declared.css}];
    if (pending.length > 0) {
      declarations.push({libs: pending, ready: require_ready});
    }
    if (exporting.length > 0) {
      declarations.push({libs: exporting, ready: libs_ready});
    }
    for (const declaration of declarations) {
      if (root.__panel_resources__ != null) {
        if (declaration.ready != null) {
          root.__panel_resources__.claim(declaration, declaration.ready);
        } else {
          root.__panel_resources__.declare(declaration);
        }
      } else {
        (root.__panel_resources_declared__ = root.__panel_resources_declared__ || []).push(declaration);
      }
    }
  }

  function run_inline_js() {
    if ((root.Bokeh !== undefined) || (force === true)) {
      for (let i = 0; i < inline_js.length; i++) {
        try {
          inline_js[i].call(root, root.Bokeh);
        } catch(e) {
          if (!reloading) {
            throw e;
          }
        }
      }
      // Views waiting on this run once the current task is done, by which
      // point the load callback has also restored root.Bokeh.
      bootstrap_done();
    } else if (Date.now() < root._bokeh_timeout) {
      setTimeout(run_inline_js, 100);
    } else if (!root._bokeh_failed_load) {
      console.log("Bokeh: BokehJS failed to load within specified timeout.");
      root._bokeh_failed_load = true;
      bootstrap_done();
    }
    root._bokeh_is_initializing = false;
  }

  function load_or_wait() {
    // Implement a backoff loop that tries to ensure we do not load multiple
    // versions of Bokeh and its dependencies at the same time.
    // In recent versions we use the root._bokeh_is_initializing flag
    // to determine whether there is an ongoing attempt to initialize
    // bokeh, however for backward compatibility we also try to ensure
    // that we do not start loading a newer (Panel>=1.0 and Bokeh>3) version
    // before older versions are fully initialized.
    if (root._bokeh_is_initializing && Date.now() > root._bokeh_timeout) {
      // If the timeout and bokeh was not successfully loaded we reset
      // everything and try loading again
      root._bokeh_timeout = Date.now() + {{ timeout|default(0)|json }};
      root._bokeh_is_initializing = false;
      root._bokeh_onload_callbacks = undefined;
      root._bokeh_is_loading = 0;
      console.log("Bokeh: BokehJS was loaded multiple times but one version failed to initialize.");
      load_or_wait();
    } else if (root._bokeh_is_initializing || (typeof root._bokeh_is_initializing === "undefined" && root._bokeh_onload_callbacks !== undefined)) {
      setTimeout(load_or_wait, 100);
    } else {
      root._bokeh_is_initializing = true;
      root._bokeh_onload_callbacks = [];
      const bokeh_loaded = Bokeh != null && ((Bokeh.version === version && Bokeh.Panel) || (Bokeh.versions?.has(version) && Bokeh.versions.get(version)?.Panel));
      if (!reloading && !bokeh_loaded) {
        if (root.Bokeh) {
          root.Bokeh = undefined;
        }
        console.debug("Bokeh: BokehJS not loaded, scheduling load and callback at", now());
      }
      load_libs(css_urls, js_urls, js_modules, Bokeh, function() {
        console.debug("Bokeh: BokehJS plotting callback run at", now());
        libs_ready_resolve();
        run_inline_js();
        if (Bokeh != undefined && !reloading) {
          const NewBokeh = root.Bokeh;
          if (Bokeh.versions === undefined) {
            Bokeh.versions = new Map();
          }
          if (NewBokeh.version !== Bokeh.version) {
            Bokeh[NewBokeh.version] = NewBokeh;
            Bokeh.versions.set(NewBokeh.version, NewBokeh);
          }
          root.Bokeh = Bokeh;
        }
      });
    }
  }
  // Declared synchronously, before anything is scheduled, so a cell whose
  // output embeds while libraries are still loading finds this in place
  // instead of fetching its own second copy of each.
  declare_resources();
  // Give older versions of the autoload script a head-start to ensure
  // they initialize before we start loading newer version.
  setTimeout(load_or_wait, 100)
}(window));
