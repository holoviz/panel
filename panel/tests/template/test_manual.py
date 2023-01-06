import holoviews as hv
import numpy as np
import pytest

import panel as pn

LOGO = "https://panel.holoviz.org/_static/logo_horizontal.png"


TEMPLATES_NAMES = {
    "vanilla": pn.template.VanillaTemplate,
    "golden": pn.template.GoldenTemplate,
    "material": pn.template.MaterialTemplate,
    "bootstrap": pn.template.BootstrapTemplate,
    "react": pn.template.ReactTemplate
}

def _get_template_class(template_class=pn.template.VanillaTemplate):
    template_name=pn.state.session_args.get("template", None)
    if template_name:
        template_name=template_name[0].decode("utf-8")
        template_class=TEMPLATES_NAMES[template_name]
    return template_class

def manualtest_template_with_sidebar(template_class=pn.template.VanillaTemplate, theme=pn.template.DefaultTheme):
    """Returns an app that uses the vanilla template in various ways.

Inspect the app and verify that the issues of [Issue 1641]\
(https://github.com/holoviz/panel/issues/1641) have been solved

- Navbar is "sticky"/ fixed to the top
- Navbar supports adding header items to left, center and right
- There is a nice padding/ margin everywhere
- Independent scroll for sidebar and main
- Only vertical scrollbars
"""
    vanilla = template_class(
        title=template_class.__name__,
        logo=LOGO,
        theme=theme
    )
    vanilla.site="My Site"


    xs = np.linspace(0, np.pi)
    freq = pn.widgets.FloatSlider(name="Frequency", start=0, end=10, value=2,
                                  sizing_mode='stretch_width')
    phase = pn.widgets.FloatSlider(name="Phase", start=0, end=np.pi,
                                   sizing_mode='stretch_width')

    @pn.depends(freq=freq, phase=phase)
    def sine(freq, phase):
        return hv.Curve((xs, np.sin(xs * freq + phase))).opts(
            responsive=True, min_height=150, max_height=450)

    @pn.depends(freq=freq, phase=phase)
    def cosine(freq, phase):
        return hv.Curve((xs, np.cos(xs * freq + phase))).opts(
            responsive=True, min_height=150, max_height=450)

    vanilla.sidebar.append(freq)
    vanilla.sidebar.append(phase)
    vanilla.sidebar.append(pn.pane.Markdown(manualtest_template_with_sidebar.__doc__, height=280,
                                            sizing_mode='stretch_width'))
    vanilla.sidebar.append(pn.pane.Markdown("## Sidebar Item\n" * 50))

    row1 = pn.Row(
        pn.Card(hv.DynamicMap(sine), title="Sine"),
        pn.Card(hv.DynamicMap(cosine), title="Cosine"),
    )
    row2 = pn.Row(
        pn.Card(hv.DynamicMap(sine), title="Sine"),
        pn.Card(hv.DynamicMap(cosine), title="Cosine"),
    )
    row3 = pn.Row(
        pn.Card(hv.DynamicMap(sine), title="Sine"),
        pn.Card(hv.DynamicMap(cosine), title="Cosine"),
    )
    if issubclass(template_class, pn.template.ReactTemplate):
        vanilla.main[0:2, :] = row1
        vanilla.main[2:4, :] = row2
        vanilla.main[4:6, :] = row3
    else:
        vanilla.main.append(row1)
        vanilla.main.append(row2)

    vanilla.header[:] = [
        pn.Row(
            pn.widgets.Button(name="Left", sizing_mode="fixed", width=50),
            pn.layout.HSpacer(),
            pn.widgets.Button(name="Center", sizing_mode="fixed", width=50),
            pn.layout.HSpacer(),
            pn.widgets.Button(name="Right", sizing_mode="fixed", width=50),
        )
    ]
    return vanilla


