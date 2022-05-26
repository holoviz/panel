import holoviews as hv
import numpy as np

import panel as pn

LOGO = "https://panel.holoviz.org/_static/logo_horizontal.png"


def test_vanilla_with_sidebar():
    """Returns an app that uses the vanilla template in various ways.

Inspect the app and verify that the issues of [Issue 1641]\
(https://github.com/holoviz/panel/issues/1641) have been solved

- Navbar is "sticky"/ fixed to the top
- Navbar supports adding header items to left, center and right
- There is a nice padding/ margin everywhere
- Independent scroll for sidebar and main
- Only vertical scrollbars
"""
    vanilla = pn.template.VanillaTemplate(
        title="Vanilla Template",
        logo=LOGO,
    )

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
    vanilla.sidebar.append(pn.pane.Markdown(test_vanilla_with_sidebar.__doc__))
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


def test_vanilla_with_no_sidebar():
    """Returns an app that uses the vanilla template in various ways.

Inspect the app and verify that the issues of [Issue 1641]\
(https://github.com/holoviz/panel/issues/1641) have been solved

- Navbar is "sticky"/ fixed to the top
- Navbar supports adding header items to left, center and right
- There is a nice padding/ margin everywhere
- Independent scroll for sidebar and main
- Only vertical scrollbars
"""
    vanilla = pn.template.VanillaTemplate(
        title="Vanilla Template",
        logo=LOGO,
        favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel/2781d86d4ed141889d633748879a120d7d8e777a/assets/images/favicon.ico",
    )

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
    vanilla.main.append(pn.pane.Markdown(test_vanilla_with_no_sidebar.__doc__))
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


if __name__.startswith("bokeh"):
    pn.extension(sizing_mode="stretch_width")
    test_vanilla_with_sidebar().servable()
    # test_vanilla_with_no_sidebar().servable()
