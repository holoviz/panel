import param

import panel as pn

from panel.themes.theme_builder import color_scheme
from panel.themes.theme_builder import css_generator

class ThemeBuilder(param.Parameterized):
    css_generator = param.ClassSelector(class_=css_generator.CssGenerator)
    color_scheme = param.ObjectSelector(default=color_scheme.COLOR_SCHEMES[2], objects=color_scheme.COLOR_SCHEMES, precedence=0.2)

    def __init__(self, **params):
        if not "css_generator" in params:
            params["css_generator"]=css_generator.CssGenerator()
        super().__init__(**params)


        # @Philippfr: They still take up some space,
        # i.e. the Theme Builder header is not shown on top
        # How do I solve that?
        self._panel_css_pane = pn.pane.HTML(height=0, width=0)
        self._dataframe_css_pane = pn.pane.HTML(height=0, width=0)

        self.css_generator.color_scheme.update(self.color_scheme)
        self._set_panel_css_pane()
        self._set_dataframe_css_pane()

    @param.depends("color_scheme", watch=True)
    def _update_css_generator_color_scheme(self):
        self.css_generator.color_scheme.update(self.color_scheme)

    @param.depends("css_generator", "css_generator.panel_css", watch=True)
    def _set_panel_css_pane(self):
        print("_set_panel_css_pane", self.css_generator.color_scheme.primary.name)
        print("diff", self._panel_css_pane.object!=self.css_generator.panel_css)
        self._panel_css_pane.object = "<style>.a {width: 100%}" + self.css_generator.panel_css + "</style>"

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
            self._dataframe_css_pane, #9c27b0
            "# Theme Builder",
            self.param.color_scheme,
            # pn.Param(
            #     self,
            #     parameters=["css_generator", "color_scheme"],
            #     show_name=False,
            #     # @Philipfr: I don't want to show expand button
            #     # But it does not seem to work?
            #     expand=False,
            # ),
            self._css_generator_view,
            **params,
        )