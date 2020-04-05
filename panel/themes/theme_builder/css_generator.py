"""In this module we define CssGenerators"""
import param

import panel as pn

from .color_scheme import COLOR_SCHEME_EDITABLE_COLORS, ColorScheme
from .color_palette import GREY

# Inspiration:
# https://github.com/angular/components/blob/master/src/material/button/_button-theme.scss
# https://material-ui.com/components/buttons/
# https://material.io/resources/color/#!/?view.left=0&view.right=0&primary.color=9C27B0&secondary.color=F44336
# See https://github.com/angular/components/blob/master/src/material/
class CssGenerator(param.Parameterized):
    color_scheme = param.ClassSelector(class_=ColorScheme)
    panel_css = param.String()
    markdown_css = param.String()
    dataframe_css = param.String()

    def __init__(self, **params):
        self.param.color_scheme.default = ColorScheme()

        super().__init__(**params)

        self._update_css()

    @param.depends("color_scheme", *COLOR_SCHEME_EDITABLE_COLORS, watch=True)
    def _update_css(self):
        self.panel_css = self._get_panel_css()
        self.markdown_css = self._get_markdown_css()
        self.dataframe_css = self._get_dataframe_css()

    def css_view(self):
        return pn.Column(
            "#### CSS",
            pn.Tabs(
                pn.Param(
                    self.param.panel_css,
                    name="Panel",
                    widgets={"panel_css": {"type": pn.widgets.TextAreaInput, "height": 600}},
                ),
                pn.Param(
                    self.param.markdown_css,
                    name="Markdown",
                    widgets={"markdown_css": {"type": pn.widgets.TextAreaInput, "height": 600}},
                ),
                pn.Param(
                    self.param.dataframe_css,
                    name="Dataframe",
                    widgets={"dataframe_css": {"type": pn.widgets.TextAreaInput, "height": 600}},
                ),
            ),
        )

    def view(self):
        return pn.Column(
            self.color_scheme.view(),
            self.css_view,
        )

    def _get_markdown_css(self):
        return f"""\
.codehilite  {{
    background: {self.color_scheme.theme.background.card};
    border-radius: 4px;
    padding: 1px;
}}
.markdown a {{
    color: {self.color_scheme.secondary.color_a400};
    text-decoration: none currentcolor solid;
}}
.markdown a:hover {{
    text-decoration: underline currentcolor solid;
}}

"""

    def _get_panel_css(self):
        panel_css = f"""\
body {{
    background-color: {self.color_scheme.theme.background.background};
    color: {self.color_scheme.theme.foreground.base};
}}

h1, h2, h3, h4, h5 {{
color: {self.color_scheme.theme.foreground.base} !important;
}}

.bk-root .bk-tabs-header .bk-tab.bk-active {{
    background:  {self.color_scheme.primary.color_500};
    color:  {self.color_scheme.primary.contrast_500};
    border-color:  {self.color_scheme.primary.color_500};
}}
"""
        panel_css += self._get_panel_button_outlined_css(button_type="default", color=self.color_scheme.theme.foreground.base, border_color=self.color_scheme.theme.foreground.disabled_text)
        panel_css += self._get_panel_button_contained_css(button_type="primary", background_color=self.color_scheme.primary.color_500, color=self.color_scheme.primary.contrast_500)
        panel_css += self._get_panel_button_contained_css(button_type="success", background_color=self.color_scheme.secondary.color_a400, color=self.color_scheme.secondary.contrast_a400)
        panel_css += self._get_panel_button_contained_css(button_type="warning", background_color=self.color_scheme.warning.color_500, color=self.color_scheme.warning.contrast_500)
        panel_css += self._get_panel_button_contained_css(button_type="danger", background_color=self.color_scheme.warning.color_500, color=self.color_scheme.warning.contrast_500)

        panel_css += self._get_panel_input_css()
        panel_css += self._get_slick_grid_css()
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
    color: {self.color_scheme.theme.foreground.disabled_button};
    background-color: transparent;
    border-color: {self.color_scheme.theme.background.disabled_button};
}}"""

    def _get_panel_input_css(self):
        return f"""\
.bk-root .bk-input {{
    background: {self.color_scheme.theme.background.background};
    color: {self.color_scheme.theme.foreground.text};
    border: 1px solid {self.color_scheme.theme.foreground.disabled_text};
    border-radius: 4px;
}}
.bk-root .bk-input:focus {{
    background: {self.color_scheme.theme.background.dialog};
    color: {self.color_scheme.theme.foreground.text};
    border-color: {self.color_scheme.primary.color_500};
    box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(102, 175, 233, 0.6);
}}

.bk-root .bk-input::placeholder,
.bk-root .bk-input:-ms-input-placeholder,
.bk-root .bk-input::-moz-placeholder,
.bk-root .bk-input::-webkit-input-placeholder {{
    color: #999;
    opacity: 1;
}}

.bk-root .bk-input[disabled],
.bk-root .bk-input[readonly] {{
    cursor: not-allowed;
    opacity: 1;
    color: {self.color_scheme.theme.foreground.disabled_button};
    background-color: transparent;
    border-color: {self.color_scheme.theme.background.disabled_button};
}}

.bk-root select[multiple].bk-input,
.bk-root select[size].bk-input,
.bk-root textarea.bk-input {{
    height: auto;
}}

.bk-root .bk-input-group {{
    width: 100%;
    height: 100%;
    display: inline-flex;
    display: -webkit-inline-flex;
    flex-wrap: nowrap;
    -webkit-flex-wrap: nowrap;
    align-items: start;
    -webkit-align-items: start;
    flex-direction: column;
    -webkit-flex-direction: column;
    white-space: nowrap;
}}
        """

    def _get_panel_button_contained_css(self, button_type="default", background_color="black", color="white"):
        return f"""\