def manualtest_template_with_no_sidebar(template_class=pn.template.VanillaTemplate, theme=pn.template.DefaultTheme):
    """Returns an app that uses the vanilla template in various ways.

Inspect the app and verify that the issues of [Issue 1641]\
(https://github.com/holoviz/panel/issues/1641) have been solved

- Navbar is "sticky"/ fixed to the top
- Navbar supports adding header items to left, center and right
- There is a nice padding/ margin everywhere
- Independent scroll for sidebar and main
- Only vertical scrollbars
"""
    vanilla = template_class(
        title="Vanilla Template",
        logo=LOGO,
        favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel/2781d86d4ed141889d633748879a120d7d8e777a/assets/images/favicon.ico",
        theme=theme
    )
    vanilla.main_max_width="1100px"

    xs = np.linspace(0, np.pi)
    freq = pn.widgets.FloatSlider(name="Frequency", start=0, end=10, value=2)
    phase = pn.widgets.FloatSlider(name="Phase", start=0, end=np.pi)

    @pn.depends(freq=freq, phase=phase)
    def sine(freq, phase):
        return hv.Curve((xs, np.sin(xs * freq + phase))).opts(responsive=True, min_height=400)

    @pn.depends(freq=freq, phase=phase)
    def cosine(freq, phase):
        return hv.Curve((xs, np.cos(xs * freq + phase))).opts(responsive=True, min_height=400)

    markdown = pn.pane.Markdown(manualtest_template_with_no_sidebar.__doc__)
    row1 = pn.Row(
        pn.Card(hv.DynamicMap(sine), title="Sine"),
        pn.Card(hv.DynamicMap(cosine), title="Cosine"),
    )
    row2 = pn.Row(
        pn.Card(hv.DynamicMap(sine), title="Sine"),
        pn.Card(hv.DynamicMap(cosine), title="Cosine"),
    )
    if issubclass(template_class, pn.template.ReactTemplate):
        vanilla.main[0, :] = freq
        vanilla.main[1, :] = phase
        vanilla.main[2, :] = markdown
        vanilla.main[3:5, :] = row1
        vanilla.main[5:7, :] = row2
    else:
        vanilla.main.append(freq)
        vanilla.main.append(phase)
        vanilla.main.append(markdown)
        vanilla.main.append(row1)
        vanilla.main.append(row2)

    vanilla.header[:] = [
        pn.Row(
            pn.widgets.Button(name="Left", sizing_mode="fixed", width=50),
            pn.layout.HSpacer(),
            pn.widgets.Button(name="Center", sizing_mode="fixed", width=50),
            pn.layout.HSpacer(),
            pn.widgets.Button(name="Right", sizing_mode="fixed", width=50),
        )
    ]
    return vanilla

TEMPLATES = [
    (pn.template.VanillaTemplate,),
    (pn.template.MaterialTemplate,),
    (pn.template.BootstrapTemplate,),
    (pn.template.GoldenTemplate,),
]

@pytest.mark.parametrize(["template_class"], TEMPLATES)
def test_all_templates_with_sidebar(template_class):
    manualtest_template_with_sidebar(template_class=template_class)

@pytest.mark.parametrize(["template_class"], TEMPLATES)
def test_all_templates_with_no_sidebar(template_class):
    manualtest_template_with_no_sidebar(template_class=template_class)

def _get_template_func(template_func=manualtest_template_with_sidebar):
    app_name = pn.state.session_args.get("app", None)
    if app_name:
        app_name = app_name[0].decode("utf-8")
        if app_name == "no_sidebar":
            return manualtest_template_with_no_sidebar
        elif app_name == "sidebar":
            return manualtest_template_with_sidebar
    return template_func

def _get_theme():
    theme_name = pn.state.session_args.get("theme", None)
    if theme_name:
        theme_name = theme_name[0].decode("utf-8")
        if theme_name == "dark":
            return pn.template.DarkTheme
        else:
            return pn.template.DefaultTheme
    return pn.template.DefaultTheme

def _get_app():
    template_class = _get_template_class()
    template_func = _get_template_func()
    theme = _get_theme()
    return template_func(template_class=template_class, theme=theme)

if pn.state.served:
    pn.extension(sizing_mode="stretch_width")
    _get_app().servable()
    # manualtest_template_with_no_sidebar().servable()
