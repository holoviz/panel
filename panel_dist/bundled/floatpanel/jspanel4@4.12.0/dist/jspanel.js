/**
 * jsPanel - A JavaScript library to create highly configurable multifunctional floating panels that can also be used as modal, tooltip, hint or contextmenu
 * @version v4.12.0
 * @homepage https://jspanel.de/
 * @license MIT
 * @author Stefan Sträßer - info@jspanel.de
 * @github https://github.com/Flyer53/jsPanel4.git
 */

'use strict';
function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && iter[Symbol.iterator] != null || iter["@@iterator"] != null) return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

// eslint-disable-next-line no-redeclare
// noinspection JSVoidFunctionReturnValueUsed
// eslint-disable-next-line no-redeclare
var jsPanel = {
  version: '4.12.0',
  date: '2021-07-09 09:15',
  ajaxAlwaysCallbacks: [],
  autopositionSpacing: 4,
  closeOnEscape: function () {
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' || e.code === 'Escape' || e.key === 'Esc') {
        jsPanel.getPanels(function (panel) {
          return panel.classList.contains('jsPanel'); // Array is sorted by z-index (highest first)
        }).some(function (item) {
          if (item.options.closeOnEscape) {
            if (typeof item.options.closeOnEscape === 'function') {
              return item.options.closeOnEscape.call(item, item); // if return value is falsy next panel in sequence will close, otherwise processing of Array.prototype.some() stops
            } else {
              item.close(null, true);
              return true;
            }
          }

          return false;
        });
      }
    }, false);
  }(),
  defaults: {
    boxShadow: 3,
    container: 'window',
    contentSize: {
      width: '400px',
      height: '200px'
    },
    // must be object
    dragit: {
      cursor: 'move',
      handles: '.jsPanel-headerlogo, .jsPanel-titlebar, .jsPanel-ftr',
      // do not use .jsPanel-headerbar
      opacity: 0.8,
      disableOnMaximized: true
    },
    header: true,
    headerTitle: 'jsPanel',
    headerControls: {
      size: 'md'
    },
    // must be object
    iconfont: undefined,
    maximizedMargin: 0,
    minimizeTo: 'default',
    paneltype: 'standard',
    position: {
      my: 'center',
      at: 'center'
    },
    // default position.of MUST NOT be set with new positioning engine
    resizeit: {
      handles: 'n, e, s, w, ne, se, sw, nw',
      minWidth: 128,
      minHeight: 38
    },
    theme: 'default'
  },
  defaultAutocloseConfig: {
    time: '8s',
    progressbar: true
  },
  defaultSnapConfig: {
    sensitivity: 70,
    trigger: 'panel',
    active: 'both'
  },
  extensions: {},
  globalCallbacks: false,
  icons: {
    close: "<svg focusable=\"false\" class=\"jsPanel-icon\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 22 22\"><path fill=\"currentColor\" d=\"M13.7,11l6.1-6.1c0.4-0.4,0.4-0.9,0-1.3l-1.4-1.4c-0.4-0.4-0.9-0.4-1.3,0L11,8.3L4.9,2.3C4.6,1.9,4,1.9,3.7,2.3L2.3,3.7 C1.9,4,1.9,4.6,2.3,4.9L8.3,11l-6.1,6.1c-0.4,0.4-0.4,0.9,0,1.3l1.4,1.4c0.4,0.4,0.9,0.4,1.3,0l6.1-6.1l6.1,6.1 c0.4,0.4,0.9,0.4,1.3,0l1.4-1.4c0.4-0.4,0.4-0.9,0-1.3L13.7,11z\"/></svg>",
    maximize: "<svg focusable=\"false\" class=\"jsPanel-icon\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 22 22\"><path fill=\"currentColor\" d=\"M18.3,2H3.7C2.8,2,2,2.9,2,3.9v14.1C2,19.1,2.8,20,3.7,20h14.6c0.9,0,1.7-0.9,1.7-1.9V3.9C20,2.9,19.2,2,18.3,2z M18.3,17.8 c0,0.1-0.1,0.2-0.2,0.2H3.9c-0.1,0-0.2-0.1-0.2-0.2V8.4h14.6V17.8z\"/></svg>",
    normalize: "<svg focusable=\"false\" class=\"jsPanel-icon\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 22 22\"><path fill=\"currentColor\" d=\"M18.3,2H7.1C6.1,2,5.4,2.8,5.4,3.7v1.7H3.7C2.8,5.4,2,6.1,2,7.1v11.3C2,19.2,2.8,20,3.7,20h11.3c0.9,0,1.7-0.8,1.7-1.7v-1.7 h1.7c0.9,0,1.7-0.8,1.7-1.7V3.7C20,2.8,19.2,2,18.3,2z M14.9,18.3H3.7V11h11.3V18.3z M18.3,14.9h-1.7V7.1c0-0.9-0.8-1.7-1.7-1.7H7.1 V3.7h11.3V14.9z\"/></svg>",
    minimize: "<svg focusable=\"false\" class=\"jsPanel-icon\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 22 22\"><path fill=\"currentColor\" d=\"M18.9,19.8H3.1c-0.6,0-1.1-0.5-1.1-1.1s0.5-1.1,1.1-1.1h15.8c0.6,0,1.1,0.5,1.1,1.1S19.5,19.8,18.9,19.8z\"/></svg>",
    smallify: "<svg focusable=\"false\" class=\"jsPanel-icon\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 22 22\"><path fill=\"currentColor\" d=\"M2.1,15.2L2.9,16c0.2,0.2,0.5,0.2,0.7,0L11,8.7l7.4,7.3c0.2,0.2,0.5,0.2,0.7,0l0.8-0.8c0.2-0.2,0.2-0.5,0-0.7L11.3,6 c-0.2-0.2-0.5-0.2-0.7,0l-8.5,8.5C2,14.7,2,15,2.1,15.2z\"/></svg>"
  },
  idCounter: 0,
  isIE: function () {
    return navigator.appVersion.match(/Trident/);
  }(),
  // pointerdown: 'onpointerdown' in window ? ['pointerdown'] : 'ontouchend' in window ? ['touchstart', 'mousedown'] : ['mousedown'],
  // pointermove: 'onpointermove' in window ? ['pointermove'] : 'ontouchend' in window ? ['touchmove', 'mousemove'] : ['mousemove'],
  // pointerup: 'onpointerup' in window ? ['pointerup'] : 'ontouchend' in window ? ['touchend', 'mouseup'] : ['mouseup'],
  pointerdown: 'ontouchend' in window ? ['touchstart', 'mousedown'] : ['mousedown'],
  pointermove: 'ontouchend' in window ? ['touchmove', 'mousemove'] : ['mousemove'],
  pointerup: 'ontouchend' in window ? ['touchend', 'mouseup'] : ['mouseup'],
  polyfills: function () {
    // Polyfills for IE11 only
    // Object.assign polyfill - https://developer.mozilla.org/de/docs/Web/JavaScript/Reference/Global_Objects/Object/assign
    if (!Object.assign) {
      Object.defineProperty(Object, 'assign', {
        enumerable: false,
        configurable: true,
        writable: true,
        value: function value(target) {
          if (target === undefined || target === null) {
            throw new TypeError('Cannot convert first argument to object');
          }

          var to = Object(target);

          for (var i = 1; i < arguments.length; i++) {
            var nextSource = arguments[i];

            if (nextSource === undefined || nextSource === null) {
              continue;
            }

            nextSource = Object(nextSource);
            var keysArray = Object.keys(Object(nextSource));

            for (var nextIndex = 0, len = keysArray.length; nextIndex < len; nextIndex++) {
              var nextKey = keysArray[nextIndex];
              var desc = Object.getOwnPropertyDescriptor(nextSource, nextKey);

              if (desc !== undefined && desc.enumerable) {
                to[nextKey] = nextSource[nextKey];
              }
            }
          }

          return to;
        }
      });
    } // NodeList.prototype.forEach() polyfill - https://developer.mozilla.org/en-US/docs/Web/API/NodeList/forEach


    if (window.NodeList && !NodeList.prototype.forEach) {
      NodeList.prototype.forEach = function (callback, thisArg) {
        thisArg = thisArg || window;

        for (var i = 0; i < this.length; i++) {
          callback.call(thisArg, this[i], i, this);
        }
      };
    } // .append() polyfill - https://developer.mozilla.org/en-US/docs/Web/API/ParentNode/append


    (function (arr) {
      arr.forEach(function (item) {
        item.append = item.append || function () {
          var argArr = Array.prototype.slice.call(arguments),
              docFrag = document.createDocumentFragment();
          argArr.forEach(function (argItem) {
            var isNode = argItem instanceof Node;
            docFrag.appendChild(isNode ? argItem : document.createTextNode(String(argItem)));
          });
          this.appendChild(docFrag);
        };
      });
    })([Element.prototype, Document.prototype, DocumentFragment.prototype]); // Element.closest() polyfill - https://developer.mozilla.org/en-US/docs/Web/API/Element/closest


    if (window.Element && !Element.prototype.closest) {
      // noinspection JSValidateTypes
      Element.prototype.closest = function (s) {
        // noinspection JSUnresolvedVariable
        var matches = (this.document || this.ownerDocument).querySelectorAll(s),
            i,
            el = this;

        do {
          i = matches.length; // eslint-disable-next-line no-empty

          while (--i >= 0 && matches.item(i) !== el) {}
        } while (i < 0 && (el = el.parentElement));

        return el;
      };
    } // CustomEvent - https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent


    (function () {
      if (typeof window.CustomEvent === 'function') return false;

      function CustomEvent(event, params) {
        params = params || {
          bubbles: false,
          cancelable: false,
          detail: undefined
        };
        var evt = document.createEvent('CustomEvent');
        evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
        return evt;
      } // noinspection JSValidateTypes


      CustomEvent.prototype = window.Event.prototype; // noinspection JSValidateTypes

      window.CustomEvent = CustomEvent;
    })(); // String.prototype.endsWith() - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/endsWith


    if (!String.prototype.endsWith) {
      String.prototype.endsWith = function (searchStr, Position) {
        // This works much better than >= because
        // it compensates for NaN:
        if (!(Position < this.length)) Position = this.length;else Position |= 0; // round position

        return this.substr(Position - searchStr.length, searchStr.length) === searchStr;
      };
    } // String.prototype.startsWith() - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/startsWith


    if (!String.prototype.startsWith) {
      String.prototype.startsWith = function (searchString, position) {
        return this.substr(position || 0, searchString.length) === searchString;
      };
    } // String.prototype.includes() - https://developer.mozilla.org/de/docs/Web/JavaScript/Reference/Global_Objects/String/includes


    if (!String.prototype.includes) {
      String.prototype.includes = function (search, start) {
        if (typeof start !== 'number') {
          start = 0;
        }

        if (start + search.length > this.length) {
          return false;
        } else {
          return this.indexOf(search, start) !== -1;
        }
      };
    } // Number.isInteger() - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isInteger


    Number.isInteger = Number.isInteger || function (value) {
      return typeof value === 'number' && isFinite(value) && Math.floor(value) === value;
    }; // Array.prototype.includes() - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/includes


    if (!Array.prototype.includes) {
      Object.defineProperty(Array.prototype, 'includes', {
        value: function value(searchElement, fromIndex) {
          if (this == null) {
            throw new TypeError('"this" is null or not defined');
          } // 1. Let O be ? ToObject(this value).


          var o = Object(this); // 2. Let len be ? ToLength(? Get(O, "length")).

          var len = o.length >>> 0; // 3. If len is 0, return false.

          if (len === 0) {
            return false;
          } // 4. Let n be ? ToInteger(fromIndex).
          //    (If fromIndex is undefined, this step produces the value 0.)


          var n = fromIndex | 0; // 5. If n ≥ 0, then
          //  a. Let k be n.
          // 6. Else n < 0,
          //  a. Let k be len + n.
          //  b. If k < 0, let k be 0.

          var k = Math.max(n >= 0 ? n : len - Math.abs(n), 0);

          function sameValueZero(x, y) {
            return x === y || typeof x === 'number' && typeof y === 'number' && isNaN(x) && isNaN(y);
          } // 7. Repeat, while k < len


          while (k < len) {
            // a. Let elementK be the result of ? Get(O, ! ToString(k)).
            // b. If SameValueZero(searchElement, elementK) is true, return true.
            if (sameValueZero(o[k], searchElement)) {
              return true;
            } // c. Increase k by 1.


            k++;
          } // 8. Return false


          return false;
        }
      });
    }
  }(),
  themes: ['default', 'primary', 'secondary', 'info', 'success', 'warning', 'danger', 'light', 'dark'],
  ziBase: 100,
  colorFilledLight: 0.81,
  colorFilledDark: 0.08,
  colorFilled: 0,
  colorBrightnessThreshold: 0.55,
  colorNames: {
    // https://developer.mozilla.org/en-US/docs/Web/CSS/color_value#Color_keywords
    aliceblue: 'f0f8ff',
    antiquewhite: 'faebd7',
    aqua: '0ff',
    aquamarine: '7fffd4',
    azure: 'f0ffff',
    beige: 'f5f5dc',
    bisque: 'ffe4c4',
    black: '000',
    blanchedalmond: 'ffebcd',
    blue: '00f',
    blueviolet: '8a2be2',
    brown: 'a52a2a',
    burlywood: 'deb887',
    cadetblue: '5f9ea0',
    chartreuse: '7fff00',
    chocolate: 'd2691e',
    coral: 'ff7f50',
    cornflowerblue: '6495ed',
    cornsilk: 'fff8dc',
    crimson: 'dc143c',
    cyan: '0ff',
    darkblue: '00008b',
    darkcyan: '008b8b',
    darkgoldenrod: 'b8860b',
    darkgray: 'a9a9a9',
    darkgrey: 'a9a9a9',
    darkgreen: '006400',
    darkkhaki: 'bdb76b',
    darkmagenta: '8b008b',
    darkolivegreen: '556b2f',
    darkorange: 'ff8c00',
    darkorchid: '9932cc',
    darkred: '8b0000',
    darksalmon: 'e9967a',
    darkseagreen: '8fbc8f',
    darkslateblue: '483d8b',
    darkslategray: '2f4f4f',
    darkslategrey: '2f4f4f',
    darkturquoise: '00ced1',
    darkviolet: '9400d3',
    deeppink: 'ff1493',
    deepskyblue: '00bfff',
    dimgray: '696969',
    dimgrey: '696969',
    dodgerblue: '1e90ff',
    firebrick: 'b22222',
    floralwhite: 'fffaf0',
    forestgreen: '228b22',
    fuchsia: 'f0f',
    gainsboro: 'dcdcdc',
    ghostwhite: 'f8f8ff',
    gold: 'ffd700',
    goldenrod: 'daa520',
    gray: '808080',
    grey: '808080',
    green: '008000',
    greenyellow: 'adff2f',
    honeydew: 'f0fff0',
    hotpink: 'ff69b4',
    indianred: 'cd5c5c',
    indigo: '4b0082',
    ivory: 'fffff0',
    khaki: 'f0e68c',
    lavender: 'e6e6fa',
    lavenderblush: 'fff0f5',
    lawngreen: '7cfc00',
    lemonchiffon: 'fffacd',
    lightblue: 'add8e6',
    lightcoral: 'f08080',
    lightcyan: 'e0ffff',
    lightgoldenrodyellow: 'fafad2',
    lightgray: 'd3d3d3',
    lightgrey: 'd3d3d3',
    lightgreen: '90ee90',
    lightpink: 'ffb6c1',
    lightsalmon: 'ffa07a',
    lightseagreen: '20b2aa',
    lightskyblue: '87cefa',
    lightslategray: '789',
    lightslategrey: '789',
    lightsteelblue: 'b0c4de',
    lightyellow: 'ffffe0',
    lime: '0f0',
    limegreen: '32cd32',
    linen: 'faf0e6',
    magenta: 'f0f',
    maroon: '800000',
    mediumaquamarine: '66cdaa',
    mediumblue: '0000cd',
    mediumorchid: 'ba55d3',
    mediumpurple: '9370d8',
    mediumseagreen: '3cb371',
    mediumslateblue: '7b68ee',
    mediumspringgreen: '00fa9a',
    mediumturquoise: '48d1cc',
    mediumvioletred: 'c71585',
    midnightblue: '191970',
    mintcream: 'f5fffa',
    mistyrose: 'ffe4e1',
    moccasin: 'ffe4b5',
    navajowhite: 'ffdead',
    navy: '000080',
    oldlace: 'fdf5e6',
    olive: '808000',
    olivedrab: '6b8e23',
    orange: 'ffa500',
    orangered: 'ff4500',
    orchid: 'da70d6',
    palegoldenrod: 'eee8aa',
    palegreen: '98fb98',
    paleturquoise: 'afeeee',
    palevioletred: 'd87093',
    papayawhip: 'ffefd5',
    peachpuff: 'ffdab9',
    peru: 'cd853f',
    pink: 'ffc0cb',
    plum: 'dda0dd',
    powderblue: 'b0e0e6',
    purple: '800080',
    rebeccapurple: '639',
    red: 'f00',
    rosybrown: 'bc8f8f',
    royalblue: '4169e1',
    saddlebrown: '8b4513',
    salmon: 'fa8072',
    sandybrown: 'f4a460',
    seagreen: '2e8b57',
    seashell: 'fff5ee',
    sienna: 'a0522d',
    silver: 'c0c0c0',
    skyblue: '87ceeb',
    slateblue: '6a5acd',
    slategray: '708090',
    slategrey: '708090',
    snow: 'fffafa',
    springgreen: '00ff7f',
    steelblue: '4682b4',
    tan: 'd2b48c',
    teal: '008080',
    thistle: 'd8bfd8',
    tomato: 'ff6347',
    turquoise: '40e0d0',
    violet: 'ee82ee',
    wheat: 'f5deb3',
    white: 'fff',
    whitesmoke: 'f5f5f5',
    yellow: 'ff0',
    yellowgreen: '9acd32',

    /* Material Design Colors https://material.io/design/color/the-color-system.html#tools-for-picking-colors */
    grey50: 'fafafa',
    grey100: 'f5f5f5',
    grey200: 'eee',
    grey300: 'e0e0e0',
    grey400: 'bdbdbd',
    grey500: '9e9e9e',
    grey600: '757575',
    grey700: '616161',
    grey800: '424242',
    grey900: '212121',
    gray50: 'fafafa',
    gray100: 'f5f5f5',
    gray200: 'eee',
    gray300: 'e0e0e0',
    gray400: 'bdbdbd',
    gray500: '9e9e9e',
    gray600: '757575',
    gray700: '616161',
    gray800: '424242',
    gray900: '212121',
    bluegrey50: 'eceff1',
    bluegrey100: 'CFD8DC',
    bluegrey200: 'B0BEC5',
    bluegrey300: '90A4AE',
    bluegrey400: '78909C',
    bluegrey500: '607D8B',
    bluegrey600: '546E7A',
    bluegrey700: '455A64',
    bluegrey800: '37474F',
    bluegrey900: '263238',
    bluegray50: 'eceff1',
    bluegray100: 'CFD8DC',
    bluegray200: 'B0BEC5',
    bluegray300: '90A4AE',
    bluegray400: '78909C',
    bluegray500: '607D8B',
    bluegray600: '546E7A',
    bluegray700: '455A64',
    bluegray800: '37474F',
    bluegray900: '263238',
    red50: 'FFEBEE',
    red100: 'FFCDD2',
    red200: 'EF9A9A',
    red300: 'E57373',
    red400: 'EF5350',
    red500: 'F44336',
    red600: 'E53935',
    red700: 'D32F2F',
    red800: 'C62828',
    red900: 'B71C1C',
    reda100: 'FF8A80',
    reda200: 'FF5252',
    reda400: 'FF1744',
    reda700: 'D50000',
    pink50: 'FCE4EC',
    pink100: 'F8BBD0',
    pink200: 'F48FB1',
    pink300: 'F06292',
    pink400: 'EC407A',
    pink500: 'E91E63',
    pink600: 'D81B60',
    pink700: 'C2185B',
    pink800: 'AD1457',
    pink900: '880E4F',
    pinka100: 'FF80AB',
    pinka200: 'FF4081',
    pinka400: 'F50057',
    pinka700: 'C51162',
    purple50: 'F3E5F5',
    purple100: 'E1BEE7',
    purple200: 'CE93D8',
    purple300: 'BA68C8',
    purple400: 'AB47BC',
    purple500: '9C27B0',
    purple600: '8E24AA',
    purple700: '7B1FA2',
    purple800: '6A1B9A',
    purple900: '4A148C',
    purplea100: 'EA80FC',
    purplea200: 'E040FB',
    purplea400: 'D500F9',
    purplea700: 'AA00FF',
    deeppurple50: 'EDE7F6',
    deeppurple100: 'D1C4E9',
    deeppurple200: 'B39DDB',
    deeppurple300: '9575CD',
    deeppurple400: '7E57C2',
    deeppurple500: '673AB7',
    deeppurple600: '5E35B1',
    deeppurple700: '512DA8',
    deeppurple800: '4527A0',
    deeppurple900: '311B92',
    deeppurplea100: 'B388FF',
    deeppurplea200: '7C4DFF',
    deeppurplea400: '651FFF',
    deeppurplea700: '6200EA',
    indigo50: 'E8EAF6',
    indigo100: 'C5CAE9',
    indigo200: '9FA8DA',
    indigo300: '7986CB',
    indigo400: '5C6BC0',
    indigo500: '3F51B5',
    indigo600: '3949AB',
    indigo700: '303F9F',
    indigo800: '283593',
    indigo900: '1A237E',
    indigoa100: '8C9EFF',
    indigoa200: '536DFE',
    indigoa400: '3D5AFE',
    indigoa700: '304FFE',
    blue50: 'E3F2FD',
    blue100: 'BBDEFB',
    blue200: '90CAF9',
    blue300: '64B5F6',
    blue400: '42A5F5',
    blue500: '2196F3',
    blue600: '1E88E5',
    blue700: '1976D2',
    blue800: '1565C0',
    blue900: '0D47A1',
    bluea100: '82B1FF',
    bluea200: '448AFF',
    bluea400: '2979FF',
    bluea700: '2962FF',
    lightblue50: 'E1F5FE',
    lightblue100: 'B3E5FC',
    lightblue200: '81D4FA',
    lightblue300: '4FC3F7',
    lightblue400: '29B6F6',
    lightblue500: '03A9F4',
    lightblue600: '039BE5',
    lightblue700: '0288D1',
    lightblue800: '0277BD',
    lightblue900: '01579B',
    lightbluea100: '80D8FF',
    lightbluea200: '40C4FF',
    lightbluea400: '00B0FF',
    lightbluea700: '0091EA',
    cyan50: 'E0F7FA',
    cyan100: 'B2EBF2',
    cyan200: '80DEEA',
    cyan300: '4DD0E1',
    cyan400: '26C6DA',
    cyan500: '00BCD4',
    cyan600: '00ACC1',
    cyan700: '0097A7',
    cyan800: '00838F',
    cyan900: '006064',
    cyana100: '84FFFF',
    cyana200: '18FFFF',
    cyana400: '00E5FF',
    cyana700: '00B8D4',
    teal50: 'E0F2F1',
    teal100: 'B2DFDB',
    teal200: '80CBC4',
    teal300: '4DB6AC',
    teal400: '26A69A',
    teal500: '009688',
    teal600: '00897B',
    teal700: '00796B',
    teal800: '00695C',
    teal900: '004D40',
    teala100: 'A7FFEB',
    teala200: '64FFDA',
    teala400: '1DE9B6',
    teala700: '00BFA5',
    green50: 'E8F5E9',
    green100: 'C8E6C9',
    green200: 'A5D6A7',
    green300: '81C784',
    green400: '66BB6A',
    green500: '4CAF50',
    green600: '43A047',
    green700: '388E3C',
    green800: '2E7D32',
    green900: '1B5E20',
    greena100: 'B9F6CA',
    greena200: '69F0AE',
    greena400: '00E676',
    greena700: '00C853',
    lightgreen50: 'F1F8E9',
    lightgreen100: 'DCEDC8',
    lightgreen200: 'C5E1A5',
    lightgreen300: 'AED581',
    lightgreen400: '9CCC65',
    lightgreen500: '8BC34A',
    lightgreen600: '7CB342',
    lightgreen700: '689F38',
    lightgreen800: '558B2F',
    lightgreen900: '33691E',
    lightgreena100: 'CCFF90',
    lightgreena200: 'B2FF59',
    lightgreena400: '76FF03',
    lightgreena700: '64DD17',
    lime50: 'F9FBE7',
    lime100: 'F0F4C3',
    lime200: 'E6EE9C',
    lime300: 'DCE775',
    lime400: 'D4E157',
    lime500: 'CDDC39',
    lime600: 'C0CA33',
    lime700: 'AFB42B',
    lime800: '9E9D24',
    lime900: '827717',
    limea100: 'F4FF81',
    limea200: 'EEFF41',
    limea400: 'C6FF00',
    limea700: 'AEEA00',
    yellow50: 'FFFDE7',
    yellow100: 'FFF9C4',
    yellow200: 'FFF59D',
    yellow300: 'FFF176',
    yellow400: 'FFEE58',
    yellow500: 'FFEB3B',
    yellow600: 'FDD835',
    yellow700: 'FBC02D',
    yellow800: 'F9A825',
    yellow900: 'F57F17',
    yellowa100: 'FFFF8D',
    yellowa200: 'FFFF00',
    yellowa400: 'FFEA00',
    yellowa700: 'FFD600',
    amber50: 'FFF8E1',
    amber100: 'FFECB3',
    amber200: 'FFE082',
    amber300: 'FFD54F',
    amber400: 'FFCA28',
    amber500: 'FFC107',
    amber600: 'FFB300',
    amber700: 'FFA000',
    amber800: 'FF8F00',
    amber900: 'FF6F00',
    ambera100: 'FFE57F',
    ambera200: 'FFD740',
    ambera400: 'FFC400',
    ambera700: 'FFAB00',
    orange50: 'FFF3E0',
    orange100: 'FFE0B2',
    orange200: 'FFCC80',
    orange300: 'FFB74D',
    orange400: 'FFA726',
    orange500: 'FF9800',
    orange600: 'FB8C00',
    orange700: 'F57C00',
    orange800: 'EF6C00',
    orange900: 'E65100',
    orangea100: 'FFD180',
    orangea200: 'FFAB40',
    orangea400: 'FF9100',
    orangea700: 'FF6D00',
    deeporange50: 'FBE9E7',
    deeporange100: 'FFCCBC',
    deeporange200: 'FFAB91',
    deeporange300: 'FF8A65',
    deeporange400: 'FF7043',
    deeporange500: 'FF5722',
    deeporange600: 'F4511E',
    deeporange700: 'E64A19',
    deeporange800: 'D84315',
    deeporange900: 'BF360C',
    deeporangea100: 'FF9E80',
    deeporangea200: 'FF6E40',
    deeporangea400: 'FF3D00',
    deeporangea700: 'DD2C00',
    brown50: 'EFEBE9',
    brown100: 'D7CCC8',
    brown200: 'BCAAA4',
    brown300: 'A1887F',
    brown400: '8D6E63',
    brown500: '795548',
    brown600: '6D4C41',
    brown700: '5D4037',
    brown800: '4E342E',
    brown900: '3E2723'
  },
  errorReporting: 1,
  modifier: false,
  helper: function () {
    document.addEventListener('keydown', function (e) {
      jsPanel.modifier = e;
    });
    document.addEventListener('keyup', function () {
      jsPanel.modifier = false;
    });
  }(),
  // color methods ---------------
  color: function color(val) {
    var color = val.toLowerCase(),
        r,
        g,
        b,
        h,
        s,
        l,
        match,
        channels,
        hsl,
        result = {};
    var hexPattern = /^#?([0-9a-f]{3}|[0-9a-f]{6})$/gi,
        // matches "#123" or "#f05a78" with or without "#"
    RGBAPattern = /^rgba?\(([0-9]{1,3}),([0-9]{1,3}),([0-9]{1,3}),?(0|1|0\.[0-9]{1,2}|\.[0-9]{1,2})?\)$/gi,
        // matches rgb/rgba color values, whitespace allowed
    HSLAPattern = /^hsla?\(([0-9]{1,3}),([0-9]{1,3}%),([0-9]{1,3}%),?(0|1|0\.[0-9]{1,2}|\.[0-9]{1,2})?\)$/gi,
        namedColors = this.colorNames; // change named color to corresponding hex value

    if (namedColors[color]) {
      color = namedColors[color];
    } // check val for hex color


    if (color.match(hexPattern) !== null) {
      // '#' remove
      color = color.replace('#', ''); // color has either 3 or 6 characters

      if (color.length % 2 === 1) {
        // color has 3 char -> convert to 6 char
        // r = color.substr(0,1).repeat(2);
        // g = color.substr(1,1).repeat(2); // String.prototype.repeat() doesn't work in IE11
        // b = color.substr(2,1).repeat(2);
        r = String(color.substr(0, 1)) + color.substr(0, 1);
        g = String(color.substr(1, 1)) + color.substr(1, 1);
        b = String(color.substr(2, 1)) + color.substr(2, 1);
        result.rgb = {
          r: parseInt(r, 16),
          g: parseInt(g, 16),
          b: parseInt(b, 16)
        };
        result.hex = "#".concat(r).concat(g).concat(b);
      } else {
        // color has 6 char
        result.rgb = {
          r: parseInt(color.substr(0, 2), 16),
          g: parseInt(color.substr(2, 2), 16),
          b: parseInt(color.substr(4, 2), 16)
        };
        result.hex = "#".concat(color);
      }

      hsl = this.rgbToHsl(result.rgb.r, result.rgb.g, result.rgb.b);
      result.hsl = hsl;
      result.rgb.css = "rgb(".concat(result.rgb.r, ",").concat(result.rgb.g, ",").concat(result.rgb.b, ")");
    } // check val for rgb/rgba color
    else if (color.match(RGBAPattern)) {
        match = RGBAPattern.exec(color);
        result.rgb = {
          css: color,
          r: match[1],
          g: match[2],
          b: match[3]
        };
        result.hex = this.rgbToHex(match[1], match[2], match[3]);
        hsl = this.rgbToHsl(match[1], match[2], match[3]);
        result.hsl = hsl;
      } // check val for hsl/hsla color
      else if (color.match(HSLAPattern)) {
          match = HSLAPattern.exec(color);
          h = match[1] / 360;
          s = match[2].substr(0, match[2].length - 1) / 100;
          l = match[3].substr(0, match[3].length - 1) / 100;
          channels = this.hslToRgb(h, s, l);
          result.rgb = {
            css: "rgb(".concat(channels[0], ",").concat(channels[1], ",").concat(channels[2], ")"),
            r: channels[0],
            g: channels[1],
            b: channels[2]
          };
          result.hex = this.rgbToHex(result.rgb.r, result.rgb.g, result.rgb.b);
          result.hsl = {
            css: "hsl(".concat(match[1], ",").concat(match[2], ",").concat(match[3], ")"),
            h: match[1],
            s: match[2],
            l: match[3]
          };
        } // or return #f5f5f5
        else {
            result.hex = '#f5f5f5';
            result.rgb = {
              css: 'rgb(245,245,245)',
              r: 245,
              g: 245,
              b: 245
            };
            result.hsl = {
              css: 'hsl(0,0%,96%)',
              h: 0,
              s: '0%',
              l: '96%'
            };
          }

    return result;
  },
  calcColors: function calcColors(primaryColor) {
    var threshold = this.colorBrightnessThreshold,
        primeColor = this.color(primaryColor),
        filledlightColor = this.lighten(primaryColor, this.colorFilledLight),
        filledColor = this.darken(primaryColor, this.colorFilled),
        fontColorForPrimary = this.perceivedBrightness(primaryColor) <= threshold ? '#ffffff' : '#000000',
        fontColorFilledlight = this.perceivedBrightness(filledlightColor) <= threshold ? '#ffffff' : '#000000',
        fontColorFilled = this.perceivedBrightness(filledColor) <= threshold ? '#ffffff' : '#000000',
        filleddarkColor = this.lighten(primaryColor, this.colorFilledDark),
        fontColorFilleddark = this.perceivedBrightness(filleddarkColor) <= threshold ? '#ffffff' : '#000000';
    return [primeColor.hsl.css, filledlightColor, filledColor, fontColorForPrimary, fontColorFilledlight, fontColorFilled, filleddarkColor, fontColorFilleddark];
  },
  darken: function darken(val, amount) {
    // amount is value between 0 and 1
    var hsl = this.color(val).hsl,
        l = parseFloat(hsl.l),
        lnew = Math.round(l - l * amount) + '%';
    return "hsl(".concat(hsl.h, ",").concat(hsl.s, ",").concat(lnew, ")");
  },
  lighten: function lighten(val, amount) {
    // amount is value between 0 and 1
    var hsl = this.color(val).hsl,
        l = parseFloat(hsl.l),
        lnew = Math.round(l + (100 - l) * amount) + '%';
    return "hsl(".concat(hsl.h, ",").concat(hsl.s, ",").concat(lnew, ")");
  },
  hslToRgb: function hslToRgb(h, s, l) {
    // h, s and l must be values between 0 and 1
    var r, g, b;

    if (s === 0) {
      r = g = b = l; // achromatic
    } else {
      var hue2rgb = function hue2rgb(p, q, t) {
        if (t < 0) {
          t += 1;
        }

        if (t > 1) {
          t -= 1;
        }

        if (t < 1 / 6) {
          return p + (q - p) * 6 * t;
        }

        if (t < 1 / 2) {
          return q;
        }

        if (t < 2 / 3) {
          return p + (q - p) * (2 / 3 - t) * 6;
        }

        return p;
      };

      var q = l < 0.5 ? l * (1 + s) : l + s - l * s,
          p = 2 * l - q;
      r = hue2rgb(p, q, h + 1 / 3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1 / 3);
    }

    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
  },
  rgbToHsl: function rgbToHsl(r, g, b) {
    r /= 255;
    g /= 255;
    b /= 255;
    var max = Math.max(r, g, b),
        min = Math.min(r, g, b),
        h,
        s,
        l = (max + min) / 2;

    if (max === min) {
      h = s = 0; // achromatic
    } else {
      var d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

      switch (max) {
        case r:
          h = (g - b) / d + (g < b ? 6 : 0);
          break;

        case g:
          h = (b - r) / d + 2;
          break;

        case b:
          h = (r - g) / d + 4;
          break;
      }

      h /= 6;
    } //return [ h, s, l ];


    h = Math.round(h * 360);
    s = Math.round(s * 100) + '%';
    l = Math.round(l * 100) + '%';
    return {
      css: 'hsl(' + h + ',' + s + ',' + l + ')',
      h: h,
      s: s,
      l: l
    };
  },
  rgbToHex: function rgbToHex(r, g, b) {
    var red = Number(r).toString(16),
        green = Number(g).toString(16),
        blue = Number(b).toString(16);

    if (red.length === 1) {
      red = "0".concat(red);
    }

    if (green.length === 1) {
      green = "0".concat(green);
    }

    if (blue.length === 1) {
      blue = "0".concat(blue);
    }

    return "#".concat(red).concat(green).concat(blue);
  },
  perceivedBrightness: function perceivedBrightness(val) {
    var rgb = this.color(val).rgb; // return value is in the range 0 - 1 and input rgb values must also be in the range 0 - 1
    // https://www.w3.org/TR/WCAG20-TECHS/G18.html

    return rgb.r / 255 * 0.2126 + rgb.g / 255 * 0.7152 + rgb.b / 255 * 0.0722;
  },
  // positioning methods ---------------
  pOposition: function pOposition(positionshorthand) {
    var result = {}; // remove leading and trailing whitespace and split position shorthand string into array

    var pos = positionshorthand.trim().split(/\s+/); // find autoposition value and assign to result, must be the first item to find and remove

    var auto = pos.filter(function (item) {
      return item.match(/^(down|right|up|left)$/i);
    });

    if (auto.length) {
      result.autoposition = auto[0];
      pos.splice(pos.indexOf(auto[0]), 1);
    } // find my and at values and assign to result


    var my_at = pos.filter(function (item) {
      return item.match(/^(left-|right-)(top|center|bottom)$|(^center-)(top|bottom)$|(^center$)/i);
    });

    if (my_at.length) {
      result.my = my_at[0];
      result.at = my_at[1] || my_at[0];
      pos.splice(pos.indexOf(my_at[0]), 1);

      if (my_at[1]) {
        pos.splice(pos.indexOf(my_at[1]), 1);
      }
    } else {
      result.my = 'center';
      result.at = 'center';
    } // find offset and assign to result


    var offsets = pos.filter(function (item) {
      return item.match(/^[+-]?\d*\.?\d+[a-z%]*$/i);
    });

    if (offsets.length) {
      result.offsetX = offsets[0].match(/^[+-]?\d*\.?\d+$/i) ? "".concat(offsets[0], "px") : offsets[0];

      if (offsets[1]) {
        result.offsetY = offsets[1].match(/^[+-]?\d*\.?\d+$/i) ? "".concat(offsets[1], "px") : offsets[1];
      } else {
        // noinspection JSSuspiciousNameCombination
        result.offsetY = result.offsetX;
      }

      pos.splice(pos.indexOf(offsets[0]), 1);

      if (offsets[1]) {
        pos.splice(pos.indexOf(offsets[1]), 1);
      }
    } // last to find and assign is of value and must be all the rest (if there is a rest)


    if (pos.length) {
      result.of = pos.join(' ');
    }

    return result;
  },
  position: function position(panel, _position) {
    // @panel:     selector string | Element | jQuery object
    //                - usually the jsPanel to position
    // @position:  object
    //                - positioning configuration
    //                - if panel config uses a position shorthand string it must be converted to object before it's passed to this function
    // if @position is not set return panel
    if (!_position) {
      panel.style.opacity = 1;
      return panel;
    } // merge position defaults with @position


    if (typeof _position === 'string') {
      _position = Object.assign({}, this.defaults.position, this.pOposition(_position));
    } else {
      _position = Object.assign({}, this.defaults.position, _position);
    } // process parameter functions for 'my', 'at', 'of'
    // 'offsetX', 'offsetY', 'minLeft', 'maxLeft', 'minTop', 'maxTop' are processed when params are applied


    ['my', 'at', 'of'].forEach(function (item) {
      if (typeof _position[item] === 'function') {
        _position[item] = _position[item].call(panel, panel);
      }
    }); // panel uses option.container: 'window' position is always fixed

    if (panel.options.container === 'window') {
      panel.style.position = 'fixed';
    } // normalize param @panel to ensure it's an Element object


    if (typeof panel === 'string') {
      panel = document.querySelector(panel);
    } else if (Object.getPrototypeOf(panel).jquery) {
      panel = panel[0];
    } // else panel is assumed to be element object
    // container is either 'window' or the panel's parent element


    var container = panel.options.container === 'window' ? 'window' : panel.parentElement; // get base values in order to calculate position deltas
    // since getBoundingClientRect() calculates values relative to the viewport the parentElement of panel/elmtToPositionAgainst is irrelevant

    var panelRect = panel.getBoundingClientRect(),
        containerDomRect = panel.parentElement.getBoundingClientRect(),
        containerRect = container === 'window' ? {
      left: 0,
      top: 0,
      width: document.documentElement.clientWidth,
      height: window.innerHeight
    } // fake window.getBoundingClientRect() return value
    : //: panel.parentElement.getBoundingClientRect(); // using 'container' instead of 'panel.parentElement' produces an error
    // https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect#Notes
    // due to the infos from above link IE and EDGE (old version not based on Chromium) report an error in strict mode -> line of code above replaced with line below
    {
      width: containerDomRect.width,
      height: containerDomRect.height,
      left: containerDomRect.left,
      top: containerDomRect.top
    }; // calculate scale factors, needed for correct positioning if container is scaled - transform: scale()
    // window is never scaled --> scale factors default to 1

    var scaleFactor = container === 'window' ? {
      x: 1,
      y: 1
    } : {
      x: containerRect.width / container.offsetWidth,
      y: containerRect.height / container.offsetHeight
    }; // get and apply border width values of container - needed for positioning corrections due to positioning with %-values

    var containerStyle = container === 'window' ? {
      borderTopWidth: '0px',
      borderRightWidth: '0px',
      borderBottomWidth: '0px',
      borderLeftWidth: '0px'
    } // fake getComputedStyle(window) return value
    : window.getComputedStyle(container);
    containerRect.width -= (parseFloat(containerStyle.borderLeftWidth) + parseFloat(containerStyle.borderRightWidth)) * scaleFactor.x;
    containerRect.height -= (parseFloat(containerStyle.borderTopWidth) + parseFloat(containerStyle.borderBottomWidth)) * scaleFactor.y; // calculate @position.of rect if @position.of is set

    var positionOfRect;

    if (!_position.of) {
      positionOfRect = containerRect;
    } else {
      if (typeof _position.of === 'string') {
        positionOfRect = _position.of === 'window' ? {
          borderTopWidth: '0px',
          borderRightWidth: '0px',
          borderBottomWidth: '0px',
          borderLeftWidth: '0px'
        } // fake getComputedStyle(window) return value
        : document.querySelector(_position.of).getBoundingClientRect();
      } else if (Object.getPrototypeOf(_position.of).jquery) {
        positionOfRect = _position.of[0].getBoundingClientRect();
      } else {
        positionOfRect = _position.of.getBoundingClientRect();
      }
    } // check for scrollbar width values


    var scrollbarwidthsWindow = this.getScrollbarWidth(document.body),
        scrollbarwidthsContainer = this.getScrollbarWidth(panel.parentElement); // calc css left for @panel in regard of @position.my and @position.at

    var left = '0px';

    if (_position.my.startsWith('left-')) {
      if (_position.at.startsWith('left-')) {
        if (_position.of) {
          left = positionOfRect.left - containerRect.left - parseFloat(containerStyle.borderLeftWidth) + 'px';
        } else {
          left = '0px';
        }
      } else if (_position.at.startsWith('center')) {
        if (_position.of) {
          left = positionOfRect.left - containerRect.left - parseFloat(containerStyle.borderLeftWidth) + positionOfRect.width / 2 + 'px';
        } else {
          left = containerRect.width / 2 + 'px';
        }
      } else if (_position.at.startsWith('right-')) {
        if (_position.of) {
          left = positionOfRect.left - containerRect.left - parseFloat(containerStyle.borderLeftWidth) + positionOfRect.width + 'px';
        } else {
          left = containerRect.width + 'px';
        }
      }
    } else if (_position.my.startsWith('center')) {
      if (_position.at.startsWith('left-')) {
        if (_position.of) {
          left = positionOfRect.left - containerRect.left - parseFloat(containerStyle.borderLeftWidth) - panelRect.width / 2 + 'px';
        } else {
          left = -panelRect.width / 2 + 'px';
        }
      } else if (_position.at.startsWith('center')) {
        if (_position.of) {
          left = positionOfRect.left - containerRect.left - parseFloat(containerStyle.borderLeftWidth) - (panelRect.width - positionOfRect.width) / 2 + 'px';
        } else {
          left = containerRect.width / 2 - panelRect.width / 2 + 'px';
        }
      } else if (_position.at.startsWith('right-')) {
        if (_position.of) {
          left = positionOfRect.left - containerRect.left - parseFloat(containerStyle.borderLeftWidth) + (positionOfRect.width - panelRect.width / 2) + 'px';
        } else {
          left = containerRect.width - panelRect.width / 2 + 'px';
        }
      }
    } else if (_position.my.startsWith('right-')) {
      if (_position.at.startsWith('left-')) {
        if (_position.of) {
          left = positionOfRect.left - containerRect.left - parseFloat(containerStyle.borderLeftWidth) - panelRect.width + 'px';
        } else {
          left = -panelRect.width + 'px';
        }
      } else if (_position.at.startsWith('center')) {
        if (_position.of) {
          left = positionOfRect.left - containerRect.left - parseFloat(containerStyle.borderLeftWidth) - panelRect.width + positionOfRect.width / 2 + 'px';
        } else {
          left = containerRect.width / 2 - panelRect.width + 'px';
        }
      } else if (_position.at.startsWith('right-')) {
        if (_position.of) {
          left = positionOfRect.left - containerRect.left - parseFloat(containerStyle.borderLeftWidth) + positionOfRect.width - panelRect.width + 'px';
        } else {
          left = containerRect.width - panelRect.width + 'px';
        } // correction for vertical scrollbar only needed for panels using my: 'right-*' together with at: 'right-*'


        if (container !== 'window') {
          left = parseFloat(left) - scrollbarwidthsContainer.y + 'px';
        }
      }
    } // calc css top for @panel in regard of @position.my and @position.at


    var top = '0px';

    if (_position.my.endsWith('-top')) {
      if (_position.at.endsWith('-top')) {
        if (_position.of) {
          top = positionOfRect.top - containerRect.top - parseFloat(containerStyle.borderTopWidth) + 'px';
        } else {
          top = '0px';
        }
      } else if (_position.at.endsWith('center')) {
        if (_position.of) {
          top = positionOfRect.top - containerRect.top - parseFloat(containerStyle.borderTopWidth) + positionOfRect.height / 2 + 'px';
        } else {
          top = containerRect.height / 2 + 'px';
        }
      } else if (_position.at.endsWith('-bottom')) {
        if (_position.of) {
          top = positionOfRect.top - containerRect.top - parseFloat(containerStyle.borderTopWidth) + positionOfRect.height + 'px';
        } else {
          top = containerRect.height + 'px';
        }
      }
    } else if (_position.my.endsWith('center')) {
      if (_position.at.endsWith('-top')) {
        if (_position.of) {
          top = positionOfRect.top - containerRect.top - parseFloat(containerStyle.borderTopWidth) - panelRect.height / 2 + 'px';
        } else {
          top = -panelRect.height / 2 + 'px';
        }
      } else if (_position.at.endsWith('center')) {
        if (_position.of) {
          top = positionOfRect.top - containerRect.top - parseFloat(containerStyle.borderTopWidth) - panelRect.height / 2 + positionOfRect.height / 2 + 'px';
        } else {
          top = containerRect.height / 2 - panelRect.height / 2 + 'px';
        }
      } else if (_position.at.endsWith('-bottom')) {
        if (_position.of) {
          top = positionOfRect.top - containerRect.top - parseFloat(containerStyle.borderTopWidth) - panelRect.height / 2 + positionOfRect.height + 'px';
        } else {
          top = containerRect.height - panelRect.height / 2 + 'px';
        }
      }
    } else if (_position.my.endsWith('-bottom')) {
      if (_position.at.endsWith('-top')) {
        if (_position.of) {
          top = positionOfRect.top - containerRect.top - parseFloat(containerStyle.borderTopWidth) - panelRect.height + 'px';
        } else {
          top = -panelRect.height + 'px';
        }
      } else if (_position.at.endsWith('center')) {
        if (_position.of) {
          top = positionOfRect.top - containerRect.top - parseFloat(containerStyle.borderTopWidth) - panelRect.height + positionOfRect.height / 2 + 'px';
        } else {
          top = containerRect.height / 2 - panelRect.height + 'px';
        }
      } else if (_position.at.endsWith('-bottom')) {
        if (_position.of) {
          top = positionOfRect.top - containerRect.top - parseFloat(containerStyle.borderTopWidth) - panelRect.height + positionOfRect.height + 'px';
        } else {
          top = containerRect.height - panelRect.height + 'px';
        } // correction for horizontal scrollbar only needed for panels using my: '*-bottom' together with at: '*-bottom'


        if (container !== 'window') {
          top = parseFloat(top) - scrollbarwidthsContainer.x + 'px';
        } else {
          top = parseFloat(top) - scrollbarwidthsWindow.x + 'px';
        }
      }
    }

    panel.style.left = scaleFactor.x === 1 ? left : parseFloat(left) / scaleFactor.x + 'px';
    panel.style.top = scaleFactor.y === 1 ? top : parseFloat(top) / scaleFactor.y + 'px'; // at this point panels are correctly positioned according to the my/at values

    var panelStyle = getComputedStyle(panel); // eslint-disable-next-line no-unused-vars

    var pos = {
      left: panelStyle.left,
      top: panelStyle.top
    }; //console.log('pos after applying my/at/of:', pos);
    // apply autoposition only if ...

    if (_position.autoposition && _position.my === _position.at && ['left-top', 'center-top', 'right-top', 'left-bottom', 'center-bottom', 'right-bottom'].indexOf(_position.my) >= 0) {
      pos = this.applyPositionAutopos(panel, pos, _position); //console.log('let pos after applying autoposition:', pos);
    } // apply position.offsetX and position.offsetY


    if (_position.offsetX || _position.offsetY) {
      pos = this.applyPositionOffset(panel, pos, _position); //console.log('pos after applying offsets:', pos);
    } // calculate and apply position.minLeft, position.minTop, position.maxLeft and position.maxTop


    if (_position.minLeft || _position.minTop || _position.maxLeft || _position.maxTop) {
      pos = this.applyPositionMinMax(panel, pos, _position); //console.log('pos after applying minLeft, maxLeft, maxTop, minTop:', pos);
    } // apply position.modify
    // must be function returning an object with keys left/top, each with valid css length value


    if (_position.modify) {
      // eslint-disable-next-line no-unused-vars
      pos = this.applyPositionModify(panel, pos, _position); //console.log('pos after applying modify():', pos);
    }

    typeof panel.options.opacity === 'number' ? panel.style.opacity = panel.options.opacity : panel.style.opacity = 1;
    return panel;
  },
  applyPositionAutopos: function applyPositionAutopos(panel, pos, position) {
    // add class with position and autoposition direction
    var newClass = "".concat(position.my, "-").concat(position.autoposition.toLowerCase());
    panel.classList.add(newClass); // get all panels with same class

    var newClassAll = Array.prototype.slice.call(document.querySelectorAll(".".concat(newClass))),
        ownIndex = newClassAll.indexOf(panel); // if more than 1 position new panel

    if (newClassAll.length > 1) {
      switch (position.autoposition) {
        case 'down':
          // collect heights of all elmts to calc new top position
          newClassAll.forEach(function (item, index) {
            if (index > 0 && index <= ownIndex) {
              pos.top = parseFloat(pos.top) + newClassAll[--index].getBoundingClientRect().height + jsPanel.autopositionSpacing + 'px';
            }
          });
          break;

        case 'up':
          newClassAll.forEach(function (item, index) {
            if (index > 0 && index <= ownIndex) {
              pos.top = parseFloat(pos.top) - newClassAll[--index].getBoundingClientRect().height - jsPanel.autopositionSpacing + 'px';
            }
          });
          break;

        case 'right':
          // collect widths of all elmts to calc new left position
          newClassAll.forEach(function (item, index) {
            if (index > 0 && index <= ownIndex) {
              pos.left = parseFloat(pos.left) + newClassAll[--index].getBoundingClientRect().width + jsPanel.autopositionSpacing + 'px';
            }
          });
          break;

        case 'left':
          newClassAll.forEach(function (item, index) {
            if (index > 0 && index <= ownIndex) {
              pos.left = parseFloat(pos.left) - newClassAll[--index].getBoundingClientRect().width - jsPanel.autopositionSpacing + 'px';
            }
          });
          break;
      }

      panel.style.left = pos.left;
      panel.style.top = pos.top;
    }

    return {
      left: pos.left,
      top: pos.top
    };
  },
  applyPositionOffset: function applyPositionOffset(panel, pos, position) {
    ['offsetX', 'offsetY'].forEach(function (offset) {
      if (position[offset]) {
        if (typeof position[offset] === 'function') {
          position[offset] = position[offset].call(pos, pos, position);
        }

        if (isNaN(position[offset]) === false) {
          // if an offset's value type is integer it's interpreted as pixel value
          position[offset] = "".concat(position[offset], "px");
        } // else it's assumed offsets are strings with valid css length values

      } else {
        position[offset] = '0px';
      }
    });
    panel.style.left = "calc(".concat(panel.style.left, " + ").concat(position.offsetX, ")"); // offsetX

    panel.style.top = "calc(".concat(panel.style.top, " + ").concat(position.offsetY, ")"); // offsetY

    var panelStyle = getComputedStyle(panel);
    return {
      left: panelStyle.left,
      top: panelStyle.top
    };
  },
  applyPositionMinMax: function applyPositionMinMax(panel, pos, position) {
    ['minLeft', 'minTop', 'maxLeft', 'maxTop'].forEach(function (val) {
      if (position[val]) {
        if (typeof position[val] === 'function') {
          position[val] = position[val].call(pos, pos, position);
        }

        if (Number.isInteger(position[val]) || position[val].match(/^\d+$/)) {
          // if  val type is integer it's interpreted as pixel value
          position[val] = "".concat(position[val], "px");
        } // else it's assumed val is string with valid css length value

      }
    }); // process minLeft

    if (position.minLeft) {
      // apply minLeft value in order to compare with previous left (pos.left)
      panel.style.left = position.minLeft; // now get computed css left

      var left = getComputedStyle(panel).left; // returns string with pixel value
      // now compare current left (minLeft) with pos.left

      if (parseFloat(left) < parseFloat(pos.left)) {
        // if minLeft is less than pos.left return to pos.left
        panel.style.left = pos.left;
      } else {
        // if minLeft is greater than pos.left keep minLeft and reset pos.left to new value
        pos.left = left;
      }
    } // process minTop


    if (position.minTop) {
      panel.style.top = position.minTop;
      var top = getComputedStyle(panel).top;

      if (parseFloat(top) < parseFloat(pos.top)) {
        panel.style.top = pos.top;
      } else {
        pos.top = top;
      }
    } // process maxLeft


    if (position.maxLeft) {
      panel.style.left = position.maxLeft;
      var _left = getComputedStyle(panel).left;

      if (parseFloat(_left) > parseFloat(pos.left)) {
        panel.style.left = pos.left;
      } else {
        pos.left = _left;
      }
    } // process maxTop


    if (position.maxTop) {
      panel.style.top = position.maxTop;
      var _top = getComputedStyle(panel).top;

      if (parseFloat(_top) > parseFloat(pos.top)) {
        panel.style.top = pos.top;
      } else {
        pos.top = _top;
      }
    }

    var panelStyle = getComputedStyle(panel);
    return {
      left: panelStyle.left,
      top: panelStyle.top
    };
  },
  applyPositionModify: function applyPositionModify(panel, pos, position) {
    if (position.modify && typeof position.modify === 'function') {
      var modifiedPosition = position.modify.call(pos, pos, position);
      panel.style.left = Number.isInteger(modifiedPosition.left) || modifiedPosition.left.match(/^\d+$/) ? "".concat(modifiedPosition.left, "px") : modifiedPosition.left;
      panel.style.top = Number.isInteger(modifiedPosition.top) || modifiedPosition.top.match(/^\d+$/) ? "".concat(modifiedPosition.top, "px") : modifiedPosition.top;
    }

    var panelStyle = getComputedStyle(panel);
    return {
      left: panelStyle.left,
      top: panelStyle.top
    };
  },
  autopositionRemaining: function autopositionRemaining(panel) {
    var autoPos,
        parent = panel.options.container;
    ['left-top-down', 'left-top-right', 'center-top-down', 'right-top-down', 'right-top-left', 'left-bottom-up', 'left-bottom-right', 'center-bottom-up', 'right-bottom-up', 'right-bottom-left'].forEach(function (item) {
      if (panel.classList.contains(item)) {
        autoPos = item;
      }
    });

    if (autoPos) {
      var box = parent === 'window' ? document.body : typeof parent === 'string' ? document.querySelector(parent) : parent;
      box.querySelectorAll(".".concat(autoPos)).forEach(function (item) {
        item.reposition();
      });
    }
  },
  // ---------------------------------------------------
  addScript: function addScript(path) {
    var type = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 'application/javascript';
    var cb = arguments.length > 2 ? arguments[2] : undefined;

    if (!document.querySelector("script[src=\"".concat(path, "\"]"))) {
      var script = document.createElement('script');

      if (cb) {
        script.onload = cb;
      }

      script.src = path;
      script.type = type;
      document.head.appendChild(script);
    }
  },
  ajax: function ajax(ajaxConfig, panel) {
    var config,
        urlParts,
        xhr = new XMLHttpRequest();
    var configDefaults = {
      method: 'GET',
      async: true,
      user: '',
      pwd: '',
      done: function done() {
        if (panel) {
          var res = jsPanel.strToHtml(this.responseText);

          if (config.urlSelector) {
            res = res.querySelector(config.urlSelector);
          }

          panel.contentRemove();
          panel.content.append(res);
        }
      },
      autoresize: true,
      autoreposition: true
    };

    if (panel && typeof ajaxConfig === 'string') {
      config = Object.assign({}, configDefaults, {
        url: ajaxConfig
      });
    } else if (_typeof(ajaxConfig) === 'object' && ajaxConfig.url) {
      config = Object.assign({}, configDefaults, ajaxConfig);
      config.url = ajaxConfig.url; // reset timeout to 0, withCredentials & responseType to false if request is synchronous

      if (config.async === false) {
        config.timeout = 0;

        if (config.withCredentials) {
          config.withCredentials = undefined;
        }

        if (config.responseType) {
          config.responseType = undefined;
        }
      }
    } else {
      if (this.errorReporting) {
        var err = 'XMLHttpRequest seems to miss the <mark>url</mark> parameter!';
        jsPanel.errorpanel(err);
      }

      return;
    } // check url for added selector


    urlParts = config.url.trim().split(/\s+/);
    config.url = encodeURI(urlParts[0]);

    if (urlParts.length > 1) {
      urlParts.shift();
      config.urlSelector = urlParts.join(' ');
    }

    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          panel ? config.done.call(xhr, xhr, panel) : config.done.call(xhr, xhr);
        } else {
          if (config.fail) {
            panel ? config.fail.call(xhr, xhr, panel) : config.fail.call(xhr, xhr);
          }
        }

        if (config.always) {
          panel ? config.always.call(xhr, xhr, panel) : config.always.call(xhr, xhr);
        } // resize and/or reposition panel if either width or height is set to 'auto'


        if (panel) {
          if (config.autoresize || config.autoreposition) {
            jsPanel.ajaxAutoresizeAutoreposition(panel, config);
          }
        } // allows plugins to add callback functions to the ajax always callback


        if (jsPanel.ajaxAlwaysCallbacks.length) {
          jsPanel.ajaxAlwaysCallbacks.forEach(function (item) {
            panel ? item.call(xhr, xhr, panel) : item.call(xhr, xhr);
          });
        }
      }
    };

    xhr.open(config.method, config.url, config.async, config.user, config.pwd);
    xhr.timeout = config.timeout || 0;

    if (config.withCredentials) {
      xhr.withCredentials = config.withCredentials;
    }

    if (config.responseType) {
      xhr.responseType = config.responseType;
    }

    if (config.beforeSend) {
      panel ? config.beforeSend.call(xhr, xhr, panel) : config.beforeSend.call(xhr, xhr);
    }

    config.data ? xhr.send(config.data) : xhr.send(null);
  },
  ajaxAutoresizeAutoreposition: function ajaxAutoresizeAutoreposition(panel, ajaxOrFetchConfig) {
    var oContentSize = panel.options.contentSize;

    if (typeof oContentSize === 'string' && oContentSize.match(/auto/i)) {
      var parts = oContentSize.split(' '),
          sizes = Object.assign({}, {
        width: parts[0],
        height: parts[1]
      });

      if (ajaxOrFetchConfig.autoresize) {
        panel.resize(sizes);
      }

      if (!panel.classList.contains('jsPanel-contextmenu')) {
        if (ajaxOrFetchConfig.autoreposition) {
          panel.reposition();
        }
      }
    } else if (_typeof(oContentSize) === 'object' && (oContentSize.width === 'auto' || oContentSize.height === 'auto')) {
      var _sizes = Object.assign({}, oContentSize);

      if (ajaxOrFetchConfig.autoresize) {
        panel.resize(_sizes);
      }

      if (!panel.classList.contains('jsPanel-contextmenu')) {
        if (ajaxOrFetchConfig.autoreposition) {
          panel.reposition();
        }
      }
    }
  },
  createPanelTemplate: function createPanelTemplate() {
    var dataAttr = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : true;
    var panel = document.createElement('div');
    panel.className = 'jsPanel';
    panel.style.left = '0';
    panel.style.top = '0';

    if (dataAttr) {
      ['close', 'maximize', 'normalize', 'minimize', 'smallify'].forEach(function (item) {
        panel.setAttribute("data-btn".concat(item), 'enabled');
      });
    }

    panel.innerHTML = "<div class=\"jsPanel-hdr\">\n                                <div class=\"jsPanel-headerbar\">\n                                    <div class=\"jsPanel-headerlogo\"></div>\n                                    <div class=\"jsPanel-titlebar\">\n                                        <div class=\"jsPanel-title\"></div>\n                                    </div>\n                                    <div class=\"jsPanel-controlbar\">\n                                        <button type=\"button\" class=\"jsPanel-btn jsPanel-btn-smallify\"  aria-label=\"Smallify\">".concat(this.icons.smallify, "</button>\n                                        <button type=\"button\" class=\"jsPanel-btn jsPanel-btn-minimize\"  aria-label=\"Minimize\">").concat(this.icons.minimize, "</button>\n                                        <button type=\"button\" class=\"jsPanel-btn jsPanel-btn-normalize\" aria-label=\"Normalize\">").concat(this.icons.normalize, "</button>\n                                        <button type=\"button\" class=\"jsPanel-btn jsPanel-btn-maximize\"  aria-label=\"Maximize\">").concat(this.icons.maximize, "</button>\n                                        <button type=\"button\" class=\"jsPanel-btn jsPanel-btn-close\"     aria-label=\"Close\">").concat(this.icons.close, "</button>\n                                    </div>\n                                </div>\n                                <div class=\"jsPanel-hdr-toolbar\"></div>\n                            </div>\n                            <div class=\"jsPanel-progressbar\">\n                                <div class=\"jsPanel-progressbar-slider\"></div>\n                            </div>\n                            <div class=\"jsPanel-content\"></div>\n                            <div class=\"jsPanel-minimized-box\"></div>\n                            <div class=\"jsPanel-ftr\"></div>");
    return panel;
  },
  createMinimizedTemplate: function createMinimizedTemplate() {
    var panel = document.createElement('div');
    panel.className = 'jsPanel-replacement';
    panel.innerHTML = "<div class=\"jsPanel-hdr\">\n                                <div class=\"jsPanel-headerbar\">\n                                    <div class=\"jsPanel-headerlogo\"></div>\n                                    <div class=\"jsPanel-titlebar\">\n                                        <div class=\"jsPanel-title\"></div>\n                                    </div>\n                                    <div class=\"jsPanel-controlbar\">\n                                        <button type=\"button\" class=\"jsPanel-btn jsPanel-btn-sm jsPanel-btn-normalize\" aria-label=\"Normalize\">".concat(this.icons.normalize, "</button>\n                                        <button type=\"button\" class=\"jsPanel-btn jsPanel-btn-sm jsPanel-btn-maximize\"  aria-label=\"Maximize\">").concat(this.icons.maximize, "</button>\n                                        <button type=\"button\" class=\"jsPanel-btn jsPanel-btn-sm jsPanel-btn-close\"     aria-label=\"Close\">").concat(this.icons.close, "</button>\n                                    </div>\n                                </div>\n                            </div>");
    return panel;
  },
  createSnapArea: function createSnapArea(panel, pos, snapsens) {
    var el = document.createElement('div'),
        parent = panel.parentElement;
    el.className = "jsPanel-snap-area jsPanel-snap-area-".concat(pos);

    if (pos === 'lt' || pos === 'rt' || pos === 'rb' || pos === 'lb') {
      el.style.width = snapsens + 'px';
      el.style.height = snapsens + 'px';
    } else if (pos === 'ct' || pos === 'cb') {
      el.style.height = snapsens + 'px';
    } else if (pos === 'lc' || pos === 'rc') {
      el.style.width = snapsens + 'px';
    }

    if (parent !== document.body) {
      el.style.position = 'absolute';
    }

    if (!document.querySelector(".jsPanel-snap-area.jsPanel-snap-area-".concat(pos))) {
      panel.parentElement.appendChild(el);
    }
  },
  emptyNode: function emptyNode(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }

    return node;
  },
  extend: function extend(obj) {
    // obj needs to be a plain object (to extend the individual panel, not the global object)
    if (Object.prototype.toString.call(obj) === '[object Object]') {
      for (var ext in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, ext)) {
          this.extensions[ext] = obj[ext];
        }
      }
    }
  },
  fetch: function (_fetch) {
    function fetch(_x, _x2) {
      return _fetch.apply(this, arguments);
    }

    fetch.toString = function () {
      return _fetch.toString();
    };

    return fetch;
  }(function (fetchConfig, panel) {
    var config;
    var configDefaults = {
      bodyMethod: 'text',
      autoresize: true,
      autoreposition: true,
      done: function done(response, panel) {
        if (panel) {
          var res = jsPanel.strToHtml(response);
          panel.contentRemove();
          panel.content.append(res);
        }
      }
    };

    if (panel && typeof fetchConfig === 'string') {
      config = Object.assign({}, configDefaults, {
        resource: encodeURI(fetchConfig)
      });
    } else if (_typeof(fetchConfig) === 'object' && fetchConfig.resource) {
      config = Object.assign({}, configDefaults, fetchConfig);
      config.resource = encodeURI(fetchConfig.resource);
    } else {
      if (this.errorReporting) {
        var err = 'Fetch Request seems to miss the <mark>resource</mark> parameter!';
        jsPanel.errorpanel(err);
      }

      return;
    }

    var fetchInit = config.fetchInit || {};

    if (config.beforeSend) {
      panel ? config.beforeSend.call(fetchConfig, fetchConfig, panel) : config.beforeSend.call(fetchConfig, fetchConfig);
    }

    fetch(config.resource, fetchInit).then(function (response) {
      if (response.ok) {
        return response[config.bodyMethod]();
      }
    }).then(function (response) {
      panel ? config.done.call(response, response, panel) : config.done.call(response, response);

      if (panel) {
        // resize and/or reposition panel if either width or height is set to 'auto'
        if (config.autoresize || config.autoreposition) {
          jsPanel.ajaxAutoresizeAutoreposition(panel, config);
        }
      }
    });
  }),
  getPanels: function getPanels() {
    var condition = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : function () {
      return this.classList.contains('jsPanel-standard');
    };
    return Array.prototype.slice.call(document.querySelectorAll('.jsPanel')).filter(function (value) {
      return condition.call(value, value);
    }).sort(function (a, b) {
      return b.style.zIndex - a.style.zIndex;
    });
  },
  pOcontainer: function pOcontainer(container) {
    if (container === 'window') {
      return document.body;
    } else if (typeof container === 'string') {
      var list = document.querySelectorAll(container); // a returned list is a NodeList

      return list.length && list.length > 0 ? list : false;
    } else if (container.nodeType === 1) {
      return container;
    } else if (container.length) {
      return container[0];
    }

    return false;
  },
  // normalizes values for option.maximizedMargin and containment of dragit/resizeit
  pOcontainment: function pOcontainment(arg) {
    var value = arg;

    if (typeof arg === 'function') {
      value = arg();
    }

    if (typeof value === 'number') {
      // value: 20 => value: [20, 20, 20, 20]
      return [value, value, value, value];
    } else if (Array.isArray(value)) {
      if (value.length === 1) {
        // value: [20] => value: [20, 20, 20, 20]
        return [value[0], value[0], value[0], value[0]];
      } else if (value.length === 2) {
        // value: [20, 40] => value: [20, 40, 20, 40]
        return value.concat(value);
      } else if (value.length === 3) {
        value[3] = value[1];
      }
    }

    return value; // assumed to be array with 4 values
  },
  pOsize: function pOsize(panel, size) {
    var values = size || this.defaults.contentSize;
    var parent = panel.parentElement;

    if (typeof values === 'string') {
      var nums = values.trim().split(' ');
      values = {};
      values.width = nums[0];
      nums.length === 2 ? values.height = nums[1] : values.height = nums[0];
    } else {
      if (values.width && !values.height) {
        // noinspection JSSuspiciousNameCombination
        values.height = values.width;
      } else if (values.height && !values.width) {
        // noinspection JSSuspiciousNameCombination
        values.width = values.height;
      }
    }

    if (String(values.width).match(/^[0-9.]+$/gi)) {
      // if number only
      values.width += 'px';
    } else if (typeof values.width === 'string' && values.width.endsWith('%')) {
      if (parent === document.body) {
        values.width = window.innerWidth * (parseFloat(values.width) / 100) + 'px';
      } else {
        var prtStyles = window.getComputedStyle(parent),
            border = parseFloat(prtStyles.borderLeftWidth) + parseFloat(prtStyles.borderRightWidth);
        values.width = (parseFloat(prtStyles.width) - border) * (parseFloat(values.width) / 100) + 'px';
      }
    } else if (typeof values.width === 'function') {
      values.width = values.width.call(panel, panel);

      if (typeof values.width === 'number') {
        values.width += 'px';
      } else if (typeof values.width === 'string' && values.width.match(/^[0-9.]+$/gi)) {
        values.width += 'px';
      }
    }

    if (String(values.height).match(/^[0-9.]+$/gi)) {
      // if number only
      values.height += 'px';
    } else if (typeof values.height === 'string' && values.height.endsWith('%')) {
      if (parent === document.body) {
        values.height = window.innerHeight * (parseFloat(values.height) / 100) + 'px';
      } else {
        var _prtStyles = window.getComputedStyle(parent),
            _border = parseFloat(_prtStyles.borderTopWidth) + parseFloat(_prtStyles.borderBottomWidth);

        values.height = (parseFloat(_prtStyles.height) - _border) * (parseFloat(values.height) / 100) + 'px';
      }
    } else if (typeof values.height === 'function') {
      values.height = values.height.call(panel, panel);

      if (typeof values.height === 'number') {
        values.height += 'px';
      } else if (typeof values.height === 'string' && values.height.match(/^[0-9.]+$/gi)) {
        values.height += 'px';
      }
    }

    return values; // return value must be object {width: xxx, height: xxx}
  },
  pOborder: function pOborder(border) {
    border = border.trim();
    var values = new Array(3),
        regexStyle = /\s*(none|hidden|dotted|dashed|solid|double|groove|ridge|inset|outset)\s*/gi,
        regexWidth = /\s*(thin|medium|thick)|(\d*\.?\d+[a-zA-Z]{2,4})\s*/gi,
        borderStyle = border.match(regexStyle),
        borderWidth = border.match(regexWidth);

    if (borderStyle) {
      values[1] = borderStyle[0].trim();
      border = border.replace(values[1], '');
    } else {
      values[1] = 'solid';
    }

    if (borderWidth) {
      values[0] = borderWidth[0].trim();
      border = border.replace(values[0], '');
    } else {
      values[0] = 'medium';
    }

    values[2] = border.trim();
    return values;
  },
  pOheaderControls: function pOheaderControls(oHdrCtrls) {
    if (typeof oHdrCtrls === 'string') {
      var setting = {},
          str = oHdrCtrls.toLowerCase(),
          sizeMatch = str.match(/xl|lg|md|sm|xs/),
          ctrlMatch = str.match(/closeonly|none/);

      if (sizeMatch) {
        setting.size = sizeMatch[0];
      }

      if (ctrlMatch) {
        setting = Object.assign({}, setting, {
          maximize: 'remove',
          normalize: 'remove',
          minimize: 'remove',
          smallify: 'remove'
        });

        if (ctrlMatch[0] === 'none') {
          setting.close = 'remove';
        }
      }

      return Object.assign({}, this.defaults.headerControls, setting);
    } else {
      return Object.assign({}, this.defaults.headerControls, oHdrCtrls);
    }
  },
  processCallbacks: function processCallbacks(panel, arg) {
    var someOrEvery = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : 'some';
    var param = arguments.length > 3 ? arguments[3] : undefined;
    var param2 = arguments.length > 4 ? arguments[4] : undefined;

    // if arg != array make it one
    if (typeof arg === 'function') {
      arg = [arg];
    } // some():  execute callbacks until one is found returning a truthy value
    // every(): execute callbacks until one is found returning a falsy value
    // truthy values are: '0' (string with single zero), 'false' (string with text false), [] (empty array), {} (empty object), function(){} ("empty" function)
    // falsy values are: false, 0, '', "", null, undefined, NaN


    if (someOrEvery) {
      return arg[someOrEvery](function (cb) {
        return cb.call(panel, panel, param, param2);
      });
    } else {
      arg.forEach(function (cb) {
        cb.call(panel, panel, param, param2);
      });
    }
  },
  removeSnapAreas: function removeSnapAreas() {
    document.querySelectorAll('.jsPanel-snap-area').forEach(function (el) {
      el.parentElement.removeChild(el);
    });
  },
  resetZi: function resetZi() {
    this.zi = function () {
      var startValue = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : jsPanel.ziBase;
      var val = startValue;
      return {
        next: function next() {
          return val++;
        }
      };
    }();

    Array.prototype.slice.call(document.querySelectorAll('.jsPanel-standard')).sort(function (a, b) {
      return a.style.zIndex - b.style.zIndex;
    }).forEach(function (panel) {
      panel.style.zIndex = jsPanel.zi.next();
    });
  },
  getScrollbarWidth: function getScrollbarWidth() {
    var elmt = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : document.body;

    if (elmt === document.body) {
      return {
        y: window.innerWidth - document.documentElement.clientWidth,
        x: window.innerHeight - document.documentElement.clientHeight
      };
    } else {
      var styles = getComputedStyle(elmt);
      return {
        y: elmt.offsetWidth - elmt.clientWidth - parseFloat(styles.borderRightWidth) - parseFloat(styles.borderLeftWidth),
        x: elmt.offsetHeight - elmt.clientHeight - parseFloat(styles.borderBottomWidth) - parseFloat(styles.borderTopWidth)
      };
    }
  },
  remClass: function remClass(elmt, classnames) {
    classnames.trim().split(/\s+/).forEach(function (item) {
      return elmt.classList.remove(item);
    });
    return elmt;
  },
  setClass: function setClass(elmt, classnames) {
    classnames.trim().split(/\s+/).forEach(function (item) {
      return elmt.classList.add(item);
    });
    return elmt;
  },
  setStyles: function setStyles(elmt, stylesobject) {
    // code taken from https://blissfuljs.com/docs.html#fn-style
    for (var prop in stylesobject) {
      if (prop in elmt.style) {
        // noinspection JSUnfilteredForInLoop,JSUnfilteredForInLoop
        elmt.style[prop] = stylesobject[prop];
      } else {
        // This way we can set CSS Variables too and use normal prop names
        // noinspection JSUnfilteredForInLoop
        elmt.style.setProperty(prop, stylesobject[prop]);
      }
    }

    return elmt;
  },
  setStyle: function setStyle(elmt, stylesobject) {
    return this.setStyles.call(elmt, elmt, stylesobject);
  },
  // alias for setStyles()
  strToHtml: function strToHtml(str) {
    // TODO: add param to strip script tags from returned DocumentFragment

    /* str has to be an HTMLString
     * returns a DocumentFragment - https://developer.mozilla.org/en-US/docs/Web/API/DocumentFragment
     * after inserting executes inline script and script tags */
    return document.createRange().createContextualFragment(str);
  },
  toggleClass: function toggleClass(elmt, classnames) {
    // IE11 doesn't support https://developer.mozilla.org/en-US/docs/Web/API/DOMTokenList/toggle
    classnames.trim().split(/\s+/).forEach(function (classname) {
      elmt.classList.contains(classname) ? elmt.classList.remove(classname) : elmt.classList.add(classname);
    });
    return elmt;
  },
  errorpanel: function errorpanel(e) {
    this.create({
      paneltype: 'error',
      dragit: false,
      resizeit: false,
      theme: {
        bgPanel: 'white',
        bgContent: 'white',
        colorHeader: 'rebeccapurple',
        colorContent: '#333',
        border: '2px solid rebeccapurple'
      },
      borderRadius: '.33rem',
      headerControls: 'closeonly xs',
      headerTitle: '&#9888; jsPanel Error',
      contentSize: {
        width: '50%',
        height: 'auto'
      },
      position: 'center-top 0 5 down',
      animateIn: 'jsPanelFadeIn',
      content: "<div class=\"jsPanel-error-content-separator\"></div><p>".concat(e, "</p>")
    });
  },
  // METHOD CREATING THE PANEL ---------------------------------------------
  create: function create() {
    var _this = this;

    var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    var cb = arguments.length > 1 ? arguments[1] : undefined;

    // initialize z-index generator
    if (!jsPanel.zi) {
      jsPanel.zi = function () {
        var startValue = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : jsPanel.ziBase;
        var val = startValue;
        return {
          next: function next() {
            return val++;
          }
        };
      }();
    }

    if (options.config) {
      options = Object.assign({}, this.defaults, options.config, options);
      delete options.config;
    } else {
      options = Object.assign({}, this.defaults, options);
    }

    if (!options.id) {
      options.id = "jsPanel-".concat(jsPanel.idCounter += 1);
    } else if (typeof options.id === 'function') {
      options.id = options.id();
    }

    var p = document.getElementById(options.id);

    if (p !== null) {
      // if a panel with passed id already exists, front it and return false
      if (p.classList.contains('jsPanel')) {
        p.front();
      }

      if (this.errorReporting) {
        var err = "&#9664; COULD NOT CREATE NEW JSPANEL &#9658;<br>An element with the ID <mark>".concat(options.id, "</mark> already exists in the document.");
        jsPanel.errorpanel(err);
      }

      return false;
    } // check whether container is valid -> if not return and throw error


    var panelContainer = this.pOcontainer(options.container); // panelContainer might be a NodeList, so use only first node in list

    if (_typeof(panelContainer) === 'object' && panelContainer.length && panelContainer.length > 0) {
      panelContainer = panelContainer[0];
    }

    if (!panelContainer) {
      if (this.errorReporting) {
        var _err = '&#9664; COULD NOT CREATE NEW JSPANEL &#9658;<br>The container to append the panel to does not exist';
        jsPanel.errorpanel(_err);
      }

      return false;
    } // normalize on... callbacks
    // callbacks must be array of function(s) in order to be able to dynamically add/remove callbacks (for example in extensions)


    ['onbeforeclose', 'onbeforemaximize', 'onbeforeminimize', 'onbeforenormalize', 'onbeforesmallify', 'onbeforeunsmallify', 'onclosed', 'onfronted', 'onmaximized', 'onminimized', 'onnormalized', 'onsmallified', 'onstatuschange', 'onunsmallified'].forEach(function (item) {
      if (options[item]) {
        if (typeof options[item] === 'function') {
          options[item] = [options[item]];
        }
      } else {
        options[item] = [];
      }
    });
    var self = options.template ? options.template : this.createPanelTemplate(); // Properties

    self.options = options;
    self.closetimer = undefined;
    self.status = 'initialized';
    self.currentData = {};
    self.header = self.querySelector('.jsPanel-hdr'); // complete header section

    self.headerbar = self.header.querySelector('.jsPanel-headerbar'); // log, title and controls

    self.titlebar = self.header.querySelector('.jsPanel-titlebar'); // div surrounding title div

    self.headerlogo = self.headerbar.querySelector('.jsPanel-headerlogo'); // logo only

    self.headertitle = self.headerbar.querySelector('.jsPanel-title'); // title div

    self.controlbar = self.headerbar.querySelector('.jsPanel-controlbar'); // div surrounding all controls

    self.headertoolbar = self.header.querySelector('.jsPanel-hdr-toolbar');
    self.content = self.querySelector('.jsPanel-content');
    self.footer = self.querySelector('.jsPanel-ftr');
    self.snappableTo = false;
    self.snapped = false;
    self.droppableTo = false;
    self.progressbar = self.autocloseProgressbar = self.querySelector('.jsPanel-progressbar'); // self.autocloseProgressbar kept for compatibility
    // Events

    var jspanelloaded = new CustomEvent('jspanelloaded', {
      detail: options.id,
      cancelable: true
    }),
        jspanelstatuschange = new CustomEvent('jspanelstatuschange', {
      detail: options.id,
      cancelable: true
    }),
        jspanelbeforenormalize = new CustomEvent('jspanelbeforenormalize', {
      detail: options.id,
      cancelable: true
    }),
        jspanelnormalized = new CustomEvent('jspanelnormalized', {
      detail: options.id,
      cancelable: true
    }),
        jspanelbeforemaximize = new CustomEvent('jspanelbeforemaximize', {
      detail: options.id,
      cancelable: true
    }),
        jspanelmaximized = new CustomEvent('jspanelmaximized', {
      detail: options.id,
      cancelable: true
    }),
        jspanelbeforeminimize = new CustomEvent('jspanelbeforeminimize', {
      detail: options.id,
      cancelable: true
    }),
        jspanelminimized = new CustomEvent('jspanelminimized', {
      detail: options.id,
      cancelable: true
    }),
        jspanelbeforesmallify = new CustomEvent('jspanelbeforesmallify', {
      detail: options.id,
      cancelable: true
    }),
        jspanelsmallified = new CustomEvent('jspanelsmallified', {
      detail: options.id,
      cancelable: true
    }),
        jspanelsmallifiedmax = new CustomEvent('jspanelsmallifiedmax', {
      detail: options.id,
      cancelable: true
    }),
        jspanelbeforeunsmallify = new CustomEvent('jspanelbeforeunsmallify', {
      detail: options.id,
      cancelable: true
    }),
        jspanelfronted = new CustomEvent('jspanelfronted', {
      detail: options.id,
      cancelable: true
    }),
        jspanelbeforeclose = new CustomEvent('jspanelbeforeclose', {
      detail: options.id,
      cancelable: true
    }),
        jspanelclosed = new CustomEvent('jspanelclosed', {
      detail: options.id,
      cancelable: true
    }),
        jspanelcloseduser = new CustomEvent('jspanelcloseduser', {
      detail: options.id,
      cancelable: true
    }); // make panel available as event object property 'panel'

    [jspanelloaded, jspanelstatuschange, jspanelbeforenormalize, jspanelnormalized, jspanelbeforemaximize, jspanelmaximized, jspanelbeforeminimize, jspanelminimized, jspanelbeforesmallify, jspanelsmallified, jspanelsmallifiedmax, jspanelbeforeunsmallify, jspanelfronted, jspanelbeforeclose].forEach(function (evt) {
      evt.panel = self;
    }); // controls buttons

    var closeBtn = self.querySelector('.jsPanel-btn-close'),
        maxBtn = self.querySelector('.jsPanel-btn-maximize'),
        normBtn = self.querySelector('.jsPanel-btn-normalize'),
        smallBtn = self.querySelector('.jsPanel-btn-smallify'),
        minBtn = self.querySelector('.jsPanel-btn-minimize');

    if (closeBtn) {
      jsPanel.pointerup.forEach(function (item) {
        closeBtn.addEventListener(item, function (e) {
          e.preventDefault(); // disable close for all mouse buttons but left

          if (e.button && e.button > 0) {
            return false;
          }

          self.close(null, true); // true indicates panel closed by using the close control
        });
      });
    }

    if (maxBtn) {
      jsPanel.pointerup.forEach(function (item) {
        maxBtn.addEventListener(item, function (e) {
          e.preventDefault();

          if (e.button && e.button > 0) {
            return false;
          }

          self.maximize();
        });
      });
    }

    if (normBtn) {
      jsPanel.pointerup.forEach(function (item) {
        normBtn.addEventListener(item, function (e) {
          e.preventDefault();

          if (e.button && e.button > 0) {
            return false;
          }

          self.normalize();
        });
      });
    }

    if (smallBtn) {
      jsPanel.pointerup.forEach(function (item) {
        smallBtn.addEventListener(item, function (e) {
          e.preventDefault();

          if (e.button && e.button > 0) {
            return false;
          }

          if (self.status === 'normalized' || self.status === 'maximized') {
            self.smallify();
          } else if (self.status === 'smallified' || self.status === 'smallifiedmax') {
            self.unsmallify();
          }
        });
      });
    }

    if (minBtn) {
      jsPanel.pointerup.forEach(function (item) {
        minBtn.addEventListener(item, function (e) {
          e.preventDefault();

          if (e.button && e.button > 0) {
            return false;
          }

          self.minimize();
        });
      });
    } // import extensions (extensions of the individual panel, not the global object jsPanel)


    var extensions = jsPanel.extensions;

    for (var ext in extensions) {
      if (Object.prototype.hasOwnProperty.call(extensions, ext)) {
        self[ext] = extensions[ext];
      }
    } // Methods


    self.clearTheme = function (cb) {
      jsPanel.themes.forEach(function (value) {
        ['panel', "jsPanel-theme-".concat(value), "panel-".concat(value), "".concat(value, "-color")].forEach(function (item) {
          self.classList.remove(item);
        });
        self.header.classList.remove("jsPanel-theme-".concat(value));
      });
      self.content.classList.remove('jsPanel-content-filled', 'jsPanel-content-filledlight');
      self.header.classList.remove('jsPanel-hdr-light');
      self.header.classList.remove('jsPanel-hdr-dark');
      self.style.backgroundColor = '';
      jsPanel.setStyle(self.headertoolbar, {
        boxShadow: '',
        width: '',
        marginLeft: '',
        borderTopColor: 'transparent'
      });
      jsPanel.setStyle(self.content, {
        background: '',
        borderTopColor: 'transparent'
      });
      self.header.style.background = '';
      Array.prototype.slice.call(self.controlbar.querySelectorAll('.jsPanel-icon')).concat([self.headerlogo, self.headertitle, self.headertoolbar, self.content]).forEach(function (item) {
        item.style.color = '';
      });

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.getThemeDetails = function (th) {
      var passedTheme = th.toLowerCase(),
          theme = {
        color: false,
        colors: false,
        filling: false
      },
          step1 = passedTheme.split('fill');
      theme.color = step1[0].trim().replace(/\s*/g, '');

      if (step1.length === 2) {
        if (step1[1].startsWith('edlight')) {
          theme.filling = 'filledlight';
        } else if (step1[1].startsWith('eddark')) {
          theme.filling = 'filleddark';
        } else if (step1[1].startsWith('ed')) {
          theme.filling = 'filled';
        } else if (step1[1].startsWith('color')) {
          var step2 = step1[1].split('color'),
              fillcolor = step2[step2.length - 1].trim().replace(/\s*/g, '');

          if (jsPanel.colorNames[fillcolor]) {
            fillcolor = jsPanel.colorNames[fillcolor];
          }

          if (fillcolor.match(/^([0-9a-f]{3}|[0-9a-f]{6})$/gi)) {
            fillcolor = '#' + fillcolor;
          }

          theme.filling = fillcolor;
        }
      }

      var builtIn = jsPanel.themes.some(function (item) {
        return item === theme.color.split(/\s/i)[0];
      });

      if (builtIn) {
        var baseTheme = theme.color.split(/\s/i)[0],
            btn = document.createElement('button');
        btn.className = baseTheme + '-bg';
        document.body.appendChild(btn);
        theme.color = getComputedStyle(btn).backgroundColor.replace(/\s+/gi, '');
        document.body.removeChild(btn); // noinspection JSUnusedAssignment

        btn = undefined;
      } else if (theme.color.startsWith('bootstrap-')) {
        // works with bootstrap 3 and 4
        var index = theme.color.indexOf('-'),
            _btn = document.createElement('button');

        _btn.className = 'btn btn' + theme.color.slice(index);
        document.body.appendChild(_btn);
        theme.color = getComputedStyle(_btn).backgroundColor.replace(/\s+/gi, '');
        document.body.removeChild(_btn); // noinspection JSUnusedAssignment

        _btn = undefined;
      } else if (theme.color.startsWith('mdb-')) {
        // material design for bootstrap theme
        var _index = theme.color.indexOf('-') + 1,
            span = document.createElement('span'),
            testClass;

        if (theme.color.endsWith('-dark')) {
          testClass = theme.color.slice(_index);
          testClass = testClass.replace('-dark', '-color-dark');
        } else {
          testClass = theme.color.slice(_index) + '-color';
        }

        span.className = testClass;
        document.body.appendChild(span);
        theme.color = getComputedStyle(span).backgroundColor.replace(/\s+/gi, '');
        document.body.removeChild(span); // noinspection JSUnusedAssignment

        span = undefined;
      }

      theme.colors = jsPanel.calcColors(theme.color);
      return theme;
    };

    self.applyColorTheme = function (themeDetails) {
      self.style.backgroundColor = themeDetails.colors[0];
      self.header.style.backgroundColor = themeDetails.colors[0];
      self.header.style.color = themeDetails.colors[3];
      ['.jsPanel-headerlogo', '.jsPanel-title', '.jsPanel-hdr-toolbar'].forEach(function (item) {
        self.querySelector(item).style.color = themeDetails.colors[3];
      });
      self.querySelectorAll('.jsPanel-controlbar .jsPanel-btn').forEach(function (item) {
        item.style.color = themeDetails.colors[3];
      }); // apply border to content only themes 'filled'

      if (typeof self.options.theme === 'string' && themeDetails.filling === 'filled') {
        self.content.style.borderTop = themeDetails.colors[3] === '#000000' ? '1px solid rgba(0,0,0,0.15)' : '1px solid rgba(255,255,255,0.15)';
      }

      if (themeDetails.colors[3] === '#000000') {
        self.header.classList.add('jsPanel-hdr-light');
      } else {
        self.header.classList.add('jsPanel-hdr-dark');
      }

      if (themeDetails.filling) {
        switch (themeDetails.filling) {
          case 'filled':
            jsPanel.setStyle(self.content, {
              backgroundColor: themeDetails.colors[2],
              color: themeDetails.colors[3]
            });
            break;

          case 'filledlight':
            self.content.style.backgroundColor = themeDetails.colors[1];
            break;

          case 'filleddark':
            jsPanel.setStyle(self.content, {
              backgroundColor: themeDetails.colors[6],
              color: themeDetails.colors[7]
            });
            break;

          default:
            self.content.style.backgroundColor = themeDetails.filling;
            self.content.style.color = jsPanel.perceivedBrightness(themeDetails.filling) <= jsPanel.colorBrightnessThreshold ? '#fff' : '#000';
        }
      }

      return self;
    };

    self.applyCustomTheme = function (theme) {
      var defaults = {
        bgPanel: '#fff',
        bgContent: '#fff',
        colorHeader: '#000',
        colorContent: '#000'
      },
          passedTheme;

      if (_typeof(theme) === 'object') {
        passedTheme = Object.assign(defaults, theme);
      } else {
        passedTheme = defaults;
      }

      var bgPanel = passedTheme.bgPanel,
          bgContent = passedTheme.bgContent,
          colorHeader = passedTheme.colorHeader,
          colorContent = passedTheme.colorContent; // set background panel/header

      jsPanel.colorNames[bgPanel] ? self.style.background = '#' + jsPanel.colorNames[bgPanel] : self.style.background = bgPanel; // set font color header

      if (jsPanel.colorNames[colorHeader]) {
        colorHeader = '#' + jsPanel.colorNames[colorHeader];
      }

      ['.jsPanel-headerlogo', '.jsPanel-title', '.jsPanel-hdr-toolbar'].forEach(function (item) {
        self.querySelector(item).style.color = colorHeader;
      });
      self.querySelectorAll('.jsPanel-controlbar .jsPanel-btn').forEach(function (item) {
        item.style.color = colorHeader;
      }); // set content background

      jsPanel.colorNames[bgContent] ? self.content.style.background = '#' + jsPanel.colorNames[bgContent] : self.content.style.background = bgContent; // set content font color

      jsPanel.colorNames[colorContent] ? self.content.style.color = '#' + jsPanel.colorNames[colorContent] : self.content.style.color = colorContent; // set border-top for header toolbar and add header class

      var pbPanel = jsPanel.perceivedBrightness(colorHeader);

      if (pbPanel > jsPanel.colorBrightnessThreshold) {
        self.header.classList.add('jsPanel-hdr-dark');
      } else {
        self.header.classList.add('jsPanel-hdr-light');
      } // set border-top for content


      var pbContent = jsPanel.perceivedBrightness(colorContent);
      pbContent > jsPanel.colorBrightnessThreshold ? self.content.style.borderTop = '1px solid rgba(255,255,255,0.15)' : self.content.style.borderTop = '1px solid rgba(0,0,0,0.15)'; // set panel border (option.border does not work for themes using an object)

      if (passedTheme.border) {
        var border = passedTheme.border,
            index = border.lastIndexOf(' '),
            col = border.slice(++index);

        if (jsPanel.colorNames[col]) {
          border = border.replace(col, '#' + jsPanel.colorNames[col]);
        }

        self.style.border = border;
      }

      return self;
    };

    self.setBorder = function (val) {
      var border = jsPanel.pOborder(val);

      if (!border[2].length) {
        border[2] = self.style.backgroundColor;
      } else if (jsPanel.colorNames[border[2]]) {
        border[2] = '#' + jsPanel.colorNames[border[2]];
      }

      border = border.join(' ');
      self.style.border = border;
      self.options.border = border;
      return self;
    };

    self.setBorderRadius = function (rad) {
      if (typeof rad === 'number') {
        rad += 'px';
      }

      self.style.borderRadius = rad;
      var br = getComputedStyle(self); // set border-radius of either header or content section depending on presence of header

      if (self.options.header) {
        self.header.style.borderTopLeftRadius = br.borderTopLeftRadius;
        self.header.style.borderTopRightRadius = br.borderTopRightRadius;
      } else {
        self.content.style.borderTopLeftRadius = br.borderTopLeftRadius;
        self.content.style.borderTopRightRadius = br.borderTopRightRadius;
      } // set border-radius of either footer or content section depending on presence of footer


      if (self.options.footerToolbar) {
        self.footer.style.borderBottomRightRadius = br.borderBottomRightRadius;
        self.footer.style.borderBottomLeftRadius = br.borderBottomLeftRadius;
      } else {
        self.content.style.borderBottomRightRadius = br.borderBottomRightRadius;
        self.content.style.borderBottomLeftRadius = br.borderBottomLeftRadius;
      }

      return self;
    };

    self.setTheme = function () {
      var theme = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : options.theme;
      var cb = arguments.length > 1 ? arguments[1] : undefined;
      // if panel is minimized normalize it for theme change
      var minimized;

      if (self.status === 'minimized') {
        minimized = true;
        self.normalize();
      } // first remove all theme related styles


      self.clearTheme();

      if (_typeof(theme) === 'object') {
        options.border = undefined;
        self.applyCustomTheme(theme);
      } else {
        if (theme === 'none') {
          theme = 'white';
        }

        var themeDetails = self.getThemeDetails(theme);
        self.applyColorTheme(themeDetails);
      } // minimize again if panel was minimized prior theme change


      if (minimized) {
        self.minimize();
      }

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.remove = function (id, closedBy, cb) {
      // self.remove() is just a helper func used in self.close()
      self.parentElement.removeChild(self);

      if (!document.getElementById(id)) {
        self.removeMinimizedReplacement();
        self.status = 'closed';

        if (closedBy) {
          document.dispatchEvent(jspanelcloseduser);
        }

        document.dispatchEvent(jspanelclosed);

        if (self.options.onclosed) {
          jsPanel.processCallbacks(self, self.options.onclosed, 'every', closedBy);
        }

        jsPanel.autopositionRemaining(self);

        if (cb) {
          cb.call(id, id);
        }
      } else {
        if (cb) {
          cb.call(self, id, self);
        }
      }

      window.removeEventListener('resize', self.windowResizeHandler);
      document.removeEventListener('jspanelresize', self.parentResizeHandler);
    };

    self.close = function (cb, closedByUser) {
      if (self.closetimer) {
        window.clearInterval(self.closetimer);
      }

      document.dispatchEvent(jspanelbeforeclose);
      self.statusBefore = self.status;

      if (self.options.onbeforeclose && self.options.onbeforeclose.length > 0 && !jsPanel.processCallbacks(self, self.options.onbeforeclose, 'some', self.status, closedByUser)) {
        return self;
      }

      if (self.options.animateOut) {
        if (self.options.animateIn) {
          jsPanel.remClass(self, self.options.animateIn);
        }

        jsPanel.setClass(self, self.options.animateOut);
        self.addEventListener('animationend', function (e) {
          e.stopPropagation();
          self.remove(self.id, closedByUser, cb);
        });
      } else {
        self.remove(self.id, closedByUser, cb);
      }
    };

    self.maximize = function (cb, donotfront) {
      // Note: do not disable maximize method for already maximized panels -> onContainerResize wouldn't work
      self.statusBefore = self.status;

      if (options.onbeforemaximize && options.onbeforemaximize.length > 0 && !jsPanel.processCallbacks(self, options.onbeforemaximize, 'some', self.statusBefore)) {
        return self;
      }

      document.dispatchEvent(jspanelbeforemaximize);
      var parent = self.parentElement,
          margins = jsPanel.pOcontainment(options.maximizedMargin); // normalize maximizedMargin

      if (parent === document.body) {
        // maximize within window

        /*
           When clientHeight is used on the root element (the <html> element), (or on <body> if the document is in quirks mode),
           the viewport's height (excluding any scrollbar) is returned. This is a special case of clientHeight.
           See https://developer.mozilla.org/en-US/docs/Web/API/Element/clientHeight
           document.documentElement in the code below returns the <html> element
        */
        self.style.width = document.documentElement.clientWidth - margins[1] - margins[3] + 'px';
        self.style.height = document.documentElement.clientHeight - margins[0] - margins[2] + 'px';
        self.style.left = margins[3] + 'px';
        self.style.top = margins[0] + 'px';
      } else {
        // maximize within parentElement
        self.style.width = parent.clientWidth - margins[1] - margins[3] + 'px';
        self.style.height = parent.clientHeight - margins[0] - margins[2] + 'px';
        self.style.left = margins[3] + 'px';
        self.style.top = margins[0] + 'px';
      }

      smallBtn.style.transform = 'unset';
      self.removeMinimizedReplacement();
      self.status = 'maximized';
      self.setControls(['.jsPanel-btn-maximize']);

      if (!donotfront) {
        self.front();
      }

      document.dispatchEvent(jspanelmaximized);
      document.dispatchEvent(jspanelstatuschange);

      if (options.onstatuschange) {
        jsPanel.processCallbacks(self, options.onstatuschange, 'every', self.statusBefore);
      }

      if (cb) {
        cb.call(self, self, self.statusBefore);
      }

      if (options.onmaximized) {
        jsPanel.processCallbacks(self, options.onmaximized, 'every', self.statusBefore);
      }

      return self;
    };

    self.minimize = function (cb) {
      if (self.status === 'minimized') {
        return self;
      }

      self.statusBefore = self.status;

      if (options.onbeforeminimize && options.onbeforeminimize.length > 0 && !jsPanel.processCallbacks(self, options.onbeforeminimize, 'some', self.statusBefore)) {
        return self;
      }

      document.dispatchEvent(jspanelbeforeminimize); // create container for minimized replacements if not already there

      if (!document.getElementById('jsPanel-replacement-container')) {
        var replacementContainer = document.createElement('div');
        replacementContainer.id = 'jsPanel-replacement-container';
        document.body.append(replacementContainer);
      }

      self.style.left = '-9999px';
      self.status = 'minimized';
      document.dispatchEvent(jspanelminimized);
      document.dispatchEvent(jspanelstatuschange);

      if (options.onstatuschange) {
        jsPanel.processCallbacks(self, options.onstatuschange, 'every', self.statusBefore);
      }

      if (options.minimizeTo) {
        var replacement = self.createMinimizedReplacement(),
            container,
            parent,
            list;

        switch (options.minimizeTo) {
          case 'default':
            document.getElementById('jsPanel-replacement-container').append(replacement);
            break;

          case 'parentpanel':
            parent = self.closest('.jsPanel-content').parentElement;
            list = parent.querySelectorAll('.jsPanel-minimized-box');
            container = list[list.length - 1];
            container.append(replacement);
            break;

          case 'parent':
            parent = self.parentElement;
            container = parent.querySelector('.jsPanel-minimized-container');

            if (!container) {
              container = document.createElement('div');
              container.className = 'jsPanel-minimized-container';
              parent.append(container);
            }

            container.append(replacement);
            break;

          default:
            // all other strings are assumed to be selector strings returning a single element to append the min replacement to
            document.querySelector(options.minimizeTo).append(replacement);
        }
      }

      if (cb) {
        cb.call(self, self, self.statusBefore);
      }

      if (options.onminimized) {
        jsPanel.processCallbacks(self, options.onminimized, 'every', self.statusBefore);
      }

      return self;
    };

    self.normalize = function (cb) {
      if (self.status === 'normalized') {
        return self;
      }

      self.statusBefore = self.status; // ensure smallify/unsmallify transition is turned off when resizing begins
      //self.style.transition = 'unset';

      if (options.onbeforenormalize && options.onbeforenormalize.length > 0 && !jsPanel.processCallbacks(self, options.onbeforenormalize, 'some', self.statusBefore)) {
        return self;
      }

      document.dispatchEvent(jspanelbeforenormalize);
      self.style.width = self.currentData.width;
      self.style.height = self.currentData.height;

      if (self.snapped) {
        // if panel is snapped before minimizing restore snapped position
        self.snap(self.snapped, true);
      } else {
        self.style.left = self.currentData.left;
        self.style.top = self.currentData.top;
      }

      smallBtn.style.transform = 'unset';
      self.removeMinimizedReplacement();
      self.status = 'normalized';
      self.setControls(['.jsPanel-btn-normalize']);
      self.front();
      document.dispatchEvent(jspanelnormalized);
      document.dispatchEvent(jspanelstatuschange);

      if (options.onstatuschange) {
        jsPanel.processCallbacks(self, options.onstatuschange, 'every', self.statusBefore);
      }

      if (cb) {
        cb.call(self, self, self.statusBefore);
      }

      if (options.onnormalized) {
        jsPanel.processCallbacks(self, options.onnormalized, 'every', self.statusBefore);
      }

      return self;
    };

    self.smallify = function (cb) {
      if (self.status === 'smallified' || self.status === 'smallifiedmax') {
        return self;
      }

      self.statusBefore = self.status;

      if (options.onbeforesmallify && options.onbeforesmallify.length > 0 && !jsPanel.processCallbacks(self, options.onbeforesmallify, 'some', self.statusBefore)) {
        return self;
      }

      document.dispatchEvent(jspanelbeforesmallify);
      self.style.overflow = 'hidden';
      var selfStyles = window.getComputedStyle(self),
          selfHeaderHeight = parseFloat(window.getComputedStyle(self.headerbar).height);
      self.style.height = parseFloat(selfStyles.borderTopWidth) + parseFloat(selfStyles.borderBottomWidth) + selfHeaderHeight + 'px';
      smallBtn.style.transform = 'rotate(180deg)';

      if (self.status === 'normalized') {
        self.setControls(['.jsPanel-btn-normalize']);
        self.status = 'smallified';
        document.dispatchEvent(jspanelsmallified);
        document.dispatchEvent(jspanelstatuschange);

        if (options.onstatuschange) {
          jsPanel.processCallbacks(self, options.onstatuschange, 'every', self.statusBefore);
        }
      } else if (self.status === 'maximized') {
        self.setControls(['.jsPanel-btn-maximize']);
        self.status = 'smallifiedmax';
        document.dispatchEvent(jspanelsmallifiedmax);
        document.dispatchEvent(jspanelstatuschange);

        if (options.onstatuschange) {
          jsPanel.processCallbacks(self, options.onstatuschange, 'every', self.statusBefore);
        }
      }

      var minBoxes = self.querySelectorAll('.jsPanel-minimized-box');
      minBoxes[minBoxes.length - 1].style.display = 'none';

      if (cb) {
        cb.call(self, self, self.statusBefore);
      }

      if (options.onsmallified) {
        jsPanel.processCallbacks(self, options.onsmallified, 'every', self.statusBefore);
      }

      return self;
    };

    self.unsmallify = function (cb) {
      self.statusBefore = self.status;

      if (self.status === 'smallified' || self.status === 'smallifiedmax') {
        if (options.onbeforeunsmallify && options.onbeforeunsmallify.length > 0 && !jsPanel.processCallbacks(self, options.onbeforeunsmallify, 'some', self.statusBefore)) {
          return self;
        }

        document.dispatchEvent(jspanelbeforeunsmallify);
        self.style.overflow = 'visible';
        self.front();

        if (self.status === 'smallified') {
          self.style.height = self.currentData.height;
          self.setControls(['.jsPanel-btn-normalize']);
          self.status = 'normalized';
          document.dispatchEvent(jspanelnormalized);
          document.dispatchEvent(jspanelstatuschange);

          if (options.onstatuschange) {
            jsPanel.processCallbacks(self, options.onstatuschange, 'every', self.statusBefore);
          }
        } else if (self.status === 'smallifiedmax') {
          self.maximize();
        } else if (self.status === 'minimized') {
          self.normalize();
        }

        smallBtn.style.transform = 'rotate(0deg)';
        var minBoxes = self.querySelectorAll('.jsPanel-minimized-box');
        minBoxes[minBoxes.length - 1].style.display = 'flex';

        if (cb) {
          cb.call(self, self, self.statusBefore);
        }

        if (options.onunsmallified) {
          jsPanel.processCallbacks(self, options.onunsmallified, 'every', self.statusBefore);
        }
      }

      return self;
    };

    self.front = function (callback) {
      var execOnFrontedCallbacks = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : true;

      if (self.status === 'minimized') {
        self.statusBefore === 'maximized' ? self.maximize() : self.normalize();
      } else {
        var newArr = Array.prototype.slice.call(document.querySelectorAll('.jsPanel-standard')).map(function (panel) {
          return panel.style.zIndex;
        });

        if (Math.max.apply(Math, _toConsumableArray(newArr)) > self.style.zIndex) {
          self.style.zIndex = jsPanel.zi.next();
        }

        jsPanel.resetZi();
      }

      document.dispatchEvent(jspanelfronted);

      if (callback) {
        callback.call(self, self);
      }

      if (options.onfronted && execOnFrontedCallbacks) {
        jsPanel.processCallbacks(self, options.onfronted, 'every', self.status);
      }

      return self;
    };

    self.snap = function (pos) {
      var alreadySnapped = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;

      // store panel size before it snaps, only if not snapped already
      if (!alreadySnapped) {
        self.currentData.beforeSnap = {
          width: self.currentData.width,
          height: self.currentData.height
        };
      } // snap panel


      if (pos && typeof pos === 'function' && !alreadySnapped) {
        pos.call(self, self, self.snappableTo);
      } else if (pos !== false) {
        var offsets = [0, 0];

        if (self.options.dragit.snap.containment) {
          if (self.options.dragit.containment) {
            var containment = jsPanel.pOcontainment(self.options.dragit.containment),
                position = self.snappableTo;

            if (position.startsWith('left')) {
              offsets[0] = containment[3];
            } else if (position.startsWith('right')) {
              offsets[0] = -containment[1];
            }

            if (position.endsWith('top')) {
              offsets[1] = containment[0];
            } else if (position.endsWith('bottom')) {
              offsets[1] = -containment[2];
            }
          }
        }

        self.reposition("".concat(self.snappableTo, " ").concat(offsets[0], " ").concat(offsets[1]));
      }

      if (!alreadySnapped) {
        self.snapped = self.snappableTo;
      }
    };

    self.move = function (target, cb) {
      var overlaps = self.overlaps(target, 'paddingbox'),
          source = self.parentElement;
      target.appendChild(self);
      self.options.container = target;
      self.style.left = overlaps.left + 'px';
      self.style.top = overlaps.top + 'px';
      self.saveCurrentDimensions();
      self.saveCurrentPosition();
      self.calcSizeFactors(); // important for option.onContainerResize

      if (cb) {
        cb.call(self, self, target, source);
      }

      return self;
    };

    self.closeChildpanels = function (cb) {
      self.getChildpanels().forEach(function (item) {
        return item.close();
      });

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.getChildpanels = function (cb) {
      var childpanels = self.content.querySelectorAll('.jsPanel');

      if (cb) {
        childpanels.forEach(function (panel, index, list) {
          cb.call(panel, panel, index, list);
        });
      }

      return childpanels;
    };

    self.isChildpanel = function (cb) {
      var pp = self.closest('.jsPanel-content'),
          parentpanel = pp ? pp.parentElement : null;

      if (cb) {
        cb.call(self, self, parentpanel);
      } // if panel is childpanel of another panel returns parentpanel, otherwise false


      return pp ? parentpanel : false;
    };

    self.contentRemove = function (cb) {
      jsPanel.emptyNode(self.content);

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.createMinimizedReplacement = function () {
      var tpl = jsPanel.createMinimizedTemplate(),
          color = window.getComputedStyle(self.headertitle).color,
          selfStyles = window.getComputedStyle(self),
          font = options.iconfont,
          controlbar = tpl.querySelector('.jsPanel-controlbar'); // if panel background is an image (that includes gradients) instead of a color value

      if (self.options.header !== 'auto-show-hide') {
        jsPanel.setStyle(tpl, {
          backgroundColor: selfStyles.backgroundColor,
          backgroundPositionX: selfStyles.backgroundPositionX,
          backgroundPositionY: selfStyles.backgroundPositionY,
          backgroundRepeat: selfStyles.backgroundRepeat,
          backgroundAttachment: selfStyles.backgroundAttachment,
          backgroundImage: selfStyles.backgroundImage,
          backgroundSize: selfStyles.backgroundSize,
          backgroundOrigin: selfStyles.backgroundOrigin,
          backgroundClip: selfStyles.backgroundClip
        });
      } else {
        tpl.style.backgroundColor = window.getComputedStyle(self.header).backgroundColor;
      }

      tpl.id = self.id + '-min';
      tpl.querySelector('.jsPanel-headerbar').replaceChild(self.headerlogo.cloneNode(true), tpl.querySelector('.jsPanel-headerlogo'));
      tpl.querySelector('.jsPanel-titlebar').replaceChild(self.headertitle.cloneNode(true), tpl.querySelector('.jsPanel-title'));
      tpl.querySelector('.jsPanel-titlebar').setAttribute('title', self.headertitle.textContent);
      tpl.querySelector('.jsPanel-title').style.color = color;
      controlbar.style.color = color;
      controlbar.querySelectorAll('button').forEach(function (btn) {
        btn.style.color = color;
      });
      ['jsPanel-hdr-dark', 'jsPanel-hdr-light'].forEach(function (item) {
        if (self.header.classList.contains(item)) {
          tpl.querySelector('.jsPanel-hdr').classList.add(item);
        }
      }); // set iconfont

      self.setIconfont(font, tpl);

      if (self.dataset.btnnormalize === 'enabled') {
        jsPanel.pointerup.forEach(function (evt) {
          tpl.querySelector('.jsPanel-btn-normalize').addEventListener(evt, function (e) {
            e.preventDefault();

            if (e.button && e.button > 0) {
              return false;
            }

            self.normalize();
          });
        });
      } else {
        controlbar.querySelector('.jsPanel-btn-normalize').style.display = 'none';
      }

      if (self.dataset.btnmaximize === 'enabled') {
        jsPanel.pointerup.forEach(function (evt) {
          tpl.querySelector('.jsPanel-btn-maximize').addEventListener(evt, function (e) {
            e.preventDefault();

            if (e.button && e.button > 0) {
              return false;
            }

            self.maximize();
          });
        });
      } else {
        controlbar.querySelector('.jsPanel-btn-maximize').style.display = 'none';
      }

      if (self.dataset.btnclose === 'enabled') {
        jsPanel.pointerup.forEach(function (evt) {
          tpl.querySelector('.jsPanel-btn-close').addEventListener(evt, function (e) {
            e.preventDefault();

            if (e.button && e.button > 0) {
              return false;
            }

            self.close(null, true);
          });
        });
      } else {
        controlbar.querySelector('.jsPanel-btn-close').style.display = 'none';
      }

      return tpl;
    };

    self.removeMinimizedReplacement = function () {
      var elmt = document.getElementById("".concat(self.id, "-min"));

      if (elmt) {
        elmt.parentElement.removeChild(elmt);
      }
    };

    self.drag = function () {
      var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      var dragstarted, dragElmt, opts;
      var jspaneldragstart = new CustomEvent('jspaneldragstart', {
        detail: self.id
      }),
          jspaneldrag = new CustomEvent('jspaneldrag', {
        detail: self.id
      }),
          jspaneldragstop = new CustomEvent('jspaneldragstop', {
        detail: self.id
      }); // make panel available as event object property 'panel'

      [jspaneldragstart, jspaneldrag, jspaneldragstop].forEach(function (evt) {
        evt.panel = self;
      });

      var camelcase = function camelcase(string) {
        // 'left-top' converted to 'snapLeftTop'
        var str = string.split('-');
        str.forEach(function (word, index) {
          str[index] = word.charAt(0).toUpperCase() + word.slice(1);
        });
        return 'snap' + str.join('');
      };

      function windowListener(e) {
        if (e.relatedTarget === null) {
          jsPanel.pointermove.forEach(function (evt) {
            document.removeEventListener(evt, dragElmt, false);
            self.style.opacity = 1;
          });
        }
      } // attach handler to each drag handle


      var handles = options.handles || jsPanel.defaults.dragit.handles;
      var cursor = options.cursor || jsPanel.defaults.dragit.cursor;

      function pointerUpHandlerDragit(e) {
        jsPanel.pointermove.forEach(function (e) {
          document.removeEventListener(e, dragElmt);
        });
        jsPanel.removeSnapAreas();

        if (dragstarted) {
          self.style.opacity = 1;
          dragstarted = undefined;

          if (opts.snap) {
            switch (self.snappableTo) {
              case 'left-top':
                self.snap(opts.snap.snapLeftTop);
                break;

              case 'center-top':
                self.snap(opts.snap.snapCenterTop);
                break;

              case 'right-top':
                self.snap(opts.snap.snapRightTop);
                break;

              case 'right-center':
                self.snap(opts.snap.snapRightCenter);
                break;

              case 'right-bottom':
                self.snap(opts.snap.snapRightBottom);
                break;

              case 'center-bottom':
                self.snap(opts.snap.snapCenterBottom);
                break;

              case 'left-bottom':
                self.snap(opts.snap.snapLeftBottom);
                break;

              case 'left-center':
                self.snap(opts.snap.snapLeftCenter);
                break;
            }

            if (opts.snap.callback && self.snappableTo && typeof opts.snap.callback === 'function') {
              opts.snap.callback.call(self, self);

              if (opts.snap.repositionOnSnap && opts.snap[camelcase(self.snappableTo)] !== false) {
                self.repositionOnSnap(self.snappableTo);
              }
            }

            if (self.snappableTo && opts.snap.repositionOnSnap && opts.snap[camelcase(self.snappableTo)]) {
              self.repositionOnSnap(self.snappableTo);
            }
          } // opts.drop


          if (self.droppableTo && self.droppableTo) {
            var sourceContainer = self.parentElement;
            self.move(self.droppableTo);

            if (opts.drop.callback) {
              opts.drop.callback.call(self, self, self.droppableTo, sourceContainer);
            }
          }

          document.dispatchEvent(jspaneldragstop);

          if (opts.stop.length) {
            var stopStyles = window.getComputedStyle(self),
                paneldata = {
              left: parseFloat(stopStyles.left),
              top: parseFloat(stopStyles.top),
              width: parseFloat(stopStyles.width),
              height: parseFloat(stopStyles.height)
            };
            jsPanel.processCallbacks(self, opts.stop, false, paneldata, e);
          }

          self.saveCurrentPosition();
          self.calcSizeFactors(); // important for options onwindowresize/onparentresize
        }

        self.controlbar.style.pointerEvents = 'inherit';
        self.content.style.pointerEvents = 'inherit'; // restore other panel's css pointer-events

        document.querySelectorAll('iframe').forEach(function (frame) {
          frame.style.pointerEvents = 'auto';
        });
        document.removeEventListener(e, pointerUpHandlerDragit);
      }

      self.querySelectorAll(handles).forEach(function (handle) {
        handle.style.touchAction = 'none';
        handle.style.cursor = cursor;
        jsPanel.pointerdown.forEach(function (evt) {
          handle.addEventListener(evt, function (e) {
            // disable dragging for all mouse buttons but left
            if (e.button && e.button > 0) {
              return false;
            } // setup and normalize dragit options


            opts = Object.assign({}, jsPanel.defaults.dragit, options);

            if (opts.disableOnMaximized && self.status === 'maximized') {
              return false;
            }

            if (opts.containment || opts.containment === 0) {
              opts.containment = jsPanel.pOcontainment(opts.containment);
            }

            if (opts.grid) {
              if (Array.isArray(opts.grid)) {
                if (opts.grid.length === 1) {
                  opts.grid[1] = opts.grid[0];
                }
              }
            }

            if (opts.snap) {
              if (_typeof(opts.snap) === 'object') {
                opts.snap = Object.assign({}, jsPanel.defaultSnapConfig, opts.snap);
              } else {
                opts.snap = jsPanel.defaultSnapConfig;
              }
            } // footer elmts with the class "jsPanel-ftr-btn" don't drag a panel
            // do not compare e.target with e.currentTarget because there might be footer elmts supposed to drag the panel
            // noinspection JSUnresolvedFunction


            if (e.target.closest('.jsPanel-ftr-btn')) {
              return;
            }

            self.controlbar.style.pointerEvents = 'none';
            self.content.style.pointerEvents = 'none'; // without this code handler might not be unbound when content has iframe or object tag
            // prevents iframes in other panel from interfering with drag action of dragged panel

            document.querySelectorAll('iframe').forEach(function (frame) {
              frame.style.pointerEvents = 'none';
            });
            var startStyles = window.getComputedStyle(self),
                startLeft = parseFloat(startStyles.left),
                startTop = parseFloat(startStyles.top),
                startWidth = parseFloat(startStyles.width),
                startHeight = parseFloat(startStyles.height),
                psx = e.touches ? e.touches[0].clientX : e.clientX,
                // pointer x on mousedown (don't use pageX, doesn't work on FF for Android)
            psy = e.touches ? e.touches[0].clientY : e.clientY,
                // same as above
            parent = self.parentElement,
                parentRect = parent.getBoundingClientRect(),
                parentStyles = window.getComputedStyle(parent),
                scaleFactor = self.getScaleFactor(),
                startLeftCorrection = 0,
                scrollbarwidths = jsPanel.getScrollbarWidth(parent); // function actually dragging the elmt

            dragElmt = function dragElmt(e) {
              e.preventDefault();

              if (!dragstarted) {
                document.dispatchEvent(jspaneldragstart);
                self.style.opacity = opts.opacity; // if configured restore panel size to values before snap and reposition reasonable before drag actually starts

                if (self.snapped && opts.snap.resizeToPreSnap && self.currentData.beforeSnap) {
                  self.resize(self.currentData.beforeSnap.width + ' ' + self.currentData.beforeSnap.height);
                  self.setControls(['.jsPanel-btn-normalize']);
                  var intermediateStyles = self.getBoundingClientRect(),
                      delta = psx - (intermediateStyles.left + intermediateStyles.width),
                      wHalf = intermediateStyles.width / 2;

                  if (delta > -wHalf) {
                    startLeftCorrection = delta + wHalf;
                  }
                }

                self.front();
                self.snapped = false; // panel is maximized on dragstart

                if (self.status === 'maximized') {
                  self.setControls(['.jsPanel-btn-normalize']);
                  self.status = 'normalized';
                } // opts.drop


                if (opts.drop && opts.drop.dropZones) {
                  //opts.drop.dropZones = opts.drop.dropZones.map(zone => jsPanel.pOcontainer(zone));
                  var dropzones = opts.drop.dropZones.map(function (zone) {
                    return jsPanel.pOcontainer(zone);
                  }); // -> array where each item is a NodeList

                  var dropzonelist = [];
                  dropzones.forEach(function (nodelist) {
                    if (nodelist.length) {
                      // an element node does not have a length property
                      nodelist.forEach(function (node) {
                        dropzonelist.push(node);
                      });
                    } else {
                      dropzonelist.push(nodelist);
                    }
                  }); // filter list to have only unique values

                  dropzonelist = dropzonelist.filter(function (value, index, self) {
                    return self.indexOf(value) === index;
                  });
                  opts.drop.dropZones = dropzonelist;
                } // dragstart callback


                if (opts.start.length) {
                  jsPanel.processCallbacks(self, opts.start, false, {
                    left: startLeft,
                    top: startTop,
                    width: startWidth,
                    height: startHeight
                  }, e);
                }
              }

              dragstarted = 1;
              var elmtL, elmtL2, elmtT, elmtT2, elmtR, elmtR2, elmtB, elmtB2, right, bottom;
              var pmx = e.touches ? e.touches[0].clientX : e.clientX,
                  // current pointer x while pointer moves (don't use pageX, doesn't work on FF for Android)
              pmy = e.touches ? e.touches[0].clientY : e.clientY,
                  // current pointer y while pointer moves (don't use pageY, doesn't work on FF for Android)
              dragStyles = window.getComputedStyle(self),
                  // get current styles while dragging
              overlaps; // EDGE reports "auto" instead of pixel value using getComputedStyle(), so some values need to be calculated different
              // this whole block of code could be removed if EDGE not based on Chromium doesn't need to be supported

              if (parent === document.body) {
                var elmtRect = self.getBoundingClientRect();
                right = window.innerWidth - parseInt(parentStyles.borderLeftWidth, 10) - parseInt(parentStyles.borderRightWidth, 10) - (elmtRect.left + elmtRect.width);
                bottom = window.innerHeight - parseInt(parentStyles.borderTopWidth, 10) - parseInt(parentStyles.borderBottomWidth, 10) - (elmtRect.top + elmtRect.height);
              } else {
                right = parseInt(parentStyles.width, 10) - parseInt(parentStyles.borderLeftWidth, 10) - parseInt(parentStyles.borderRightWidth, 10) - (parseInt(dragStyles.left, 10) + parseInt(dragStyles.width, 10));
                bottom = parseInt(parentStyles.height, 10) - parseInt(parentStyles.borderTopWidth, 10) - parseInt(parentStyles.borderBottomWidth, 10) - (parseInt(dragStyles.top, 10) + parseInt(dragStyles.height, 10));
              } // -- -- --


              elmtL = parseFloat(dragStyles.left);
              elmtT = parseFloat(dragStyles.top);
              elmtR = right; // replace line with parseFloat(dragStyles.right); if EDGE code block above is removed

              elmtB = bottom; // replace line with parseFloat(dragStyles.bottom); if EDGE code block above is removed

              if (opts.snap) {
                if (opts.snap.trigger === 'panel') {
                  elmtL2 = Math.pow(elmtL, 2);
                  elmtT2 = Math.pow(elmtT, 2);
                  elmtR2 = Math.pow(elmtR, 2);
                  elmtB2 = Math.pow(elmtB, 2);
                } else if (opts.snap.trigger === 'pointer') {
                  if (self.options.container === 'window') {
                    elmtL = pmx;
                    elmtT = pmy;
                    elmtR = window.innerWidth - pmx;
                    elmtB = window.innerHeight - pmy;
                    elmtL2 = Math.pow(pmx, 2);
                    elmtT2 = Math.pow(elmtT, 2);
                    elmtR2 = Math.pow(elmtR, 2);
                    elmtB2 = Math.pow(elmtB, 2);
                  } else {
                    overlaps = self.overlaps(parent, 'paddingbox', e);
                    elmtL = overlaps.pointer.left;
                    elmtT = overlaps.pointer.top;
                    elmtR = overlaps.pointer.right;
                    elmtB = overlaps.pointer.bottom;
                    elmtL2 = Math.pow(overlaps.pointer.left, 2);
                    elmtT2 = Math.pow(overlaps.pointer.top, 2);
                    elmtR2 = Math.pow(overlaps.pointer.right, 2);
                    elmtB2 = Math.pow(overlaps.pointer.bottom, 2);
                  }
                }
              }

              var lefttopVectorDrag = Math.sqrt(elmtL2 + elmtT2),
                  leftbottomVectorDrag = Math.sqrt(elmtL2 + elmtB2),
                  righttopVectorDrag = Math.sqrt(elmtR2 + elmtT2),
                  rightbottomVectorDrag = Math.sqrt(elmtR2 + elmtB2),
                  horizontalDeltaDrag = Math.abs(elmtL - elmtR) / 2,
                  verticalDeltaDrag = Math.abs(elmtT - elmtB) / 2,
                  leftVectorDrag = Math.sqrt(elmtL2 + Math.pow(verticalDeltaDrag, 2)),
                  topVectorDrag = Math.sqrt(elmtT2 + Math.pow(horizontalDeltaDrag, 2)),
                  rightVectorDrag = Math.sqrt(elmtR2 + Math.pow(verticalDeltaDrag, 2)),
                  bottomVectorDrag = Math.sqrt(elmtB2 + Math.pow(horizontalDeltaDrag, 2)); // prevent selections while dragging

              window.getSelection().removeAllRanges(); // trigger drag permanently while dragging

              document.dispatchEvent(jspaneldrag); // move elmt and apply axis option

              if (!opts.axis || opts.axis === 'x') {
                self.style.left = startLeft + (pmx - psx) / scaleFactor.x + startLeftCorrection + 'px'; // set new css left of elmt depending on opts.axis
              }

              if (!opts.axis || opts.axis === 'y') {
                self.style.top = startTop + (pmy - psy) / scaleFactor.y + 'px'; // set new css top of elmt depending on opts.axis
              } // apply grid option


              if (opts.grid) {
                var grid = opts.grid,
                    axis = opts.axis; // formula rounds to nearest multiple of grid
                // https://www.webveteran.com/blog/web-coding/javascript-round-to-any-multiple-of-a-specific-number/

                var x = grid[0] * Math.round((startLeft + (pmx - psx)) / grid[0]),
                    y = grid[1] * Math.round((startTop + (pmy - psy)) / grid[1]);

                if (!axis || axis === 'x') {
                  self.style.left = "".concat(x, "px");
                }

                if (!axis || axis === 'y') {
                  self.style.top = "".concat(y, "px");
                }
              } // apply containment option


              if (opts.containment || opts.containment === 0) {
                var containment = opts.containment;
                var maxLeft, maxTop; // calc maxLeft and maxTop (minLeft and MinTop is equal to containment setting)

                if (self.options.container === 'window') {
                  maxLeft = window.innerWidth - parseFloat(dragStyles.width) - containment[1] - scrollbarwidths.y;
                  maxTop = window.innerHeight - parseFloat(dragStyles.height) - containment[2] - scrollbarwidths.x;
                } else {
                  var xCorr = parseFloat(parentStyles.borderLeftWidth) + parseFloat(parentStyles.borderRightWidth),
                      yCorr = parseFloat(parentStyles.borderTopWidth) + parseFloat(parentStyles.borderBottomWidth);
                  maxLeft = parentRect.width / scaleFactor.x - parseFloat(dragStyles.width) - containment[1] - xCorr - scrollbarwidths.y;
                  maxTop = parentRect.height / scaleFactor.y - parseFloat(dragStyles.height) - containment[2] - yCorr - scrollbarwidths.x;
                }

                if (parseFloat(self.style.left) <= containment[3]) {
                  self.style.left = containment[3] + 'px';
                }

                if (parseFloat(self.style.top) <= containment[0]) {
                  self.style.top = containment[0] + 'px';
                }

                if (parseFloat(self.style.left) >= maxLeft) {
                  self.style.left = maxLeft + 'px';
                }

                if (parseFloat(self.style.top) >= maxTop) {
                  self.style.top = maxTop + 'px';
                }
              } // callback while dragging


              if (opts.drag.length) {
                var paneldata = {
                  left: elmtL,
                  top: elmtT,
                  right: elmtR,
                  bottom: elmtB,
                  width: parseFloat(dragStyles.width),
                  height: parseFloat(dragStyles.height)
                };
                jsPanel.processCallbacks(self, opts.drag, false, paneldata, e);
              } // apply snap options


              if (opts.snap) {
                var snapSens = opts.snap.sensitivity,
                    topSensAreaLength = parent === document.body ? window.innerWidth / 8 : parentRect.width / 8,
                    sideSensAreaLength = parent === document.body ? window.innerHeight / 8 : parentRect.height / 8;
                self.snappableTo = false;
                jsPanel.removeSnapAreas();

                if (lefttopVectorDrag < snapSens) {
                  if (opts.snap.snapLeftTop !== false) {
                    if (!opts.snap.active || opts.snap.active === 'both') {
                      self.snappableTo = 'left-top';
                      jsPanel.createSnapArea(self, 'lt', snapSens);
                    } else if (opts.snap.trigger === 'pointer' && opts.snap.active && opts.snap.active === 'inside') {
                      if (overlaps.pointer.left > 0 && overlaps.pointer.top > 0) {
                        self.snappableTo = 'left-top';
                        jsPanel.createSnapArea(self, 'lt', snapSens);
                      } else {
                        self.snappableTo = false;
                        jsPanel.removeSnapAreas();
                      }
                    }
                  }
                } else if (leftbottomVectorDrag < snapSens) {
                  if (opts.snap.snapLeftBottom !== false) {
                    if (!opts.snap.active || opts.snap.active === 'both') {
                      self.snappableTo = 'left-bottom';
                      jsPanel.createSnapArea(self, 'lb', snapSens);
                    } else if (opts.snap.trigger === 'pointer' && opts.snap.active && opts.snap.active === 'inside') {
                      if (overlaps.pointer.left > 0 && overlaps.pointer.bottom > 0) {
                        self.snappableTo = 'left-bottom';
                        jsPanel.createSnapArea(self, 'lb', snapSens);
                      } else {
                        self.snappableTo = false;
                        jsPanel.removeSnapAreas();
                      }
                    }
                  }
                } else if (righttopVectorDrag < snapSens) {
                  if (opts.snap.snapRightTop !== false) {
                    if (!opts.snap.active || opts.snap.active === 'both') {
                      self.snappableTo = 'right-top';
                      jsPanel.createSnapArea(self, 'rt', snapSens);
                    } else if (opts.snap.trigger === 'pointer' && opts.snap.active && opts.snap.active === 'inside') {
                      if (overlaps.pointer.right > 0 && overlaps.pointer.top > 0) {
                        self.snappableTo = 'right-top';
                        jsPanel.createSnapArea(self, 'rt', snapSens);
                      } else {
                        self.snappableTo = false;
                        jsPanel.removeSnapAreas();
                      }
                    }
                  }
                } else if (rightbottomVectorDrag < snapSens) {
                  if (opts.snap.snapRightBottom !== false) {
                    if (!opts.snap.active || opts.snap.active === 'both') {
                      self.snappableTo = 'right-bottom';
                      jsPanel.createSnapArea(self, 'rb', snapSens);
                    } else if (opts.snap.trigger === 'pointer' && opts.snap.active && opts.snap.active === 'inside') {
                      if (overlaps.pointer.right > 0 && overlaps.pointer.bottom > 0) {
                        self.snappableTo = 'right-bottom';
                        jsPanel.createSnapArea(self, 'rb', snapSens);
                      } else {
                        self.snappableTo = false;
                        jsPanel.removeSnapAreas();
                      }
                    }
                  }
                } else if (elmtT < snapSens && topVectorDrag < topSensAreaLength) {
                  if (opts.snap.snapCenterTop !== false) {
                    if (!opts.snap.active || opts.snap.active === 'both') {
                      self.snappableTo = 'center-top';
                      jsPanel.createSnapArea(self, 'ct', snapSens);
                    } else if (opts.snap.trigger === 'pointer' && opts.snap.active && opts.snap.active === 'inside') {
                      if (overlaps.pointer.top > 0) {
                        self.snappableTo = 'center-top';
                        jsPanel.createSnapArea(self, 'ct', snapSens);
                      } else {
                        self.snappableTo = false;
                        jsPanel.removeSnapAreas();
                      }
                    }
                  }
                } else if (elmtL < snapSens && leftVectorDrag < sideSensAreaLength) {
                  if (opts.snap.snapLeftCenter !== false) {
                    if (!opts.snap.active || opts.snap.active === 'both') {
                      self.snappableTo = 'left-center';
                      jsPanel.createSnapArea(self, 'lc', snapSens);
                    } else if (opts.snap.trigger === 'pointer' && opts.snap.active && opts.snap.active === 'inside') {
                      if (overlaps.pointer.left > 0) {
                        self.snappableTo = 'left-center';
                        jsPanel.createSnapArea(self, 'lc', snapSens);
                      } else {
                        self.snappableTo = false;
                        jsPanel.removeSnapAreas();
                      }
                    }
                  }
                } else if (elmtR < snapSens && rightVectorDrag < sideSensAreaLength) {
                  if (opts.snap.snapRightCenter !== false) {
                    if (!opts.snap.active || opts.snap.active === 'both') {
                      self.snappableTo = 'right-center';
                      jsPanel.createSnapArea(self, 'rc', snapSens);
                    } else if (opts.snap.trigger === 'pointer' && opts.snap.active && opts.snap.active === 'inside') {
                      if (overlaps.pointer.right > 0) {
                        self.snappableTo = 'right-center';
                        jsPanel.createSnapArea(self, 'rc', snapSens);
                      } else {
                        self.snappableTo = false;
                        jsPanel.removeSnapAreas();
                      }
                    }
                  }
                } else if (elmtB < snapSens && bottomVectorDrag < topSensAreaLength) {
                  if (opts.snap.snapCenterBottom !== false) {
                    if (!opts.snap.active || opts.snap.active === 'both') {
                      self.snappableTo = 'center-bottom';
                      jsPanel.createSnapArea(self, 'cb', snapSens);
                    } else if (opts.snap.trigger === 'pointer' && opts.snap.active && opts.snap.active === 'inside') {
                      if (overlaps.pointer.bottom > 0) {
                        self.snappableTo = 'center-bottom';
                        jsPanel.createSnapArea(self, 'cb', snapSens);
                      } else {
                        self.snappableTo = false;
                        jsPanel.removeSnapAreas();
                      }
                    }
                  }
                }
              } // opts.drop


              if (opts.drop && opts.drop.dropZones) {
                // IE doesn't offer document.elementsFromPoint() but document.msElementsFromPoint()
                var elementsFromPoint = jsPanel.isIE ? 'msElementsFromPoint' : 'elementsFromPoint';
                var elementsFrom = document[elementsFromPoint](e.clientX, e.clientY); // document.msElementsFromPoint() returns a nodeList -> convert to array

                if (!Array.isArray(elementsFrom)) {
                  elementsFrom = Array.prototype.slice.call(elementsFrom);
                }

                opts.drop.dropZones.forEach(function (zone) {
                  // Array.prototype.includes() needs polyfill in IE
                  if (elementsFrom.includes(zone)) {
                    self.droppableTo = zone;
                  }
                }); // do not include following if statement in this.options.dragit.drop.dropZones.forEach !!!!

                if (!elementsFrom.includes(self.droppableTo)) {
                  self.droppableTo = false;
                }
              }
            };

            jsPanel.pointermove.forEach(function (e) {
              document.addEventListener(e, dragElmt);
            }); // remove drag handler when mouse leaves browser window (mouseleave doesn't work)

            window.addEventListener('mouseout', windowListener, false);
          });
        });
        jsPanel.pointerup.forEach(function (event) {
          document.addEventListener(event, pointerUpHandlerDragit);
          window.removeEventListener('mouseout', windowListener);
        }); // dragit is initialized - now disable if set

        if (options.disable) {
          handle.style.pointerEvents = 'none';
        }
      });
      return self;
    };

    self.dragit = function (string) {
      var dragitOptions = Object.assign({}, jsPanel.defaults.dragit, options.dragit),
          handles = self.querySelectorAll(dragitOptions.handles);

      if (string === 'disable') {
        handles.forEach(function (handle) {
          handle.style.pointerEvents = 'none';
        });
      } else {
        handles.forEach(function (handle) {
          handle.style.pointerEvents = 'auto';
        });
      }

      return self;
    };

    self.sizeit = function () {
      var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      var jspanelresizestart = new CustomEvent('jspanelresizestart', {
        detail: self.id
      }),
          jspanelresize = new CustomEvent('jspanelresize', {
        detail: self.id
      }),
          jspanelresizestop = new CustomEvent('jspanelresizestop', {
        detail: self.id
      }); // make panel available as event object property 'panel'

      [jspanelresizestart, jspanelresize, jspanelresizestop].forEach(function (evt) {
        evt.panel = self;
      });
      var opts = {},
          resizePanel,
          resizestarted,
          w,
          h,
          startWidth,
          startHeight;
      opts.handles = options.handles || jsPanel.defaults.resizeit.handles;
      opts.handles.split(',').forEach(function (item) {
        var node = document.createElement('DIV');
        node.className = "jsPanel-resizeit-handle jsPanel-resizeit-".concat(item.trim()); //node.style.zIndex = 90;

        self.append(node);
      }); // cache option aspectRatio of original resizeit configuration (is restored on pointerup)

      var cachedOptionAspectRatio = options.aspectRatio ? options.aspectRatio : false;

      function windowListener(e) {
        if (e.relatedTarget === null) {
          jsPanel.pointermove.forEach(function (evt) {
            document.removeEventListener(evt, resizePanel, false);
          });
        }
      }

      function pointerUpHandlerResizeit(e) {
        jsPanel.pointermove.forEach(function (evt) {
          document.removeEventListener(evt, resizePanel, false);
        });

        if (e.target.classList && e.target.classList.contains('jsPanel-resizeit-handle')) {
          var isLeftChange,
              isTopChange,
              cl = e.target.className;

          if (cl.match(/jsPanel-resizeit-nw|jsPanel-resizeit-w|jsPanel-resizeit-sw/i)) {
            isLeftChange = true;
          }

          if (cl.match(/jsPanel-resizeit-nw|jsPanel-resizeit-n|jsPanel-resizeit-ne/i)) {
            isTopChange = true;
          } // snap panel to grid (doesn't work that well if inside function resizePanel)


          if (opts.grid && Array.isArray(opts.grid)) {
            if (opts.grid.length === 1) {
              opts.grid[1] = opts.grid[0];
            }

            var cw = parseFloat(self.style.width),
                ch = parseFloat(self.style.height),
                modW = cw % opts.grid[0],
                modH = ch % opts.grid[1],
                cx = parseFloat(self.style.left),
                cy = parseFloat(self.style.top),
                modX = cx % opts.grid[0],
                modY = cy % opts.grid[1];

            if (modW < opts.grid[0] / 2) {
              self.style.width = cw - modW + 'px';
            } else {
              self.style.width = cw + (opts.grid[0] - modW) + 'px';
            }

            if (modH < opts.grid[1] / 2) {
              self.style.height = ch - modH + 'px';
            } else {
              self.style.height = ch + (opts.grid[1] - modH) + 'px';
            }

            if (isLeftChange) {
              if (modX < opts.grid[0] / 2) {
                self.style.left = cx - modX + 'px';
              } else {
                self.style.left = cx + (opts.grid[0] - modX) + 'px';
              }
            }

            if (isTopChange) {
              if (modY < opts.grid[1] / 2) {
                self.style.top = cy - modY + 'px';
              } else {
                self.style.top = cy + (opts.grid[1] - modY) + 'px';
              }
            }
          }
        }

        if (resizestarted) {
          self.content.style.pointerEvents = 'inherit';
          resizestarted = undefined;
          self.saveCurrentDimensions();
          self.saveCurrentPosition();
          self.calcSizeFactors();
          var smallifyBtn = self.controlbar.querySelector('.jsPanel-btn-smallify');
          var elmtRect = self.getBoundingClientRect();

          if (smallifyBtn && elmtRect.height > startHeight + 5) {
            smallifyBtn.style.transform = 'rotate(0deg)';
          }

          document.dispatchEvent(jspanelresizestop);

          if (opts.stop.length) {
            var stopStyles = window.getComputedStyle(self),
                paneldata = {
              left: parseFloat(stopStyles.left),
              top: parseFloat(stopStyles.top),
              width: parseFloat(stopStyles.width),
              height: parseFloat(stopStyles.height)
            };
            jsPanel.processCallbacks(self, opts.stop, false, paneldata, e);
          }
        }

        self.content.style.pointerEvents = 'inherit'; // restore other panel's css pointer-events

        document.querySelectorAll('iframe').forEach(function (frame) {
          frame.style.pointerEvents = 'auto';
        }); // restore option aspectRatio to original configuration

        opts.aspectRatio = cachedOptionAspectRatio;
        document.removeEventListener(e, pointerUpHandlerResizeit);
      }

      self.querySelectorAll('.jsPanel-resizeit-handle').forEach(function (handle) {
        handle.style.touchAction = 'none';
        jsPanel.pointerdown.forEach(function (event) {
          handle.addEventListener(event, function (e) {
            // prevent window scroll while resizing elmt
            e.preventDefault();
            e.stopPropagation(); // disable resizing for all mouse buttons but left

            if (e.button && e.button > 0) {
              return false;
            } // factor is needed only for the modifier key Shift feature


            var factor = 1; // setup and normalize resizeit options

            opts = Object.assign({}, jsPanel.defaults.resizeit, options);

            if (opts.containment || opts.containment === 0) {
              opts.containment = jsPanel.pOcontainment(opts.containment);
            } // legacy line: aspectRatio should be either 'panel' or 'content', not just true


            if (opts.aspectRatio && opts.aspectRatio === true) {
              opts.aspectRatio = 'panel';
            } // set aspectRatio according to modifier key


            if (jsPanel.modifier) {
              var modifier = jsPanel.modifier;

              if (modifier.altKey) {
                opts.aspectRatio = 'content';
              } else if (modifier.ctrlKey) {
                opts.aspectRatio = 'panel';
              } else if (modifier.shiftKey) {
                opts.aspectRatio = false;
                factor = 2; // does work only with 2 as value
              }
            } // noinspection JSUnresolvedFunction


            var maxWidth = typeof opts.maxWidth === 'function' ? opts.maxWidth() : opts.maxWidth || 10000,
                maxHeight = typeof opts.maxHeight === 'function' ? opts.maxHeight() : opts.maxHeight || 10000,
                minWidth = typeof opts.minWidth === 'function' ? opts.minWidth() : opts.minWidth,
                minHeight = typeof opts.minHeight === 'function' ? opts.minHeight() : opts.minHeight;
            self.content.style.pointerEvents = 'none'; // prevents iframes in other panel from interfering with resize action of dragged panel

            document.querySelectorAll('iframe').forEach(function (frame) {
              frame.style.pointerEvents = 'none';
            }); // noinspection JSUnresolvedVariable

            var elmtParent = self.parentElement,
                elmtParentTagName = elmtParent.tagName.toLowerCase(),
                elmtRect = self.getBoundingClientRect(),
                elmtParentRect = elmtParent.getBoundingClientRect(),
                elmtParentStyles = window.getComputedStyle(elmtParent, null),
                elmtParentBLW = parseInt(elmtParentStyles.borderLeftWidth, 10),
                elmtParentBTW = parseInt(elmtParentStyles.borderTopWidth, 10),
                elmtParentPosition = elmtParentStyles.getPropertyValue('position'),
                startX = e.clientX || e.clientX === 0 || e.touches[0].clientX,
                startY = e.clientY || e.clientY === 0 || e.touches[0].clientY,
                startRatio = startX / startY,
                resizeHandleClassList = e.target.classList,
                scaleFactor = self.getScaleFactor(),
                aspectRatio = elmtRect.width / elmtRect.height,
                elmtContentRect = self.content.getBoundingClientRect(),
                aspectRatioContent = elmtContentRect.width / elmtContentRect.height,
                hdrHeight = self.header.getBoundingClientRect().height,
                // needed in aspectRatio
            ftrHeight = self.footer.getBoundingClientRect().height || 0; // needed in aspectRatio

            var startLeft = elmtRect.left,
                startTop = elmtRect.top,
                maxWidthEast = 10000,
                maxWidthWest = 10000,
                maxHeightSouth = 10000,
                maxHeightNorth = 10000;
            startWidth = elmtRect.width;
            startHeight = elmtRect.height;

            if (elmtParentTagName !== 'body') {
              startLeft = elmtRect.left - elmtParentRect.left + elmtParent.scrollLeft;
              startTop = elmtRect.top - elmtParentRect.top + elmtParent.scrollTop;
            } // calc min/max left/top values if containment is set - code from jsDraggable


            if (elmtParentTagName === 'body' && opts.containment) {
              maxWidthEast = document.documentElement.clientWidth - elmtRect.left;
              maxHeightSouth = document.documentElement.clientHeight - elmtRect.top;
              maxWidthWest = elmtRect.width + elmtRect.left;
              maxHeightNorth = elmtRect.height + elmtRect.top;
            } else {
              // if panel is NOT in body
              if (opts.containment) {
                if (elmtParentPosition === 'static') {
                  maxWidthEast = elmtParentRect.width - elmtRect.left + elmtParentBLW;
                  maxHeightSouth = elmtParentRect.height + elmtParentRect.top - elmtRect.top + elmtParentBTW;
                  maxWidthWest = elmtRect.width + (elmtRect.left - elmtParentRect.left) - elmtParentBLW;
                  maxHeightNorth = elmtRect.height + (elmtRect.top - elmtParentRect.top) - elmtParentBTW;
                } else {
                  maxWidthEast = elmtParent.clientWidth - (elmtRect.left - elmtParentRect.left) / scaleFactor.x + elmtParentBLW;
                  maxHeightSouth = elmtParent.clientHeight - (elmtRect.top - elmtParentRect.top) / scaleFactor.y + elmtParentBTW;
                  maxWidthWest = (elmtRect.width + elmtRect.left - elmtParentRect.left) / scaleFactor.x - elmtParentBLW;
                  maxHeightNorth = self.clientHeight + (elmtRect.top - elmtParentRect.top) / scaleFactor.y - elmtParentBTW;
                }
              }
            } // if original opts.containment is array


            if (opts.containment) {
              maxWidthWest -= opts.containment[3];
              maxHeightNorth -= opts.containment[0];
              maxWidthEast -= opts.containment[1];
              maxHeightSouth -= opts.containment[2];
            } // calculate corrections for rotated panels


            var computedStyle = window.getComputedStyle(self),
                wDif = parseFloat(computedStyle.width) - elmtRect.width,
                hDif = parseFloat(computedStyle.height) - elmtRect.height;
            var xDif = parseFloat(computedStyle.left) - elmtRect.left,
                yDif = parseFloat(computedStyle.top) - elmtRect.top;

            if (elmtParent !== document.body) {
              xDif += elmtParentRect.left;
              yDif += elmtParentRect.top;
            } // used in aspectRatio code


            var borderTopWidth = parseInt(computedStyle.borderTopWidth, 10),
                borderRightWidth = parseInt(computedStyle.borderRightWidth, 10),
                borderBottomWidth = parseInt(computedStyle.borderBottomWidth, 10),
                borderLeftWidth = parseInt(computedStyle.borderLeftWidth, 10);

            resizePanel = function resizePanel(evt) {
              evt.preventDefault(); // trigger resizestarted only once per resize

              if (!resizestarted) {
                document.dispatchEvent(jspanelresizestart);

                if (opts.start.length) {
                  jsPanel.processCallbacks(self, opts.start, false, {
                    width: startWidth,
                    height: startHeight,
                    left: startLeft,
                    top: startTop
                  }, evt);
                }

                self.front();

                if (elmtRect.height > startHeight + 5) {
                  self.status = 'normalized';
                  self.setControls(['.jsPanel-btn-normalize']);
                }
              }

              resizestarted = 1; // trigger resize permanently while resizing

              document.dispatchEvent(jspanelresize); // possibly updated while resizing

              var eventX = evt.touches ? evt.touches[0].clientX : evt.clientX,
                  eventY = evt.touches ? evt.touches[0].clientY : evt.clientY,
                  overlaps;

              if (resizeHandleClassList.contains('jsPanel-resizeit-e')) {
                //w = startWidth + (eventX - startX) / scaleFactor.x + wDif;
                w = startWidth + (eventX - startX) * factor / scaleFactor.x + wDif; // needs left adjust, for width and height adjust factor may be either 1 (no adjust) or 2

                if (w >= maxWidthEast) {
                  w = maxWidthEast;
                }

                if (w >= maxWidth) {
                  w = maxWidth;
                }

                if (w <= minWidth) {
                  w = minWidth;
                }

                self.style.width = w + 'px';

                if (factor === 2) {
                  // factor works only with value of 2 when adjusting left or top
                  self.style.left = startLeft - (eventX - startX) + 'px';
                }

                if (opts.aspectRatio === 'content') {
                  // if aspectRatio is true and set to 'content' the panels content section maintains its aspect ratio
                  self.style.height = (w - borderRightWidth - borderLeftWidth) / aspectRatioContent + hdrHeight + ftrHeight + borderTopWidth + borderBottomWidth + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.bottom <= opts.containment[2]) {
                      self.style.height = maxHeightSouth + 'px';
                      self.style.width = maxHeightSouth * aspectRatioContent + 'px';
                    }
                  }
                } else if (opts.aspectRatio === 'panel') {
                  // otherwise the complete panel maintains its aspect ratio
                  self.style.height = w / aspectRatio + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.bottom <= opts.containment[2]) {
                      self.style.height = maxHeightSouth + 'px';
                      self.style.width = maxHeightSouth * aspectRatio + 'px';
                    }
                  }
                }
              } else if (resizeHandleClassList.contains('jsPanel-resizeit-s')) {
                //h = startHeight + (eventY - startY) / scaleFactor.y + hDif;
                h = startHeight + (eventY - startY) * factor / scaleFactor.y + hDif; // needs top adjust

                if (h >= maxHeightSouth) {
                  h = maxHeightSouth;
                }

                if (h >= maxHeight) {
                  h = maxHeight;
                }

                if (h <= minHeight) {
                  h = minHeight;
                }

                self.style.height = h + 'px';

                if (factor === 2) {
                  self.style.top = startTop - (eventY - startY) + 'px';
                }

                if (opts.aspectRatio === 'content') {
                  // if aspectRatio is true and set to 'content' the panels content section maintains its aspect ratio
                  self.style.width = (h - hdrHeight - ftrHeight - borderTopWidth - borderBottomWidth) * aspectRatioContent + borderTopWidth + borderBottomWidth + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.right <= opts.containment[1]) {
                      self.style.width = maxWidthEast + 'px';
                      self.style.height = maxWidthEast / aspectRatioContent + 'px';
                    }
                  }
                } else if (opts.aspectRatio === 'panel') {
                  // otherwise the complete panel maintains its aspect ratio
                  self.style.width = h * aspectRatio + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.right <= opts.containment[1]) {
                      self.style.width = maxWidthEast + 'px';
                      self.style.height = maxWidthEast / aspectRatio + 'px';
                    }
                  }
                }
              } else if (resizeHandleClassList.contains('jsPanel-resizeit-w')) {
                //w = startWidth + (startX - eventX) / scaleFactor.x + wDif;
                w = startWidth + (startX - eventX) * factor / scaleFactor.x + wDif; // doesn't need left adjust

                if (w <= maxWidth && w >= minWidth && w <= maxWidthWest) {
                  self.style.left = startLeft + (eventX - startX) / scaleFactor.x + xDif + 'px';
                }

                if (w >= maxWidthWest) {
                  w = maxWidthWest;
                }

                if (w >= maxWidth) {
                  w = maxWidth;
                }

                if (w <= minWidth) {
                  w = minWidth;
                }

                self.style.width = w + 'px';

                if (opts.aspectRatio === 'content') {
                  // if aspectRatio is true and set to 'content' the panels content section maintains its aspect ratio
                  self.style.height = (w - borderRightWidth - borderLeftWidth) / aspectRatioContent + hdrHeight + ftrHeight + borderTopWidth + borderBottomWidth + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.bottom <= opts.containment[2]) {
                      self.style.height = maxHeightSouth + 'px';
                      self.style.width = maxHeightSouth * aspectRatioContent + 'px';
                    }
                  }
                } else if (opts.aspectRatio === 'panel') {
                  // otherwise the complete panel maintains its aspect ratio
                  self.style.height = w / aspectRatio + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.bottom <= opts.containment[2]) {
                      self.style.height = maxHeightSouth + 'px';
                      self.style.width = maxHeightSouth * aspectRatio + 'px';
                    }
                  }
                }
              } else if (resizeHandleClassList.contains('jsPanel-resizeit-n')) {
                //h = startHeight + (startY - eventY) / scaleFactor.y + hDif;
                h = startHeight + (startY - eventY) * factor / scaleFactor.y + hDif; // doesn't need top adjust

                if (h <= maxHeight && h >= minHeight && h <= maxHeightNorth) {
                  self.style.top = startTop + (eventY - startY) / scaleFactor.y + yDif + 'px';
                }

                if (h >= maxHeightNorth) {
                  h = maxHeightNorth;
                }

                if (h >= maxHeight) {
                  h = maxHeight;
                }

                if (h <= minHeight) {
                  h = minHeight;
                }

                self.style.height = h + 'px';

                if (opts.aspectRatio === 'content') {
                  // if aspectRatio is true and set to 'content' the panels content section maintains its aspect ratio
                  self.style.width = (h - hdrHeight - ftrHeight - borderTopWidth - borderBottomWidth) * aspectRatioContent + borderTopWidth + borderBottomWidth + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.right <= opts.containment[1]) {
                      self.style.width = maxWidthEast + 'px';
                      self.style.height = maxWidthEast / aspectRatioContent + 'px';
                    }
                  }
                } else if (opts.aspectRatio === 'panel') {
                  // otherwise the complete panel maintains its aspect ratio
                  self.style.width = h * aspectRatio + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.right <= opts.containment[1]) {
                      self.style.width = maxWidthEast + 'px';
                      self.style.height = maxWidthEast / aspectRatio + 'px';
                    }
                  }
                }
              } else if (resizeHandleClassList.contains('jsPanel-resizeit-se')) {
                //w = startWidth + (eventX - startX) / scaleFactor.x + wDif;
                w = startWidth + (eventX - startX) * factor / scaleFactor.x + wDif; // needs left adjust

                if (w >= maxWidthEast) {
                  w = maxWidthEast;
                }

                if (w >= maxWidth) {
                  w = maxWidth;
                }

                if (w <= minWidth) {
                  w = minWidth;
                }

                self.style.width = w + 'px';

                if (factor === 2) {
                  self.style.left = startLeft - (eventX - startX) + 'px';
                }

                if (opts.aspectRatio) {
                  self.style.height = w / aspectRatio + 'px';
                } //h = startHeight + (eventY - startY) / scaleFactor.y + hDif;


                h = startHeight + (eventY - startY) * factor / scaleFactor.y + hDif; // needs top adjust

                if (h >= maxHeightSouth) {
                  h = maxHeightSouth;
                }

                if (h >= maxHeight) {
                  h = maxHeight;
                }

                if (h <= minHeight) {
                  h = minHeight;
                }

                self.style.height = h + 'px';

                if (factor === 2) {
                  self.style.top = startTop - (eventY - startY) + 'px';
                }

                if (opts.aspectRatio === 'content') {
                  // if aspectRatio is true and set to 'content' the panels content section maintains its aspect ratio
                  self.style.width = (h - hdrHeight - ftrHeight - borderTopWidth - borderBottomWidth) * aspectRatioContent + borderTopWidth + borderBottomWidth + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.right <= opts.containment[1]) {
                      self.style.width = maxWidthEast + 'px';
                      self.style.height = maxWidthEast / aspectRatioContent + 'px';
                    }
                  }
                } else if (opts.aspectRatio === 'panel') {
                  // otherwise the complete panel maintains its aspect ratio
                  self.style.width = h * aspectRatio + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.right <= opts.containment[1]) {
                      self.style.width = maxWidthEast + 'px';
                      self.style.height = maxWidthEast / aspectRatio + 'px';
                    }
                  }
                }
              } else if (resizeHandleClassList.contains('jsPanel-resizeit-sw')) {
                //h = startHeight + (eventY - startY) / scaleFactor.y + hDif;
                h = startHeight + (eventY - startY) * factor / scaleFactor.y + hDif; // needs top adjust

                if (h >= maxHeightSouth) {
                  h = maxHeightSouth;
                }

                if (h >= maxHeight) {
                  h = maxHeight;
                }

                if (h <= minHeight) {
                  h = minHeight;
                }

                self.style.height = h + 'px';

                if (factor === 2) {
                  self.style.top = startTop - (eventY - startY) + 'px';
                }

                if (opts.aspectRatio) {
                  self.style.width = h * aspectRatio + 'px';
                } //w = startWidth + (startX - eventX) / scaleFactor.x + wDif;


                w = startWidth + (startX - eventX) * factor / scaleFactor.x + wDif; // doesn't need left adjust

                if (w <= maxWidth && w >= minWidth && w <= maxWidthWest) {
                  self.style.left = startLeft + (eventX - startX) / scaleFactor.x + xDif + 'px';
                }

                if (w >= maxWidthWest) {
                  w = maxWidthWest;
                }

                if (w >= maxWidth) {
                  w = maxWidth;
                }

                if (w <= minWidth) {
                  w = minWidth;
                }

                self.style.width = w + 'px';

                if (opts.aspectRatio === 'content') {
                  // if aspectRatio is true and set to 'content' the panels content section maintains its aspect ratio
                  self.style.height = (w - borderRightWidth - borderLeftWidth) / aspectRatioContent + hdrHeight + ftrHeight + borderTopWidth + borderBottomWidth + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.bottom <= opts.containment[2]) {
                      self.style.height = maxHeightSouth + 'px';
                      self.style.width = maxHeightSouth * aspectRatioContent + 'px';
                    }
                  }
                } else if (opts.aspectRatio === 'panel') {
                  // otherwise the complete panel maintains its aspect ratio
                  self.style.height = w / aspectRatio + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.bottom <= opts.containment[2]) {
                      self.style.height = maxHeightSouth + 'px';
                      self.style.width = maxHeightSouth * aspectRatio + 'px';
                    }
                  }
                }
              } else if (resizeHandleClassList.contains('jsPanel-resizeit-ne')) {
                //w = startWidth + (eventX - startX) / scaleFactor.x + wDif;
                w = startWidth + (eventX - startX) * factor / scaleFactor.x + wDif; // needs left adjust

                if (w >= maxWidthEast) {
                  w = maxWidthEast;
                }

                if (w >= maxWidth) {
                  w = maxWidth;
                }

                if (w <= minWidth) {
                  w = minWidth;
                }

                self.style.width = w + 'px';

                if (factor === 2) {
                  self.style.left = startLeft - (eventX - startX) + 'px';
                }

                if (opts.aspectRatio) {
                  self.style.height = w / aspectRatio + 'px';
                } //h = startHeight + (startY - eventY) / scaleFactor.y + hDif;


                h = startHeight + (startY - eventY) * factor / scaleFactor.y + hDif; // doesn't need top adjust

                if (h <= maxHeight && h >= minHeight && h <= maxHeightNorth) {
                  self.style.top = startTop + (eventY - startY) / scaleFactor.y + yDif + 'px';
                }

                if (h >= maxHeightNorth) {
                  h = maxHeightNorth;
                }

                if (h >= maxHeight) {
                  h = maxHeight;
                }

                if (h <= minHeight) {
                  h = minHeight;
                }

                self.style.height = h + 'px';

                if (opts.aspectRatio === 'content') {
                  // if aspectRatio is true and set to 'content' the panels content section maintains its aspect ratio
                  self.style.width = (h - hdrHeight - ftrHeight - borderTopWidth - borderBottomWidth) * aspectRatioContent + borderTopWidth + borderBottomWidth + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.right <= opts.containment[1]) {
                      self.style.width = maxWidthEast + 'px';
                      self.style.height = maxWidthEast / aspectRatioContent + 'px';
                    }
                  }
                } else if (opts.aspectRatio === 'panel') {
                  // otherwise the complete panel maintains its aspect ratio
                  self.style.width = h * aspectRatio + 'px';

                  if (opts.containment) {
                    overlaps = self.overlaps(elmtParent);

                    if (overlaps.right <= opts.containment[1]) {
                      self.style.width = maxWidthEast + 'px';
                      self.style.height = maxWidthEast / aspectRatio + 'px';
                    }
                  }
                }
              } else if (resizeHandleClassList.contains('jsPanel-resizeit-nw')) {
                if (opts.aspectRatio && resizeHandleClassList.contains('jsPanel-resizeit-nw')) {
                  eventX = eventY * startRatio;
                  eventY = eventX / startRatio;
                } //w = startWidth + (startX - eventX) / scaleFactor.x + wDif;


                w = startWidth + (startX - eventX) * factor / scaleFactor.x + wDif; // doesn't need left adjust

                if (w <= maxWidth && w >= minWidth && w <= maxWidthWest) {
                  self.style.left = startLeft + (eventX - startX) / scaleFactor.x + xDif + 'px';
                }

                if (w >= maxWidthWest) {
                  w = maxWidthWest;
                }

                if (w >= maxWidth) {
                  w = maxWidth;
                }

                if (w <= minWidth) {
                  w = minWidth;
                }

                self.style.width = w + 'px';

                if (opts.aspectRatio) {
                  self.style.height = w / aspectRatio + 'px';
                } //h = startHeight + (startY - eventY) / scaleFactor.y + hDif;


                h = startHeight + (startY - eventY) * factor / scaleFactor.y + hDif; // doesn't need top adjust

                if (h <= maxHeight && h >= minHeight && h <= maxHeightNorth) {
                  self.style.top = startTop + (eventY - startY) / scaleFactor.y + yDif + 'px';
                }

                if (h >= maxHeightNorth) {
                  h = maxHeightNorth;
                }

                if (h >= maxHeight) {
                  h = maxHeight;
                }

                if (h <= minHeight) {
                  h = minHeight;
                }

                self.style.height = h + 'px';

                if (opts.aspectRatio === 'content') {
                  // if aspectRatio is true and set to 'content' the panels content section maintains its aspect ratio
                  self.style.width = (h - hdrHeight - ftrHeight - borderTopWidth - borderBottomWidth) * aspectRatioContent + borderTopWidth + borderBottomWidth + 'px';
                } else if (opts.aspectRatio === 'panel') {
                  // otherwise the complete panel maintains its aspect ratio
                  self.style.width = h * aspectRatio + 'px';
                }
              }

              window.getSelection().removeAllRanges(); // get current position and size values while resizing

              var styles = window.getComputedStyle(self),
                  values = {
                left: parseFloat(styles.left),
                top: parseFloat(styles.top),
                right: parseFloat(styles.right),
                bottom: parseFloat(styles.bottom),
                width: parseFloat(styles.width),
                height: parseFloat(styles.height)
              }; // callback while resizing

              if (opts.resize.length) {
                jsPanel.processCallbacks(self, opts.resize, false, values, evt);
              }
            };

            jsPanel.pointermove.forEach(function (event) {
              document.addEventListener(event, resizePanel, false);
            }); // remove resize handler when mouse leaves browser window (mouseleave doesn't work)

            window.addEventListener('mouseout', windowListener, false);
          });
        });
        jsPanel.pointerup.forEach(function (event) {
          document.addEventListener(event, pointerUpHandlerResizeit);
          window.removeEventListener('mouseout', windowListener);
        }); // resizeit is initialized - now disable if set

        if (options.disable) {
          handle.style.pointerEvents = 'none';
        }
      });
      return self;
    };

    self.resizeit = function (string) {
      var handles = self.querySelectorAll('.jsPanel-resizeit-handle');

      if (string === 'disable') {
        handles.forEach(function (handle) {
          handle.style.pointerEvents = 'none';
        });
      } else {
        handles.forEach(function (handle) {
          handle.style.pointerEvents = 'auto';
        });
      }

      return self;
    };

    self.getScaleFactor = function () {
      var rect = self.getBoundingClientRect();
      return {
        x: rect.width / self.offsetWidth,
        y: rect.height / self.offsetHeight
      };
    };

    self.calcSizeFactors = function () {
      var styles = window.getComputedStyle(self);

      if (options.container === 'window') {
        self.hf = parseFloat(styles.left) / (window.innerWidth - parseFloat(styles.width));
        self.vf = parseFloat(styles.top) / (window.innerHeight - parseFloat(styles.height));
      } else {
        if (self.parentElement) {
          var parentStyles = self.parentElement.getBoundingClientRect();
          self.hf = parseFloat(styles.left) / (parentStyles.width - parseFloat(styles.width));
          self.vf = parseFloat(styles.top) / (parentStyles.height - parseFloat(styles.height));
        }
      }
    };

    self.saveCurrentDimensions = function () {
      var setStyleHeight = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
      var normData = window.getComputedStyle(self);
      self.currentData.width = normData.width;

      if (self.status === 'normalized') {
        self.currentData.height = normData.height;
      }

      if (setStyleHeight) {
        self.style.height = normData.height;
      }
    };

    self.saveCurrentPosition = function () {
      var normData = window.getComputedStyle(self);
      self.currentData.left = normData.left;
      self.currentData.top = normData.top;
    };

    self.reposition = function () {
      var pos = options.position,
          updateCache = true,
          callback;

      for (var _len = arguments.length, params = new Array(_len), _key = 0; _key < _len; _key++) {
        params[_key] = arguments[_key];
      }

      params.forEach(function (value) {
        if (typeof value === 'string' || _typeof(value) === 'object') {
          pos = value;
        } else if (typeof value === 'boolean') {
          updateCache = value;
        } else if (typeof value === 'function') {
          callback = value;
        }
      });
      jsPanel.position(self, pos); // check whether self has docked panels -> reposition docked panels as well

      if (self.slaves && self.slaves.size > 0) {
        self.slaves.forEach(function (slave) {
          slave.reposition();
        });
      }

      if (updateCache) {
        self.saveCurrentPosition();
      }

      if (callback) {
        callback.call(self, self);
      }

      return self;
    };

    self.repositionOnSnap = function (pos) {
      var offsetX = '0',
          offsetY = '0',
          margins = jsPanel.pOcontainment(options.dragit.containment); // calculate offsets

      if (options.dragit.snap.containment) {
        switch (pos) {
          case 'left-top':
            offsetX = margins[3];
            offsetY = margins[0];
            break;

          case 'right-top':
            offsetX = -margins[1];
            offsetY = margins[0];
            break;

          case 'right-bottom':
            offsetX = -margins[1];
            offsetY = -margins[2];
            break;

          case 'left-bottom':
            offsetX = margins[3];
            offsetY = -margins[2];
            break;

          case 'center-top':
            offsetX = margins[3] / 2 - margins[1] / 2;
            offsetY = margins[0];
            break;

          case 'center-bottom':
            offsetX = margins[3] / 2 - margins[1] / 2;
            offsetY = -margins[2];
            break;

          case 'left-center':
            offsetX = margins[3];
            offsetY = margins[0] / 2 - margins[2] / 2;
            break;

          case 'right-center':
            offsetX = -margins[1];
            offsetY = margins[0] / 2 - margins[2] / 2;
            break;
        }
      }
      /* jsPanel.position(self, `${pos} ${offsetX} ${offsetY}`);
         For some reason I could not find the line above does not work (pos and offsets in one string), but only when
         center-bottom is used with different settings for left/right margin.
      */


      jsPanel.position(self, pos);
      jsPanel.setStyle(self, {
        left: "calc(".concat(self.style.left, " + ").concat(offsetX, "px)"),
        top: "calc(".concat(self.style.top, " + ").concat(offsetY, "px)")
      });
    };

    self.overlaps = function (reference, elmtBox, event) {
      var panelRect = self.getBoundingClientRect(),
          parentStyle = getComputedStyle(self.parentElement),
          scaleFactor = self.getScaleFactor(),
          parentBorderWidth = {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
      },
          referenceRect,
          evtX = 0,
          evtY = 0,
          evtXparent = 0,
          evtYparent = 0;

      if (self.options.container !== 'window' && elmtBox === 'paddingbox') {
        parentBorderWidth.top = parseInt(parentStyle.borderTopWidth, 10) * scaleFactor.y;
        parentBorderWidth.right = parseInt(parentStyle.borderRightWidth, 10) * scaleFactor.x;
        parentBorderWidth.bottom = parseInt(parentStyle.borderBottomWidth, 10) * scaleFactor.y;
        parentBorderWidth.left = parseInt(parentStyle.borderLeftWidth, 10) * scaleFactor.x;
      }

      if (typeof reference === 'string') {
        if (reference === 'window') {
          referenceRect = {
            left: 0,
            top: 0,
            right: window.innerWidth,
            bottom: window.innerHeight
          };
        } else if (reference === 'parent') {
          referenceRect = self.parentElement.getBoundingClientRect();
        } else {
          referenceRect = document.querySelector(reference).getBoundingClientRect();
        }
      } else {
        referenceRect = reference.getBoundingClientRect();
      }

      if (event) {
        evtX = event.touches ? event.touches[0].clientX : event.clientX;
        evtY = event.touches ? event.touches[0].clientY : event.clientY;
        evtXparent = evtX - referenceRect.left;
        evtYparent = evtY - referenceRect.top;
      }

      var overlapsX = panelRect.left < referenceRect.right && panelRect.right > referenceRect.left,
          overlapsY = panelRect.top < referenceRect.bottom && panelRect.bottom > referenceRect.top,
          overlaps = overlapsX && overlapsY;
      return {
        overlaps: overlaps,
        top: panelRect.top - referenceRect.top - parentBorderWidth.top,
        right: referenceRect.right - panelRect.right - parentBorderWidth.right,
        bottom: referenceRect.bottom - panelRect.bottom - parentBorderWidth.bottom,
        left: panelRect.left - referenceRect.left - parentBorderWidth.left,
        parentBorderWidth: parentBorderWidth,
        panelRect: panelRect,
        referenceRect: referenceRect,
        pointer: {
          // pointer coords relative to window and reference
          clientX: evtX,
          clientY: evtY,
          left: evtXparent - parentBorderWidth.left,
          top: evtYparent - parentBorderWidth.top,
          right: referenceRect.width - evtXparent - parentBorderWidth.right,
          bottom: referenceRect.height - evtYparent - parentBorderWidth.bottom
        }
      };
    };

    self.setSize = function () {
      if (options.panelSize) {
        var values = jsPanel.pOsize(self, options.panelSize);
        self.style.width = values.width;
        self.style.height = values.height;
      } else if (options.contentSize) {
        var _values = jsPanel.pOsize(self, options.contentSize);

        self.content.style.width = _values.width;
        self.content.style.height = _values.height;
        self.style.width = _values.width; // explicitly assign current width/height to panel

        self.content.style.width = '100%';
      }

      return self;
    };

    self.resize = function () {
      var dimensions = window.getComputedStyle(self),
          size = {
        width: dimensions.width,
        height: dimensions.height
      },
          updateCache = true,
          callback;

      for (var _len2 = arguments.length, params = new Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
        params[_key2] = arguments[_key2];
      }

      params.forEach(function (value) {
        if (typeof value === 'string') {
          size = value;
        } else if (_typeof(value) === 'object') {
          size = Object.assign(size, value);
        } else if (typeof value === 'boolean') {
          updateCache = value;
        } else if (typeof value === 'function') {
          callback = value;
        }
      });
      var values = jsPanel.pOsize(self, size);
      self.style.width = values.width;
      self.style.height = values.height; // check whether self has docked panels -> reposition docked panels

      if (self.slaves && self.slaves.size > 0) {
        self.slaves.forEach(function (slave) {
          slave.reposition();
        });
      }

      if (updateCache) {
        self.saveCurrentDimensions();
      }

      self.status = 'normalized';
      var smallifyBtn = self.controlbar.querySelector('.jsPanel-btn-smallify');

      if (smallifyBtn) {
        smallifyBtn.style.transform = 'rotate(0deg)';
      }

      if (callback) {
        callback.call(self, self);
      }

      self.calcSizeFactors();
      return self;
    };

    self.windowResizeHandler = function (e) {
      if (e.target === window) {
        // see https://bugs.jqueryui.com/ticket/7514
        var status = self.status,
            onWindowResize = options.onwindowresize,
            left,
            top;

        if (status === 'maximized' && onWindowResize) {
          self.maximize(false, true);
        } else if (self.snapped && status !== 'minimized') {
          self.snap(self.snapped, true);
        } else if (status === 'normalized' || status === 'smallified' || status === 'maximized') {
          if (typeof onWindowResize === 'function') {
            onWindowResize.call(self, e, self);
          } else {
            left = (window.innerWidth - self.offsetWidth) * self.hf;
            self.style.left = left <= 0 ? 0 : left + 'px';
            top = (window.innerHeight - self.offsetHeight) * self.vf;
            self.style.top = top <= 0 ? 0 : top + 'px';
          }
        } else if (status === 'smallifiedmax' && onWindowResize) {
          self.maximize(false, true).smallify();
        } // check whether self has docked panels -> reposition docked panels as well


        if (self.slaves && self.slaves.size > 0) {
          self.slaves.forEach(function (slave) {
            slave.reposition();
          });
        }
      }
    };

    self.setControls = function (sel, cb) {
      self.header.querySelectorAll('.jsPanel-btn').forEach(function (item) {
        var btnClass = item.className.split('-'),
            btn = btnClass[btnClass.length - 1];

        if (self.getAttribute("data-btn".concat(btn)) !== 'hidden') {
          item.style.display = 'block';
        }
      });
      sel.forEach(function (item) {
        var btn = self.controlbar.querySelector(item);

        if (btn) {
          btn.style.display = 'none';
        }
      });

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.setControlStatus = function (ctrl) {
      var action = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 'enable';
      var cb = arguments.length > 2 ? arguments[2] : undefined;
      var btn = self.controlbar.querySelector(".jsPanel-btn-".concat(ctrl));

      switch (action) {
        case 'disable':
          if (self.getAttribute("data-btn".concat(ctrl)) !== 'removed') {
            self.setAttribute("data-btn".concat(ctrl), 'disabled');
            btn.style.pointerEvents = 'none';
            btn.style.opacity = 0.4;
            btn.style.cursor = 'default';
          }

          break;

        case 'hide':
          if (self.getAttribute("data-btn".concat(ctrl)) !== 'removed') {
            self.setAttribute("data-btn".concat(ctrl), 'hidden');
            btn.style.display = 'none';
          }

          break;

        case 'show':
          if (self.getAttribute("data-btn".concat(ctrl)) !== 'removed') {
            self.setAttribute("data-btn".concat(ctrl), 'enabled');
            btn.style.display = 'block';
            btn.style.pointerEvents = 'auto';
            btn.style.opacity = 1;
            btn.style.cursor = 'pointer';
          }

          break;

        case 'enable':
          if (self.getAttribute("data-btn".concat(ctrl)) !== 'removed') {
            if (self.getAttribute("data-btn".concat(ctrl)) === 'hidden') {
              btn.style.display = 'block';
            }

            self.setAttribute("data-btn".concat(ctrl), 'enabled');
            btn.style.pointerEvents = 'auto';
            btn.style.opacity = 1;
            btn.style.cursor = 'pointer';
          }

          break;

        case 'remove':
          self.controlbar.removeChild(btn);
          self.setAttribute("data-btn".concat(ctrl), 'removed');
          break;
      }

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.setControlSize = function (ctrlSize) {
      // does not work with Font Awesome webfont (only svg/js)
      var size = ctrlSize.toLowerCase(),
          icons = self.controlbar.querySelectorAll('.jsPanel-btn');
      icons.forEach(function (icon) {
        ['jsPanel-btn-xl', 'jsPanel-btn-lg', 'jsPanel-btn-md', 'jsPanel-btn-sm', 'jsPanel-btn-xs'].forEach(function (item) {
          icon.classList.remove(item);
        });
        icon.classList.add("jsPanel-btn-".concat(size));
      }); // adjust font-size of title

      if (size === 'xl') {
        self.titlebar.style.fontSize = '1.5rem';
      } else if (size === 'lg') {
        self.titlebar.style.fontSize = '1.25rem';
      } else if (size === 'md') {
        self.titlebar.style.fontSize = '1.05rem';
      } else if (size === 'sm') {
        self.titlebar.style.fontSize = '.9rem';
      } else if (size === 'xs') {
        self.titlebar.style.fontSize = '.8rem';
      }
    };

    self.setHeaderControls = function (cb) {
      // add custom controls
      if (self.options.headerControls.add) {
        var customControls = self.options.headerControls.add;

        if (!Array.isArray(customControls)) {
          // if options.addControls is not an array make it one
          customControls = [customControls];
        }

        customControls.forEach(function (ctrl) {
          self.addControl(ctrl);
        });
      } // get all control names including controls added with option.addControls


      var controls = [],
          ctrls = self.controlbar.querySelectorAll('.jsPanel-btn');
      ctrls.forEach(function (ctrl) {
        var match = ctrl.className.match(/jsPanel-btn-[a-z0-9]{3,}/i),
            ctrlName = match[0].substring(12);
        controls.push(ctrlName);
      }); // normalize option headerControls and reset it accordingly

      var option = jsPanel.pOheaderControls(options.headerControls);
      options.headerControls = option; // set status of controls

      controls.forEach(function (item) {
        if (option[item]) {
          self.setControlStatus(item, option[item]);
        }
      }); // set size of controls

      self.setControlSize(option.size);

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.setHeaderLogo = function (logo, cb) {
      var logos = [self.headerlogo],
          minPanel = document.querySelector('#' + self.id + '-min');

      if (minPanel) {
        logos.push(minPanel.querySelector('.jsPanel-headerlogo'));
      }

      if (typeof logo === 'string') {
        if (logo.substr(0, 1) !== '<') {
          // is assumed to be an img url
          logos.forEach(function (item) {
            jsPanel.emptyNode(item);
            var img = document.createElement('img');
            img.src = logo;
            item.append(img);
          });
        } else {
          logos.forEach(function (item) {
            item.innerHTML = logo;
          });
        }
      } else {
        // assumed to be a node object
        logos.forEach(function (item) {
          jsPanel.emptyNode(item);
          item.append(logo);
        });
      } // images must not be draggable, otherwise dragit interactions locks


      self.headerlogo.childNodes.forEach(function (logo) {
        if (logo.nodeName && logo.nodeName === 'IMG') {
          logo.setAttribute('draggable', 'false');
        }
      });

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.setHeaderRemove = function (cb) {
      self.removeChild(self.header);
      self.content.classList.add('jsPanel-content-noheader');
      ['close', 'maximize', 'normalize', 'minimize', 'smallify'].forEach(function (item) {
        self.setAttribute("data-btn".concat(item), 'removed');
      });

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.setHeaderTitle = function (hdrTitle, cb) {
      var titles = [self.headertitle],
          minPanel = document.querySelector('#' + self.id + '-min');

      if (minPanel) {
        titles.push(minPanel.querySelector('.jsPanel-title'));
      }

      if (typeof hdrTitle === 'string') {
        titles.forEach(function (item) {
          item.innerHTML = hdrTitle;
        });
      } else if (typeof hdrTitle === 'function') {
        titles.forEach(function (item) {
          jsPanel.emptyNode(item);
          item.innerHTML = hdrTitle();
        });
      } else {
        // assumed to be a node object
        titles.forEach(function (item) {
          jsPanel.emptyNode(item);
          item.append(hdrTitle);
        });
      }

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.setIconfont = function (font) {
      var panel = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : self;
      var cb = arguments.length > 2 ? arguments[2] : undefined;

      if (font) {
        var classArray, textArray;

        if (font === 'fa' || font === 'far' || font === 'fal' || font === 'fas' || font === 'fad') {
          classArray = ["".concat(font, " fa-window-close"), "".concat(font, " fa-window-maximize"), "".concat(font, " fa-window-restore"), "".concat(font, " fa-window-minimize"), "".concat(font, " fa-chevron-up")];
        } else if (font === 'material-icons') {
          classArray = [font, font, font, font, font, font];
          textArray = ['close', 'fullscreen', 'fullscreen_exit', 'call_received', 'expand_less'];
        } else if (Array.isArray(font)) {
          classArray = ["custom-control-icon ".concat(font[4]), "custom-control-icon ".concat(font[3]), "custom-control-icon ".concat(font[2]), "custom-control-icon ".concat(font[1]), "custom-control-icon ".concat(font[0])];
        } else if (font === 'bootstrap' || font === 'glyphicon') {
          classArray = ['glyphicon glyphicon-remove', 'glyphicon glyphicon-fullscreen', 'glyphicon glyphicon-resize-full', 'glyphicon glyphicon-minus', 'glyphicon glyphicon-chevron-up'];
        } else {
          return panel;
        }

        panel.querySelectorAll('.jsPanel-controlbar .jsPanel-btn').forEach(function (item) {
          jsPanel.emptyNode(item).innerHTML = '<span></span>';
        });
        Array.prototype.slice.call(panel.querySelectorAll('.jsPanel-controlbar .jsPanel-btn > span')).reverse().forEach(function (item, i) {
          item.className = classArray[i];

          if (font === 'material-icons') {
            item.textContent = textArray[i];
          }
        });
      }

      if (cb) {
        cb.call(panel, panel);
      }

      return panel;
    };

    self.addToolbar = function (place, tb, cb) {
      if (place === 'header') {
        place = self.headertoolbar;
      } else if (place === 'footer') {
        place = self.footer;
      }

      if (typeof tb === 'string') {
        place.innerHTML = tb;
      } else if (Array.isArray(tb)) {
        tb.forEach(function (item) {
          if (typeof item === 'string') {
            place.innerHTML += item;
          } else {
            place.append(item);
          }
        });
      } else if (typeof tb === 'function') {
        var tool = tb.call(self, self);

        if (typeof tool === 'string') {
          place.innerHTML = tool;
        } else {
          place.append(tool);
        }
      } else {
        place.append(tb);
      }

      place.classList.add('active');

      if (cb) {
        cb.call(self, self);
      }

      return self;
    };

    self.addCloseControl = function () {
      var ctrl = document.createElement('button'),
          colorContent = self.content.style.color;
      ctrl.classList.add('jsPanel-addCloseCtrl');
      ctrl.innerHTML = jsPanel.icons.close;
      ctrl.style.color = colorContent;

      if (self.options.rtl) {
        ctrl.classList.add('rtl');
      }

      self.appendChild(ctrl);
      jsPanel.pointerup.forEach(function (evt) {
        ctrl.addEventListener(evt, function (e) {
          e.preventDefault(); // disable close for all mouse buttons but left

          if (e.button && e.button > 0) {
            return false;
          }

          self.close(null, true);
        });
      }); // pointerdown handler needed to prevent side effect with resize handles

      jsPanel.pointerdown.forEach(function (evt) {
        ctrl.addEventListener(evt, function (e) {
          e.preventDefault();
        });
      });
      return self;
    };

    self.addControl = function (obj) {
      // obj.name - string, the name of the control, results for example in "jsPanel-btn jsPanel-btn-menu"
      // obj.html - string, the html of the control to add, for example "<span class='fa fa-menu'></span>"
      // obj.handler - function(panel, control), the event handler to assign to the new control
      // obj.position - number, the position within the controlbar where the control is to be added
      if (!obj.html) {
        return self;
      }

      if (!obj.position) {
        obj.position = 1;
      }

      var count = self.controlbar.querySelectorAll('.jsPanel-btn').length;
      var control = document.createElement('button');
      control.innerHTML = obj.html;
      control.className = "jsPanel-btn jsPanel-btn-".concat(obj.name, " jsPanel-btn-").concat(options.headerControls.size);
      control.style.color = self.header.style.color;

      if (obj.position > count) {
        // new control is the first from right (default ltr text-direction) or the first from left (if option rtl is used)
        self.controlbar.append(control);
      } else {
        self.controlbar.insertBefore(control, self.querySelector(".jsPanel-controlbar .jsPanel-btn:nth-child(".concat(obj.position, ")")));
      }

      var ariaLabel = obj.ariaLabel || obj.name;

      if (ariaLabel) {
        control.setAttribute('aria-label', ariaLabel);
      }

      jsPanel.pointerup.forEach(function (evt) {
        control.addEventListener(evt, function (e) {
          e.preventDefault();

          if (e.button && e.button > 0) {
            return false;
          }

          obj.handler.call(self, self, control);
        });
      });

      if (obj.afterInsert) {
        obj.afterInsert.call(control, control);
      }

      return self;
    };

    self.setRtl = function () {
      [self.header, self.content, self.footer].forEach(function (item) {
        item.dir = 'rtl';

        if (options.rtl.lang) {
          item.lang = options.rtl.lang;
        }
      });
    }; // option.id


    self.id = options.id; // option.paneltype classname

    self.classList.add('jsPanel-' + options.paneltype); // set z-index and paneltype class

    if (options.paneltype === 'standard') {
      self.style.zIndex = this.zi.next();
    } // option.container


    panelContainer.append(self);
    self.front(false, false); // just to ensure iframe code in self.front() works for very first panel as well, second false prevents onfronted callbacks to be executed
    // option.theme

    self.setTheme(options.theme); // option.boxShadow

    if (options.boxShadow) {
      self.classList.add("jsPanel-depth-".concat(options.boxShadow));
    }
    /* option.header, option.iconfont, option.headerControls, option.headerLogo, option.headerTitle */


    if (options.header) {
      if (options.headerLogo) {
        self.setHeaderLogo(options.headerLogo);
      }

      self.setIconfont(options.iconfont);
      self.setHeaderTitle(options.headerTitle);
      self.setHeaderControls(); // now handles controls added with option addControls as well
      // compatibility code for IE11 due to flex bug - https://caniuse.com/#feat=flexbox

      if (jsPanel.isIE) {
        var bars = [self.headerbar, self.controlbar];

        switch (self.options.headerControls.size) {
          case 'md':
            bars.forEach(function (bar) {
              bar.style.height = '34px';
            });
            break;

          case 'xs':
            bars.forEach(function (bar) {
              bar.style.height = '26px';
            });
            break;

          case 'sm':
            bars.forEach(function (bar) {
              bar.style.height = '30px';
            });
            break;

          case 'lg':
            bars.forEach(function (bar) {
              bar.style.height = '38px';
            });
            break;

          case 'xl':
            bars.forEach(function (bar) {
              bar.style.height = '42px';
            });
            break;
        }
      } // end - - - - - - - - -


      if (options.header === 'auto-show-hide') {
        var boxShadow = 'jsPanel-depth-' + options.boxShadow;
        self.header.style.opacity = 0;
        self.style.backgroundColor = 'transparent';
        this.remClass(self, boxShadow);
        this.setClass(self.content, boxShadow);
        self.header.addEventListener('mouseenter', function () {
          self.header.style.opacity = 1;
          jsPanel.setClass(self, boxShadow);
          jsPanel.remClass(self.content, boxShadow);
        });
        self.header.addEventListener('mouseleave', function () {
          self.header.style.opacity = 0;
          jsPanel.remClass(self, boxShadow);
          jsPanel.setClass(self.content, boxShadow);
        });
      }
    } else {
      self.setHeaderRemove();

      if (options.addCloseControl) {
        self.addCloseControl();
      }
    } // option.headerToolbar


    if (options.headerToolbar) {
      self.addToolbar(self.headertoolbar, options.headerToolbar);
    } // option.footerToolbar


    if (options.footerToolbar) {
      self.addToolbar(self.footer, options.footerToolbar);
    } // option.border


    if (options.border) {
      self.setBorder(options.border);
    } // option.borderRadius


    if (options.borderRadius) {
      self.setBorderRadius(options.borderRadius);
    } // option.content


    if (options.content) {
      if (typeof options.content === 'function') {
        options.content.call(self, self);
      } else if (typeof options.content === 'string') {
        self.content.innerHTML = options.content;
      } else {
        self.content.append(options.content);
      }
    } // option.contentAjax


    if (options.contentAjax) {
      this.ajax(options.contentAjax, self);
    } // option.contentFetch


    if (options.contentFetch) {
      this.fetch(options.contentFetch, self);
    } // option.contentOverflow


    if (options.contentOverflow) {
      var value = options.contentOverflow.split(' ');

      if (value.length === 1) {
        self.content.style.overflow = value[0];
      } else if (value.length === 2) {
        self.content.style.overflowX = value[0];
        self.content.style.overflowY = value[1];
      }
    } // option.autoclose -- should be before option.size


    if (options.autoclose) {
      if (typeof options.autoclose === 'number') {
        options.autoclose = {
          time: options.autoclose + 'ms'
        };
      } else if (typeof options.autoclose === 'string') {
        options.autoclose = {
          time: options.autoclose
        };
      }

      var autoclose = Object.assign({}, jsPanel.defaultAutocloseConfig, options.autoclose);

      if (autoclose.time && typeof autoclose.time === 'number') {
        autoclose.time += 'ms';
      }

      var slider = self.progressbar.querySelector('div');
      slider.addEventListener('animationend', function (e) {
        e.stopPropagation();
        self.progressbar.classList.remove('active');
        self.close();
      });

      if (autoclose.progressbar) {
        self.progressbar.classList.add('active');

        if (autoclose.background) {
          if (jsPanel.themes.indexOf(autoclose.background) > -1) {
            self.progressbar.classList.add(autoclose.background + '-bg');
          } else if (jsPanel.colorNames[autoclose.background]) {
            self.progressbar.style.background = '#' + jsPanel.colorNames[autoclose.background];
          } else {
            self.progressbar.style.background = autoclose.background;
          }
        } else {
          self.progressbar.classList.add('success-bg'); // default background for progressbar
        }
      }

      slider.style.animation = "".concat(autoclose.time, " progressbar");
    } // option.rtl


    if (options.rtl) {
      self.setRtl();
    } // option.size -- should be after option.theme


    self.setSize(); // option.position

    self.status = 'normalized'; // if option.position evaluates to false panel will not be positioned at all

    if (options.position) {
      this.position(self, options.position);
    } else {
      self.style.opacity = 1;
    }

    document.dispatchEvent(jspanelnormalized);
    self.calcSizeFactors(); // option.animateIn

    if (options.animateIn) {
      // remove class again on animationend, otherwise opacity doesn't change when panel is dragged
      self.addEventListener('animationend', function () {
        _this.remClass(self, options.animateIn);
      });
      this.setClass(self, options.animateIn);
    } // option.dragit AND option.resizeit AND option.syncMargins


    if (options.syncMargins) {
      var containment = this.pOcontainment(options.maximizedMargin);

      if (options.dragit) {
        options.dragit.containment = containment;

        if (options.dragit.snap === true) {
          // options.dragit.snap must be object in order to set options.dragit.snap.containment = true;
          options.dragit.snap = jsPanel.defaultSnapConfig;
          options.dragit.snap.containment = true;
        } else if (options.dragit.snap) {
          options.dragit.snap.containment = true;
        }
      }

      if (options.resizeit) {
        options.resizeit.containment = containment;
      }
    }

    if (options.dragit) {
      // callbacks must be array of function(s) in order to be able to dynamically add/remove callbacks (for example in extensions)
      ['start', 'drag', 'stop'].forEach(function (item) {
        if (options.dragit[item]) {
          if (typeof options.dragit[item] === 'function') {
            options.dragit[item] = [options.dragit[item]];
          }
        } else {
          options.dragit[item] = [];
        }
      });
      self.drag(options.dragit); // do not use self.options.dragit.stop.push() !!!

      self.addEventListener('jspaneldragstop', function (e) {
        if (e.panel === self) {
          self.calcSizeFactors();
        }
      }, false);
    } else {
      self.titlebar.style.cursor = 'default';
    }

    if (options.resizeit) {
      // callbacks must be array of function(s) in order to be able to dynamically add/remove callbacks (for example in extensions)
      ['start', 'resize', 'stop'].forEach(function (item) {
        if (options.resizeit[item]) {
          if (typeof options.resizeit[item] === 'function') {
            options.resizeit[item] = [options.resizeit[item]];
          }
        } else {
          options.resizeit[item] = [];
        }
      });
      self.sizeit(options.resizeit);
      var startstatus = void 0; // do not use self.options.resizeit.start.push() !!!

      self.addEventListener('jspanelresizestart', function (e) {
        if (e.panel === self) {
          startstatus = self.status;
        }
      }, false); // do not use self.options.resizeit.stop.push() !!!

      self.addEventListener('jspanelresizestop', function (e) {
        if (e.panel === self) {
          if ((startstatus === 'smallified' || startstatus === 'smallifiedmax' || startstatus === 'maximized') && parseFloat(self.style.height) > parseFloat(window.getComputedStyle(self.header).height)) {
            self.setControls(['.jsPanel-btn-normalize']);
            self.status = 'normalized';
            document.dispatchEvent(jspanelnormalized);
            document.dispatchEvent(jspanelstatuschange);

            if (options.onstatuschange) {
              jsPanel.processCallbacks(self, options.onstatuschange, 'every');
            }

            self.calcSizeFactors();
          }
        }
      }, false);
    } // initialize self.currentData - must be after options position & size


    self.saveCurrentDimensions(true);
    self.saveCurrentPosition(); // option.setStatus

    if (options.setStatus) {
      if (options.setStatus === 'smallifiedmax') {
        self.maximize().smallify();
      } else if (options.setStatus === 'smallified') {
        self.smallify();
      } else {
        // remove the char 'd' from end of string to get function name to call
        self[options.setStatus.substr(0, options.setStatus.length - 1)]();
      }
    } // front panel on mousedown


    this.pointerdown.forEach(function (item) {
      self.addEventListener(item, function (e) {
        if (!e.target.closest('.jsPanel-btn-close') && !e.target.closest('.jsPanel-btn-minimize') && options.paneltype === 'standard') {
          self.front();
        }
      }, false);
    }); // option onwindowresize

    if (options.onwindowresize) {
      // if container is 'window'
      if (self.options.container === 'window') {
        window.addEventListener('resize', self.windowResizeHandler, false);
      }
    } // option onparentresize


    if (options.onparentresize) {
      var onResize = options.onparentresize,
          parentPanel = self.isChildpanel();

      if (parentPanel) {
        var parentContainer = parentPanel.content;
        var parentContainerSize = [];

        self.parentResizeHandler = function (e) {
          // if resized panel is the parent panel of the one whose option onContentResize is set to true
          if (e.panel === parentPanel) {
            // get dimensions of parent panel's content section
            parentContainerSize[0] = parentContainer.offsetWidth;
            parentContainerSize[1] = parentContainer.offsetHeight;
            var status = self.status,
                left,
                top;

            if (status === 'maximized' && onResize) {
              self.maximize();
            } else if (self.snapped && status !== 'minimized') {
              self.snap(self.snapped, true);
            } else if (status === 'normalized' || status === 'smallified' || status === 'maximized') {
              if (typeof onResize === 'function') {
                onResize.call(self, self, {
                  width: parentContainerSize[0],
                  height: parentContainerSize[1]
                });
              } else {
                left = (parentContainerSize[0] - self.offsetWidth) * self.hf;
                self.style.left = left <= 0 ? 0 : left + 'px';
                top = (parentContainerSize[1] - self.offsetHeight) * self.vf;
                self.style.top = top <= 0 ? 0 : top + 'px';
              }
            } else if (status === 'smallifiedmax' && onResize) {
              self.maximize().smallify();
            }
          }
        };

        document.addEventListener('jspanelresize', self.parentResizeHandler, false);
      }
    } // global callbacks


    if (this.globalCallbacks) {
      if (Array.isArray(this.globalCallbacks)) {
        this.globalCallbacks.forEach(function (item) {
          item.call(self, self);
        });
      } else {
        this.globalCallbacks.call(self, self);
      }
    } // option.callback


    if (options.callback) {
      if (Array.isArray(options.callback)) {
        options.callback.forEach(function (item) {
          item.call(self, self);
        });
      } else {
        options.callback.call(self, self);
      }
    } // constructor callback


    if (cb) {
      cb.call(self, self);
    }

    document.dispatchEvent(jspanelloaded);
    return self;
  }
};

// Add CommonJS module exports, so it can be imported using require() in Node.js
// https://nodejs.org/docs/latest/api/modules.html
if (typeof module !== 'undefined') { module.exports = jsPanel; }
