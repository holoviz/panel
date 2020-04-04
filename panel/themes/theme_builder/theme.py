"""Definition of Light and Dark Foreground and Background themes

According to Material Design Palette.

Source: https://github.com/angular/components/blob/master/src/material/core/theming/_palette.scss
"""
import param

from . import color
from .color_palette import GREY


class ThemeForeground(param.Parameterized):
    """Material Design Theme Foreground settings"""
    base = param.String(color.BLACK)
    divider = param.String(color.DARK_DIVIDERS)
    dividers = param.String(color.DARK_DIVIDERS)
    disabled = param.String(color.DARK_DISABLED_TEXT)
    disabled_button = param.String("rgba(0,0,0, 0.26)")
    disabled_text = param.String(color.DARK_DISABLED_TEXT)
    elevation = param.String(color.BLACK)
    hint_text = param.String(color.DARK_DISABLED_TEXT)
    primary_text = param.String(color.DARK_PRIMARY_TEXT)
    secondary_text = param.String(color.DARK_SECONDARY_TEXT)
    icon = param.String("rgba(0,0,0 , 0.54)")
    icons = param.String("rgba(0,0,0 , 0.54)")
    text = param.String("rgba(0,0,0 , 0.87)")
    slider_min = param.String("rgba(0,0,0 , 0.87)")
    slider_off = param.String("rgba(0,0,0 , 0.26)")
    slider_off_active = param.String("rgba(0,0,0 , 0.38)")


class ThemeBackground(param.Parameterized):
    """Material Design Theme Background settings"""
    status_bar = param.String(GREY.color_300)
    app_bar = param.String(GREY.color_100)
    background = param.String(GREY.color_50)
    hover = param.String("rgba(0,0,0, 0.04)")
    card = param.String(color.WHITE)
    dialog = param.String(color.WHITE)
    disabled_button = param.String("rgba(0,0,0, 0.12)")
    raised_button = param.String(color.WHITE)
    focused_button = param.String(color.DARK_FOCUSED)
    selected_button = param.String(GREY.color_300)
    selected_disabled_button = param.String(GREY.color_400)
    disabled_button_toggle = param.String(GREY.color_200)
    unselected_chip = param.String(GREY.color_300)
    disabled_list_option = param.String(GREY.color_200)
    tooltip = param.String(GREY.color_700)


LIGHT_THEME_FOREGROUND = ThemeForeground(name="Light Theme Foreground")
LIGHT_THEME_BACKGROUND = ThemeBackground(name="Light Theme Background")

DARK_THEME_FOREGROUND = ThemeForeground(
    name = "Dark Theme Foreground",
    base=color.WHITE,
    divider=color.LIGHT_DIVIDERS,
    dividers=color.LIGHT_DIVIDERS,
    disabled=color.LIGHT_DISABLED_TEXT,
    disabled_button="rgba(255,255,255, 0.3)",
    disabled_text=color.LIGHT_DISABLED_TEXT,
    elevation=color.BLACK,
    hint_text=color.LIGHT_DISABLED_TEXT,
    primary_text = color.LIGHT_PRIMARY_TEXT,
    secondary_text=color.LIGHT_SECONDARY_TEXT,
    icon=color.WHITE,
    icons=color.WHITE,
    text=color.WHITE,
    slider_min=color.WHITE,
    slider_off="rgba(255,255,255, 0.3",
    slider_off_active="rgba(255, 255, 255, 0.3",
)

DARK_THEME_BACKGRUND = ThemeBackground(
    name = "Dark Theme Background",
    status_bar=color.BLACK,
    app_bar=GREY.color_900,
    background="#303030",
    hover="rgba(255,255,255, 0.04)",
    card=GREY.color_800,
    dialog=GREY.color_800,
    disabled_button="rgba(255,255,255, 0.12)",
    raised_button=GREY.color_800,
    focused_button=color.LIGHT_FOCUSED,
    selected_button=GREY.color_900,
    selected_disabled_button=GREY.color_800,
    disabled_button_toggle=color.BLACK,
    unselected_chip=GREY.color_700,
    disabled_list_option=color.BLACK,
    tooltip=GREY.color_700,
)
FOREGROUNDS = [LIGHT_THEME_FOREGROUND, DARK_THEME_FOREGROUND]
BACKGROUNDS = [LIGHT_THEME_BACKGROUND, DARK_THEME_BACKGRUND]

class Theme(param.Parameterized):
    foreground = param.ObjectSelector(LIGHT_THEME_FOREGROUND, objects=FOREGROUNDS)
    background = param.ObjectSelector(LIGHT_THEME_BACKGROUND, objects=BACKGROUNDS)

LIGHT_THEME = Theme(name="White Theme")
DARK_THEME = Theme(
    name = "Dark Theme",
    foreground = DARK_THEME_FOREGROUND,
    background = DARK_THEME_BACKGRUND,
)

THEMES = [LIGHT_THEME, DARK_THEME]