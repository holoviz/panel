/*
 * Minimal MCP Apps (SEP-1865) client for the Panel document.
 *
 * This runs before Bokeh/Panel JS so the `ui/initialize` handshake completes as
 * early as possible: hosts send `ui/notifications/tool-input` immediately after
 * initialize resolves, which is long before the Panel session has a WebSocket.
 * Notifications received before Python attaches are buffered and replayed.
 *
 * Deliberately dependency-free vanilla ES5-ish JS: the View runs under a strict
 * CSP without `unsafe-eval`, which rules out the SDK's Zod JIT paths.
 */
(function() {
  "use strict";

  var PROTOCOL_VERSION = "2026-01-26";
  var parent = window.parent;

  if (!parent || parent === window) {
    // Not embedded, so there is no host to talk to. Leave the bridge undefined
    // so the Panel model knows to stay inert rather than wait for a handshake.
    return;
  }

  var nextId = 1;
  var pending = {};
  var buffered = [];
  var handlers = {notification: null, request: null};

  var bridge = {
    state: "connecting",
    hostContext: {},
    hostCapabilities: {},
    hostInfo: null,
    protocolVersion: null,
    error: null,
    onstatechange: null
  };

  function setState(state, error) {
    bridge.state = state;
    bridge.error = error || null;
    if (bridge.onstatechange) {
      try {
        bridge.onstatechange(state, bridge.error);
      } catch (e) {
        console.error("panel-mcp: onstatechange handler failed", e);
      }
    }
  }

  function send(msg) {
    // The host origin is not knowable ahead of time (hosts mint per-conversation
    // sandbox origins), and the spec's own reference client uses "*" here.
    parent.postMessage(msg, "*");
  }

  function request(method, params) {
    var id = nextId++;
    return new Promise(function(resolve, reject) {
      pending[id] = {resolve: resolve, reject: reject};
      send({jsonrpc: "2.0", id: id, method: method, params: params || {}});
    });
  }

  function notify(method, params) {
    send({jsonrpc: "2.0", method: method, params: params || {}});
  }

  function respond(id, result) {
    send({jsonrpc: "2.0", id: id, result: result || {}});
  }

  function respondError(id, code, message) {
    send({jsonrpc: "2.0", id: id, error: {code: code, message: message}});
  }

  function mergeHostContext(patch) {
    if (!patch) {
      return;
    }
    for (var key in patch) {
      if (Object.prototype.hasOwnProperty.call(patch, key)) {
        bridge.hostContext[key] = patch[key];
      }
    }
  }

  function dispatchNotification(method, params) {
    if (handlers.notification) {
      try {
        handlers.notification(method, params);
      } catch (e) {
        console.error("panel-mcp: notification handler failed", e);
      }
    } else {
      buffered.push({method: method, params: params});
    }
  }

  function handleRequest(msg) {
    if (msg.method === "ping") {
      respond(msg.id, {});
      return;
    }
    if (handlers.request) {
      var result;
      try {
        result = handlers.request(msg.method, msg.params);
      } catch (e) {
        respondError(msg.id, -32000, String((e && e.message) || e));
        return;
      }
      if (result && typeof result.then === "function") {
        result.then(
          function(value) { respond(msg.id, value); },
          function(err) { respondError(msg.id, -32000, String((err && err.message) || err)); }
        );
      } else {
        respond(msg.id, result);
      }
      return;
    }
    // Defaults for requests that arrive before Python attaches. Teardown is
    // acknowledged so the host is never left waiting on a session that may
    // never connect; tools/list is empty until the app registers any.
    if (msg.method === "ui/resource-teardown") {
      respond(msg.id, {});
    } else if (msg.method === "tools/list") {
      respond(msg.id, {tools: []});
    } else {
      respondError(msg.id, -32601, "Method not found: " + msg.method);
    }
  }

  window.addEventListener("message", function(event) {
    if (event.source !== parent) {
      return;
    }
    var msg = event.data;
    if (!msg || msg.jsonrpc !== "2.0") {
      return;
    }
    var hasId = msg.id !== undefined && msg.id !== null;
    if (hasId && msg.method === undefined) {
      var entry = pending[msg.id];
      if (!entry) {
        return;
      }
      delete pending[msg.id];
      if (msg.error) {
        entry.reject(msg.error);
      } else {
        entry.resolve(msg.result);
      }
      return;
    }
    if (msg.method === undefined) {
      return;
    }
    if (hasId) {
      handleRequest(msg);
      return;
    }
    if (msg.method === "ui/notifications/host-context-changed") {
      mergeHostContext(msg.params);
      applyHostStyles();
      if (msg.params && "containerDimensions" in msg.params && document.body) {
        applyContainerDimensions();
      }
    }
    dispatchNotification(msg.method, msg.params);
  });

  /* -------------------------------------------------------------------- */
  /* Theming                                                              */
  /* -------------------------------------------------------------------- */

  var styleEl = null;
  var fontEl = null;

  function applyHostStyles() {
    var styles = bridge.hostContext.styles;
    if (!styles) {
      return;
    }
    var variables = styles.variables;
    if (variables) {
      var decls = [];
      for (var key in variables) {
        if (Object.prototype.hasOwnProperty.call(variables, key) && variables[key] != null) {
          decls.push(key + ": " + variables[key] + ";");
        }
      }
      if (decls.length) {
        if (!styleEl) {
          styleEl = document.createElement("style");
          styleEl.setAttribute("data-panel-mcp", "host-variables");
          document.head.appendChild(styleEl);
        }
        styleEl.textContent = ":root, :host {\n  " + decls.join("\n  ") + "\n}";
      }
    }
    var css = styles.css;
    if (css && css.fonts) {
      if (!fontEl) {
        fontEl = document.createElement("style");
        fontEl.setAttribute("data-panel-mcp", "host-fonts");
        // @import must precede other rules, so fonts get their own element
        // inserted ahead of the variables block.
        document.head.insertBefore(fontEl, document.head.firstChild);
      }
      fontEl.textContent = css.fonts;
    }
    var theme = bridge.hostContext.theme;
    if (theme === "light" || theme === "dark") {
      document.documentElement.style.colorScheme = theme;
      document.documentElement.setAttribute("data-mcp-theme", theme);
    }
  }

  /* -------------------------------------------------------------------- */
  /* Container dimensions and size reporting                              */
  /* -------------------------------------------------------------------- */

  var resizeObserver = null;
  var lastWidth = -1;
  var lastHeight = -1;
  var resizeTimer = null;

  function applyContainerDimensions() {
    var dims = bridge.hostContext.containerDimensions;
    var root = document.documentElement;
    var fixedHeight = false;
    var fixedWidth = false;
    // Hosts switch between fixed and flexible boxes (e.g. fullscreen and back
    // to inline), so clear whatever the previous context imposed.
    root.style.height = "";
    root.style.maxHeight = "";
    root.style.width = "";
    root.style.maxWidth = "";
    if (dims) {
      if ("height" in dims && dims.height != null) {
        root.style.height = "100vh";
        fixedHeight = true;
      } else if (dims.maxHeight != null) {
        root.style.maxHeight = dims.maxHeight + "px";
      }
      if ("width" in dims && dims.width != null) {
        root.style.width = "100vw";
        fixedWidth = true;
      } else if (dims.maxWidth != null) {
        root.style.maxWidth = dims.maxWidth + "px";
      }
    }
    // Only report our own size when the host lets the View drive at least one
    // dimension; otherwise the host already controls the box.
    if (!(fixedHeight && fixedWidth)) {
      lastWidth = -1;
      lastHeight = -1;
      startSizeReporting();
      reportSize();
    }
  }

  function reportSize() {
    var body = document.body;
    if (!body) {
      return;
    }
    var rect = body.getBoundingClientRect();
    var width = Math.ceil(rect.width);
    var height = Math.ceil(rect.height);
    if (width === lastWidth && height === lastHeight) {
      return;
    }
    lastWidth = width;
    lastHeight = height;
    notify("ui/notifications/size-changed", {width: width, height: height});
  }

  function startSizeReporting() {
    if (resizeObserver || typeof ResizeObserver === "undefined" || !document.body) {
      return;
    }
    resizeObserver = new ResizeObserver(function() {
      // ResizeObserver fires many times per frame while Bokeh lays out; debounce
      // so the host isn't flooded with near-identical notifications.
      if (resizeTimer != null) {
        clearTimeout(resizeTimer);
      }
      resizeTimer = setTimeout(reportSize, 100);
    });
    resizeObserver.observe(document.body);
  }

  /* -------------------------------------------------------------------- */
  /* Public surface consumed by panel/models/mcp.ts                       */
  /* -------------------------------------------------------------------- */

  bridge.request = request;
  bridge.notify = notify;

  /*
   * Called by the Bokeh model once the Panel session is connected. Registers
   * the live handlers and replays everything buffered during startup.
   */
  bridge.attach = function(notificationHandler, requestHandler) {
    handlers.notification = notificationHandler || null;
    handlers.request = requestHandler || null;
    var replay = buffered;
    buffered = [];
    if (handlers.notification) {
      for (var i = 0; i < replay.length; i++) {
        try {
          handlers.notification(replay[i].method, replay[i].params);
        } catch (e) {
          console.error("panel-mcp: replay failed", e);
        }
      }
    }
    setState("attached");
    return {
      hostContext: bridge.hostContext,
      hostCapabilities: bridge.hostCapabilities,
      hostInfo: bridge.hostInfo,
      protocolVersion: bridge.protocolVersion
    };
  };

  bridge.detach = function() {
    handlers.notification = null;
    handlers.request = null;
  };

  window.__panelMCP__ = bridge;

  /* -------------------------------------------------------------------- */
  /* Handshake                                                            */
  /* -------------------------------------------------------------------- */

  bridge.ready = request("ui/initialize", {
    protocolVersion: PROTOCOL_VERSION,
    appInfo: {name: "panel", version: window.__panelMCPVersion__ || "unknown"},
    appCapabilities: {
      tools: {listChanged: true},
      availableDisplayModes: ["inline", "fullscreen"]
    }
  }).then(function(result) {
    result = result || {};
    bridge.protocolVersion = result.protocolVersion || null;
    bridge.hostCapabilities = result.hostCapabilities || {};
    bridge.hostInfo = result.hostInfo || null;
    mergeHostContext(result.hostContext);
    notify("ui/notifications/initialized", {});
    setState("connected");
    applyHostStyles();
    if (document.body) {
      applyContainerDimensions();
    } else {
      document.addEventListener("DOMContentLoaded", applyContainerDimensions);
    }
    return result;
  }, function(err) {
    // A host that does not speak MCP Apps is not fatal: the app still renders,
    // just without host context.
    setState("error", String((err && err.message) || err));
    throw err;
  });
})();