.bk-root .bk-btn-{button_type} {{
    color: {color};
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
  color: {self.color_scheme.theme.foreground.disabled_button};
  background-color: {self.color_scheme.theme.background.disabled_button};
}}"""

# border-bottom: 1px solid {self.color_scheme.primary};
    def _get_dataframe_css(self):
        return f"""\
table.panel-df {{
    color: {self.color_scheme.theme.foreground.base};
    border-radius: 4px;
}}
.panel-df tbody tr:nth-child(odd) {{
    background: {self.color_scheme.theme.background.card};
}}
.panel-df tbody tr {{
    background: {self.color_scheme.theme.background.card};
    border-top-style: solid;
    border-top-width: 1px;
    border-top-color: {self.color_scheme.theme.foreground.disabled_text};
   }}
.panel-df thead {{
    background: {self.color_scheme.theme.background.card};
    color: {self.color_scheme.theme.foreground.base};
    font-weight: 500px;
}}
.panel-df tr:hover:nth-child(odd) {{
    background: {self.color_scheme.theme.background.card} !important;
}}
.panel-df tr:hover {{
    background: {self.color_scheme.theme.background.card} !important;
}}
.panel-df thead tr:hover:nth-child(1) {{
    background-color: inherit !important;
}}

.panel-df thead:hover {{
    background: {self.color_scheme.theme.background.card} !important;
}}"""


    def _get_slick_grid_css(self):
        return f"""\
.bk-root .slick-header-column.ui-state-default {{
    border-right: 1px solid silver;
}}

.bk-root .slick-sort-indicator-numbered {{
    color: #6190CD;
}}

.bk-root .slick-sortable-placeholder {{
    background: silver;
}}

.bk-root .slick-cell,
.bk-root .slick-headerrow-column,
.bk-root .slick-footerrow-column {{
    border: 1px solid transparent;
    border-right: 1px dotted silver;
    border-bottom-color: silver;
}}

.bk-root .slick-cell,
.bk-root .slick-headerrow-column {{
    border-bottom-color: silver;
}}

.bk-root .slick-footerrow-column {{
    border-top-color: silver;
}}

.bk-root .slick-cell.highlighted {{
    background: lightskyblue;
    background: rgba(0, 0, 255, 0.2);
}}

.bk-root .slick-cell.flashing {{
    border: 1px solid red !important;
}}

.bk-root .slick-cell.editable {{
    background: white;
    border-color: black;
    border-style: solid;
}}

.bk-root .slick-reorder-proxy {{
    background: blue;
    opacity: 0.15;
}}

.bk-root .slick-reorder-guide {{
    background: blue;
    opacity: 0.7;
}}

.bk-root .slick-selection {{
    border: 2px dashed black;
}}

.bk-root .slick-header-columns {{
    border-bottom: 1px solid silver;
}}

.bk-root .slick-header-column {{
    border-right: 1px solid silver;
    background: {self.color_scheme.theme.background.dialog};
    font-weight: 500px;
}}

.bk-root .slick-header-column:hover,
.bk-root .slick-header-column-active {{
    background: {self.color_scheme.theme.background.dialog} url('images/header-columns-over-bg.gif') repeat-x center bottom;
}}

.bk-root .slick-headerrow {{
    background: #fafafa;
}}

.bk-root .slick-headerrow-column {{
    background: #fafafa;
}}

.bk-root .slick-row.ui-state-active {{
    background: #F5F7D7;
}}

.bk-root .slick-row {{
    background: {self.color_scheme.theme.background.dialog};
}}

.bk-root .slick-row.selected {{
    background: #DFE8F6;
}}

.bk-root .slick-group {{
    border-bottom: 2px solid silver;
}}

.bk-root .slick-group-totals {{
    color: gray;
    background: white;
}}

.bk-root .slick-cell.selected {{
    background-color: {self.color_scheme.secondary.color_a200};
    color: {self.color_scheme.secondary.contrast_a200};
}}

.bk-root .slick-cell.active {{
    border-color: gray;
    border-style: solid;
}}

.bk-root .slick-sortable-placeholder {{
    background: silver !important;
}}

.bk-root .slick-row.odd {{
    background: {self.color_scheme.theme.background.dialog};
}}

.bk-root .slick-row.ui-state-active {{
    background: #F5F7D7;
}}

.bk-root .slick-row.loading {{
    opacity: 0.5;
}}

.bk-root .slick-cell.invalid {{
    border-color: red;
}}

@-moz-keyframes slickgrid-invalid-hilite {{
    from {{
        box-shadow: 0 0 6px red;
    }}
    to {{
        box-shadow: none;
    }}
}}

@-webkit-keyframes slickgrid-invalid-hilite {{
    from {{
        box-shadow: 0 0 6px red;
    }}
    to {{
        box-shadow: none;
    }}
}}

.bk-root .slick-header-button {{
.bk-root .slick-header-menuitem-disabled {{
    color: silver;
}}

.bk-root .slick-columnpicker {{
    background: #f0f0f0;
}}

.bk-root .slick-columnpicker li {{
    background: none;
}}

.bk-root .slick-columnpicker li a:hover {{
    background: white;
}}

.bk-root .slick-pager .ui-icon-container {{
    border-color: gray;
}}

.bk-root .bk-cell-special-defaults {{
    border-right-color: silver;
    border-right-style: solid;
    background: #f5f5f5;
}}

.bk-root .bk-cell-select {{
    border-right-color: silver;
    border-right-style: solid;
    background: #f5f5f5;
}}

.bk-root .bk-cell-index {{
    border-right-color: silver;
    border-right-style: solid;
    background: #f5f5f5;
    color: gray;
}}

"""

