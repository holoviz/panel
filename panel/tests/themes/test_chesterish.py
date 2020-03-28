import panel as pn
pn.themes.Theme(theme="chesterish").configure()

from panel.tests.themes.theme_test_app import ThemeTestApp
ThemeTestApp().view().servable()

