import panel as pn
pn.themes.Theme(theme="angular_dark").configure()

from panel.tests.themes.theme_test_app import ThemeTestApp
ThemeTestApp().view().servable()

