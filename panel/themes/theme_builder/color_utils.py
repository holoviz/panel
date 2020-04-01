from typing import Dict
import math
import colorsys
# https://stackoverflow.com/questions/3380726/converting-a-rgb-color-tuple-to-a-six-digit-code-in-python
def rgb_to_hex(rgb):
    r = int(round(rgb[0]))
    g = int(round(rgb[1]))
    b = int(round(rgb[2]))
    return "#{:02x}{:02x}{:02x}".format(r,g,b)
def hex_to_rgb(color):
    color = color.replace("#", "")
    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
# https://gist.github.com/mathebox/e0805f72e7db3269ec22
def rgb_to_hsl(rgb):
    rgb = tuple(float(item)/255 for item in rgb)
    h,l,s = colorsys.rgb_to_hls(*rgb)
    return (h,s,l)

def hsl_to_rgb(hsl):
    h,s,l = hsl
    r,g,b = colorsys.hls_to_rgb(h,l,s)
    r = int(round(r*255))
    g = int(round(g*255))
    b = int(round(b*255))
    return (r,g,b)
def hex_to_hsl(color):
    rgb = hex_to_rgb(color)
    return rgb_to_hsl(rgb)
def hsl_to_hex(hsl):
    rgb = hsl_to_rgb(hsl)
    return rgb_to_hex(rgb)
# https://github.com/bgrins/TinyColor/blob/master/tinycolor.js
def get_brightness(color):
        rgb = hex_to_rgb(color)
        return (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
def is_dark(color):
    return get_brightness(color)<128

def is_light(color):
    return not is_dark(color)

# https://github.com/bgrins/TinyColor/blob/master/tinycolor.js
def mix(color1: str, color2: str, amount: float) -> str:
    if amount < 0:
        amount = 0
    elif amount > 100:
        amount = 100

    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    ratio = amount / 100

    rgb = (
        (rgb2[0]-rgb1[0])*ratio+rgb1[0],
        (rgb2[1]-rgb1[1])*ratio+rgb1[1],
        (rgb2[2]-rgb1[2])*ratio+rgb1[2],
    )
    return rgb_to_hex(rgb)
# https://github.com/mbitson/mcg/blob/master/scripts/controllers/ColorGeneratorCtrl.js
def multiply(color1, color2):
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    rgb = (
        math.floor(rgb1[0] * rgb2[0] / 255),
        math.floor(rgb1[1] * rgb2[1] / 255),
        math.floor(rgb1[2] * rgb2[2] / 255),
    )
    return rgb_to_hex(rgb)
def clamp01(val):
    if val < 0:
        return 0
    if val > 1:
        return 1
    return val
def saturate(color, amount):
    if not amount:
        amount = 0
    elif amount < 0:
        amount = 0
    elif amount > 100:
        amount = 100

    hsl = hex_to_hsl(color)
    h,s,l = hsl
    s += amount / 100
    s = clamp01(s)
    colorsat = hsl_to_hex((h,s,l))
    return colorsat
def lighten(color, amount):
    if not amount:
        amount = 0
    elif amount < 0:
        amount = 0
    elif amount > 100:
        amount = 100

    hsl = hex_to_hsl(color)
    h,s,l = hsl
    l += amount / 100
    l = clamp01(l)
    colorlight = hsl_to_hex((h,s,l))
    return colorlight
def tetrad(color):
    hsl = hex_to_hsl(color)
    h,s,l = hsl
    hsl1 = (((h+90) % 360)/360,s,l)
    hsl2 = (((h+180) % 360)/360,s,l)
    hsl3 = (((h+270) % 360)/360,s,l)

    return [
        color, hsl_to_hex(hsl1),hsl_to_hex(hsl2),hsl_to_hex(hsl3),
    ]
# https://github.com/mbitson/mcg/blob/master/scripts/controllers/ColorGeneratorCtrl.js
def compute_colors(color: str)-> Dict:
    baselight = "#ffffff"
    basedark = multiply(color,color)
    basetriad = tetrad(color)
    return {
        '50' : mix(baselight, color, 12),
        '100' : mix(baselight, color, 30),
        '200' : mix(baselight, color, 50),
        '300' : mix(baselight, color, 70),
        '400' : mix(baselight, color, 85),
        '500' : mix(baselight, color, 100),
        '600' : mix(basedark, color, 87),
        '700' : mix(basedark, color, 70),
        '800' : mix(basedark, color, 54),
        '900' : mix(basedark, color, 25),
        'A100' : lighten(saturate(mix(basedark, basetriad[3], 15), 80), 65),
        'A200' : lighten(saturate(mix(basedark, basetriad[3], 15), 80), 55),
        'A400' : lighten(saturate(mix(basedark, basetriad[3], 15), 100), 45),
        'A700' : lighten(saturate(mix(basedark, basetriad[3], 15), 100), 40),
    }