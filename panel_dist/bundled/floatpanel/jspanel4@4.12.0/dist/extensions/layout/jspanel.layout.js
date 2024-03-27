/**
 * jsPanel - A JavaScript library to create highly configurable multifunctional floating panels that can also be used as modal, tooltip, hint or contextmenu
 * @version v4.12.0
 * @homepage https://jspanel.de/
 * @license MIT
 * @author Stefan Sträßer - info@jspanel.de
 * @github https://github.com/Flyer53/jsPanel4.git
 */

'use strict';
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

if (!jsPanel.layout) {
  jsPanel.layout = {
    version: '1.4.1',
    date: '2021-01-19 10:50',
    storage: localStorage,
    save: function save() {
      var saveConfig = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      var selector = saveConfig.selector ? saveConfig.selector : '.jsPanel-standard';
      var storageName = saveConfig.storagename ? saveConfig.storagename : 'jspanels';
      var collection = document.querySelectorAll(selector);
      var panels = [];
      collection.forEach(function (item) {
        var panelData = item.currentData;
        panelData.status = item.status;
        panelData.zIndex = item.style.zIndex;
        panelData.id = item.id;
        panelData.data = item.options.data || undefined;
        panels.push(panelData);
      });
      panels.sort(function (a, b) {
        return a.zIndex - b.zIndex;
      });
      this.storage.removeItem(storageName);
      var storedData = JSON.stringify(panels);
      this.storage.setItem(storageName, storedData);
      return storedData;
    },
    getAll: function getAll() {
      var storagename = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 'jspanels';

      if (this.storage[storagename]) {
        return JSON.parse(this.storage[storagename]);
      } else {
        return false;
      }
    },
    getDataset: function getDataset(value) {
      var attr = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 'id';
      var storagename = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : 'jspanels';
      var findall = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : false;

      if (this.storage[storagename]) {
        var datasets = this.getAll(storagename),
            set; // findall true will return an array with all matches or at least an empty array

        if (findall) {
          set = [];
        }

        datasets.forEach(function (item) {
          var type = _typeof(item[attr]);

          if (type === 'string' || type === 'number') {
            if (item[attr] === value) {
              if (!set) {
                set = item;
              } else {
                set.push(item);
              }
            }
          } else if (Array.isArray(item[attr])) {
            if (item[attr].includes(value)) {
              if (!set) {
                set = item;
              } else {
                set.push(item);
              }
            }
          } else if (_typeof(item[attr]) === 'object') {
            for (var prop in item[attr]) {
              if (item[attr][prop] === value) {
                if (!set) {
                  set = item;
                  break;
                } else {
                  set.push(item);
                }
              }
            }
          }
        });
        return set ? set : false;
      } else {
        return false;
      }
    },
    restoreId: function restoreId() {
      var restoreConfig = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      var id, config, storageName;

      if (!restoreConfig.id || !restoreConfig.config) {
        // eslint-disable-next-line no-console
        console.error('Id or predefined panel configuration is missing!');
        return false;
      } else {
        id = restoreConfig.id;
        config = restoreConfig.config;
        storageName = restoreConfig.storagename ? restoreConfig.storagename : 'jspanels';
      }

      var storedpanel = this.getDataset(id, 'id', storageName);

      if (storedpanel) {
        var savedConfig = {
          id: storedpanel.id,
          panelSize: {
            width: storedpanel.width,
            height: storedpanel.height
          },
          position: "left-top ".concat(storedpanel.left, " ").concat(storedpanel.top),
          zIndex: storedpanel.zIndex
        };
        var useConfig = Object.assign({}, config, savedConfig);
        return jsPanel.create(useConfig, function (panel) {
          panel.style.zIndex = savedConfig.zIndex;
          panel.saveCurrentDimensions();
          panel.saveCurrentPosition();
          panel.calcSizeFactors(); // don't put code below in savedConfig.setStatus

          if (storedpanel.status !== 'normalized') {
            if (storedpanel.status === 'minimized') {
              panel.minimize();
            } else if (storedpanel.status === 'maximized') {
              panel.maximize();
            } else if (storedpanel.status === 'smallified') {
              panel.smallify();
            } else if (storedpanel.status === 'smallifiedmax') {
              panel.maximize().smallify();
            }
          }
        });
      }
    },
    restore: function restore() {
      var restoreConfig = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      var predefinedConfigs, storageName;

      if (!restoreConfig.configs) {
        // eslint-disable-next-line no-console
        console.error('Object with predefined panel configurations is missing!');
        return false;
      } else {
        predefinedConfigs = restoreConfig.configs;
        storageName = restoreConfig.storagename ? restoreConfig.storagename : 'jspanels';
      }

      if (this.storage[storageName]) {
        var storedPanels = this.getAll(storageName); // loop over all panels in storageName

        storedPanels.forEach(function (item) {
          var pId = item.id; // loop over predefined configs to find config with pId
          // this makes it unnecessary that identifiers for a certain config is the same as id in config

          for (var conf in predefinedConfigs) {
            if (Object.prototype.hasOwnProperty.call(predefinedConfigs, conf)) {
              if (predefinedConfigs[conf].id === pId) {
                jsPanel.layout.restoreId({
                  id: pId,
                  config: predefinedConfigs[conf],
                  storagename: storageName
                });
              }
            }
          }
        });
      } else {
        return false;
      }
    }
  };
}

// Add CommonJS module exports, so it can be imported using require() in Node.js
// https://nodejs.org/docs/latest/api/modules.html
if (typeof module !== 'undefined') { module.exports = jsPanel; }
