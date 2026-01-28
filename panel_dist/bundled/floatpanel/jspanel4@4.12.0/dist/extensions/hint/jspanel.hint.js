/**
 * jsPanel - A JavaScript library to create highly configurable multifunctional floating panels that can also be used as modal, tooltip, hint or contextmenu
 * @version v4.12.0
 * @homepage https://jspanel.de/
 * @license MIT
 * @author Stefan Sträßer - info@jspanel.de
 * @github https://github.com/Flyer53/jsPanel4.git
 */

'use strict';
if (!jsPanel.hint) {
  jsPanel.hint = {
    version: '1.2.3',
    date: '2019-05-18 10:50',
    defaults: {
      autoclose: true,
      dragit: false,
      resizeit: false,
      headerControls: 'closeonly xs'
    },
    create: function create() {
      var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      options.paneltype = 'hint';
      var opts = options;

      if (options.config) {
        opts = Object.assign({}, options.config, options);
        delete opts.config;
      }

      opts = Object.assign({}, this.defaults, opts);
      return jsPanel.create(opts, function (hint) {
        hint.style.zIndex = 9999;
        hint.header.style.cursor = 'default';
        hint.footer.style.cursor = 'default';
      });
    }
  };
}

// Add CommonJS module exports, so it can be imported using require() in Node.js
// https://nodejs.org/docs/latest/api/modules.html
if (typeof module !== 'undefined') { module.exports = jsPanel; }
