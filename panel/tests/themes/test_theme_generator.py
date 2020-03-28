import panel as pn
from panel.themes.theme_generator import BoostrapThemeGenerator
from panel.tests.themes.theme_test_app import ThemeTestApp

pn.config.sizing_mode="stretch_width"

app = pn.Column(
    BoostrapThemeGenerator().view(),
    ThemeTestApp().view(),
    sizing_mode="stretch_width",
).servable()