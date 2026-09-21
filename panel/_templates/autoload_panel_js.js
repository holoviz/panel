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
  const JUPYTER_EXTENSION_PATH = "/panel-preview/static/extensions/panel/";
  const CDN_DIST = {{ cdn_dist|json }};
  // Exposed so the lazy-resource registry (models/resources.ts) can fall
  // back to the CDN for the same endpoint, not just the eager bootstrap
  // resources loaded below.
  root.__panel_cdn_dist__ = CDN_DIST;

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
  fetch(JUPYTER_EXTENSION_PATH + "panel.min.js", {method: "HEAD"}).then((response) => {
    if (!response.ok) {
      show_jupyter_extension_error();
    }
  }).catch(() => show_jupyter_extension_error());
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
      if (url.includes(JUPYTER_EXTENSION_PATH)) {
        show_jupyter_extension_error();
      }
    }

    function fallback_to_cdn(element, url, attribute, parent) {
      const index = url.indexOf(JUPYTER_EXTENSION_PATH);
      if (index === -1 || element.dataset.panelCdnFallback != null) {
        return false;
      }
      element.dataset.panelCdnFallback = "";
      element.remove();
      element[attribute] = CDN_DIST + url.slice(index + JUPYTER_EXTENSION_PATH.length);
      parent.appendChild(element);
      return true;
    }

    function inject_script_tag(url) {
      const element = document.createElement('script');
      element.onload = on_load;
      element.onerror = () => {
        if (!fallback_to_cdn(element, url, "src", document.head)) {
          on_error(url);
        }
      };
      element.async = false;
      element.src = url;
      console.debug("Bokeh: injecting script tag for BokehJS library: ", url);
      document.head.appendChild(element);
    }

    const skip = [];
    // Held open until every resource below has been queued, then released
    // by on_load() at the end of this function.
    root._bokeh_is_loading = 1;
    if (window.requirejs) {
      window.requirejs.config({{ config|conffilter }});
      {% if requirements %}
      // Assigns each library's global as its own module resolves, since a
      // library whose factory reads another's global (e.g. deck.gl's carto
      // layers reading window.deck) runs during the batch, not after it.
      {% for r in requirements %}
      {% if r in exports %}
      define("{{ r }}{{ global_suffix }}", ["{{ r }}"], function(module) {
        const name = "{{ exports[r] }}"
        const existing = window[name]
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
      element.href = url;
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
        element.src = url;
      } else {
        // Namespace import rather than a default import, matching what the
        // resource registry's module wrapper assigns, so a library that only
        // has named exports resolves to its namespace instead of to undefined.
        // The import loads the module, so it gets no bare tag as well. The url
        // is absolutized because an import specifier resolves through the
        // import map unless it starts with a scheme, / or ./, whereas a src
        // resolves against the document.
        element.textContent = `
        import * as ns from "${new URL(url, document.baseURI).href}"
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
      {{ js|indent(6) }}
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
    } else if (Date.now() < root._bokeh_timeout) {
      setTimeout(run_inline_js, 100);
    } else if (!root._bokeh_failed_load) {
      console.log("Bokeh: BokehJS failed to load within specified timeout.");
      root._bokeh_failed_load = true;
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
