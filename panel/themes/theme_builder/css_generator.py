"""In this module we define CssGenerators"""
import param

import panel as pn

from .color_scheme import COLOR_SCHEME_EDITABLE_COLORS, ColorScheme


class CssGenerator(param.Parameterized):
    color_scheme = param.ClassSelector(class_=ColorScheme, readonly=True)
    panel_css = param.String()
    dataframe_css = param.String()

    def __init__(self, **params):
        self.param.color_scheme.default = ColorScheme()

        super().__init__(**params)

        self._set_panel_css()
        self._set_dataframe_css()

    def _get_panel_css(self):
        return ""

    def _get_dataframe_css(self):
        return ""

    @param.depends("color_scheme", *COLOR_SCHEME_EDITABLE_COLORS, watch=True)
    def _set_panel_css(self):
        self.panel_css = self._get_panel_css()

    @param.depends("color_scheme", *COLOR_SCHEME_EDITABLE_COLORS, watch=True)
    def _set_dataframe_css(self):
        self.dataframe_css = self._get_dataframe_css()

    @param.depends("color_scheme")
    def _color_scheme_view(self):
        return self.color_scheme.view()

    def _css_view(self):
        return pn.Column(
            "## CSS",
            pn.Tabs(
                pn.Param(
                    self.param.panel_css,
                    name="Panel",
                    widgets={"panel_css": {"type": pn.widgets.TextAreaInput, "height": 600}},
                ),
                pn.Param(
                    self.param.dataframe_css,
                    name="Dataframe",
                    widgets={"dataframe_css": {"type": pn.widgets.TextAreaInput, "height": 600}},
                ),
            ),
        )

    @param.depends("color_scheme")
    def view(self):
        return pn.Column(self._color_scheme_view, pn.layout.HSpacer(width=10), self._css_view,)

# Inspiration:
# https://github.com/angular/components/blob/master/src/material/button/_button-theme.scss
# https://material-ui.com/components/buttons/
# https://material.io/resources/color/#!/?view.left=0&view.right=0&primary.color=9C27B0&secondary.color=F44336

class DarkCssGenerator(CssGenerator):
    def _get_panel_css(self):
        panel_css = f"""\
body {{
    background-color: {self.color_scheme.dark};
    color: {self.color_scheme.light};
}}

h1, h2, h3, h4, h5 {{
color: {self.color_scheme.primary} !important;
}}

"""
        panel_css += self._get_panel_button_outlined_css(button_type="default", color=self.color_scheme.text_primary, border_color=self.color_scheme.disabled_text)
        panel_css += self._get_panel_button_contained_css(button_type="primary", background_color=self.color_scheme.primary)
        panel_css += self._get_panel_button_contained_css(button_type="success", background_color=self.color_scheme.secondary)
        # panel_css += self._get_panel_button_css(button_type="info", background_color=self.color_scheme.secondary)
        panel_css += self._get_panel_button_contained_css(button_type="warning", background_color=self.color_scheme.warning)
        panel_css += self._get_panel_button_contained_css(button_type="danger", background_color=self.color_scheme.warning)

        return panel_css

    def _get_panel_button_outlined_css(self, button_type="default", color="gray", border_color="gray"):
        return f"""\
.bk-root .bk-btn-{button_type} {{
    color: {color};
    background-color: transparent;
    border: 0px;
    border-radius: 4px;
    border-width: 1px;
    border-style: solid;
    border-color: {border_color};
  }}
.bk-root .bk-btn-{button_type}:hover {{
  color: {color};
  background-color: transparent;
  border-color: {border_color};
}}
.bk-root .bk-btn-{button_type}.bk-active {{
  color: {color};
  background-color: transparent;
  border-color: {border_color};
}}
.bk-root .bk-btn-{button_type}[disabled],
.bk-root .bk-btn-{button_type}[disabled]:hover,
.bk-root .bk-btn-{button_type}[disabled]:focus,
.bk-root .bk-btn-{button_type}[disabled]:active,
.bk-root .bk-btn-{button_type}[disabled].bk-active {{
  background-color: transparent;
  border-color: {border_color};
}}"""



    def _get_panel_button_contained_css(self, button_type="default", background_color="black"):
        return f"""\
.bk-root .bk-btn-{button_type} {{
    color: inherit;
    background-color: {background_color};
    border: 0px;
    border-radius: 4px;
  }}
.bk-root .bk-btn-{button_type}:hover {{
  /* color: #1a2028; */
  background-color: {background_color};
  /* border-color: #1a2028; */
}}
.bk-root .bk-btn-{button_type}.bk-active {{
  background-color: {background_color};
  border-color: #adadad;
}}
.bk-root .bk-btn-{button_type}[disabled],
.bk-root .bk-btn-{button_type}[disabled]:hover,
.bk-root .bk-btn-{button_type}[disabled]:focus,
.bk-root .bk-btn-{button_type}[disabled]:active,
.bk-root .bk-btn-{button_type}[disabled].bk-active {{
  background-color: transparent;
  border-color: #ccc;
}}"""

# border-bottom: 1px solid {self.color_scheme.primary};
    def _get_dataframe_css(self, background="#424242", border_color="rgba(255,255,255, 0.5)", color="#ffffff"):
        return f"""\
table.panel-df {{
    color: {color};
    border-radius: 4px;
}}
.panel-df tbody tr:nth-child(odd) {{
    background: {background};
}}
.panel-df tbody tr {{
    background: {background};
    border-top-style: solid;
    border-top-width: 1px;
    border-top-color: {border_color};
   }}
.panel-df thead {{
    background: {background};
    color: {color};
    font-weight: 500px;
}}
.panel-df tr:hover:nth-child(odd) {{
    background: {background} !important;
}}
.panel-df tr:hover {{
    background: {background} !important;
}}
.panel-df thead tr:hover:nth-child(1) {{
    background-color: inherit !important;
}}

.panel-df thead:hover {{
    background: {background} !important;
}}"""


DEFAULT_CSS_GENERATOR = CssGenerator(name="Default")
DARK_CSS_GENERATOR = DarkCssGenerator(name="Dark")

CSS_GENERATORS = [DEFAULT_CSS_GENERATOR, DARK_CSS_GENERATOR]
