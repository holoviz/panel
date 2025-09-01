from __future__ import annotations

import pathlib

from collections.abc import Callable

import param

from bokeh.themes import Theme as _BkTheme

from ..config import config
from ..io.resources import CDN_DIST
from ..layout import Accordion
from ..reactive import ReactiveHTML
from ..viewable import Child, Viewable
from ..widgets import Tabulator
from ..widgets.indicators import Dial, Number, String
from .base import (
    DarkTheme, DefaultTheme, Design, Inherit,
)

COLLAPSED_SVG_ICON = """
<svg style="stroke: var(--accent-fill-rest);" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg" slot="collapsed-icon">
  <path d="M15.2222 1H2.77778C1.79594 1 1 1.79594 1 2.77778V15.2222C1 16.2041 1.79594 17 2.77778 17H15.2222C16.2041 17 17 16.2041 17 15.2222V2.77778C17 1.79594 16.2041 1 15.2222 1Z" stroke-linecap="round" stroke-linejoin="round"></path>
  <path d="M9 5.44446V12.5556" stroke-linecap="round" stroke-linejoin="round"></path>
  <path d="M5.44446 9H12.5556" stroke-linecap="round" stroke-linejoin="round"></path>
</svg>
""" # noqa

EXPANDED_SVG_ICON = """
<svg style="stroke: var(--accent-fill-rest);" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg" slot="expanded-icon">
  <path d="M15.2222 1H2.77778C1.79594 1 1 1.79594 1 2.77778V15.2222C1 16.2041 1.79594 17 2.77778 17H15.2222C16.2041 17 17 16.2041 17 15.2222V2.77778C17 1.79594 16.2041 1 15.2222 1Z" stroke-linecap="round" stroke-linejoin="round"></path>
  <path d="M5.44446 9H12.5556" stroke-linecap="round" stroke-linejoin="round"></path>
</svg>
""" # noqa

FONT_URL = "//fonts.googleapis.com/css?family=Open+Sans"


class FastStyle(param.Parameterized):
    """
    The FastStyle class provides the different colors and icons used
    to style the Fast Templates.
    """

    background_color = param.String(default="#ffffff")
    neutral_color = param.String(default="#000000")
    accent_base_color = param.String(default="#0072B5")
    collapsed_icon = param.String(default=COLLAPSED_SVG_ICON)
    expanded_icon = param.String(default=EXPANDED_SVG_ICON)
    color = param.String(default="#2B2B2B")
    neutral_fill_card_rest = param.String(default="#F7F7F7")
    neutral_focus = param.String(default="#888888")
    neutral_foreground_rest = param.String(default="#2B2B2B")

    header_luminance = param.Magnitude(default=0.23)
    header_background = param.String(default="#0072B5")
    header_neutral_color = param.String(default="#0072B5")
    header_accent_base_color = param.String(default="#ffffff")
    header_color = param.String(default="#ffffff")
    font = param.String(default="Open Sans, sans-serif")
    font_url = param.String(default=FONT_URL)
    corner_radius = param.Integer(default=3)
    shadow = param.Boolean(default=True)
    luminance = param.Magnitude(default=1.0)

    def create_bokeh_theme(self):
        """Returns a custom bokeh theme based on the style parameters

        Returns:
            Dict: A Bokeh Theme
        """

        return {
            "attrs": {
                "figure": {
                    "background_fill_color": self.background_color,
                    "border_fill_color": self.neutral_fill_card_rest,
                    "border_fill_alpha": 0,
                    "outline_line_color": self.neutral_focus,
                    "outline_line_alpha": 0.5,
                    "outline_line_width": 1,
                },
                "Grid": {"grid_line_color": self.neutral_focus, "grid_line_alpha": 0.25},
                "Axis": {
                    "major_tick_line_alpha": 0.5,
                    "major_tick_line_color": self.neutral_foreground_rest,
                    "minor_tick_line_alpha": 0.25,
                    "minor_tick_line_color": self.neutral_foreground_rest,
                    "axis_line_alpha": 0.1,
                    "axis_line_color": self.neutral_foreground_rest,
                    "major_label_text_color": self.neutral_foreground_rest,
                    "major_label_text_font": self.font,
                    "major_label_text_font_size": "1.025em",
                    "axis_label_standoff": 10,
                    "axis_label_text_color": self.neutral_foreground_rest,
                    "axis_label_text_font": self.font,
                    "axis_label_text_font_size": "1.25em",
                    "axis_label_text_font_style": "normal",
                },
                "Legend": {
                    "spacing": 8,
                    "glyph_width": 15,
                    "label_standoff": 8,
                    "label_text_color": self.neutral_foreground_rest,
                    "label_text_font": self.font,
                    "label_text_font_size": "1.025em",
                    "border_line_alpha": 0.5,
                    "border_line_color": self.neutral_focus,
                    "background_fill_alpha": 0.25,
                    "background_fill_color": self.neutral_fill_card_rest,
                },
                "ColorBar": {
                    "background_fill_color": self.background_color,
                    "title_text_color": self.neutral_foreground_rest,
                    "title_text_font": self.font,
                    "title_text_font_size": "1.025em",
                    "title_text_font_style": "normal",
                    "major_label_text_color": self.neutral_foreground_rest,
                    "major_label_text_font": self.font,
                    "major_label_text_font_size": "1.025em",
                    "major_tick_line_alpha": 0,
                    "bar_line_alpha": 0,
                },
                "Title": {
                    "text_color": self.neutral_foreground_rest,
                    "text_font": self.font,
                    "text_font_size": "1.15em",
                },
            }
        }


