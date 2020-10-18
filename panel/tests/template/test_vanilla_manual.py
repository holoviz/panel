import panel as pn
import numpy as np
import holoviews as hv


def test_vanilla():
    """Returns an app that uses the vanilla template in various ways.

Inspect the app and verify that the issues of [Issue 1641]\
(https://github.com/holoviz/panel/issues/1641) have been solved

- Navbar is "sticky"/ fixed to the top
- Navbar supports adding header items to left, center and right
- There is a nice padding/ margin everywhere
- Independent scroll for sidebar and main
- Only vertical scrollbars
"""
    vanilla = pn.template.VanillaTemplate(title="Vanilla Template")

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
    vanilla.sidebar.append(pn.pane.Markdown(test_vanilla.__doc__))
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
    return vanilla


if __name__.startswith("bokeh"):
    test_vanilla().servable()
