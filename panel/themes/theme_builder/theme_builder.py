import param

import panel as pn

from .color_scheme import COLOR_SCHEMES
from .css_generator import CSS_GENERATORS


class ThemeBuilder(param.Parameterized):
    css_generator = param.ObjectSelector(default=CSS_GENERATORS[1], objects=CSS_GENERATORS, precedence=0.1)
    color_scheme = param.ObjectSelector(default=COLOR_SCHEMES[0], objects=COLOR_SCHEMES, precedence=0.2)

    def __init__(self, **params):
        super().__init__(**params)

        # @Philippfr: They still take up some space,
        # i.e. the Theme Builder header is not shown on top
        # How do I solve that?
        self._panel_css_pane = pn.pane.HTML(height=0, width=0)
        self._dataframe_css_pane = pn.pane.HTML(height=0, width=0)

        self._set_panel_css_pane()
        self._set_dataframe_css_pane()

    @param.depends("color_scheme", watch=True)
    def _update_css_generator_color_scheme(self):
        self.css_generator.color_scheme.update(self.color_scheme)

    @param.depends("css_generator", "css_generator.panel_css", watch=True)
    def _set_panel_css_pane(self):
        # print("_set_panel_css_pane", self.css_generator.panel_css)
        self._panel_css_pane.object = "<style>" + self.css_generator.panel_css + "</style>"

    @param.depends("css_generator", "css_generator.dataframe_css", watch=True)
    def _set_dataframe_css_pane(self):
        # print("_set_dataframe_css_pane")
        self._dataframe_css_pane.object = "<style>" + self.css_generator.dataframe_css + "</style>"

    @param.depends("css_generator")
    def _css_generator_view(self):
        return self.css_generator.view()

    def view(self, **params):
        return pn.Column(
            self._panel_css_pane,
            self._dataframe_css_pane,
            "# Theme Builder",
            pn.Param(
                self,
                parameters=["css_generator", "color_scheme"],
                show_name=False,
                # @Philipfr: I don't want to show expand button
                # But it does not seem to work?
                expand=False,
            ),
            self._css_generator_view,
            **params,
        )