class FastWrapper(ReactiveHTML):
    """
    Wraps any Panel component and initializes the Fast design provider.

    Wrapping a component in this way ensures that so that any children
    using the Fast design system have access to the Fast CSS variables.
    """

    object = Child(doc="""
        The Panel component to wrap with the Fast design provider.""")

    style = param.ClassSelector(class_=FastStyle, doc="""
        The style to apply to the Fast design provider""")

    _template = '<div id="fast-wrapper" class="fast-wrapper">${object}</div>'

    _scripts = {
        'render': """
        let accent, bg, luminance
        if (!window.fastDesignProvider) {
          return
        } else if (window._JUPYTERLAB) {
          accent = getComputedStyle(document.body).getPropertyValue('--jp-brand-color0').trim();
          bg = getComputedStyle(document.body).getPropertyValue('--jp-layout-color0').trim();
          let color = getComputedStyle(document.body).getPropertyValue('--jp-ui-font-color0').trim();
          luminance = color == 'rgba(255, 255, 255, 1)' ? 0.23 : 1.0;
        } else {
          accent = data.style.accent_base_color;
          bg = data.style.background_color;
          luminance = data.style.luminance;
        }
        bg = bg === 'white' ? '#ffffff' : bg;
        bg = bg === 'black' ? '#000000' : bg;
        state.design = design = new window.fastDesignProvider(view.el)
        design.setLuminance(luminance);
        design.setNeutralColor(data.style.neutral_color);
        design.setAccentColor(accent);
        design.setBackgroundColor(bg);
        design.setCornerRadius(data.style.corner_radius);
        """
    }

    def select(
        self, selector: type | Callable[[Viewable], bool] | None = None
    ) -> list[Viewable]:
        return [] if self.object is None else self.object.select(selector)

DEFAULT_STYLE = FastStyle()

DARK_STYLE = FastStyle(
    background_color="#181818", #242424
    color="#ffffff",
    header_color="#ffffff",
    luminance=0.1,
    neutral_fill_card_rest="#212121",
    neutral_focus="#717171",
    neutral_foreground_rest="#e5e5e5",
    shadow = False,
)

class FastThemeMixin(param.Parameterized):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'css' / 'fast_variables.css')


class FastDefaultTheme(DefaultTheme):

    style = param.ClassSelector(default=DEFAULT_STYLE, class_=FastStyle)

    __abstract = True

    @property
    def bokeh_theme(self):
        return _BkTheme(json=self.style.create_bokeh_theme())


class FastDarkTheme(DarkTheme):

    style = param.ClassSelector(default=DARK_STYLE, class_=FastStyle)

    modifiers = {
        Dial: {
            'label_color': 'white'
        },
        Number: {
            'default_color': 'var(--neutral-foreground-rest)'
        },
        String: {
            'default_color': 'var(--neutral-foreground-rest)'
        }
    }

    __abstract = True

    @property
    def bokeh_theme(self):
        return _BkTheme(json=self.style.create_bokeh_theme())


class Fast(Design):

    modifiers = {
        Accordion: {
            'active_header_background': 'var(--neutral-fill-active)'
        },
        Tabulator: {
            'theme': 'fast'
        },
        Viewable: {
            'stylesheets': [Inherit, f'{CDN_DIST}bundled/theme/fast.css']
        }
    }

    _resources = {
        'font': {
            'opensans': f'https:{FONT_URL}',
        },
        'js_modules': {
            'fast': f'{config.npm_cdn}/@microsoft/fast-components@2.30.6/dist/fast-components.js',
            'fast-design': 'js/fast_design.js'
        },
        'bundle': True,
        'tarball': {
            'fast': {
                'tar': 'https://registry.npmjs.org/@microsoft/fast-components/-/fast-components-2.30.6.tgz',
                'src': 'package/',
                'dest': '@microsoft/fast-components@2.30.6',
                'exclude': ['*.d.ts', '*.json', '*.md', '*/esm/*']
            }
        }
    }

    _themes = {
        'default': FastDefaultTheme,
        'dark': FastDarkTheme
    }

    def _wrapper(self, model):
        return FastWrapper(design=None, object=model, style=self.theme.style)
