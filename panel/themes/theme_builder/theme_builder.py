import param

import panel as pn

from panel.themes.theme_builder import color_scheme
from panel.themes.theme_builder import css_generator


class ThemeBuilder(param.Parameterized):
    css_generator = param.ClassSelector(class_=css_generator.CssGenerator)
    color_scheme = param.ObjectSelector(
        default=color_scheme.COLOR_SCHEMES[2], objects=color_scheme.COLOR_SCHEMES, precedence=0.2
    )

    def __init__(self, **params):
        if not "css_generator" in params:
            params["css_generator"] = css_generator.CssGenerator()
        super().__init__(**params)

        # @Philippfr: They still take up some space,
        # i.e. the Theme Builder header is not shown on top
        # How do I solve that?
        self._panel_css_pane = pn.pane.HTML(height=0, width=0)
        self._markdown_css_pane = pn.pane.HTML(height=0, width=0)
        self._dataframe_css_pane = pn.pane.HTML(height=0, width=0)

        self.css_generator.color_scheme.update(self.color_scheme)
        self._set_panel_css_pane()
        self._set_markdown_css_pane()
        self._set_dataframe_css_pane()

    @param.depends("color_scheme", watch=True)
    def _update_css_generator_color_scheme(self):
        self.css_generator.color_scheme.update(self.color_scheme)

    @param.depends("css_generator", "css_generator.panel_css", watch=True)
    def _set_panel_css_pane(self):
        self._panel_css_pane.object = (
            "<style>.a {width: 100%}" + self.css_generator.panel_css + "</style>"
        )

    @param.depends("css_generator", "css_generator.dataframe_css", watch=True)
    def _set_dataframe_css_pane(self):
        self._dataframe_css_pane.object = "<style>" + self.css_generator.dataframe_css + "</style>"

    @param.depends("css_generator", "css_generator.markdown_css", watch=True)
    def _set_markdown_css_pane(self):
        self._markdown_css_pane.object = "<style>" + self.css_generator.markdown_css + "</style>"

    def view(self, **params):
        return pn.Column(
            "### Selections",
            pn.Param(
                self,
                parameters=["color_scheme"],
                expand_button=False,
                show_name=False,
                sizing_mode="stretch_width",
            ),
            self.css_generator.view(),
            self._panel_css_pane,
            self._markdown_css_pane,
            self._dataframe_css_pane,
            **params,
        )
