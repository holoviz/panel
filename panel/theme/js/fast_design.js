import {
  parseColorHexRGB
} from "../../js/@microsoft/fast-colors@5.3.1/dist/index.js";

import {
  createColorPalette,
  accentFillActiveBehavior,
  accentFillHoverBehavior,
  accentFillRestBehavior,
  accentForegroundActiveBehavior,
  accentForegroundCutRestBehavior,
  accentForegroundFocusBehavior,
  accentForegroundHoverBehavior,
  accentForegroundRestBehavior,
  neutralDividerRestBehavior,
  neutralFillHoverBehavior,
  neutralFillInputActiveBehavior,
  neutralFillInputHoverBehavior,
  neutralFillInputRestBehavior,
  neutralFillRestBehavior,
  neutralFillStealthActiveBehavior,
  neutralFillStealthHoverBehavior,
  neutralFillStealthRestBehavior,
  neutralFocusBehavior,
  neutralFocusInnerAccentBehavior,
  neutralForegroundActiveBehavior,
  neutralForegroundHoverBehavior,
  neutralLayerFloatingBehavior,
  neutralOutlineActiveBehavior,
  neutralOutlineHoverBehavior,
  neutralOutlineRestBehavior
} from "../../js/@microsoft/fast-components@1.21.8/dist/fast-components.js";

function standardize_color(str) {
  var ctx = document.createElement('canvas').getContext('2d');
  ctx.fillStyle = str;
  return ctx.fillStyle;
}

function setAccentColor(color, selector) {
  color = standardize_color(color);
  const accent = color;
  const palette = createColorPalette(parseColorHexRGB(accent));
  const provider = document.querySelector(selector);
  provider.accentBaseColor = accent;
  provider.accentPalette = palette;
  }

function setNeutralColor(color, selector) {
  color = standardize_color(color);
  const palette = createColorPalette(parseColorHexRGB(color));
  const provider = document.querySelector(selector);
  provider.neutralPalette = palette;
}
  
function setBackgroundColor(color, selector) {
  color = standardize_color(color);
  const provider = document.querySelector(selector);
  provider.backgroundColor = color;
}

function registerCSSCustomProperties(selector) {
  const provider = document.querySelector(selector);
  provider.registerCSSCustomProperty(accentFillActiveBehavior)
  provider.registerCSSCustomProperty(neutralFillRestBehavior)
  provider.registerCSSCustomProperty(accentFillHoverBehavior)
  provider.registerCSSCustomProperty(accentFillRestBehavior)
  provider.registerCSSCustomProperty(accentForegroundActiveBehavior)
  provider.registerCSSCustomProperty(accentForegroundCutRestBehavior)
  provider.registerCSSCustomProperty(accentForegroundFocusBehavior)
  provider.registerCSSCustomProperty(accentForegroundHoverBehavior)
  provider.registerCSSCustomProperty(accentForegroundRestBehavior)
  provider.registerCSSCustomProperty(neutralDividerRestBehavior)
  provider.registerCSSCustomProperty(neutralFillHoverBehavior)
  provider.registerCSSCustomProperty(neutralFillInputActiveBehavior)
  provider.registerCSSCustomProperty(neutralFillInputHoverBehavior)
  provider.registerCSSCustomProperty(neutralFillInputRestBehavior)
  provider.registerCSSCustomProperty(neutralFillRestBehavior)
  provider.registerCSSCustomProperty(neutralFillStealthActiveBehavior)
  provider.registerCSSCustomProperty(neutralFillStealthHoverBehavior)
  provider.registerCSSCustomProperty(neutralFillStealthRestBehavior)
  provider.registerCSSCustomProperty(neutralFocusBehavior)
  provider.registerCSSCustomProperty(neutralFocusInnerAccentBehavior)
  provider.registerCSSCustomProperty(neutralForegroundActiveBehavior)
  provider.registerCSSCustomProperty(neutralForegroundHoverBehavior)
  provider.registerCSSCustomProperty(neutralLayerFloatingBehavior)
  provider.registerCSSCustomProperty(neutralOutlineActiveBehavior)
  provider.registerCSSCustomProperty(neutralOutlineHoverBehavior)
  provider.registerCSSCustomProperty(neutralOutlineRestBehavior)
}

class FastDesignProvider {
  register(element) {
    registerCSSCustomProperties(element)
  }
  setAccentColor(value, element){
    setAccentColor(value, element);
  }
  setNeutralColor(value, element){
    setNeutralColor(value, element);
  }
  setBackgroundColor(value, element){
    setBackgroundColor(value, element)
  }
}

window.fastDesignProvider = new FastDesignProvider()
