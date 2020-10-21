import panel as pn
import numpy as np
import holoviews as hv
import pytest

LOGO = "https://panel.holoviz.org/_static/logo_horizontal.png"


TEMPLATES_NAMES = {
    "vanilla": pn.template.VanillaTemplate,
    "golden": pn.template.GoldenTemplate,
    "material": pn.template.MaterialTemplate,
}

def _get_template_class(template_class=pn.template.VanillaTemplate):
    template_name=pn.state.session_args.get("template", None)
    if template_name:
        template_name=template_name[0].decode("utf-8")
        template_class=TEMPLATES_NAMES[template_name]
    return template_class

def test_template_with_sidebar(template_class=pn.template.VanillaTemplate):
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
    )

    pn.config.sizing_mode = "stretch_width"

    xs = np.linspace(0, np.pi)
    freq = pn.widgets.FloatSlider(name="Frequency", start=0, end=10, value=2)
    phase = pn.widgets.FloatSlider(name="Phase", start=0, end=np.pi)

    @pn.depends(freq=freq, phase=phase)
    def sine(freq, phase):
        return hv.Curve((xs, np.sin(xs * freq + phase))).opts(responsive=True, min_height=400)

    @pn.depends(freq=freq, phase=phase)
    def cosine(freq, phase):
        return hv.Curve((xs, np.cos(xs * freq + phase))).opts(responsive=True, min_height=400)

    vanilla.sidebar.append(freq)
    vanilla.sidebar.append(phase)
    vanilla.sidebar.append(pn.pane.Markdown(test_template_with_sidebar.__doc__))
    vanilla.sidebar.append(pn.pane.Markdown("## Sidebar Item\n" * 50))

    vanilla.main.append(
        pn.Row(
            pn.Card(hv.DynamicMap(sine), title="Sine"),
            pn.Card(hv.DynamicMap(cosine), title="Cosine"),
        )
    )
    vanilla.main.append(
        pn.Row(
            pn.Card(hv.DynamicMap(sine), title="Sine"),
            pn.Card(hv.DynamicMap(cosine), title="Cosine"),
        )
    )
    vanilla.header[:] = [
        pn.Row(
            pn.widgets.Button(name="Left", sizing_mode="fixed", width=50),
            pn.layout.HSpacer(),
            pn.widgets.Button(name="Center", sizing_mode="fixed", width=50),
            pn.layout.HSpacer(),
            pn.widgets.Button(name="Right", sizing_mode="fixed", width=50),
        )
    ]
    vanilla.main_max_width = "600px"
    return vanilla


def test_template_with_no_sidebar(template_class=pn.template.VanillaTemplate):
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
    )

    pn.config.sizing_mode = "stretch_width"

    xs = np.linspace(0, np.pi)
    freq = pn.widgets.FloatSlider(name="Frequency", start=0, end=10, value=2)
    phase = pn.widgets.FloatSlider(name="Phase", start=0, end=np.pi)

    @pn.depends(freq=freq, phase=phase)
    def sine(freq, phase):
        return hv.Curve((xs, np.sin(xs * freq + phase))).opts(responsive=True, min_height=400)

    @pn.depends(freq=freq, phase=phase)
    def cosine(freq, phase):
        return hv.Curve((xs, np.cos(xs * freq + phase))).opts(responsive=True, min_height=400)

    vanilla.main.append(freq)
    vanilla.main.append(phase)
    vanilla.main.append(pn.pane.Markdown(test_template_with_no_sidebar.__doc__))
    vanilla.main.append(
        pn.Row(
            pn.Card(hv.DynamicMap(sine), title="Sine"),
            pn.Card(hv.DynamicMap(cosine), title="Cosine"),
        )
    )
    vanilla.main.append(
        pn.Row(
            pn.Card(hv.DynamicMap(sine), title="Sine"),
            pn.Card(hv.DynamicMap(cosine), title="Cosine"),
        )
    )
    vanilla.header[:] = [
        pn.Row(
            pn.widgets.Button(name="Left", sizing_mode="fixed", width=50),
            pn.layout.HSpacer(),
            pn.widgets.Button(name="Center", sizing_mode="fixed", width=50),
            pn.layout.HSpacer(),
            pn.widgets.Button(name="Right", sizing_mode="fixed", width=50),
        )
    ]
    vanilla.main_max_width = "600px"
    return vanilla

TEMPLATES = [
    (pn.template.VanillaTemplate, ),
    (pn.template.MaterialTemplate),
    (pn.template.BootstrapTemplate),
    (pn.template.GoldenTemplate),
]

@pytest.mark.parametrize(["template_class"], TEMPLATES)
def test_all_templates_with_sidebar(template_class):
    test_template_with_sidebar(template_class=template_class)

@pytest.mark.parametrize(["template_class"], TEMPLATES)
def test_all_templates_with_no_sidebar(template_class):
    test_template_with_no_sidebar(template_class=template_class)

def _get_template_func(template_func=test_template_with_sidebar):
    app_name=pn.state.session_args.get("app", None)
    if app_name:
        app_name=app_name[0].decode("utf-8")
        if app_name=="no_sidebar":
            return test_template_with_no_sidebar
        elif app_name=="sidebar":
            return test_template_with_sidebar
    return template_func

def _get_app():
    template_class = _get_template_class()
    template_func = _get_template_func()
    return template_func(template_class=template_class)

if __name__.startswith("bokeh"):
    _get_app().servable()
    # test_template_with_no_sidebar().servable()
