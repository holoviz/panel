import {
  accentPalette,
  baseLayerLuminance,
  fillColor,
  neutralPalette,
  PaletteRGB,
  SwatchRGB,
  provideFASTDesignSystem,
} from '../../@microsoft/fast-components@2.30.6/dist/fast-components.js'

const hexRGBRegex = /^#((?:[0-9a-f]{6}|[0-9a-f]{3}))$/i

function standardize_color(str) {
  var ctx = document.createElement('canvas').getContext('2d')
  ctx.fillStyle = str
  return ctx.fillStyle
}

export function normalize(i, min, max) {
  if (isNaN(i) || i <= min) {
    return 0.0
  } else if (i >= max) {
    return 1.0
  }
  return i / (max - min)
}

function parseColorHexRGB(raw) {
  const hex_color = standardize_color(raw)
  const result = hexRGBRegex.exec(hex_color)

  if (result === null) {
    return null
  }

  let digits = result[1]

  if (digits.length === 3) {
    const r = digits.charAt(0)
    const g = digits.charAt(1)
    const b = digits.charAt(2)

    digits = r.concat(r, g, g, b, b)
  }

  const rawInt = parseInt(digits, 16)

  if (isNaN(rawInt)) {
    return null
  }

  // Note the use of >>> rather than >> as we want JS to manipulate these as unsigned numbers
  return SwatchRGB.create(
    normalize((rawInt & 0xff0000) >>> 16, 0, 255),
    normalize((rawInt & 0x00ff00) >>> 8, 0, 255),
    normalize(rawInt & 0x0000ff, 0, 255),
    1
  )
}

class FastDesignProvider {
  constructor(selector) {
    if (typeof selector === 'string') {
      this.provider = document.querySelector(selector)
    } else {
      this.provider = selector
    }
    provideFASTDesignSystem(this.provider)
  }

  setAccentColor(value) {
    accentPalette.setValueFor(
      this.provider,
      PaletteRGB.create(parseColorHexRGB(value))
    )
  }

  setNeutralColor(value) {
    neutralPalette.setValueFor(
      this.provider,
      PaletteRGB.create(parseColorHexRGB(value))
    )
  }

  setBackgroundColor(value) {
    fillColor.setValueFor(this.provider, parseColorHexRGB(value))
    this.provider.style.setProperty(
      'background-color',
      `var(${fillColor.cssCustomProperty})`
    )
  }

  setLuminance(value) {
    baseLayerLuminance.setValueFor(
      this.provider,
      value
    )
  }

  setCornerRadius(value) {
    this.provider.style.setProperty('--corner-radius', value)
  }
}

window.fastDesignProvider = FastDesignProvider
