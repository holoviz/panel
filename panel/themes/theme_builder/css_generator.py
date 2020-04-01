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


class DarkCssGenerator(CssGenerator):
    def _get_panel_css(self):
        return f"""\
body {{
    background-color: {self.color_scheme.dark};
    color: {self.color_scheme.light};
}}

h1, h2, h3, h4, h5 {{
color: {self.color_scheme.primary} !important;
}}"""

    def _get_dataframe_css(self):
        return f"""\
table.panel-df {{
    color: rgb(236,236,236);
}}
.panel-df tbody tr:nth-child(odd) {{
    background: #3f495a;
}}
.panel-df tbody tr {{
    background: #394251;
   }}
.panel-df thead {{
    background: {self.color_scheme.dark};
    color: {self.color_scheme.light};
    border-bottom: 1px solid {self.color_scheme.primary};
}}
.panel-df tr:hover:nth-child(odd) {{
    background: #3d4757 !important;
}}
.panel-df tr:hover {{
    background: #373f4e !important;
}}
.panel-df thead tr:hover:nth-child(1) {{
    background-color: inherit !important;
}}

.panel-df thead:hover {{
    background: #27313d !important;
}}"""


DEFAULT_CSS_GENERATOR = CssGenerator(name="Default")
DARK_CSS_GENERATOR = DarkCssGenerator(name="Dark")

CSS_GENERATORS = [DEFAULT_CSS_GENERATOR, DARK_CSS_GENERATOR]
