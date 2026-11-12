/*
 * Minimal, dependency-free host side of the MCP Apps (SEP-1865) postMessage
 * protocol, driving a single View rendered in an iframe.
 *
 *   const host = new MCPAppHost(iframe, {hostContext: {theme: "dark"}})
 *   host.onRequest("tools/call", (params) => callServerTool(params))
 *   host.initialized.then(() => host.sendToolInput({query: "..."}))
 *   iframe.src = viewUrl
 *
 * The host must be created before the iframe navigates so the View's
 * `ui/initialize` request is not missed.
 */
(function(root) {
  "use strict";

  var PROTOCOL_VERSION = "2026-01-26";

  var METHOD_NOT_FOUND = -32601;
  var INTERNAL_ERROR = -32603;

  function MCPAppHost(iframe, options) {
    options = options || {};
    this.iframe = iframe;
    this.protocolVersion = options.protocolVersion || PROTOCOL_VERSION;
    this.hostInfo = options.hostInfo || {name: "mcp-app-host", version: "0.0.0"};
    this.hostCapabilities = options.hostCapabilities || {};
    this.hostContext = copy(options.hostContext || {});
    this.autoResize = options.autoResize !== false;
    this.requestTimeout = options.requestTimeout || 60000;
    // Every JSON-RPC message exchanged with the View, in order, tagged with
    // the direction it travelled in ("in" from the View, "out" to it).
    this.messages = [];
    this.appInfo = null;
    this.appCapabilities = null;
    this.isInitialized = false;

    this._nextId = 1;
    this._pending = {};
    this._requestHandlers = {};
    this._notificationHandlers = {};
    this._queued = [];

    var self = this;
    this.initialized = new Promise(function(resolve) {
      self._resolveInitialized = resolve;
    });

    this.onRequest("ui/initialize", function(params) {
      params = params || {};
      self.appInfo = params.clientInfo || params.appInfo || null;
      self.appCapabilities = params.appCapabilities || null;
      return {
        protocolVersion: self.protocolVersion,
        hostInfo: self.hostInfo,
        hostCapabilities: self.hostCapabilities,
        hostContext: copy(self.hostContext)
      };
    });
    this.onRequest("ping", function() { return {}; });
    this.onNotification("ui/notifications/initialized", function() {
      self.isInitialized = true;
      var queued = self._queued;
      self._queued = [];
      for (var i = 0; i < queued.length; i++) {
        self._post(queued[i]);
      }
      self._resolveInitialized();
    });
    this.onNotification("ui/notifications/size-changed", function(params) {
      if (self.autoResize && params && params.height != null) {
        self.iframe.style.height = params.height + "px";
      }
    });

    this._listener = function(event) { self._receive(event); };
    window.addEventListener("message", this._listener);
  }

  MCPAppHost.prototype = {

    /* Registration ------------------------------------------------------ */

    /*
     * Handles a request from the View. The handler receives the params and
     * returns the result (or a Promise of it); throwing or rejecting sends a
     * JSON-RPC error. Replaces any existing handler for the method.
     */
    onRequest: function(method, handler) {
      this._requestHandlers[method] = handler;
    },

    /*
     * Subscribes to a notification from the View. Returns a function that
     * removes the subscription.
     */
    onNotification: function(method, handler) {
      var handlers = this._notificationHandlers[method] || (this._notificationHandlers[method] = []);
      handlers.push(handler);
      return function() {
        var index = handlers.indexOf(handler);
        if (index >= 0) {
          handlers.splice(index, 1);
        }
      };
    },

    /* Outbound ---------------------------------------------------------- */

    /*
     * Sends a notification. Notifications sent before the View completed the
     * handshake are queued and delivered once it did.
     */
    notify: function(method, params) {
      var msg = {jsonrpc: "2.0", method: method, params: params || {}};
      if (this.isInitialized) {
        this._post(msg);
      } else {
        this._queued.push(msg);
      }
    },

    /*
     * Sends a request to the View, e.g. `tools/call` on a tool the View
     * registered, and resolves with its result or rejects with its error.
     */
    request: function(method, params) {
      var self = this;
      var id = this._nextId++;
      return new Promise(function(resolve, reject) {
        var timer = setTimeout(function() {
          if (self._pending[id]) {
            delete self._pending[id];
            reject({code: INTERNAL_ERROR, message: "Request " + method + " timed out"});
          }
        }, self.requestTimeout);
        self._pending[id] = {resolve: resolve, reject: reject, timer: timer};
        self._post({jsonrpc: "2.0", id: id, method: method, params: params || {}});
      });
    },

    sendToolInput: function(args) {
      this.notify("ui/notifications/tool-input", {arguments: args || {}});
    },

    sendToolInputPartial: function(args) {
      this.notify("ui/notifications/tool-input-partial", {arguments: args || {}});
    },

    sendToolResult: function(result) {
      this.notify("ui/notifications/tool-result", result || {content: []});
    },

    sendToolCancelled: function(reason) {
      this.notify("ui/notifications/tool-cancelled", {reason: reason || ""});
    },

    /*
     * Merges a patch into the host context and tells the View about it.
     */
    setHostContext: function(patch) {
      for (var key in patch) {
        if (Object.prototype.hasOwnProperty.call(patch, key)) {
          this.hostContext[key] = patch[key];
        }
      }
      if (this.isInitialized) {
        this.notify("ui/notifications/host-context-changed", copy(patch));
      }
    },

    listTools: function() {
      return this.request("tools/list", {});
    },

    callTool: function(name, args) {
      return this.request("tools/call", {name: name, arguments: args || {}});
    },

    /*
     * Asks the View to clean up before it is removed; resolves once it did.
     */
    teardown: function(reason) {
      return this.request("ui/resource-teardown", {reason: reason || ""});
    },

    dispose: function() {
      window.removeEventListener("message", this._listener);
      for (var id in this._pending) {
        if (Object.prototype.hasOwnProperty.call(this._pending, id)) {
          clearTimeout(this._pending[id].timer);
          this._pending[id].reject({code: INTERNAL_ERROR, message: "Host disposed"});
        }
      }
      this._pending = {};
    },

    /* Inbound ----------------------------------------------------------- */

    _post: function(msg) {
      var target = this.iframe.contentWindow;
      if (!target) {
        return;
      }
      this.messages.push({direction: "out", message: msg});
      // Views are typically served from a sandbox origin the host cannot
      // predict, and the View checks event.source rather than the origin.
      target.postMessage(msg, "*");
    },

    _receive: function(event) {
      if (event.source !== this.iframe.contentWindow) {
        return;
      }
      var msg = event.data;
      if (!msg || msg.jsonrpc !== "2.0") {
        return;
      }
      this.messages.push({direction: "in", message: msg});
      var hasId = msg.id !== undefined && msg.id !== null;
      if (msg.method === undefined) {
        if (hasId) {
          this._resolve(msg);
        }
      } else if (hasId) {
        this._handleRequest(msg);
      } else {
        this._handleNotification(msg);
      }
    },

    _resolve: function(msg) {
      var entry = this._pending[msg.id];
      if (!entry) {
        return;
      }
      delete this._pending[msg.id];
      clearTimeout(entry.timer);
      if (msg.error) {
        entry.reject(msg.error);
      } else {
        entry.resolve(msg.result);
      }
    },

    _handleRequest: function(msg) {
      var self = this;
      var handler = this._requestHandlers[msg.method];
      if (!handler) {
        this._post({
          jsonrpc: "2.0", id: msg.id,
          error: {code: METHOD_NOT_FOUND, message: "Method not found: " + msg.method}
        });
        return;
      }
      Promise.resolve().then(function() {
        return handler(msg.params || {}, msg);
      }).then(function(result) {
        self._post({jsonrpc: "2.0", id: msg.id, result: result == null ? {} : result});
      }, function(error) {
        self._post({jsonrpc: "2.0", id: msg.id, error: toError(error)});
      });
    },

    _handleNotification: function(msg) {
      var handlers = (this._notificationHandlers[msg.method] || []).slice();
      for (var i = 0; i < handlers.length; i++) {
        try {
          handlers[i](msg.params || {}, msg);
        } catch (e) {
          console.error("mcp-host: notification handler failed", e);
        }
      }
    }
  };

  function toError(error) {
    if (error && typeof error === "object" && typeof error.code === "number" && error.message) {
      return {code: error.code, message: String(error.message), data: error.data};
    }
    return {code: INTERNAL_ERROR, message: String((error && error.message) || error)};
  }

  function copy(obj) {
    return JSON.parse(JSON.stringify(obj));
  }

  if (typeof module === "object" && module.exports) {
    module.exports = {MCPAppHost: MCPAppHost};
  } else {
    root.MCPAppHost = MCPAppHost;
  }
})(typeof self !== "undefined" ? self : this);
