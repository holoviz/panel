"""Tests of the Tqdm indicator"""
import panel as pn

from panel.widgets import Tqdm


def test_tqdm():
    tqdm = Tqdm(layout="row", sizing_mode="stretch_width")

    for index in tqdm(range(0, 3)):
        pass

    assert tqdm.value == 3
    assert tqdm.max == 3
    assert tqdm.text.startswith('100% 3/3')

    assert isinstance(tqdm.progress, pn.widgets.indicators.Progress)
    assert isinstance(tqdm.text_pane, pn.pane.Str)
    assert isinstance(tqdm.layout, pn.Row)


def test_tqdm_leave_false():
    tqdm = Tqdm(layout="row", sizing_mode="stretch_width")

    for index in tqdm(range(0, 3), leave=False):
        pass

    assert tqdm.value == 0
    assert tqdm.max == 3
    assert tqdm.text == ''


def test_tqdm_color():
    tqdm = Tqdm()

    for index in tqdm(range(0, 3), colour='red'):
        pass

    assert tqdm.text_pane.style == {'color': 'red'}


def get_tqdm_app():
    import time

    import numpy as np
    import pandas as pd

    tqdm = Tqdm(layout="row", sizing_mode="stretch_width")

    def run(*events):
        for index in tqdm(range(0, 10)):
            time.sleep(0.2)

    button = pn.widgets.Button(name="Run Loop", button_type="primary")
    button.on_click(run)

    # Register Pandas. This gives DataFrame.progress_apply method
    tqdm.tqdm.pandas(desc="my bar!")

    df = pd.DataFrame(np.random.randint(0, 100, (100000, 6)))

    def run_df(*events):
        df.progress_apply(lambda x: x ** 2)

    pandas_button = pn.widgets.Button(name="Pandas Apply", button_type="success")
    pandas_button.on_click(run_df)
    pandas_button

    component = pn.Column(button, pandas_button, tqdm, sizing_mode="stretch_width")
    template = pn.template.FastListTemplate(
        title="Panel - Tqdm Indicator",
        main=[component],
        sidebar=[
            pn.Param(tqdm, sizing_mode="stretch_width"),
        ],
    )
    return template

def get_tqdm_app_simple():
    import time

    tqdm = Tqdm(layout="row", sizing_mode="stretch_width")

    def run(*events):
        for index in tqdm(range(0, 10)):
            time.sleep(0.2)

    button = pn.widgets.Button(name="Run Loop", button_type="primary")
    button.on_click(run)
    return pn.Column(
        tqdm, button
    )

if __name__.startswith("bokeh"):
    # get_tqdm_app_simple().servable()
    get_tqdm_app().servable()
