{#
Renders JavaScript code for "autoloading".

The code automatically and asynchronously loads BokehJS (if necessary) and
then replaces the AUTOLOAD_TAG ``<script>`` tag that
calls it with the rendered model.

:param js_urls: URLs of JS files making up Bokeh library
:type js_urls: list

:param js_modules: URLs of JS modules making up Bokeh library
:type js_modules: list

:param js_exports: URLs of JS modules to be exported
:type js_exports: dict

:param css_urls: CSS urls to inject
:type css_urls: list

#}
(function(root) {
  function now() {
    return new Date();
  }

  var force = {{ force|default(False)|json }};
  var py_version = '{{ version }}'.replace('rc', '-rc.').replace('.dev', '-dev.');
  var is_dev = py_version.indexOf("+") !== -1 || py_version.indexOf("-") !== -1;
  var reloading = {{ reloading|default(False)|json }};
  var Bokeh = root.Bokeh;
  var bokeh_loaded = Bokeh != null && (Bokeh.version === py_version || (Bokeh.versions !== undefined && Bokeh.versions.has(py_version)));

  if (typeof (root._bokeh_timeout) === "undefined" || force) {
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

  function load_libs(css_urls, js_urls, js_modules, js_exports, callback) {
    if (css_urls == null) css_urls = [];
    if (js_urls == null) js_urls = [];
    if (js_modules == null) js_modules = [];
    if (js_exports == null) js_exports = {};

    root._bokeh_onload_callbacks.push(callback);

    if (root._bokeh_is_loading > 0) {
      console.debug("Bokeh: BokehJS is being loaded, scheduling callback at", now());
      return null;
    }
    if (js_urls.length === 0 && js_modules.length === 0 && Object.keys(js_exports).length === 0) {
      run_callbacks();
      return null;
    }
    if (!reloading) {
      console.debug("Bokeh: BokehJS not loaded, scheduling load and callback at", now());
    }

    function on_load() {
      root._bokeh_is_loading--;
      if (root._bokeh_is_loading === 0) {
        console.debug("Bokeh: all BokehJS libraries/stylesheets loaded");
        run_callbacks()
      }
    }
    window._bokeh_on_load = on_load

    function on_error() {
      console.error("failed to load " + url);
    }

    var skip = [];
    if (window.requirejs) {
      window.requirejs.config({{ config|conffilter }});
      {% for r in requirements %}
      require(["{{ r }}"], function({{ exports[r] }}) {
	{% if r in exports %}
	window.{{ exports[r] }} = {{ exports[r] }}
	{% endif %}
	on_load()
      })
      {% endfor %}
      root._bokeh_is_loading = css_urls.length + {{ requirements|length }};
    } else {
      root._bokeh_is_loading = css_urls.length + js_urls.length + js_modules.length + Object.keys(js_exports).length;
    }

    var existing_stylesheets = []
    var links = document.getElementsByTagName('link')
    for (var i = 0; i < links.length; i++) {
      var link = links[i]
      if (link.href != null) {
	existing_stylesheets.push(link.href)
      }
    }
    for (var i = 0; i < css_urls.length; i++) {
      var url = css_urls[i];
      if (existing_stylesheets.indexOf(url) !== -1) {
	on_load()
	continue;
      }
      const element = document.createElement("link");
      element.onload = on_load;
      element.onerror = on_error;
      element.rel = "stylesheet";
      element.type = "text/css";
      element.href = url;
      console.debug("Bokeh: injecting link tag for BokehJS stylesheet: ", url);
      document.body.appendChild(element);
    }

    {%- for lib, urls in skip_imports.items() %}
    if (((window['{{ lib }}'] !== undefined) && (!(window['{{ lib }}'] instanceof HTMLElement))) || window.requirejs) {
      var urls = {{ urls }};
      for (var i = 0; i < urls.length; i++) {
        skip.push(urls[i])
      }
    }
    {%- endfor %}
    var existing_scripts = []
    var scripts = document.getElementsByTagName('script')
    for (var i = 0; i < scripts.length; i++) {
      var script = scripts[i]
      if (script.src != null) {
	existing_scripts.push(script.src)
      }
    }
    for (var i = 0; i < js_urls.length; i++) {
      var url = js_urls[i];
      if (skip.indexOf(url) !== -1 || existing_scripts.indexOf(url) !== -1) {
	if (!window.requirejs) {
	  on_load();
	}
	continue;
      }
      var element = document.createElement('script');
      element.onload = on_load;
      element.onerror = on_error;
      element.async = false;
      element.src = url;
      console.debug("Bokeh: injecting script tag for BokehJS library: ", url);
      document.head.appendChild(element);
    }
    for (var i = 0; i < js_modules.length; i++) {
      var url = js_modules[i];
      if (skip.indexOf(url) !== -1 || existing_scripts.indexOf(url) !== -1) {
	if (!window.requirejs) {
	  on_load();
	}
	continue;
      }
      var element = document.createElement('script');
      element.onload = on_load;
      element.onerror = on_error;
      element.async = false;
      element.src = url;
      element.type = "module";
      console.debug("Bokeh: injecting script tag for BokehJS library: ", url);
      document.head.appendChild(element);
    }
    for (const name in js_exports) {
      var url = js_exports[name];
      if (skip.indexOf(url) >= 0 || root[name] != null) {
	if (!window.requirejs) {
	  on_load();
	}
	continue;
      }
      var element = document.createElement('script');
      element.onerror = on_error;
      element.async = false;
      element.type = "module";
      console.debug("Bokeh: injecting script tag for BokehJS library: ", url);
      element.textContent = `
      import ${name} from "${url}"
      window.${name} = ${name}
      window._bokeh_on_load()
      `
      document.head.appendChild(element);
    }
    if (!js_urls.length && !js_modules.length) {
      on_load()
    }
  };

  function inject_raw_css(css) {
    const element = document.createElement("style");
    element.appendChild(document.createTextNode(css));
    document.body.appendChild(element);
  }

  var js_urls = {{ bundle.js_urls|json }};
  var js_modules = {{ bundle.js_modules|json }};
  var js_exports = {{ bundle.js_module_exports|json }};
  var css_urls = {{ bundle.css_urls|json }};
  var inline_js = [
    {%- for css in bundle.css_raw %}
    function(Bokeh) {
      inject_raw_css({{ css|json }});
    },
    {%- endfor %}
    {%- for js in (bundle.js_raw if bundle else js_raw) %}
    function(Bokeh) {
      {{ js|indent(6) }}
    },
    {% endfor -%}
    function(Bokeh) {} // ensure no trailing comma for IE
  ];

  function run_inline_js() {
    if ((root.Bokeh !== undefined) || (force === true)) {
      for (var i = 0; i < inline_js.length; i++) {
        inline_js[i].call(root, root.Bokeh);
      }
      // Cache old bokeh versions
      if (Bokeh != undefined && !reloading) {
	var NewBokeh = root.Bokeh;
	if (Bokeh.versions === undefined) {
	  Bokeh.versions = new Map();
	}
	if (NewBokeh.version !== Bokeh.version) {
	  Bokeh.versions.set(NewBokeh.version, NewBokeh)
	}
	root.Bokeh = Bokeh;
      }
      {%- if elementid -%}
      if (force === true) {
        display_loaded();
      }
      {%- endif -%}
    } else if (Date.now() < root._bokeh_timeout) {
      setTimeout(run_inline_js, 100);
    } else if (!root._bokeh_failed_load) {
      console.log("Bokeh: BokehJS failed to load within specified timeout.");
      root._bokeh_failed_load = true;
    }
    root._bokeh_is_initializing = false
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
      root._bokeh_is_initializing = false;
      root._bokeh_onload_callbacks = undefined;
      console.log("Bokeh: BokehJS was loaded multiple times but one version failed to initialize.");
      load_or_wait();
    } else if (root._bokeh_is_initializing || (typeof root._bokeh_is_initializing === "undefined" && root._bokeh_onload_callbacks !== undefined)) {
      setTimeout(load_or_wait, 100);
    } else {
      Bokeh = root.Bokeh;
      bokeh_loaded = Bokeh != null && (Bokeh.version === py_version || (Bokeh.versions !== undefined && Bokeh.versions.has(py_version)));
      root._bokeh_is_initializing = true
      root._bokeh_onload_callbacks = []
      if (!reloading && (!bokeh_loaded || is_dev)) {
	root.Bokeh = undefined;
      }
      load_libs(css_urls, js_urls, js_modules, js_exports, function() {
	console.debug("Bokeh: BokehJS plotting callback run at", now());
	run_inline_js();
      });
    }
  }
  // Give older versions of the autoload script a head-start to ensure
  // they initialize before we start loading newer version.
  setTimeout(load_or_wait, 100)
}(window));
