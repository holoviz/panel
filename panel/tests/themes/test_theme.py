from panel.themes import Theme, THEMES
from panel.templates import AppTemplate
import pytest
import random

@pytest.mark.parametrize("theme", THEMES)
def test_configure(theme):
    Theme(theme=theme).configure()

def test_app_with_template(theme="bootstrap"):
    # Todo: Right now the order of app and Theme.configure matters
    app = AppTemplate()

    import pandas as pd
    import hvplot.pandas
    import holoviews.plotting.bokeh
    import holoviews as hv
    import numpy as np
    import panel as pn

    def sine(frequency=1.0, amplitude=1.0, function='sin'):
        xs = np.arange(200)/200*20.0
        ys = amplitude*getattr(np, function)(frequency*xs)
        return pd.DataFrame(dict(y=ys), index=xs).hvplot()

    dmap = hv.DynamicMap(sine, kdims=['frequency', 'amplitude', 'function']).redim.range(
        frequency=(0.1, 10), amplitude=(1, 10)).redim.values(function=['sin', 'cos', 'tan'])

    hv_panel = pn.panel(dmap)
    app.main[:]=["# Hello World"]

    Theme(theme=theme).configure()
    return app

if __name__.startswith("bk"):
    theme = random.choice(THEMES)
    theme="angular_dark"
    print(theme)
    test_app_with_template(theme=theme).servable()


