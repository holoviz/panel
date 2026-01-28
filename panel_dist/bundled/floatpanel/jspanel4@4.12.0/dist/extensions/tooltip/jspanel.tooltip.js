/**
 * jsPanel - A JavaScript library to create highly configurable multifunctional floating panels that can also be used as modal, tooltip, hint or contextmenu
 * @version v4.12.0
 * @homepage https://jspanel.de/
 * @license MIT
 * @author Stefan Sträßer - info@jspanel.de
 * @github https://github.com/Flyer53/jsPanel4.git
 */

'use strict';
function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

// https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent/MouseEvent#Polyfill - needed for IE11
(function (window) {
  try {
    new MouseEvent('test');
    return false; // No need to polyfill
  } catch (e) {// Need to polyfill - fall through
  } // Polyfills DOM4 MouseEvent


  var MouseEvent = function MouseEvent(eventType, params) {
    params = params || {
      bubbles: false,
      cancelable: false
    };
    var mouseEvent = document.createEvent('MouseEvent');
    mouseEvent.initMouseEvent(eventType, params.bubbles, params.cancelable, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
    return mouseEvent;
  };

  MouseEvent.prototype = Event.prototype;
  window.MouseEvent = MouseEvent;
})(window); // -----------------------------------------------------------


if (!jsPanel.tooltip) {
  jsPanel.tooltip = {
    version: '1.4.0',
    date: '2021-03-13 11:20',
    defaults: {
      //tip.options.position: is set in jsPanel.tooltip.create()
      border: '1px',
      dragit: false,
      resizeit: false,
      headerControls: 'none',
      delay: 400,
      ttipEvent: 'mouseenter',
      ttipName: 'default',
      parentPanelFront: false
    },
    create: function create() {
      var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      var callback = arguments.length > 1 ? arguments[1] : undefined;
      options.paneltype = 'tooltip';

      if (!options.id) {
        options.id = "jsPanel-".concat(jsPanel.idCounter += 1);
      } else if (typeof options.id === 'function') {
        options.id = options.id();
      }

      var target = options.target,
          mode = options.mode || 'default',
          timer;

      if (typeof target === 'string') {
        target = document.querySelector(target);
      }

      if (!target) {
        try {
          throw new jsPanel.jsPanelError('TOOLTIP SETUP FAILED!<br>Either option target is missing in the tooltip configuration or the target does nor exist in the document!');
        } catch (e) {
          jsPanel.error(e);
        }

        return false;
      } // don't close tooltip or contextmenu on mousedown in target


      jsPanel.pointerdown.forEach(function (evt) {
        target.addEventListener(evt, function (e) {
          e.stopPropagation();
        }, false);
      });
      var opts = options;

      if (options.config) {
        opts = Object.assign({}, options.config, options);
        delete opts.config;
      }

      opts = Object.assign({}, jsPanel.tooltip.defaults, opts);
      opts.position = Object.assign({}, options.position);
      opts.position.of = options.position.of || target;

      target[opts.ttipName] = function () {
        timer = window.setTimeout(function () {
          // do nothing if id already exists in document
          if (document.getElementById(options.id)) {
            return false;
          }

          jsPanel.create(opts, function (panel) {
            var tipToClose = panel,
                closeTip = function closeTip() {
              tipToClose.close();
              target.removeEventListener('mouseleave', closeTip);
              panel.removeEventListener('mouseleave', closeTip);
            }; // by default tooltip will close when mouse leaves trigger


            if (mode === 'default') {
              target.addEventListener('mouseleave', closeTip, false);
            } else if (mode === 'semisticky') {
              // close tooltip when mouse leaves tooltip
              panel.addEventListener('mouseleave', closeTip, false);
            } // some more tooltip specifics


            panel.classList.add('jsPanel-tooltip');
            panel.style.overflow = 'visible';
            panel.header.style.cursor = 'default';
            panel.footer.style.cursor = 'default'; // check whether tooltip is triggered from within a modal panel or panel and if so update z-index

            if (target.closest('.jsPanel-modal')) {
              panel.style.zIndex = target.closest('.jsPanel-modal').style.zIndex;
            } else {
              if (target.closest('.jsPanel') && opts.parentPanelFront) {
                target.closest('.jsPanel').front();
              }

              panel.style.zIndex = jsPanel.zi.next();
            } // do not use 'click' instead of jsPanel.pointerdown


            jsPanel.pointerdown.forEach(function (evt) {
              panel.addEventListener(evt, function (e) {
                e.stopPropagation();
              }, false);
            }); // add tooltip connector

            if (opts.connector) {
              var tipPos = jsPanel.tooltip.relativeTipPos(panel.options.position);

              if (tipPos !== 'over') {
                panel.append(jsPanel.tooltip.addConnector(panel, tipPos));
              }
            }

            if (callback) {
              callback.call(panel, panel);
            }
          });
        }, opts.delay);
      };

      target.addEventListener(opts.ttipEvent, target[opts.ttipName], false); // immediately show tooltip

      if (opts.autoshow) {
        var event = new MouseEvent('mouseenter');
        target.dispatchEvent(event);
      } // do not create tooltip if mouse leaves target before delay elapsed


      target.addEventListener('mouseleave', function () {
        window.clearTimeout(timer);
      }, false);
    },
    relativeTipPos: function relativeTipPos(position) {
      // returns the basic tip.options.position of the tooltip relative to option.tip.options.position.of (top, right, right-bottom etc.)
      var relPos; // TODO: relative positions leave out a few positions

      if (position.my === 'center-bottom' && position.at === 'center-top') {
        relPos = 'top';
      } else if (position.my === 'left-center' && position.at === 'right-center') {
        relPos = 'right';
      } else if (position.my === 'center-top' && position.at === 'center-bottom') {
        relPos = 'bottom';
      } else if (position.my === 'right-center' && position.at === 'left-center') {
        relPos = 'left';
      } else if (position.my === 'right-bottom' && position.at === 'left-top') {
        relPos = 'left-top-corner';
      } else if (position.my === 'left-bottom' && position.at === 'right-right') {
        relPos = 'right-top-corner';
      } else if (position.my === 'left-top' && position.at === 'right-bottom') {
        relPos = 'right-bottom-corner';
      } else if (position.my === 'right-top' && position.at === 'left-bottom') {
        relPos = 'left-bottom-corner';
      } else if (position.my === 'left-bottom' && position.at === 'left-top') {
        relPos = 'topleft';
      } else if (position.my === 'right-bottom' && position.at === 'right-top') {
        relPos = 'topright';
      } else if (position.my === 'left-top' && position.at === 'right-top') {
        relPos = 'righttop';
      } else if (position.my === 'left-bottom' && position.at === 'right-bottom') {
        relPos = 'rightbottom';
      } else if (position.my === 'right-top' && position.at === 'right-bottom') {
        relPos = 'bottomright';
      } else if (position.my === 'left-top' && position.at === 'left-bottom') {
        relPos = 'bottomleft';
      } else if (position.my === 'right-bottom' && position.at === 'left-bottom') {
        relPos = 'leftbottom';
      } else if (position.my === 'right-top' && position.at === 'left-top') {
        relPos = 'lefttop';
      } else {
        relPos = 'over';
      }

      return relPos;
    },
    addConnector: function addConnector(tip, relposition) {
      var left,
          top,
          connCSS,
          connBg,
          conn = document.createElement('div');
      conn.className = "jsPanel-connector jsPanel-connector-".concat(relposition); // rest of tooltip positioning is in jspanel.sass

      if (relposition === 'top' || relposition === 'topleft' || relposition === 'topright') {
        tip.style.top = "calc(".concat(tip.style.top, " - 12px)");
      } else if (relposition === 'right' || relposition === 'righttop' || relposition === 'rightbottom') {
        tip.style.left = "calc(".concat(tip.style.left, " + 12px)");
      } else if (relposition === 'bottom' || relposition === 'bottomleft' || relposition === 'bottomright') {
        tip.style.top = "calc(".concat(tip.style.top, " + 12px)");
      } else if (relposition === 'left' || relposition === 'lefttop' || relposition === 'leftbottom') {
        tip.style.left = "calc(".concat(tip.style.left, " - 12px)");
      }

      if (typeof tip.options.connector === 'string') {
        connBg = tip.options.connector;
      } else {
        connBg = window.getComputedStyle(tip).borderBottomColor;
      }

      if (relposition.match(/-/)) {
        connCSS = {
          left: left,
          top: top,
          backgroundColor: connBg
        };
      } else {
        var styles = window.getComputedStyle(tip);

        if (relposition === 'topleft' || relposition === 'topright') {
          if (relposition === 'topleft') {
            left = styles.borderBottomLeftRadius;
          } else {
            var corr = 24 + parseInt(styles.borderBottomLeftRadius) + 'px';
            left = "calc(100% - ".concat(corr, ")");
          }

          relposition = 'top';
        } else if (relposition === 'bottomleft' || relposition === 'bottomright') {
          if (relposition === 'bottomleft') {
            left = styles.borderTopLeftRadius;
          } else {
            var _corr = 24 + parseInt(styles.borderTopRightRadius) + 'px';

            left = "calc(100% - ".concat(_corr, ")");
          }

          relposition = 'bottom';
        } else if (relposition === 'lefttop' || relposition === 'leftbottom') {
          if (relposition === 'lefttop') {
            top = styles.borderTopRightRadius;
          } else {
            var _corr2 = 24 + parseInt(styles.borderBottomRightRadius) + 'px';

            top = "calc(100% - ".concat(_corr2, ")");
          }

          relposition = 'left';
        } else if (relposition === 'righttop' || relposition === 'rightbottom') {
          if (relposition === 'righttop') {
            top = styles.borderTopLeftRadius;
          } else {
            var _corr3 = 24 + parseInt(styles.borderBottomLeftRadius) + 'px';

            top = "calc(100% - ".concat(_corr3, ")");
          }

          relposition = 'right';
        }

        connCSS = _defineProperty({
          left: left,
          top: top
        }, "border-".concat(relposition, "-color"), connBg);
      }

      jsPanel.setStyle(conn, connCSS);
      return conn;
    },
    // reposition is still experimental
    reposition: function reposition(tip, newposition, cb) {
      setTimeout(function () {
        // switch of connector doesn't work properly without timeout
        // newposition must be an object
        // get option.tip.position.of
        newposition.of = tip.options.position.of; // reposition tooltip

        tip.reposition(newposition); // ... and add connector again

        if (tip.options.connector) {
          var connector = tip.querySelector('div.jsPanel-connector');
          tip.removeChild(connector);
          var tipPos = jsPanel.tooltip.relativeTipPos(newposition);

          if (tipPos !== 'over') {
            // relative positions leave out a few positions -> connectors are not added for some positions
            tip.append(jsPanel.tooltip.addConnector(tip, tipPos));
          }
        }

        if (cb) {
          cb.call(tip, tip);
        }

        return tip;
      }, 200);
    },
    // removes specific tooltip from target
    remove: function remove(tgt) {
      var evt = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 'mouseenter';
      var tip = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : 'default';
      var tooltipToRemove = tgt[tip];
      tgt.removeEventListener(evt, tooltipToRemove);
    }
  }; // close tooltips on pointerdown in document

  jsPanel.pointerdown.forEach(function (evt) {
    document.addEventListener(evt, function (e) {
      document.querySelectorAll('.jsPanel-tooltip').forEach(function (item) {
        if (!e.target.closest('.jsPanel-tooltip')) {
          if (!item.options.autoshow) {
            item.close();
          }
        }
      });
    }, false);
  });
}

// Add CommonJS module exports, so it can be imported using require() in Node.js
// https://nodejs.org/docs/latest/api/modules.html
if (typeof module !== 'undefined') { module.exports = jsPanel; }
